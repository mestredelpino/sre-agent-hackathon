#!/usr/bin/env bash
set -euo pipefail
source "$(dirname -- "${BASH_SOURCE[0]}")/common.sh"
k rollout status "deployment/$ORDER_NAME" --timeout="${ROLLOUT_TIMEOUT}s"
before=$(pod_snapshot)
printf '%s\n' 'Checking health, publishing a real synthetic order, and observing the configured stability interval.'
k exec -i "deployment/$ORDER_NAME" -c "$ORDER_CONTAINER" -- node - "$BROKER_JSON" "$TIMING_JSON" <"$HERE/verify-order.cjs"
deployment=$(k get deployment "$ORDER_NAME" -o json)
after=$(pod_snapshot)
[[ "$before" == "$after" ]] || fail "Pod identity, placement or restart count changed during verification."
printf '%s\n' 'PASS: target replicas Ready, no recent restarts, stable for the configured interval, and a real order accepted by RabbitMQ.'