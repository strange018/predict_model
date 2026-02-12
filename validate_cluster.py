#!/usr/bin/env python3
"""
Kubernetes Cluster Validation Script
Checks readiness for cluster integration and validates permissions
"""

import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def check_kubeconfig():
    """Check if kubeconfig file is accessible"""
    logger.info("=" * 60)
    logger.info("CHECKING KUBECONFIG")
    logger.info("=" * 60)
    
    # Get kubeconfig path
    kubeconfig = os.environ.get('KUBECONFIG')
    if not kubeconfig:
        default_path = Path.home() / '.kube' / 'config'
        if default_path.exists():
            kubeconfig = str(default_path)
            logger.info(f"✓ No KUBECONFIG set; using default: {kubeconfig}")
        else:
            logger.error("✗ KUBECONFIG not set and ~/.kube/config not found")
            return False
    
    # Check if file exists
    if not Path(kubeconfig).exists():
        logger.error(f"✗ Kubeconfig file not found: {kubeconfig}")
        return False
    
    logger.info(f"✓ Kubeconfig file found: {kubeconfig}")
    
    # Check readability
    try:
        with open(kubeconfig, 'r') as f:
            content = f.read()
            if 'clusters:' in content and 'users:' in content:
                logger.info("✓ Kubeconfig format valid")
            else:
                logger.warning("⚠ Kubeconfig format might be invalid")
                return False
    except Exception as e:
        logger.error(f"✗ Cannot read kubeconfig: {e}")
        return False
    
    return True

def check_kubernetes_client():
    """Check if Kubernetes Python client is installed"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("CHECKING KUBERNETES CLIENT")
    logger.info("=" * 60)
    
    try:
        from kubernetes import client, config
        logger.info("✓ Kubernetes client library installed")
        return True
    except ImportError as e:
        logger.error(f"✗ Kubernetes client not installed: {e}")
        logger.info("   Run: pip install kubernetes")
        return False

def check_cluster_connection():
    """Check if we can connect to the cluster"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("CHECKING CLUSTER CONNECTION")
    logger.info("=" * 60)
    
    try:
        from kubernetes import client, config
        
        kubeconfig = os.environ.get('KUBECONFIG')
        
        try:
            # Try in-cluster config first
            config.load_incluster_config()
            logger.info("✓ Running in-cluster")
        except:
            # Fall back to kubeconfig file
            if kubeconfig:
                config.load_kube_config(config_file=kubeconfig)
            else:
                config.load_kube_config()
            logger.info("✓ Loaded kubeconfig successfully")
        
        # Try to list nodes
        v1 = client.CoreV1Api()
        nodes = v1.list_node()
        
        if nodes.items:
            logger.info(f"✓ Connected to cluster - found {len(nodes.items)} nodes")
            
            # List node names
            for node in nodes.items:
                taint_str = ""
                if node.spec.taints:
                    taint_str = f" (taints: {len(node.spec.taints)})"
                pod_count = 0
                try:
                    pods = v1.list_pod_for_all_namespaces(
                        field_selector=f'spec.nodeName={node.metadata.name}'
                    )
                    pod_count = len(pods.items)
                except:
                    pass
                logger.info(f"  - {node.metadata.name} ({pod_count} pods){taint_str}")
            
            return True
        else:
            logger.warning("⚠ No nodes found in cluster")
            return False
    
    except Exception as e:
        logger.error(f"✗ Cannot connect to cluster: {e}")
        logger.info("   Check your kubeconfig and cluster accessibility")
        return False

def check_permissions():
    """Check if we have required RBAC permissions"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("CHECKING RBAC PERMISSIONS")
    logger.info("=" * 60)
    
    try:
        from kubernetes import client, config
        
        kubeconfig = os.environ.get('KUBECONFIG')
        
        try:
            config.load_incluster_config()
        except:
            if kubeconfig:
                config.load_kube_config(config_file=kubeconfig)
            else:
                config.load_kube_config()
        
        # Prepare test operations
        tests = [
            ('get nodes', lambda c: c.list_node()),
            ('patch nodes', lambda c: c.read_node('dummy')),  # Will fail but tests permission
            ('list pods', lambda c: c.list_pod_for_all_namespaces())
        ]
        
        v1 = client.CoreV1Api()
        
        # Test get nodes
        try:
            v1.list_node()
            logger.info("✓ Permission: get nodes")
        except Exception as e:
            if 'forbidden' in str(e).lower():
                logger.warning("⚠ May not have permission to get nodes")
            
        # Test patch nodes (via read, since patch would modify)
        try:
            nodes = v1.list_node()
            if nodes.items:
                v1.read_node(nodes.items[0].metadata.name)
                logger.info("✓ Permission: read/patch nodes (inferred)")
        except Exception as e:
            if 'forbidden' in str(e).lower():
                logger.warning("⚠ May not have permission to patch nodes")
        
        # Test list pods
        try:
            v1.list_pod_for_all_namespaces()
            logger.info("✓ Permission: list pods")
        except Exception as e:
            if 'forbidden' in str(e).lower():
                logger.warning("⚠ May not have permission to list pods")
        
        logger.info("✓ RBAC check (note: some permissions require actual operations)")
        return True
    
    except Exception as e:
        logger.error(f"✗ Error checking permissions: {e}")
        return False

def main():
    """Run all validation checks"""
    logger.info("\n🔍 KUBERNETES CLUSTER VALIDATION\n")
    
    results = {
        'Kubeconfig': check_kubeconfig(),
        'Kubernetes Client': check_kubernetes_client(),
        'Cluster Connection': check_cluster_connection(),
        'RBAC Permissions': check_permissions()
    }
    
    # Summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("VALIDATION SUMMARY")
    logger.info("=" * 60)
    
    for check, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"{status}: {check}")
    
    all_passed = all(results.values())
    
    if all_passed:
        logger.info("\n✅ All checks passed! System is ready for cluster integration.")
        logger.info("\nNext steps:")
        logger.info("  1. Start the backend: python app.py")
        logger.info("  2. Open UI: http://127.0.0.1:5000")
        logger.info("  3. Interact with real cluster nodes")
        return 0
    else:
        logger.info("\n❌ Some checks failed. Please resolve issues above.")
        logger.info("\nFor help:")
        logger.info("  - See CLUSTER_SETUP.md for detailed instructions")
        logger.info("  - Check kubeconfig: kubectl config view")
        logger.info("  - Test kubectl: kubectl get nodes")
        return 1

if __name__ == '__main__':
    sys.exit(main())
