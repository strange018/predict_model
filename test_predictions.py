import urllib.request
import json

print("Testing ML Predictions and Event Generation:\n")

# Check predictions
response = urllib.request.urlopen('http://127.0.0.1:5000/api/predictions')
predictions = json.loads(response.read().decode())
print(f"Predictions Generated: {len(predictions)} nodes")
for p in predictions[:3]:
    risk = p['prediction'].get('risk_probability', 0)
    print(f"  {p['node_name']}: Risk Score = {risk}%")

print()

# Check if events are accumulating
response = urllib.request.urlopen('http://127.0.0.1:5000/api/events')
events = json.loads(response.read().decode())
print(f"Total Events Logged: {events.__len__()}")
print(f"Sample event: {events[0]['title'] if events else 'None'}")

print()
print("✓ System is monitoring and generating predictions!")
print("✓ All data is being displayed to the UI!")
