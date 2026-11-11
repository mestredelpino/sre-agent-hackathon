#!/usr/bin/env bash
set -euo pipefail
source "$(dirname -- "${BASH_SOURCE[0]}")/common.sh"
case "${1:---plan}" in
  --plan)
    printf '%s\n' "Cluster: $CONTEXT" "Namespace: $NAMESPACE" \
      "Change only $BROKER_SECRET.data.$BROKER_PASSWORD_KEY, then roll $ORDER_NAME." \
      'Expected symptom: failed order POSTs; health may stay green.' \
      'No injection performed. Run with --apply only after facilitator approval.'
    exit 0 ;;
  --apply) ;;
  *) fail "Usage: bash inject.sh [--plan|--apply]" ;;
esac
if [[ -f "$STATE" ]]; then
  check_baseline_ids
else
  pod_snapshot >/dev/null
  jq -e '(.spec.template.metadata.annotations // {}) | has("injects.sre/scenario01") | not' <<<"$deployment" >/dev/null || fail "Existing scenario marker has no baseline."
  jq -n --arg deployment_uid "$(jq -r '.metadata.uid' <<<"$deployment")" \
    --arg secret_uid "$(jq -r '.metadata.uid' <<<"$secret")" \
    --arg password "$(jq -r --arg key "$BROKER_PASSWORD_KEY" '.data[$key]' <<<"$secret")" \
    '{deployment_uid:$deployment_uid,secret_uid:$secret_uid,password:$password}' >"$STATE.tmp"
  mv "$STATE.tmp" "$STATE"
fi
wrong=$(printf '%s' "$S01_WRONG_PASSWORD" | base64 | tr -d '\n')
original=$(jq -r '.password' "$STATE")
current=$(jq -r --arg key "$BROKER_PASSWORD_KEY" '.data[$key]' <<<"$secret")
[[ "$current" == "$original" || "$current" == "$wrong" ]] || fail "Credential changed outside this scenario; refusing to overwrite it."
if [[ "$current" != "$wrong" ]]; then
  patch=$(jq -nc --arg uid "$(jq -r '.metadata.uid' <<<"$secret")" --arg current "$current" --arg wrong "$wrong" --arg key "$BROKER_PASSWORD_KEY" \
    '($key | gsub("~";"~0") | gsub("/";"~1") | "/data/" + .) as $path |
    [{op:"test",path:"/metadata/uid",value:$uid},{op:"test",path:$path,value:$current},{op:"replace",path:$path,value:$wrong}]')
  printf '%s' "$patch" | k patch secret "$BROKER_SECRET" --type=json --patch-file=/dev/stdin >/dev/null
fi
k patch deployment "$ORDER_NAME" --type=merge -p '{"spec":{"template":{"metadata":{"annotations":{"injects.sre/scenario01":"bad-credential"}}}}}' >/dev/null
printf '%s\n' 'Injected Scenario 01. Health can remain green; failed order POSTs are the decisive symptom.' \
  'Baseline saved locally with mode 0600. Do not delete .state until reset is confirmed.'