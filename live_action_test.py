import json
import sys

url_base = 'http://127.0.0.1:5000'

try:
    import requests
except Exception:
    requests = None

node_id = 'node-01'

def post(path, data):
    url = url_base + path
    if requests:
        r = requests.post(url, json=data)
        print(path, r.status_code, r.text)
    else:
        import urllib.request
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')
        with urllib.request.urlopen(req) as resp:
            print(path, resp.status, resp.read().decode())

def get(path):
    url = url_base + path
    if requests:
        r = requests.get(url)
        print(path, r.status_code, r.text)
    else:
        import urllib.request
        with urllib.request.urlopen(url) as resp:
            print(path, resp.status, resp.read().decode())

if __name__ == '__main__':
    get(f'/api/nodes/{node_id}')
    post(f'/api/nodes/{node_id}/taint', {'taint': 'degradation=true:NoSchedule'})
    get(f'/api/nodes/{node_id}')
    post(f'/api/nodes/{node_id}/drain', {'grace_period': 5})
    get(f'/api/nodes/{node_id}')
    post(f'/api/nodes/{node_id}/remove-taint', {'key': 'degradation'})
    get(f'/api/nodes/{node_id}')
