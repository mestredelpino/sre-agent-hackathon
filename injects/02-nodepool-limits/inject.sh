#!/usr/bin/env bash
set -euo pipefail
source "$(dirname -- "${BASH_SOURCE[0]}")/common.sh"
case "${1:---plan}" in
  --plan)
    printf '%s\n' "Cluster: $CONTEXT; namespace: $NAMESPACE" \
      "Create only NodePool $POOL with CPU limit $S02_CPU_LIMIT and allowed CPU sizes $S02_CPU_SIZES." \
      "Pin $CUSTOMER_NAME with a dedicated label/toleration and scale to $S02_REPLICAS replicas." \
      "Reference $NODECLASS_RESOURCE $NODECLASS read-only. No failure injected."
    exit 0 ;;
  --apply) ;;
  *) fail 'Usage: bash inject.sh [--plan|--apply]' ;;
esac
if [[ -f "$STATE" ]]; then
  check_state
else
  [[ -z "$(k get nodepool "$POOL" --ignore-not-found -o name)" ]] || fail 'Reserved NodePool name already exists.'
  jq -e '.spec.replicas > 0 and .status.readyReplicas == .spec.replicas and
    ((.spec.template.spec.nodeSelector // {}) | has("injects.sre/scenario02") | not) and
    ([.spec.template.spec.tolerations[]? | select(.key == "injects.sre/scenario02")] | length == 0)' <<<"$deployment" >/dev/null || fail 'Workload is not at a clean healthy baseline.'
  jq --arg token "inject02-$(date +%s)-$RANDOM" \
    '{uid:.metadata.uid,replicas:.spec.replicas,selector:(.spec.template.spec.nodeSelector // {}),
      tolerations:(.spec.template.spec.tolerations // []),token:$token}' <<<"$deployment" >"$STATE.tmp"
  mv "$STATE.tmp" "$STATE"
fi
owned_pool
if [[ -z "$pool" ]]; then
  python3 "$HERE/manifest.py" "$(jq -r '.token' "$STATE")" | k create -f - >/dev/null
else
  k patch nodepool "$POOL" --type=json -p "$(jq -nc --arg uid "$(jq -r '.metadata.uid' <<<"$pool")" --arg cpu "$S02_CPU_LIMIT" '[{op:"test",path:"/metadata/uid",value:$uid},{op:"add",path:"/spec/limits/cpu",value:$cpu}]')" >/dev/null
fi
selector=$(jq -c '.selector + {"injects.sre/scenario02":"limits"}' "$STATE")
tolerations=$(jq -c '.tolerations + [{key:"injects.sre/scenario02",value:"limits",operator:"Equal",effect:"NoSchedule"}]' "$STATE")
deployment_patch "$S02_REPLICAS" "$selector" "$tolerations"
printf '%s\n' "Injected: $CUSTOMER_NAME requires the dedicated pool $POOL with the configured CPU limit." \
  "Inspect Pending pods, events, NodeClaims and $POOL.spec.limits.cpu."