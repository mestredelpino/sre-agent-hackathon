#!/usr/bin/env bash
set -euo pipefail
source "$(dirname -- "${BASH_SOURCE[0]}")/common.sh"
check_baseline_ids
original=$(jq -r '.password' "$STATE")
wrong=$(printf '%s' "$S01_WRONG_PASSWORD" | base64 | tr -d '\n')
current=$(jq -r --arg key "$BROKER_PASSWORD_KEY" '.data[$key]' <<<"$secret")
[[ "$current" == "$original" || "$current" == "$wrong" ]] || fail "Credential changed outside this scenario; refusing to overwrite it."
if [[ "$current" != "$original" ]]; then
  patch=$(jq -nc --arg uid "$(jq -r '.metadata.uid' <<<"$secret")" --arg current "$current" --arg original "$original" --arg key "$BROKER_PASSWORD_KEY" \
    '($key | gsub("~";"~0") | gsub("/";"~1") | "/data/" + .) as $path |
    [{op:"test",path:"/metadata/uid",value:$uid},{op:"test",path:$path,value:$current},{op:"replace",path:$path,value:$original}]')
  printf '%s' "$patch" | k patch secret "$BROKER_SECRET" --type=json --patch-file=/dev/stdin >/dev/null
fi
k patch deployment "$ORDER_NAME" --type=merge -p '{"spec":{"template":{"metadata":{"annotations":{"injects.sre/scenario01":null}}}}}' >/dev/null
k rollout status "deployment/$ORDER_NAME" --timeout="${ROLLOUT_TIMEOUT}s"
printf '%s\n' 'Credential and scenario marker restored. Run verify.sh for functional recovery.'