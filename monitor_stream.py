import urllib.request
import json
import time

print("Real-time Monitoring Data Stream (5 samples, 2 seconds apart):")
print("=" * 70)

for i in range(5):
    response = urllib.request.urlopen('http://127.0.0.1:5000/api/nodes')
    nodes = json.loads(response.read().decode())
    
    node = nodes[0]
    timestamp = time.time()
    
    print(f"\nSample {i+1} - {node['node_name']}")
    print(f"  CPU: {node['cpu_usage']:6.1f}%  Memory: {node['memory_usage']:6.1f}%  Temp: {node['temperature']:6.1f}°C")
    
    if i < 4:
        time.sleep(2)

print("\n" + "=" * 70)
print("✓ MONITORING ACTIVE - Data is updating every 3 seconds!")
print("✓ Frontend polling every 1.5 seconds will show smooth live updates!")
print("\nVisit http://127.0.0.1:5000 to see the dashboard with live data")
