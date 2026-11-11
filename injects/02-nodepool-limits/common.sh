#!/usr/bin/env bash
set -euo pipefail
umask 077
HERE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
output=$(python3 "$HERE/../config.py") || exit
eval "$output"
POOL=$S02_POOL
STATE="$HERE/.state/$CONFIG_ID/baseline.json"
NODECLASS_RESOURCE=$(python3 "$HERE/manifest.py" --nodeclass-resource) || exit
for executable in kubectl jq flock; do
  command -v "$executable" >/dev/null || { echo "Missing $executable" >&2; exit 1; }
done
k() { kubectl --kubeconfig="$KUBECONFIG" --context="$CONTEXT" --namespace="$NAMESPACE" --request-timeout="$REQUEST_TIMEOUT" "$@"; }
fail() { echo "$*" >&2; exit 1; }
[[ "$(k config view --minify -o jsonpath='{.clusters[0].cluster.server}')" == "$EXPECTED_SERVER" ]] || fail 'Wrong cluster API.'
deployment=$(k get deployment "$CUSTOMER_NAME" -o json)
jq -e --arg container "$CUSTOMER_CONTAINER" --arg image "$CUSTOMER_IMAGE" '
  (.spec.template.spec.containers | length == 1) and
  .spec.template.spec.containers[0].name == $container and
  ($image == "" or .spec.template.spec.containers[0].image == $image)' <<<"$deployment" >/dev/null || fail 'Workload contract changed.'
k get "$NODECLASS_RESOURCE" "$NODECLASS" -o json | jq -e 'any(.status.conditions[]; .type == "Ready" and .status == "True")' >/dev/null || fail 'Referenced NodeClass is not Ready.'
mkdir -p "$(dirname "$STATE")"
chmod 700 "$HERE/.state" "$(dirname "$STATE")"
exec 9>"$(dirname "$STATE")/lock"
flock -n 9 || fail 'Another Scenario 02 script is running.'
check_state() {
  [[ -f "$STATE" ]] || fail 'No saved scenario baseline.'
  jq -e --arg uid "$(jq -r '.metadata.uid' <<<"$deployment")" '.uid == $uid' "$STATE" >/dev/null || fail 'Deployment recreated; manual review required.'
}
owned_pool() {
  pool=$(k get nodepool "$POOL" --ignore-not-found -o json)
  if [[ -n "$pool" ]]; then
    jq -e --arg token "$(jq -r '.token' "$STATE")" '.metadata.labels["injects.sre/owner"] == $token' <<<"$pool" >/dev/null || fail 'NodePool is not owned by this saved scenario.'
  fi
}
deployment_patch() {
  local replicas=$1 selector=$2 tolerations=$3
  jq -nc --arg uid "$(jq -r '.metadata.uid' <<<"$deployment")" \
    --arg version "$(jq -r '.metadata.resourceVersion' <<<"$deployment")" \
    --argjson replicas "$replicas" --argjson selector "$selector" --argjson tolerations "$tolerations" \
    '[{op:"test",path:"/metadata/uid",value:$uid},{op:"test",path:"/metadata/resourceVersion",value:$version},
      {op:"add",path:"/spec/replicas",value:$replicas},
      {op:"add",path:"/spec/template/spec/nodeSelector",value:$selector},
      {op:"add",path:"/spec/template/spec/tolerations",value:$tolerations}]' |
    k patch deployment "$CUSTOMER_NAME" --type=json --patch-file=/dev/stdin >/dev/null
}