import urllib.request
import json
import time

print("Monitoring Data Updates:")
print("=" * 60)

# Get first set of data
response1 = urllib.request.urlopen('http://127.0.0.1:5000/api/nodes')
nodes1 = json.loads(response1.read().decode())

# Extract metrics from first node
node1_first = nodes1[0]
print(f"Time 0s - {node1_first['node_name']}:")
print(f"  CPU: {node1_first['cpu_usage']:.1f}%")
print(f"  Memory: {node1_first['memory_usage']:.1f}%")
print(f"  Temperature: {node1_first['temperature']:.1f}°C")

print("\nWaiting 3 seconds for monitoring update...")
time.sleep(3)

# Get second set of data
response2 = urllib.request.urlopen('http://127.0.0.1:5000/api/nodes')
nodes2 = json.loads(response2.read().decode())

node1_second = nodes2[0]
print(f"\nTime 3s - {node1_second['node_name']}:")
print(f"  CPU: {node1_second['cpu_usage']:.1f}%")
print(f"  Memory: {node1_second['memory_usage']:.1f}%")
print(f"  Temperature: {node1_second['temperature']:.1f}°C")

print("\n" + "=" * 60)

# Check if values changed
cpu_changed = node1_first['cpu_usage'] != node1_second['cpu_usage']
memory_changed = node1_first['memory_usage'] != node1_second['memory_usage']
temp_changed = node1_first['temperature'] != node1_second['temperature']

if cpu_changed or memory_changed or temp_changed:
    print("✓ DATA IS UPDATING! System is monitoring!")
    print(f"  CPU changed: {cpu_changed}")
    print(f"  Memory changed: {memory_changed}")
    print(f"  Temperature changed: {temp_changed}")
else:
    print("✗ Data not updating")
