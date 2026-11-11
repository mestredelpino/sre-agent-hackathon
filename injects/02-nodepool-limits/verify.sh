#!/usr/bin/env bash
set -euo pipefail
source "$(dirname -- "${BASH_SOURCE[0]}")/common.sh"
check_state
owned_pool
[[ -n "$pool" ]] || fail 'Scenario pool missing; unpinning the workload is not a fix.'
jq -e --argjson replicas "$S02_REPLICAS" '.spec.replicas == $replicas and .spec.template.spec.nodeSelector["injects.sre/scenario02"] == "limits"' <<<"$deployment" >/dev/null || fail 'Target replicas or scenario placement not preserved.'
k rollout status "deployment/$CUSTOMER_NAME" --timeout="${ROLLOUT_TIMEOUT}s"
deployment=$(k get deployment "$CUSTOMER_NAME" -o json)
jq -e --argjson replicas "$S02_REPLICAS" '.status.observedGeneration >= .metadata.generation and .status.readyReplicas == $replicas and .status.updatedReplicas == $replicas and .status.availableReplicas == $replicas' <<<"$deployment" >/dev/null || fail 'Target replica status not healthy.'
pods=$(k get pods -l "$CUSTOMER_SELECTOR" -o json)
jq -e --argjson replicas "$S02_REPLICAS" '[.items[] | select(.metadata.deletionTimestamp == null)] | length == $replicas and all(.[];
  .status.phase == "Running" and (.spec.nodeName | length > 0) and
  any(.status.conditions[]?; .type == "Ready" and .status == "True"))' <<<"$pods" >/dev/null || fail 'Pending, missing or unready replicas remain.'
while IFS= read -r node; do
  k get node "$node" -o json | jq -e --arg pool "$POOL" '
    .metadata.labels["karpenter.sh/nodepool"] == $pool and
    .metadata.labels["injects.sre/scenario02"] == "limits" and
    any(.status.conditions[]; .type == "Ready" and .status == "True")' >/dev/null || fail 'Pod is not on a Ready scenario node.'
done < <(jq -r '[.items[] | select(.metadata.deletionTimestamp == null) | .spec.nodeName] | unique[]' <<<"$pods")
printf '%s\n' "PASS: all $S02_REPLICAS replicas Ready, no Pending pods, and actual placement on Ready scenario-pool nodes."