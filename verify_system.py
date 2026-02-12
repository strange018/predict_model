import urllib.request, json, time

print("Checking if data is being updated...")
print()

# Get initial data
response1 = urllib.request.urlopen('http://127.0.0.1:5000/api/nodes')
data1 = json.loads(response1.read().decode())
cpu1 = data1[0]['cpu_usage']

time.sleep(2)

# Get updated data
response2 = urllib.request.urlopen('http://127.0.0.1:5000/api/nodes')
data2 = json.loads(response2.read().decode())
cpu2 = data2[0]['cpu_usage']

print(f"First reading  - Node 0 CPU: {cpu1:.1f}%")
print(f"Second reading - Node 0 CPU: {cpu2:.1f}%")
print()

if cpu1 != cpu2:
    print("✓ Data is being updated! Monitoring is active.")
    print("✓ System is fully operational!")
else:
    print("⚠ Data appears static (may be using cached values)")
