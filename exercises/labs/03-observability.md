# Lab 3: Dashboards And Azure Monitor Alerts

Day 1 14:00-14:45, 45 minutes. Prerequisites: a healthy app, fresh collection,
Grafana publishing rights, metrics/log read permissions and approved notification
recipient. A connector or action group without a receiver is not monitoring proof.

## Steps

1. Spend 0-10 minutes opening Azure Monitor and Grafana. Confirm actual metric
   data-source UID, Log Analytics resource ID, table schema, cluster identity and
   sample freshness. Query namespace inventory and compare replicas with the
   deployed app. No data, stale data and denied access are distinct outcomes.
2. Spend 10-20 minutes following [dashboard publishing](../../scenarios/kubernetes/store-demo/README.md#managed-grafana-monitoring):

   ```bash
   : "${GRAFANA_ENDPOINT:?Set the approved Grafana HTTPS endpoint}"
   : "${PROMETHEUS_DATASOURCE_UID:?Set the actual data-source UID}"
   : "${LOG_WORKSPACE_RESOURCE_ID:?Set the full Azure resource ID}"
   python3 scenarios/kubernetes/store-demo/configure_monitoring.py \
     --grafana-endpoint "$GRAFANA_ENDPOINT" \
     --prometheus-datasource-uid "$PROMETHEUS_DATASOURCE_UID" \
     --log-workspace-resource-id "$LOG_WORKSPACE_RESOURCE_ID" --verify-only
   ```

   After authorization, rerun without `--verify-only` to publish. Export/review
   existing manual edits first: publication overwrites the stable dashboard UID.
   Add `--diagram-plugins` only with the approved Graphviz plugin already installed.
   Inspect CPU, memory, restarts and logs; topology is configured dependencies,
   not measured traffic or a public availability probe. The helper uses legacy
   `ContainerLog`; adapt queries for a ContainerLogV2-only environment.
3. Spend 20-30 minutes reviewing the [Terraform operational alerts](../../scenarios/kubernetes/monitoring.tf).
   In the team's authoritative root, configure `alert_email` to the approved
   recipient, review a fresh plan and apply only authorized changes. The root
   creates gateway, AKS and log-query rules plus an action group. Inspect real
   scopes and queries; several defaults cover an entire workspace, not a team
   namespace. Use a dedicated team workspace or reviewed scoping adaptations.
   Check populated schemas because skipped creation-time query validation does
   not prove a rule works. Test the action group with its offered test control.
4. Spend 30-40 minutes creating a temporary **test** log-search alert in Azure
   Monitor's supported Create alert rule flow, with the approved operator. This
   is separate manual configuration, not a feature of the dashboard helper.
   Use the team's workspace, name `[TEST] aks <team> telemetry intake`, severity
   Sev3 and the approved action group. Run this query first, replacing both
   placeholders with the actual team cluster ID and namespace:

   ```kusto
   KubePodInventory
   | where TimeGenerated > ago(5m)
   | where _ResourceId =~ '<approved-full-aks-resource-id>'
   | where Namespace == 'aks-store-demo'
   | summarize arg_max(TimeGenerated, *) by PodUid
   ```

   Use **Table rows**, **Count**, **Greater than 0**, a five-minute lookback and
   a supported evaluation interval (one minute where available). Existing healthy
   inventory intentionally fires this test rule without causing a fault. Review
   title/severity with the agent response-plan filters for Lab 5. Capture the rule
   ID, Fired alert ID/time and delivered notification. An action-group test alone
   does not exercise rule evaluation. If ingestion/evaluation exceeds the slot,
   retain the pending result for the checkpoint; do not invent a delivery.
5. Spend 40-45 minutes recording rule, alert and dashboard evidence, then disable
   the temporary rule to avoid repeated test notifications. Keep operational rules
   enabled only under their approved ownership. Lab 5 will rearm the test safely.

## Monitoring Components And Signal Boundaries

| Component | Verify in this lab |
| --- | --- |
| Managed Prometheus -> Azure Monitor Workspace | Fresh namespace metrics, correct Grafana Prometheus UID and Grafana managed-identity query access |
| Container Insights -> Log Analytics | Fresh inventory/logs, actual legacy `ContainerLog` versus `ContainerLogV2` schema; querying rights do not enable collection |
| Managed Grafana dashboard | Six working base panels; approved `grafana-graphviz-panel` installation before the optional seventh topology panel |
| ACNS network observability/security | Inspect the enabled configuration and available network dashboards separately; no inference of measured traffic from Graphviz edges |
| Azure Monitor alert rules -> action group | Actual rule evaluation, populated receiver, notification and team-isolated scope; `alert_email` defaults empty |
| Agent incident connection -> response plan | Configure in Lab 4 and prove actual intake in Lab 5; not created by the dashboard helper |

The gateway unhealthy-backend alert covers Application Gateway, not the store's
independent LoadBalancer/NSG path. No continuous external storefront probe,
dedicated queue/HPA/NAP dashboard or distributed tracing was installed by this
helper. Use Lab 6's timestamped status/metric/object evidence for scaling. Record
missing signals explicitly; do not call a manual curl a continuous availability
monitor or invent Grafana-managed alerts because Azure Monitor rules exist.

## Checkpoint

PASS requires fresh successful panel queries, a published dashboard, scoped
operational rules with real receivers and a rule-generated test notification.
Automatic agent intake is a separate Lab 5 gate. Record portal-created test
resources in the cleanup inventory; Terraform will not own them automatically.

## Troubleshooting And Safe Stop

Check collection, schema, identities, action suppression/processing rules and
evaluation windows separately. No receiver means BLOCKED, not delivered. The
test rule is not an outage alert and the existing rules do not continuously probe
the public storefront. Do not alter production alerting or loosen workspace
permissions to repair a lab query. Run the offline dashboard tests for the six
base panels and optional seventh Graphviz panel; passing mocks does not replace
the live query and notification checkpoints.

Next: [Lab 4](04-agent-configuration.md).