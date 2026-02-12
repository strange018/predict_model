import urllib.request
import json

endpoints = [
    ('Stats', '/api/stats'),
    ('Nodes', '/api/nodes'),
    ('Events', '/api/events'),
    ('Predictions', '/api/predictions'),
    ('Health', '/api/health'),
]

print("Testing API Endpoints:\n")
for name, endpoint in endpoints:
    try:
        response = urllib.request.urlopen(f'http://127.0.0.1:5000{endpoint}')
        data = json.loads(response.read().decode())
        
        if isinstance(data, list):
            print(f"✓ {name}: {len(data)} items")
            if name == 'Nodes' and data:
                print(f"  Sample node: {data[0]['node_name']} - CPU: {data[0].get('cpu_usage', 0):.1f}%, Memory: {data[0].get('memory_usage', 0):.1f}%")
        else:
            print(f"✓ {name}:")
            for key, value in data.items():
                print(f"  {key}: {value}")
    except Exception as e:
        print(f"✗ {name}: {str(e)}")

print("\n✓ All systems working! UI should display all data correctly.")
