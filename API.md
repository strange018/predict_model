# API Documentation

## Overview

The Predictive Infrastructure system exposes a REST API for monitoring, controlling, and interacting with Kubernetes nodes.

## Base URL

```
http://127.0.0.1:5000/api
```

## Endpoints

### Health & Status

#### GET /api/health
Check system health and connectivity status.

**Response:**
```json
{
  "status": "healthy",
  "kubernetes": "connected" | "demo_mode",
  "monitoring": "active" | "inactive",
  "timestamp": "2026-02-10T22:34:32.435070"
}
```

**Status Codes:**
- `200`: System healthy
- `500`: System error

---

### Statistics

#### GET /api/stats
Get aggregate system statistics.

**Response:**
```json
{
  "nodes_monitored": 5,
  "risks_detected": 0,
  "workloads_moved": 0,
  "events_total": 42,
  "monitoring_active": true
}
```

**Status Codes:**
- `200`: OK
- `500`: Error fetching stats

---

### Nodes

#### GET /api/nodes
Get all nodes with metrics.

**Response:**
```json
[
  {
    "node_id": "node-01",
    "node_name": "worker-01",
    "cpu_usage": 45.2,
    "memory_usage": 62.1,
    "temperature": 58.5,
    "network_latency": 12.3,
    "disk_io": 25.4,
    "pods": ["pod-1", "pod-2", "pod-3"],
    "status": "healthy",
    "taints": []
  },
  ...
]
```

**Query Parameters:**
- None

**Status Codes:**
- `200`: OK
- `500`: Error fetching nodes

---

#### GET /api/nodes/{node_id}
Get details for a specific node.

**Path Parameters:**
- `node_id` (string): Node identifier (e.g., "node-01")

**Response:**
```json
{
  "node_id": "node-01",
  "node_name": "worker-01",
  "cpu_usage": 45.2,
  "memory_usage": 62.1,
  "temperature": 58.5,
  "network_latency": 12.3,
  "disk_io": 25.4,
  "pods": ["pod-1", "pod-2"],
  "status": "healthy",
  "taints": [
    {
      "key": "degradation",
      "value": "true",
      "effect": "NoSchedule"
    }
  ]
}
```

**Status Codes:**
- `200`: OK
- `404`: Node not found
- `500`: Error fetching node

---

### Node Actions

#### POST /api/nodes/{node_id}/taint
Apply a taint to a node (prevents new pod scheduling).

**Path Parameters:**
- `node_id` (string): Node identifier

**Request Body:**
```json
{
  "taint": "degradation=true:NoSchedule"
}
```

**Taint Format:** `key=value:effect`
- `key`: Taint key (e.g., "degradation")
- `value`: Taint value (e.g., "true")
- `effect`: NoSchedule | NoExecute | PreferNoSchedule

**Response:**
```json
{
  "status": "tainted" | "demo_tainted",
  "node": "node-01",
  "taint": "degradation=true:NoSchedule"
}
```

**Status Codes:**
- `200`: Taint applied (or simulated)
- `404`: Node not found
- `500`: Error applying taint

---

#### POST /api/nodes/{node_id}/drain
Drain a node (evict all user pods gracefully).

**Path Parameters:**
- `node_id` (string): Node identifier

**Request Body:**
```json
{
  "grace_period": 30
}
```

**Parameters:**
- `grace_period` (integer, optional): Seconds to wait for pod termination (default: 30)

**Response:**
```json
{
  "status": "drained" | "demo_drained",
  "node": "node-01",
  "evicted": 5
}
```

**Status Codes:**
- `200`: Drain requested (or simulated)
- `404`: Node not found
- `500`: Error draining node

**Notes:**
- System pods (kube-system, kube-public, kube-node-lease) are never evicted
- Pods respect their graceful termination period
- Operation may take 30+ seconds for large workloads

---

#### POST /api/nodes/{node_id}/remove-taint
Remove a taint from a node.

**Path Parameters:**
- `node_id` (string): Node identifier

**Request Body:**
```json
{
  "key": "degradation"
}
```

**Parameters:**
- `key` (string): Taint key to remove

**Response:**
```json
{
  "status": "removed" | "demo_removed",
  "node": "node-01",
  "taintKey": "degradation"
}
```

**Status Codes:**
- `200`: Taint removed (or simulated)
- `404`: Node not found
- `500`: Error removing taint

---

### Events

#### GET /api/events
Get event log.

**Query Parameters:**
- `type` (string, optional): Filter by type (risk|action|info)
- `limit` (integer, optional): Limit number of events (default: 50)

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "type": "action",
    "title": "Node Tainted",
    "description": "Applied taint degradation=true:NoSchedule to node-01",
    "nodeId": "node-01",
    "details": {
      "taint": "degradation=true:NoSchedule",
      "mode": "demo"
    },
    "timestamp": "2026-02-10T22:34:32.435070",
    "timeString": "22:34:32"
  },
  ...
]
```

**Event Types:**
- `risk`: Risk detected (degradation, high metrics)
- `action`: Action taken (taint, drain, migration)
- `info`: Information message

**Status Codes:**
- `200`: OK
- `500`: Error fetching events

---

#### GET /api/events/stream
Server-Sent Events stream for real-time event updates.

**Headers:**
- `Content-Type`: text/event-stream
- `Cache-Control`: no-cache

**Event Format:**
```
data: {"id":"...", "type":"action", "title":"...", ...}\n\n
```

**Usage Example (JavaScript):**
```javascript
const es = new EventSource('/api/events/stream');
es.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('New event:', data);
};
```

**Status Codes:**
- `200`: Stream established
- `500`: Connection error

---

### Monitoring

#### POST /api/monitoring/start
Start the monitoring service.

**Request Body:**
```json
{}
```

**Response:**
```json
{
  "status": "started",
  "message": "Monitoring service started successfully"
}
```

**Status Codes:**
- `200`: OK
- `500`: Error starting monitoring

---

#### POST /api/monitoring/stop
Stop the monitoring service.

**Request Body:**
```json
{}
```

**Response:**
```json
{
  "status": "stopped",
  "message": "Monitoring service stopped"
}
```

**Status Codes:**
- `200`: OK
- `500`: Error stopping monitoring

---

### Machine Learning

#### GET /api/predictions
Get ML predictions for all nodes.

**Response:**
```json
[
  {
    "node_id": "node-01",
    "node_name": "worker-01",
    "prediction": {
      "is_at_risk": false,
      "risk_score": 0.23,
      "risk_factors": ["cpu_high", "temp_elevated"]
    }
  },
  ...
]
```

**Status Codes:**
- `200`: OK
- `500`: Error fetching predictions

---

#### GET /api/ml-insights
Get ML model information and insights.

**Response:**
```json
{
  "model_type": "Gradient Boosting",
  "features": [
    {"feature": "cpu_usage", "importance": 0.25},
    {"feature": "memory_usage", "importance": 0.20},
    {"feature": "temperature", "importance": 0.18},
    ...
  ],
  "accuracy": 0.87,
  "threshold": 0.65,
  "retrain_interval": "24h"
}
```

**Status Codes:**
- `200`: OK
- `500`: Error fetching insights

---

## Error Responses

All error responses follow this format:

```json
{
  "error": "Error message describing what went wrong"
}
```

**Common Error Codes:**
- `400`: Bad request (invalid parameters)
- `404`: Resource not found
- `500`: Server error

---

## Rate Limits

No rate limiting is currently implemented. For production use, consider adding:
- Per-IP limits
- Per-user limits
- Burst limits

---

## Authentication

Currently, there is **no authentication** on the API. For production:
1. Add API key authentication
2. Use JWT tokens
3. Integrate with OAuth2
4. Use mTLS for in-cluster communication

---

## Example Workflows

### Workflow 1: Taint a Degraded Node

```bash
# Get all nodes
curl http://127.0.0.1:5000/api/nodes

# Find degraded node (high CPU/memory)
# Note the node_id

# Apply taint
curl -X POST http://127.0.0.1:5000/api/nodes/node-01/taint \
  -H "Content-Type: application/json" \
  -d '{"taint": "degradation=true:NoSchedule"}'

# Check event log
curl http://127.0.0.1:5000/api/events
```

### Workflow 2: Drain and Recover

```bash
# Drain node
curl -X POST http://127.0.0.1:5000/api/nodes/node-01/drain \
  -H "Content-Type: application/json" \
  -d '{"grace_period": 30}'

# Wait for eviction to complete
sleep 35

# Remove taint to allow new pods
curl -X POST http://127.0.0.1:5000/api/nodes/node-01/remove-taint \
  -H "Content-Type: application/json" \
  -d '{"key": "degradation"}'

# Verify node is healthy
curl http://127.0.0.1:5000/api/nodes/node-01
```

### Workflow 3: Monitor for Risks

```bash
# Get ML predictions
curl http://127.0.0.1:5000/api/predictions

# Subscribe to events (JavaScript)
const es = new EventSource('/api/events/stream');
es.onmessage = (e) => {
  const event = JSON.parse(e.data);
  if (event.type === 'risk') {
    console.log('Risk detected:', event.description);
  }
};
```

---

## Testing with curl

```bash
# Health check
curl http://127.0.0.1:5000/api/health | jq

# Get nodes
curl http://127.0.0.1:5000/api/nodes | jq

# Get specific node
curl http://127.0.0.1:5000/api/nodes/node-01 | jq

# Get stats
curl http://127.0.0.1:5000/api/stats | jq

# Get events
curl http://127.0.0.1:5000/api/events | jq

# Apply taint
curl -X POST http://127.0.0.1:5000/api/nodes/node-01/taint \
  -H "Content-Type: application/json" \
  -d '{"taint":"test=true:NoSchedule"}' | jq
```

---

## Performance Considerations

### Request Latency
- Health check: ~10ms
- Node listing: ~100-500ms (depends on cluster size)
- Taint/Drain: ~1-60s (depends on pod count)

### Resource Usage
- Memory: ~100-200MB base
- CPU: Minimal (mostly idle)
- Network: 1-5KB per request

---

## Versioning

Current API version: `v1` (implicit)

Future versions may be:
- `/api/v2/nodes` (with additional fields)
- `/api/v1/legacy` (deprecated)

---

## CORS

CORS is enabled for all origins. For production, restrict to:
```python
CORS(app, resources={
    r"/api/*": {"origins": ["https://internal.domain.com"]}
})
```

---

## See Also

- [Kubernetes API Documentation](https://kubernetes.io/docs/reference/kubernetes-api/)
- [REST API Best Practices](https://restfulapi.net/)
- [System Architecture](CLUSTER_INTEGRATION.md)
