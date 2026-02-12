#!/usr/bin/env python3
"""
Quick test to verify UI updates are working
This simulates button clicks and verifies the backend responds correctly
"""

import requests
import json
import time
import sys

# Fix Unicode issues on Windows
if sys.platform == 'win32':
    import os
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_URL = "http://127.0.0.1:5000"

def test_health():
    """Test backend is running"""
    try:
        resp = requests.get(f"{BASE_URL}/api/health")
        print(f"✓ Backend health: {resp.json()}")
        return resp.status_code == 200
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False

def test_nodes():
    """Get current nodes"""
    try:
        resp = requests.get(f"{BASE_URL}/api/nodes")
        nodes = resp.json()
        print(f"✓ Got {len(nodes)} nodes")
        for n in nodes:
            print(f"  - {n['node_name']} (taints: {len(n.get('taints', []))})")
        return nodes
    except Exception as e:
        print(f"✗ Failed to get nodes: {e}")
        return []

def test_taint_action():
    """Test taint button action"""
    nodes = test_nodes()
    if not nodes:
        return False
    
    node_id = nodes[0]['node_id']
    print(f"\n📌 Tainting node: {node_id}")
    
    try:
        resp = requests.post(
            f"{BASE_URL}/api/nodes/{node_id}/taint",
            json={"taint": "degradation=true:NoSchedule"},
            headers={"Content-Type": "application/json"}
        )
        print(f"✓ Taint response: {resp.status_code}")
        
        # Check if taints were applied
        time.sleep(0.5)
        resp2 = requests.get(f"{BASE_URL}/api/nodes/{node_id}")
        node = resp2.json()
        taints = node.get('taints', [])
        print(f"  Node now has {len(taints)} taints: {taints}")
        return len(taints) > 0
    except Exception as e:
        print(f"✗ Taint failed: {e}")
        return False

def test_remove_taint():
    """Test remove taint button action"""
    nodes = test_nodes()
    if not nodes:
        return False
    
    # Find a tainted node
    tainted_node = None
    for n in nodes:
        if n.get('taints'):
            tainted_node = n
            break
    
    if not tainted_node:
        print("\n✗ No tainted node to test remove-taint")
        return False
    
    print(f"\n🧹 Removing taint from: {tainted_node['node_id']}")
    
    try:
        resp = requests.post(
            f"{BASE_URL}/api/nodes/{tainted_node['node_id']}/remove-taint",
            json={"key": "degradation"},
            headers={"Content-Type": "application/json"}
        )
        print(f"✓ Remove-taint response: {resp.status_code}")
        
        # Check if taints were removed
        time.sleep(0.5)
        resp2 = requests.get(f"{BASE_URL}/api/nodes/{tainted_node['node_id']}")
        node = resp2.json()
        taints = node.get('taints', [])
        print(f"  Node now has {len(taints)} taints")
        return len(taints) == 0
    except Exception as e:
        print(f"✗ Remove-taint failed: {e}")
        return False

def test_drain():
    """Test drain button action"""
    nodes = test_nodes()
    if not nodes or not nodes[0].get('pods'):
        print("\n⚠️ No pods to drain (demo may not have any)")
        return False
    
    node_id = nodes[0]['node_id']
    pod_count_before = len(nodes[0].get('pods', []))
    print(f"\n💧 Draining node: {node_id} (has {pod_count_before} pods)")
    
    try:
        resp = requests.post(
            f"{BASE_URL}/api/nodes/{node_id}/drain",
            json={"grace_period": 30},
            headers={"Content-Type": "application/json"}
        )
        print(f"✓ Drain response: {resp.status_code}")
        
        # Check if pods were drained
        time.sleep(0.5)
        resp2 = requests.get(f"{BASE_URL}/api/nodes/{node_id}")
        node = resp2.json()
        pod_count_after = len(node.get('pods', []))
        print(f"  Pods before: {pod_count_before}, after: {pod_count_after}")
        return pod_count_after == 0
    except Exception as e:
        print(f"✗ Drain failed: {e}")
        return False

def test_events():
    """Check if events are being recorded"""
    try:
        resp = requests.get(f"{BASE_URL}/api/events")
        events = resp.json()
        print(f"\n📋 Recent events ({len(events)} total):")
        for e in events[-5:]:  # Show last 5
            print(f"  [{e['type']}] {e['description']}")
        return len(events) > 0
    except Exception as e:
        print(f"✗ Failed to get events: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("UI UPDATE INTEGRATION TEST")
    print("=" * 50)
    
    if not test_health():
        print("\n❌ Backend not running! Start it first with: python app.py")
        exit(1)
    
    test_nodes()
    test_events()
    
    success = 0
    total = 3
    
    if test_taint_action():
        success += 1
        print("✓ Taint action works")
    else:
        print("✗ Taint action failed")
    
    if test_remove_taint():
        success += 1
        print("✓ Remove-taint action works")
    else:
        print("✗ Remove-taint action failed")
    
    if test_drain():
        success += 1
        print("✓ Drain action works")
    else:
        print("✗ Drain action skipped (no pods)")
    
    print("\n" + "=" * 50)
    print(f"RESULT: {success}/{total} button actions working")
    print("=" * 50)
