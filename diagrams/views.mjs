const node = (id, label, x, y, w, h, icon, font) => ({ id, label, x, y, w, h, icon, font });
const note = (id, label, x, y, w, h = 28, font = 19) => ({ ...node(id, label, x, y, w, h, undefined, font), kind: 'note' });
const boundary = (id, label, x, y, w, h) => ({ ...node(id, label, x, y, w, h, undefined, 23), kind: 'boundary' });
const edge = (from, to, options = {}) => ({ from, to, ...options });
const down = { exit: [0.5, 1], entry: [0.5, 0] };
const up = { exit: [0.5, 0], entry: [0.5, 1] };
const control = { kind: 'control' };

function ingress(id, height, combined) {
  const top = combined ? 90 : 100;
  const nodes = [
    boundary('aks', 'AKS / Azure CNI Overlay + Cilium', combined ? 550 : 615, 10, combined ? 592 : 527, height - 20),
    node('browser', 'Browser', 12, top, 155, 76),
    node('gateway', 'Application Gateway\nWAF_v2 / TLS ends here', 260, top, 275, 76, 'gateway', 19),
    node('front', 'store-front\nClusterIP :80', 650, top, 225, 76),
    node('pods', 'Pod\nendpoints', 970, top, 150, 76),
    note('https', 'HTTPS / IP', 164, top - 31, 120),
    note('http1', 'HTTP', 550, top - 31, 60),
    note('http2', 'HTTP', 890, top - 31, 60),
  ];
  const edges = [edge('browser', 'gateway'), edge('gateway', 'front'), edge('front', 'pods')];
  if (combined) {
    nodes.push(node('cert', 'cert-manager', 937, 224, 185, 66), node('secret', 'Store TLS Secret\nIP-SAN certificate', 700, 224, 205, 66, undefined, 20), node('agic', 'AGIC', 560, 224, 100, 66), note('legend', 'Dashed green: certificate / Ingress reconciliation, not requests', 260, 304, 800));
    edges.push(edge('cert', 'secret', { ...control, exit: [0, 0.5], entry: [1, 0.5] }), edge('secret', 'agic', { ...control, exit: [0, 0.5], entry: [1, 0.5] }), edge('agic', 'gateway', { ...control, exit: [0, 0.5], entry: [0.5, 1], points: [[397, 257]] }));
  } else {
    nodes.push(note('trust', 'Public IP + IP-SAN trust', 12, 226, 350), note('logical', 'Logical Service route, not a packet capture', 650, 226, 480));
  }
  return { id, width: 1152, height, title: 'IP-only Store ingress and TLS boundary', description: 'Browser HTTPS to Application Gateway public IP using IP-SAN trust. TLS terminates at the gateway; HTTP continues through store-front ClusterIP :80 to pod endpoints. Both frontend Services are private ClusterIP. No DNS mapping, redirect or ACME challenge. Dashed certificate and AGIC reconciliation paths are control, not requests.', nodes, edges };
}

function application(id, width, height, full) {
  const nodes = full ? [
    node('front', 'store-front', 10, 28, 190, 54),
    node('admin', 'store-admin\nprivate', 10, 180, 190, 66),
    node('product', 'product-service', 275, 28, 215, 54),
    node('order', 'order-service', 275, 122, 215, 54),
    node('customer', 'virtual-customer', 275, 273, 215, 54),
    node('queue', 'RabbitMQ', 585, 122, 160, 54),
    node('makeline', 'makeline-service', 835, 122, 206, 54),
    node('db', 'DocumentDB', 835, 28, 206, 54),
    node('worker', 'virtual-worker', 835, 273, 206, 54),
    note('amqp1', 'AMQP', 500, 88, 85), note('amqp2', 'AMQP', 750, 88, 85),
    note('mongo', 'MongoDB', 1048, 84, 100),
    note('private', 'HTTP / private fulfillment view', 510, 232, 320),
    note('http', 'Other calls: HTTP', 12, 282, 230),
    node('context', 'AKS', 1050, 273, 95, 54, 'aks', 18),
  ] : [
    node('front', 'store-front', 12, 30, 190, 65), node('product', 'product-service', 300, 30, 230, 65),
    node('order', 'order-service', 12, 181, 230, 70), node('queue', 'RabbitMQ', 342, 181, 170, 70),
    node('makeline', 'makeline-service', 625, 181, 220, 70), node('db', 'DocumentDB', 954, 181, 186, 70),
    note('http', 'HTTP', 216, 0, 80), note('submit', 'HTTP: submit', 124, 125, 180),
    note('amqp1', 'AMQP', 252, 144, 90), note('amqp2', 'AMQP', 520, 144, 100), note('mongo', 'MongoDB', 850, 144, 110),
    note('consumer', 'Makeline initiates its broker connection.\nThe arrow shows message delivery.', 625, 65, 510, 56),
    node('context', 'AKS', 970, 0, 170, 56, 'aks', 20),
  ];
  const edges = [edge('front', 'product'), edge('front', 'order', full ? { exit: [1, 0.7], entry: [0, 0.5], points: [[235, 66], [235, 149]] } : down), edge('order', 'queue'), edge('queue', 'makeline'), edge('makeline', 'db', full ? up : {})];
  if (full) edges.push(edge('admin', 'product', { exit: [1, 0.2], entry: [0, 0.8], points: [[253, 193], [253, 71]] }), edge('admin', 'makeline', { exit: [1, 0.65], entry: [0.5, 1], points: [[938, 223]] }), edge('customer', 'order', up), edge('worker', 'makeline', up));
  return { id, width, height, title: 'Configured Store application dependencies', description: 'Application Gateway HTTPS enters store-front. HTTP catalog reads go to product-service; HTTP order submission goes to order-service, including virtual-customer. Order-service publishes AMQP to RabbitMQ; makeline initiates the broker connection and consumes messages, then writes order state over a MongoDB-compatible protocol to DocumentDB. Private store-admin reads product-service and makeline; virtual-worker calls makeline over HTTP. Seven Deployments and two ephemeral StatefulSets. Configured logical interactions, not captured traces.', nodes, edges };
}

function signals(id, height, agent) {
  const nodes = [
    node('aks', 'AKS\nsignals', 10, 28, 190, 70, 'aks'),
    node('amw', 'Azure Monitor Workspace\nManaged Prometheus', 290, 8, 330, 70, 'prometheus', 20),
    node('law', 'Log Analytics (LAW)\nLogs / inventory', 290, 124, 330, 70, 'law', 20),
    node('grafana', 'Managed Grafana', 790, 8, 350, 70, 'grafana'),
    node('gateway', 'Gateway\nsignals', 10, height - 84, 190, 66, 'gateway', 21),
    node('alert', 'Azure Monitor\nAlert rules', agent ? 290 : 680, height - 84, agent ? 330 : 200, 66, 'monitor', 20),
    node('receiver', 'Action group\nApproved receiver', agent ? 790 : 958, height - 84, agent ? 350 : 182, 66, undefined, 20),
  ];
  const edges = [edge('aks', 'amw', { exit: [1, 0.2], points: [[245, 42], [245, 43]] }), edge('aks', 'law', { exit: [1, 0.75], points: [[245, 80], [245, 159]] }), edge('amw', 'grafana'), edge('law', 'grafana', { exit: [1, 0.2], entry: [0, 0.8], points: [[710, 138], [710, 64]] }), edge('gateway', 'alert'), edge('alert', 'receiver')];
  if (agent) {
    nodes.push(node('agent', 'SRE Agent / scoped reads\nSeparate execution identity', 790, 124, 350, 70, undefined, 21), note('metadata', 'Also: authorized resource metadata reads', 740, 207, 410, 28, 18));
    edges.push(edge('law', 'alert', down), edge('agent', 'law', { ...control, exit: [0, 0.6], entry: [1, 0.6] }));
  } else {
    edges.push(edge('law', 'alert', { exit: [1, 0.8], points: [[650, 180], [650, height - 51]] }));
  }
  return { id, width: 1152, height, title: 'Telemetry collection, visualization and investigation boundaries', description: 'AKS managed Prometheus metrics go to Azure Monitor Workspace (AMW). Container Insights logs and inventory go to Log Analytics (LAW). Managed Grafana visualizes both. Gateway signals and LAW feed Azure Monitor alert rules and the configured action group approved receiver. Agent reads use a separately scoped identity and authorized LAW and resource metadata tools; native incident intake is conditional on independent configuration and testing, not established by receiver delivery.', nodes, edges };
}

const controls = {
  id: '06-control', width: 1152, height: 300, title: 'Certificate issuance and AGIC reconciliation',
  description: 'cert-manager issues aks-store-demo/store-front-tls with an IP-SAN certificate. AGIC consumes the Store Ingress and its namespaced TLS Secret to reconcile Application Gateway. Dashed green paths represent control, not browser requests. Terraform bootstrap sre-lab-tls PFX is separate. AGIC is not an inline proxy.',
  nodes: [node('cert', 'cert-manager', 12, 40, 205, 76), node('secret', 'Store TLS Secret\nstore-front-tls / IP-SAN', 300, 40, 285, 76), node('ingress', 'Store Ingress', 300, 188, 285, 76), node('agic', 'AGIC', 680, 114, 150, 76), node('gateway', 'Application\nGateway', 920, 114, 220, 76, 'gateway'), note('legend', 'Dashed green: issuance and reconciliation, not requests', 12, 270, 900)],
  edges: [edge('cert', 'secret', control), edge('secret', 'agic', { ...control, entry: [0, 0.3], points: [[630, 78], [630, 137]] }), edge('ingress', 'agic', { ...control, entry: [0, 0.7], points: [[630, 226], [630, 167]] }), edge('agic', 'gateway', control)],
};

const platform = {
  id: 'platform', width: 1500, height: 960, title: 'Pre-provisioned Azure platform and control boundaries',
  description: 'Browser HTTPS uses the Application Gateway WAF_v2 public IP and trusted IP-SAN certificate; TLS terminates at the gateway. HTTP continues logically through store-front ClusterIP :80 to application pods. Inside AKS Azure CNI Overlay with Cilium, cert-manager issues the namespaced Store TLS Secret consumed by managed AGIC for Ingress reconciliation. A fixed system node pool hosts platform workloads. Managed KEDA reconciles replicas; managed NAP provisions a bounded lab node pool for eligible pending pods. Registry image pulls are conditional. Key Vault and Storage private endpoints are supporting facilities, not assumed app dependencies.',
  nodes: [boundary('platform', 'Azure workshop platform / configured baseline, not observed health', 10, 10, 1480, 895), boundary('aks', 'AKS / Azure CNI Overlay + Cilium', 570, 68, 895, 730),
    node('browser', 'Participant\nbrowser', 30, 150, 170, 85), node('gateway', 'Application Gateway\nWAF_v2 / TLS ends here', 280, 150, 270, 85, 'gateway', 19), node('front', 'store-front\nClusterIP :80', 620, 150, 250, 85), node('pods', 'Application pods', 1110, 150, 300, 85, 'aks'),
    note('https', 'HTTPS / IP-SAN', 190, 112, 190), note('http1', 'HTTP', 552, 120, 65), note('http2', 'HTTP', 940, 120, 100),
    node('agic', 'Managed AGIC', 620, 330, 250, 80), node('secret', 'Store TLS Secret\nstore-front-tls / IP-SAN', 930, 330, 265, 80, undefined, 21), node('cert', 'cert-manager', 1250, 330, 190, 80),
    node('system', 'Fixed system node pool\nTwo Ready nodes expected', 610, 500, 290, 85, undefined, 21), node('keda', 'Managed KEDA\nWorkload replicas', 1110, 500, 300, 85),
    node('nap', 'Managed NAP\nAuto / default pools None', 610, 680, 290, 85, undefined, 21), node('pool', 'Bounded lab node pool\nIntroduced in Lab 6', 1110, 680, 300, 85),
    node('acr', 'Container Registry\nImage pulls if configured', 35, 505, 360, 85, 'acr', 21), node('vault', 'Key Vault\nPrivate endpoints', 35, 665, 360, 85, 'vault'), node('storage', 'Storage account\nPrivate endpoints', 35, 800, 360, 85, 'storage'),
    note('replicas', 'Reconciles configured replicas', 1110, 435, 335), note('capacity', 'Node capacity for scheduling', 1120, 610, 330), note('pending', 'Eligible pending pods', 905, 715, 205), note('hosts', 'Hosts platform workloads', 620, 435, 330),
    note('legend', 'Solid blue: configured requests. Dashed green: control / support, not measured traffic.', 20, 916, 1460, 30, 22),
    note('facilities', 'Supporting facilities: do not infer Store use.\nVerify manifests and the private handover.', 450, 820, 960, 60, 22)],
  edges: [edge('browser', 'gateway'), edge('gateway', 'front'), edge('front', 'pods'), edge('cert', 'secret', { ...control, exit: [0, 0.5], entry: [1, 0.5] }), edge('secret', 'agic', { ...control, exit: [0, 0.5], entry: [1, 0.5] }), edge('agic', 'gateway', { ...control, exit: [0, 0.5], entry: [0.5, 1], points: [[415, 370]] }), edge('system', 'agic', { ...control, ...up }), edge('keda', 'pods', { ...control, ...up, points: [[1220, 460], [1450, 460], [1450, 270], [1260, 270]] }), edge('nap', 'pool', control), edge('pool', 'pods', { ...control, ...up, points: [[1460, 640], [1460, 250], [1300, 250]] }), edge('acr', 'pods', { ...control, exit: [0.5, 0], entry: [0.5, 0], points: [[215, 70], [1260, 70]] })],
};

const handoutApp = application('application', 1500, 650, true);
for (const item of handoutApp.nodes) { item.x += 130; item.y += 150; }
for (const connection of handoutApp.edges) if (connection.points) connection.points = connection.points.map(([horizontal, vertical]) => [horizontal + 130, vertical + 150]);
handoutApp.nodes.unshift(boundary('namespace', 'AKS / aks-store-demo / seven Deployments + two ephemeral StatefulSets', 10, 10, 1480, 540), node('entry', 'Application Gateway\nHTTPS / IP-SAN', 140, 60, 300, 80, 'gateway'));
handoutApp.edges.push(edge('entry', 'front', { ...down, exit: [0.32, 1] }));
handoutApp.nodes.push(note('disposable', 'RabbitMQ and DocumentDB: disposable synthetic data; StatefulSet identity does not establish durable storage.', 25, 565, 1450, 32, 22), note('semantics', 'Logical dependencies, not captured traces. Makeline initiates its AMQP broker connection; arrows show message delivery.', 25, 607, 1450, 32, 22));

const handoutSignals = signals('observability', 338, true);
handoutSignals.width = 1500;
handoutSignals.height = 720;
for (const item of handoutSignals.nodes) { item.x += 150; item.y += 140; }
for (const connection of handoutSignals.edges) if (connection.points) connection.points = connection.points.map(([horizontal, vertical]) => [horizontal + 150, vertical + 140]);
handoutSignals.nodes.push(note('metrics', 'Managed metrics collection', 170, 70, 470, 32, 22), note('logs', 'Container Insights logs / inventory', 170, 110, 520, 32, 22), node('resources', 'Azure resource metadata', 940, 550, 350, 66), note('reads', 'Authorized resource reads', 650, 560, 280, 32, 21), note('conditional', 'Conditional intake: only when configured and independently tested', 160, 620, 1040, 32, 22), note('legend', 'Solid blue: configured telemetry / alert path. Dashed green: intended authorized reads or conditional intake, not runtime proof.', 20, 675, 1470, 32, 21));
handoutSignals.edges.push(edge('agent', 'resources', { ...control, ...down, exit: [1, 0.8], entry: [1, 0.5], points: [[1320, 320], [1320, 583]] }), edge('alert', 'agent', { ...control, exit: [0.5, 1], entry: [1, 0.5], points: [[605, 655], [1410, 655], [1410, 300]] }));

const platformSlide = {
  id: '05-platform', width: 1152, height: 338, title: 'Azure platform topology and supporting facilities',
  description: 'Application Gateway WAF_v2 public HTTPS and AKS use separate subnets in workshop VNet 10.30.0.0/16. AKS Cilium Overlay pods use 10.244.0.0/16, separate from the node subnet. Fixed system nodes and managed NAP bounded lab capacity host workloads. Private endpoints in a separate subnet connect to infrastructure Key Vault and Storage, not inferred Store dependencies. Managed observability is outside the VNet boundary. Dashed paths are supporting relationships, not measured traffic.',
  nodes: [boundary('vnet', 'Workshop VNet: 10.30.0.0/16', 8, 8, 790, 322), node('gateway', 'Application Gateway\nWAF_v2 / HTTPS\nsubnet-appgw /24', 28, 65, 235, 108, 'gateway', 17), node('aks', 'AKS / Cilium Overlay\nNode subnet-aks /22\nPods 10.244.0.0/16', 330, 65, 438, 108, 'aks', 20), node('pe', 'Private endpoints\nsubnet-pe /24', 28, 218, 235, 74, undefined, 19), node('system', 'Fixed system pool\nTwo baseline nodes', 330, 218, 207, 74, undefined, 18), node('nap', 'Managed NAP\nBounded lab capacity', 561, 218, 207, 74, undefined, 18), node('monitoring', 'Managed observability\nMetrics / logs / Grafana\nOutside VNet boundary', 835, 65, 303, 108, 'grafana', 18), node('facilities', 'Key Vault + Storage\nInfrastructure services', 835, 218, 303, 74, 'vault', 18)],
  edges: [edge('gateway', 'aks'), edge('aks', 'monitoring'), edge('system', 'aks', { ...control, ...up, entry: [0.25, 1] }), edge('nap', 'aks', { ...control, ...up, entry: [0.76, 1] }), edge('pe', 'facilities', { ...control, points: [[286, 255], [286, 315], [812, 315], [812, 255]] })],
};

const sreAgentArchitecture = {
  id: 'sre-agent-architecture', width: 1800, height: 1580,
  title: 'Azure SRE Agent / workshop logical architecture',
  description: 'Workshop logical architecture, not Azure backend internals. Human chat starts with the main agent; explicit custom-agent invocation or an accepted incident response plan selects lab-triage. Intended AKS delegation returns evidence to triage before analyst synthesis. Skills and knowledge retrieval are separate. Approved read tools require execution identity, effective RBAC, connector authorization and network reachability. Incident plans remain Off in Review until acceptance; optional scheduled tasks are separate. All runtime paths need independent Lab 5 proof.',
  nodes: [
    note('heading', 'Azure SRE Agent / workshop logical architecture', 30, 12, 1740, 40, 30),
    note('scope', 'Configured intent, not runtime proof or a diagram of Azure backend internals', 30, 58, 1740, 32, 22),
    node('human', 'Human chat\nLab 3: start here', 30, 120, 310, 100),
    node('main', 'Product main agent\nNormal chat entry', 420, 120, 350, 100),
    node('invoke', 'Explicit /agent lab-triage\nor supported playground selection\nNot a default replacement', 850, 120, 390, 120, undefined, 21),
    node('schedule', 'Optional scheduled task\nSeparate trigger / explicit Review\nOnly if needed and accepted', 1340, 120, 410, 120, undefined, 21),
    node('incident', 'Incident platform\nAzure Monitor connection\nReceiver != agent intake', 30, 270, 310, 120, 'monitor', 19),
    node('plan', 'Matching response plan\nOff (paused) / Review\nIntended handler: lab-triage', 420, 270, 350, 120, undefined, 21),
    note('intake', 'Conditional incident intake:\naccepted handler + enabled plan\ncorrelated alert/thread/tool trace', 1100, 270, 650, 100, 21),
    boundary('workflow', 'Custom workflow / verify delegation', 20, 415, 1750, 410),
    node('triage', '1. lab-triage\nOwn intake and final response\nOnly coordinator delegates', 420, 485, 350, 110, undefined, 21),
    node('k8s', '2. lab-k8s-specialist\nBounded AKS investigation\nReturn evidence to triage', 900, 485, 350, 110, 'aks', 20),
    node('optional', 'Optional library\nlab-network-specialist\nlab-vm-specialist', 1350, 485, 370, 110, undefined, 21),
    note('returned', '3. Evidence returns to triage', 685, 620, 240, 30, 18),
    node('analyst', '4. lab-incident-analyst\nSynthesize returned evidence\nNo diagnostic tools needed', 420, 690, 350, 100, undefined, 20),
    node('skills', 'Selected skills\nDescription-led retrieval / use\nProcedures, not permission grants', 900, 690, 350, 100, undefined, 20),
    node('knowledge', 'Knowledge files\nSeparate reference retrieval\nSanitized docs + source revision', 1350, 690, 370, 100, undefined, 20),
    note('manual', 'No native delegation? Explicit role calls = MANUAL HANDOVER, not automation.', 45, 838, 1700, 30, 21),
    boundary('reads', 'Shared read boundary / main agent, triage and specialists use only their own approved bindings', 20, 885, 1750, 390),
    node('tools', 'Inspected tools + connections\nAvailable/configured is not guaranteed\nRead-only tool policy enforced\nNo shell, Secrets or guest execution', 60, 980, 430, 160, undefined, 21),
    node('checks', 'Per-call permission + reachability checks\nActual execution UAMI / effective RBAC\nConnector consent / data-plane access\nNetwork route to the target\nReview is not a universal gate', 580, 980, 520, 160, undefined, 21),
    node('resources', 'Azure resources\nAKS / gateway metadata', 1190, 950, 250, 80, 'aks', 18),
    node('law', 'Log Analytics\nLAW / scoped KQL', 1470, 950, 250, 80, 'law', 18),
    node('prometheus', 'Managed Prometheus\nSeparate query tool', 1190, 1060, 250, 80, 'prometheus', 18),
    node('grafana', 'Managed Grafana\nMetadata != data query', 1470, 1060, 250, 80, 'grafana', 18),
    node('repository', 'Approved repository / known file at resolved revision', 1190, 1170, 530, 65, undefined, 18),
    boundary('identities', 'Distinct identities and responsibilities / do not infer one identity from another', 20, 1300, 1750, 220),
    node('author', 'Signed-in configuration user\nAuthors settings / approved consent\nNot proof of execution permissions', 45, 1370, 395, 120, undefined, 20),
    node('uami', 'Actual execution UAMI\nVerify principal + inherited roles\nInstructions do not enforce RBAC', 480, 1370, 395, 120, undefined, 20),
    node('grafanaIdentity', 'Grafana managed identity\nDashboard data-source access\nDoes not grant agent access', 915, 1370, 395, 120, undefined, 20),
    node('operator', 'Separate authorized operator\nApproved recovery / infrastructure\nNo agent recovery credentials', 1350, 1370, 395, 120, undefined, 20),
    note('legend', 'Solid blue: intended interaction. Dashed green: conditional / optional / retrieval. Neither proves execution; see Lab 5.', 30, 1535, 1730, 30, 21),
  ],
  edges: [
    edge('human', 'main'), edge('main', 'invoke'),
    edge('invoke', 'triage', { ...down, points: [[1045, 400], [595, 400]] }),
    edge('incident', 'plan', control), edge('plan', 'triage', { ...control, ...down }),
    edge('schedule', 'triage', { ...control, exit: [1, 0.5], entry: [1, 0.15], points: [[1785, 180], [1785, 475], [800, 475], [800, 501.5]] }),
    edge('triage', 'k8s'),
    edge('k8s', 'triage', { exit: [0.1, 1], entry: [0.7, 1], points: [[935, 665], [665, 665]] }),
    edge('triage', 'optional', { ...control, exit: [0.9, 0], entry: [0.5, 0], points: [[735, 465], [1535, 465]] }),
    edge('triage', 'analyst', { ...down, exit: [0.3, 1], entry: [0.3, 0] }),
    edge('analyst', 'triage', { exit: [0, 0.5], entry: [0, 0.65], points: [[380, 740], [380, 556.5]] }),
    edge('k8s', 'skills', { ...control, ...down, exit: [0.85, 1], entry: [0.85, 0] }),
    edge('analyst', 'skills', control),
    edge('optional', 'knowledge', { ...control, ...down }),
    edge('tools', 'checks'),
    edge('checks', 'resources', { ...control, exit: [1, 0.2], points: [[1140, 1012], [1140, 990]] }),
    edge('checks', 'law', { ...control, exit: [1, 0.35], entry: [0.5, 0], points: [[1155, 1036], [1155, 935], [1595, 935]] }),
    edge('checks', 'prometheus', { ...control, exit: [1, 0.5], points: [[1140, 1060], [1140, 1100]] }),
    edge('checks', 'grafana', { ...control, exit: [1, 0.65], entry: [0.5, 0], points: [[1125, 1084], [1125, 1045], [1595, 1045]] }),
    edge('checks', 'repository', { ...control, exit: [1, 0.8], points: [[1140, 1108], [1140, 1202.5]] }),
  ],
};

const sreAgentPresentation = {
  id: '07-sre-agent-architecture',
  title: 'SRE Agent workshop architecture / presentation view',
  width: 1152, height: 408,
  description: 'Presentation-focused view derived from sre-agent-architecture. Human chat starts with the product main agent; explicit custom triage delegates to AKS and receives evidence before analyst synthesis and final response. Selected skills and knowledge are separate retrieval sources. Each role uses only approved tool bindings and independently authorized connections. Review is not a universal gate. Configured intent requires Lab 5 runtime proof; optional triggers and identities are detailed in the full architecture.',
  nodes: [
    node('human', 'Human chat', 6, 8, 166, 52, undefined, 22),
    node('main', 'Main agent', 212, 8, 204, 52, undefined, 22),
    note('lab3', 'Lab 3: start here', 454, 12, 340, 40, 22),
    note('invoke', 'Explicit /agent selection below; not the default chat route', 6, 72, 1138, 32, 21),
    node('triage', 'Custom triage\nFinal response', 6, 122, 240, 76, undefined, 22),
    node('k8s', 'AKS specialist\nReturn evidence', 318, 122, 248, 76, 'aks', 22),
    node('analyst', 'Analyst\nSynthesize returns', 638, 122, 248, 76, undefined, 22),
    note('order', 'Triage coordinates: AKS returns first, then analyst; no direct AKS-to-analyst route.', 6, 217, 1138, 31, 20),
    node('skills', 'Selected skills\nProcedures', 6, 279, 240, 72, undefined, 22),
    node('knowledge', 'Knowledge\nReference sources', 318, 279, 248, 72, undefined, 22),
    node('tools', 'Own approved tools\n+ connections', 638, 279, 248, 72, undefined, 22),
    note('bounds', 'Read-only policy + execution identity / RBAC + connector authorization + network', 6, 368, 1138, 32, 21),
    note('retrieval', 'Permitted retrieval for main / custom agents; not permission grants', 6, 248, 1138, 31, 20),
    note('proof', 'Lab 4 config\nLab 5 proof', 920, 122, 222, 76, 22),
    note('review', 'Review is not\na universal gate', 920, 279, 222, 72, 21),
  ],
  edges: [
    edge('human', 'main'),
    edge('triage', 'k8s'),
    edge('k8s', 'triage', { exit: [0.5, 1], entry: [0.5, 1], points: [[442, 210], [126, 210]] }),
    edge('triage', 'analyst', { exit: [0.5, 0], entry: [0.5, 0], points: [[126, 110], [762, 110]] }),
    edge('analyst', 'triage', { exit: [0.5, 1], entry: [0.5, 1], points: [[762, 216], [126, 216]] }),
  ],
};

export const views = [platform, handoutApp, handoutSignals, ingress('05-ingress', 338, true), application('05-application', 1152, 338, true), signals('05-observability', 338, true), ingress('06-entry', 300, false), controls, application('06-order', 1152, 300, false), signals('06-observability', 300, false), platformSlide, sreAgentArchitecture, sreAgentPresentation];