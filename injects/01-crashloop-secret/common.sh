#!/usr/bin/env bash
set -euo pipefail
umask 077

HERE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
output=$(python3 "$HERE/../config.py") || exit
eval "$output"
STATE="$HERE/.state/$CONFIG_ID/baseline.json"
for executable in kubectl jq flock; do
  command -v "$executable" >/dev/null || { echo "Missing $executable" >&2; exit 1; }
done
k() { kubectl --kubeconfig="$KUBECONFIG" --context="$CONTEXT" --namespace="$NAMESPACE" --request-timeout="$REQUEST_TIMEOUT" "$@"; }
fail() { echo "$*" >&2; exit 1; }
server=$(k config view --minify -o jsonpath='{.clusters[0].cluster.server}')
[[ "$server" == "$EXPECTED_SERVER" ]] || fail "Cluster API does not match the inspected baseline."
deployment=$(k get deployment "$ORDER_NAME" -o json)
secret=$(k get secret "$BROKER_SECRET" -o json)
config=$(k get configmap "$BROKER_CONFIGMAP" -o json)
jq -e --arg container "$ORDER_CONTAINER" --arg image "$ORDER_IMAGE" --arg secret "$BROKER_SECRET" --arg password_env "$BROKER_PASSWORD_ENV" '
  .spec.replicas > 0 and (.spec.template.spec.containers | length == 1) and
  .spec.template.spec.containers[0].name == $container and
  ($image == "" or .spec.template.spec.containers[0].image == $image) and
  ([.spec.template.spec.containers[0].envFrom[]?.secretRef.name] | index($secret) != null) and
  ([.spec.template.spec.containers[0].env[]?.name] | index($password_env) == null)' <<<"$deployment" >/dev/null || fail "Deployment contract changed; inspect it before proceeding."
jq -e --arg key "$BROKER_PASSWORD_KEY" '.data[$key] | type == "string" and length > 0' <<<"$secret" >/dev/null || fail "Missing credential key."
jq -e --argjson broker "$BROKER_JSON" '.data[$broker.hostname_key] == $broker.host and .data[$broker.port_key] == $broker.port and .data[$broker.queue_key] == $broker.queue' <<<"$config" >/dev/null || fail "Queue contract changed."
mkdir -p "$(dirname "$STATE")"
chmod 700 "$HERE/.state" "$(dirname "$STATE")"
exec 9>"$(dirname "$STATE")/lock"
flock -n 9 || fail "Another Scenario 01 script is running."
check_baseline_ids() {
  [[ -f "$STATE" ]] || fail "No saved baseline. Do not guess the original password."
  jq -e --arg deployment_uid "$(jq -r '.metadata.uid' <<<"$deployment")" \
    --arg secret_uid "$(jq -r '.metadata.uid' <<<"$secret")" \
    '.deployment_uid == $deployment_uid and .secret_uid == $secret_uid' "$STATE" >/dev/null || fail "Resources were recreated; manual baseline review required."
}
pod_snapshot() {
  k get pods -l "$ORDER_SELECTOR" -o json | jq -ce --argjson recent "$RECENT_RESTARTS" --argjson target "$(jq '.spec.replicas' <<<"$deployment")" '
    [.items[] | select(.metadata.deletionTimestamp == null)] |
    if length != $target or any(.[]; .status.phase != "Running" or
      ([.status.conditions[]? | select(.type == "Ready" and .status == "True")] | length) != 1 or
      any(.status.containerStatuses[]?; .ready != true or
        ((.lastState.terminated.finishedAt // "1970-01-01T00:00:00Z" | fromdateiso8601) > (now - $recent))))
      then error("Replicas not Ready or a restart occurred within the configured interval")
    else [.[] | {uid:.metadata.uid, node:.spec.nodeName, statuses:[.status.containerStatuses[] | {name,restartCount}]}] | sort_by(.uid) end'
}