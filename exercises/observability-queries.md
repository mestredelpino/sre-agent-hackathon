# Queries To Try In Lab 3

These are suggested queries, not a mandatory checklist. Adapt them to your
environment and questions while retaining approved scope and time filters.
Pick two or three during [Lab 3](labs/03-observability.md); the rest are available
for exploration afterward. These are read-only queries, not alert definitions.
For each result, note its UTC time, source, scope and one thing it cannot tell you.
Do not generate load or inject a fault just to make a chart more interesting.

## Before You Query

Use the supplied team workspace/data source. Replace the full AKS resource-ID
placeholder and change `aks-store-demo` only if your assigned namespace differs.
Keep the time ranges short and inspect results before exporting: logs can contain
private data. No rows can mean no matching events, missing collection, stale data
or a filter mismatch; it is not automatically a healthy result.

## Azure Monitor Logs: KQL

Open Logs in the approved Log Analytics workspace, or choose the supplied Azure
Monitor data source and Log Analytics workspace in Grafana Explore. These queries
use explicit time filters, not Grafana macros. Confirm table availability first;
`ContainerLog` and `ContainerLogV2` are different collection schemas.

### Which Pods Have Reported Recently?

```kusto
KubePodInventory
| where TimeGenerated > ago(15m)
| where _ResourceId =~ '<approved-full-aks-resource-id>'
| where Namespace == 'aks-store-demo'
| summarize arg_max(TimeGenerated, *) by PodUid
| project LastSeen=TimeGenerated, Pod=Name, PodStatus, Computer
| order by LastSeen asc
```

Compare the oldest and newest samples. `PodStatus` is pod phase, not the Ready
condition: a Running pod can still be unready. Missing pods require comparison
with the supplied baseline, not a conclusion that they were deleted.

### Which Pods Have A Restart History?

```kusto
KubePodInventory
| where TimeGenerated > ago(15m)
| where _ResourceId =~ '<approved-full-aks-resource-id>'
| where Namespace == 'aks-store-demo'
| summarize arg_max(TimeGenerated, *) by PodUid
| project Pod=Name, PodRestartCount, PodStatus, LastSeen=TimeGenerated
| order by PodRestartCount desc
```

The restart count is the latest reported cumulative count, not restarts during
these fifteen minutes. Compare with the Prometheus counter-increase query below.
A replacement pod has a new identity and may start its count at zero.

### Are Kubernetes Events Explaining A Symptom?

```kusto
KubeEvents
| where TimeGenerated > ago(15m)
| where _ResourceId =~ '<approved-full-aks-resource-id>'
| where Namespace == 'aks-store-demo'
| project TimeGenerated, Name, Reason, Message
| order by TimeGenerated desc
| take 50
```

Find an event you can explain. Events are sampled records, can repeat and are
not a complete audit trail; fifty rows are not fifty unique incidents. Empty
results do not prove all scheduling and image pulls succeeded.

### ContainerLogV2: What Are The Workloads Saying?

Use this version only if `ContainerLogV2` is collected:

```kusto
ContainerLogV2
| where TimeGenerated > ago(15m)
| where _ResourceId =~ '<approved-full-aks-resource-id>'
| where PodNamespace == 'aks-store-demo'
| project TimeGenerated, PodName, ContainerName, LogSource, Message=tostring(LogMessage)
| order by TimeGenerated desc
| take 50
```

Pick a pod from inventory and add a `PodName` filter before `project`. Can you
identify actual work, or only startup messages? A log message is application
evidence, not independent proof that an order completed.

### Legacy ContainerLog: Find Logs Through Inventory

Use this alternative if the workspace collects `ContainerLog`:

```kusto
let StoreContainers = KubePodInventory
| where TimeGenerated > ago(30m)
| where _ResourceId =~ '<approved-full-aks-resource-id>'
| where Namespace == 'aks-store-demo'
| distinct ContainerID, PodName=Name;
ContainerLog
| where TimeGenerated > ago(15m)
| where _ResourceId =~ '<approved-full-aks-resource-id>'
| join kind=inner StoreContainers on ContainerID
| project TimeGenerated, PodName, LogSource=LogEntrySource, Message=tostring(LogEntry)
| order by TimeGenerated desc
| take 50
```

The inventory join supplies namespace scope and pod names. If inventory and logs
exist but the join is empty, inspect container-ID formats with the approved
owner. Do not remove scope filters or assume there are no logs.

### ContainerLogV2: Who Is Producing The Most Logs?

```kusto
ContainerLogV2
| where TimeGenerated > ago(15m)
| where _ResourceId =~ '<approved-full-aks-resource-id>'
| where PodNamespace == 'aks-store-demo'
| summarize Entries=count() by bin(TimeGenerated, 1m), PodName
| render timechart
```

For legacy logs, reuse the previous query through its join and replace the
`project`, `order by` and `take` lines with this `summarize` and `render`.
Log volume is not request volume: logging settings and retries affect it.

## Grafana Explore: PromQL

Choose the supplied Prometheus data source. These queries extend the dashboard's
existing metric families. In a shared workspace, inspect an existing approved
panel to identify its actual cluster label and value. The examples use
`cluster="<team-cluster-label-value>"`; replace the label name too if your source
uses another one. Do not drop that selector to fix empty results in a shared
source. In a verified single-cluster source without a cluster label, omit only
that selector. Namespace filters alone do not isolate identically named team
namespaces across clusters.

Use Table/Instant for a current snapshot, or Time series/Range to see history.
Check Grafana's selected time range; the `[5m]` and `[15m]` windows below are
calculation windows, not the whole chart duration.

### Which Pods Are Ready Right Now?

```promql
max by (pod) (
  kube_pod_status_ready{cluster="<team-cluster-label-value>",namespace="aks-store-demo",condition="true"}
)
```

`1` means Ready and `0` means not Ready at the sample time. Missing series mean
unknown, not zero. `max` collapses duplicate series for this view; it does not
repair inconsistent collection. Try a state timeline in a scratch dashboard.

### Which Containers Restarted In The Last Fifteen Minutes?

```promql
sum by (pod) (
  increase(kube_pod_container_status_restarts_total{cluster="<team-cluster-label-value>",namespace="aks-store-demo"}[15m])
)
```

This estimates counter increases over the window; extrapolation can produce
fractional values. Zero is different from an absent series. Restarts do not
identify their cause, and pod replacements can hide older identities.

### Which Pods Are Using CPU?

```promql
sum by (pod) (
  rate(container_cpu_usage_seconds_total{cluster="<team-cluster-label-value>",namespace="aks-store-demo",container!="",container!="POD"}[5m])
)
```

Set the unit to CPU cores: `0.1` is one tenth of a core, not ten percent of a
node. This does not show throttling or percentage of a configured CPU limit.
Compare two time ranges without changing the workload.

### How Much Memory Is Each Pod Using?

```promql
sum by (pod) (
  container_memory_working_set_bytes{cluster="<team-cluster-label-value>",namespace="aks-store-demo",container!="",container!="POD"}
) / 1024 / 1024
```

The result is MiB of working set, not a request, limit or total process heap.
Which workload has the largest footprint? A single high value does not prove a
memory leak; look at history and workload context.

### How Old Is The Latest Readiness Sample?

```promql
max by (pod) (
  time() - timestamp(kube_pod_status_ready{cluster="<team-cluster-label-value>",namespace="aks-store-demo",condition="true"})
)
```

Use an instant query and seconds as the unit. This is the age of the exported
sample, not the time since a pod changed state. Prometheus eventually drops stale
series, so a missing result still needs investigation; this is not a complete
ingestion-delay or missing-telemetry monitor.

## Bring One Finding Back

Keep one useful query, its source and UTC window, and a short interpretation.
Explain what additional evidence you would need before diagnosing a fault.
Share sanitized results only; do not export raw private logs into agent knowledge
or public visualization tools.