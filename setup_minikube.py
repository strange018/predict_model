#!/usr/bin/env python3
"""
Minikube Setup Helper - Automated setup for local K8s testing
Checks for Minikube, starts cluster, validates connection
"""

import subprocess
import sys
import os
import time

def run_cmd(cmd, shell=True, check=False):
    """Run command and return output"""
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, check=check)
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return 1, "", str(e)

def check_minikube():
    """Check if Minikube is installed"""
    print("=" * 60)
    print("CHECKING MINIKUBE")
    print("=" * 60)
    
    code, out, err = run_cmd("minikube version")
    if code == 0:
        print(f"✓ Minikube installed: {out}")
        return True
    else:
        print("✗ Minikube not found")
        print("\nTo install Minikube:")
        print("  1. Download: https://minikube.sigs.k8s.io/docs/start/")
        print("  2. Or use Chocolatey: choco install minikube")
        print("  3. Then run this script again")
        return False

def check_virtualization():
    """Check if Hyper-V is available"""
    print("\n" + "=" * 60)
    print("CHECKING VIRTUALIZATION")
    print("=" * 60)
    
    # Windows Hyper-V check
    code, out, err = run_cmd("powershell -Command \"(Get-WindowsOptionalFeature -FeatureName Hyper-V).State\"", shell=True)
    
    if code == 0 and "Enabled" in out:
        print("✓ Hyper-V is available")
        return "hyperv"
    
    # Check if VirtualBox is available
    code, out, err = run_cmd("VirtualBoxVM --version")
    if code == 0:
        print("✓ VirtualBox is available")
        return "virtualbox"
    
    print("⚠ No virtualization backend found")
    print("  Install one of:")
    print("  • Hyper-V (built-in on Windows Pro/Enterprise)")
    print("  • VirtualBox (free): https://www.virtualbox.org/")
    print("  • Docker Desktop (has built-in K8s support, alternative to Minikube)")
    return None

def start_minikube(driver):
    """Start Minikube cluster"""
    print("\n" + "=" * 60)
    print("STARTING MINIKUBE")
    print("=" * 60)
    
    print(f"Starting Minikube with {driver} driver...")
    print("(This may take 2-3 minutes on first startup)\n")
    
    code, out, err = run_cmd(f"minikube start --driver {driver}")
    
    if code == 0:
        print("✓ Minikube started successfully")
        return True
    else:
        print(f"✗ Failed to start Minikube: {err}")
        return False

def verify_kubectl():
    """Verify kubectl can access cluster"""
    print("\n" + "=" * 60)
    print("VERIFYING KUBECTL CONNECTION")
    print("=" * 60)
    
    code, out, err = run_cmd("kubectl get nodes")
    
    if code == 0:
        print("✓ kubectl connected to cluster")
        print(f"\nAvailable nodes:")
        lines = out.split('\n')
        for line in lines:
            print(f"  {line}")
        return True
    else:
        print(f"✗ kubectl connection failed: {err}")
        return False

def get_kubeconfig_path():
    """Get kubeconfig path"""
    print("\n" + "=" * 60)
    print("KUBECONFIG LOCATION")
    print("=" * 60)
    
    home = os.path.expanduser("~")
    kubeconfig = os.path.join(home, ".kube", "config")
    
    if os.path.exists(kubeconfig):
        print(f"✓ Kubeconfig found at: {kubeconfig}")
        return kubeconfig
    else:
        print(f"⚠ Kubeconfig not found at: {kubeconfig}")
        code, out, err = run_cmd("kubectl config view")
        if code == 0:
            print("✓ But kubectl can access cluster (in-memory config)")
        return kubeconfig

def show_next_steps():
    """Show what to do next"""
    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    
    print("""
1. Verify cluster is running:
   kubectl get pods -A

2. Validate our system's cluster access:
   python validate_cluster.py

3. Connect system to cluster:
   python app.py

4. Open web UI:
   http://127.0.0.1:5000

5. Test operations:
   • Click "Taint" to prevent new pod scheduling
   • Click "Drain" to evict pods from node
   • Click "Remove Taint" to restore node
   • Watch events in log for live updates

6. When done, stop Minikube:
   minikube stop
""")

def main():
    print("\n🚀 MINIKUBE SETUP FOR PREDICTIVE INFRASTRUCTURE\n")
    
    # Check Minikube installation
    if not check_minikube():
        return 1
    
    # Check virtualization
    driver = check_virtualization()
    if not driver:
        print("\n❌ Please install a virtualization backend first")
        return 1
    
    # Start Minikube
    if not start_minikube(driver):
        print("\n❌ Failed to start Minikube")
        print("Try: minikube delete && minikube start --driver", driver)
        return 1
    
    # Wait a moment for cluster to be ready
    print("\nWaiting for cluster to stabilize...")
    time.sleep(5)
    
    # Verify connection
    if not verify_kubectl():
        print("\n⚠ Kubectl connection issues - trying again...")
        time.sleep(10)
        if not verify_kubectl():
            print("\n❌ Could not verify cluster access")
            return 1
    
    # Get kubeconfig
    kubeconfig = get_kubeconfig_path()
    
    # Show next steps
    show_next_steps()
    
    print("\n✅ MINIKUBE READY!")
    print(f"✅ Kubeconfig: {kubeconfig}")
    print("✅ Ready to run: python app.py\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
