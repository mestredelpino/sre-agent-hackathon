#!/usr/bin/env bash
set -euo pipefail
source "$(dirname -- "${BASH_SOURCE[0]}")/common.sh"
check_state
owned_pool
selector=$(jq -c '.selector' "$STATE")
tolerations=$(jq -c '.tolerations' "$STATE")
expected_selector=$(jq -c '.selector + {"injects.sre/scenario02":"limits"}' "$STATE")
expected_tolerations=$(jq -c '.tolerations + [{key:"injects.sre/scenario02",value:"limits",operator:"Equal",effect:"NoSchedule"}]' "$STATE")
jq -e --argjson original "$selector" --argjson expected "$expected_selector" \
  '(.spec.template.spec.nodeSelector // {}) == $original or (.spec.template.spec.nodeSelector // {}) == $expected' <<<"$deployment" >/dev/null || fail 'Unexpected selector edits; review before reset.'
jq -e --argjson original "$tolerations" --argjson expected "$expected_tolerations" \
  '(.spec.template.spec.tolerations // []) == $original or (.spec.template.spec.tolerations // []) == $expected' <<<"$deployment" >/dev/null || fail 'Unexpected toleration edits; review before reset.'
deployment_patch "$(jq '.replicas' "$STATE")" "$selector" "$tolerations"
k rollout status "deployment/$CUSTOMER_NAME" --timeout="${ROLLOUT_TIMEOUT}s"
pods=$(k get pods --all-namespaces -o json)
jq -e --arg pool "$POOL" --argjson nodes "$(k get nodes -l "karpenter.sh/nodepool=$POOL" -o json | jq '[.items[].metadata.name]')" \
  '[.items[] | select(.metadata.deletionTimestamp == null and (.metadata.ownerReferences // [] | any(.kind == "DaemonSet") | not)) |
    .spec.nodeName as $node | select($nodes | index($node) != null)] | length == 0' <<<"$pods" >/dev/null || fail 'Non-DaemonSet pods still on scenario nodes; refusing NodePool deletion.'
if [[ -n "$pool" ]]; then
  jq -nc --arg uid "$(jq -r '.metadata.uid' <<<"$pool")" \
    '{apiVersion:"v1",kind:"DeleteOptions",preconditions:{uid:$uid},propagationPolicy:"Background"}' |
    k delete --raw "/apis/$POOL_API/nodepools/$POOL" -f - >/dev/null
  k wait --for=delete "nodepool/$POOL" --timeout="$(jq -r '.delete' <<<"$TIMING_JSON")s"
fi
if [[ -n "$(k get nodeclaims -l "karpenter.sh/nodepool=$POOL" -o name)" ]]; then
  k wait --for=delete nodeclaims -l "karpenter.sh/nodepool=$POOL" --timeout="$(jq -r '.delete' <<<"$TIMING_JSON")s"
fi
if [[ -n "$(k get nodes -l "karpenter.sh/nodepool=$POOL" -o name)" ]]; then
  k wait --for=delete nodes -l "karpenter.sh/nodepool=$POOL" --timeout="$(jq -r '.delete' <<<"$TIMING_JSON")s"
fi
printf '%s\n' 'Baseline replicas and scheduling restored; dedicated pool/claims/nodes removed.'