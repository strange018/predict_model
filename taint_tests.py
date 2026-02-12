import json
from app import app, _ensure_demo_nodes

client = app.test_client()

# Ensure demo nodes exist
_ensure_demo_nodes()
nodes = client.get('/api/nodes').get_json()
print('Nodes:', [n['node_id'] for n in nodes])

node_id = nodes[0]['node_id']
print('Testing on node:', node_id)

# Taint
resp = client.post(f'/api/nodes/{node_id}/taint', json={'taint': 'degradation=true:NoSchedule'})
print('Taint response:', resp.status_code, resp.get_json())

# Get node details
resp = client.get(f'/api/nodes/{node_id}')
print('Node after taint:', resp.status_code, json.dumps(resp.get_json(), indent=2))

# Drain
resp = client.post(f'/api/nodes/{node_id}/drain', json={'grace_period': 5})
print('Drain response:', resp.status_code, resp.get_json())

# Get node details after drain
resp = client.get(f'/api/nodes/{node_id}')
print('Node after drain:', resp.status_code, json.dumps(resp.get_json(), indent=2))

# Remove taint
resp = client.post(f'/api/nodes/{node_id}/remove-taint', json={'key': 'degradation'})
print('Remove taint response:', resp.status_code, resp.get_json())

# Final node state
resp = client.get(f'/api/nodes/{node_id}')
print('Final node:', json.dumps(resp.get_json(), indent=2))
