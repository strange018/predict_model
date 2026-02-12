"""
Kubernetes Integration Manager
Handles cluster communication, node management, and workload orchestration
"""

import logging
import os
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import random

logger = logging.getLogger(__name__)


class KubernetesManager:
    """
    Manages interaction with Kubernetes cluster
    Gathers metrics, applies taints, drains nodes, and migrates workloads
    """
    
    def __init__(self):
        """Initialize Kubernetes client"""
        self.available = False
        try:
            # Try to load in-cluster config first (running in pod)
            config.load_incluster_config()
            logger.info("✓ Loaded in-cluster Kubernetes config")
            self.available = True
        except:
            try:
                # Fall back to kubeconfig file
                kube_path = None
                if 'KUBECONFIG' in os.environ:
                    kube_path = os.environ.get('KUBECONFIG')

                if kube_path:
                    config.load_kube_config(config_file=kube_path)
                    logger.info(f"✓ Loaded kubeconfig from {kube_path}")
                    self.available = True
                else:
                    config.load_kube_config()
                    logger.info("✓ Loaded kubeconfig from default location")
                    self.available = True
            except Exception as e:
                logger.warning(f"Kubernetes config not available: {e}")
                logger.info("Will operate in DEMO MODE without real cluster")
                self.available = False
        
        # Try to initialize clients only if kubeconfig loaded
        if self.available:
            try:
                self.v1 = client.CoreV1Api()
                self.apps_v1 = client.AppsV1Api()
                self.batch_v1 = client.BatchV1Api()
                logger.info("✓ Kubernetes manager initialized successfully")
            except Exception as e:
                logger.warning(f"Could not initialize K8s clients: {e}")
                self.available = False
        else:
            # Create placeholder clients (won't be used in demo mode)
            self.v1 = None
            self.apps_v1 = None
            self.batch_v1 = None
            logger.info("Kubernetes manager in DEMO MODE")
    
    def get_nodes_metrics(self):
        """Get all nodes with their current metrics"""
        # In demo mode (no K8s cluster), return empty list
        # App will use demo generator instead
        if not self.available or self.v1 is None:
            return []
        
        try:
            nodes = self.v1.list_node()
            nodes_data = []
            
            for node in nodes.items:
                node_data = {
                    'node_id': node.metadata.name,
                    'node_name': node.metadata.name,
                    'region': node.metadata.labels.get('topology.kubernetes.io/region', 'unknown'),
                    'status': node.status.conditions[-1].status if node.status.conditions else 'Unknown',
                    'pods': self._get_node_pods(node.metadata.name)
                }
                
                # Try to get metrics if metrics-server is available
                try:
                    cpu, memory = self._get_node_resource_usage(node.metadata.name)
                    node_data['cpu_usage'] = cpu
                    node_data['memory_usage'] = memory
                except:
                    # Fallback to random for demo
                    node_data['cpu_usage'] = random.uniform(20, 80)
                    node_data['memory_usage'] = random.uniform(25, 75)
                
                # Simulated data (would come from monitoring stack in production)
                node_data['temperature'] = random.uniform(45, 75)
                node_data['network_latency'] = random.uniform(2, 30)
                node_data['disk_io'] = random.uniform(10, 70)
                
                nodes_data.append(node_data)
            
            return nodes_data
        
        except Exception as e:
            logger.error(f"Error fetching nodes: {e}")
            raise
    
    def get_node_details(self, node_id):
        """Get detailed information about a specific node"""
        try:
            node = self.v1.read_node(node_id)
            
            node_data = {
                'node_id': node.metadata.name,
                'node_name': node.metadata.name,
                'labels': node.metadata.labels,
                'taints': [
                    {'key': t.key, 'value': t.value, 'effect': t.effect}
                    for t in (node.spec.taints or [])
                ],
                'capacity': {
                    'cpu': node.status.capacity.get('cpu'),
                    'memory': node.status.capacity.get('memory')
                },
                'pods': self._get_node_pods(node_id)
            }
            
            return node_data
        
        except Exception as e:
            logger.error(f"Error fetching node {node_id}: {e}")
            raise
    
    def _get_node_pods(self, node_name):
        """Get all pods running on a specific node"""
        try:
            pods = self.v1.list_pod_for_all_namespaces(
                field_selector=f'spec.nodeName={node_name}'
            )
            return [
                {
                    'name': pod.metadata.name,
                    'namespace': pod.metadata.namespace,
                    'status': pod.status.phase
                }
                for pod in pods.items
            ]
        except Exception as e:
            logger.warning(f"Error fetching pods for node {node_name}: {e}")
            return []
    
    def _get_node_resource_usage(self, node_name):
        """
        Get resource usage for node
        Note: Requires metrics-server to be installed in cluster
        """
        try:
            # This would use metrics API if available
            # For now, return placeholder values
            return random.uniform(20, 80), random.uniform(25, 75)
        except Exception as e:
            logger.warning(f"Metrics not available: {e}")
            raise
    
    def taint_node(self, node_name, taint_spec):
        """
        Apply a taint to a node to prevent new pod scheduling
        
        taint_spec format: "key=value:effect" (e.g., "degradation=true:NoSchedule")
        """
        try:
            key, effect = taint_spec.split(':')
            key_val = key.split('=')
            key_name = key_val[0]
            key_value = key_val[1] if len(key_val) > 1 else 'true'
            
            node = self.v1.read_node(node_name)
            
            # Create new taint object
            new_taint = client.V1Taint(
                key=key_name,
                value=key_value,
                effect=effect
            )
            
            # Add to existing taints
            if node.spec.taints:
                node.spec.taints.append(new_taint)
            else:
                node.spec.taints = [new_taint]
            
            # Update node
            self.v1.patch_node(node_name, node)
            logger.info(f"✓ Applied taint '{taint_spec}' to node {node_name}")
            
            return True
        
        except Exception as e:
            logger.error(f"Error tainting node {node_name}: {e}")
            raise
    
    def remove_taint(self, node_name, taint_key):
        """Remove a taint from a node"""
        try:
            node = self.v1.read_node(node_name)
            
            if node.spec.taints:
                node.spec.taints = [
                    t for t in node.spec.taints if t.key != taint_key
                ]
                self.v1.patch_node(node_name, node)
                logger.info(f"✓ Removed taint '{taint_key}' from node {node_name}")
            
            return True
        
        except Exception as e:
            logger.error(f"Error removing taint from node {node_name}: {e}")
            raise
    
    def label_node(self, node_name, labels):
        """Add labels to a node"""
        try:
            node = self.v1.read_node(node_name)
            
            if node.metadata.labels:
                node.metadata.labels.update(labels)
            else:
                node.metadata.labels = labels
            
            self.v1.patch_node(node_name, node)
            logger.info(f"✓ Applied labels to node {node_name}")
            
            return True
        
        except Exception as e:
            logger.error(f"Error labeling node {node_name}: {e}")
            raise
    
    def find_best_target_node(self, source_node_id):
        """Find the best healthy node to migrate workloads to"""
        try:
            nodes = self.v1.list_node()
            
            best_node = None
            best_score = float('inf')
            
            for node in nodes.items:
                node_name = node.metadata.name
                
                # Skip source node and tainted nodes
                if node_name == source_node_id:
                    continue
                
                if node.spec.taints:
                    continue  # Skip tainted nodes
                
                # Calculate fitness score (lower is better)
                pods = len(self._get_node_pods(node_name))
                score = pods
                
                if score < best_score:
                    best_score = score
                    best_node = {
                        'name': node_name,
                        'pod_count': pods
                    }
            
            return best_node
        
        except Exception as e:
            logger.error(f"Error finding target node: {e}")
            return None
    
    def drain_node(self, node_name, grace_period=30):
        """
        Drain a node by evicting pods gracefully
        Returns number of pods evicted
        """
        try:
            pods = self.v1.list_pod_for_all_namespaces(
                field_selector=f'spec.nodeName={node_name}'
            )
            
            evicted_count = 0
            
            for pod in pods.items:
                # Skip pods in kube-system and kube-public (system pods)
                if pod.metadata.namespace in ['kube-system', 'kube-public', 'kube-node-lease']:
                    continue
                
                try:
                    # Create eviction request
                    eviction = client.V1Eviction(
                        metadata=client.V1ObjectMeta(
                            name=pod.metadata.name,
                            namespace=pod.metadata.namespace
                        ),
                        delete_options=client.V1DeleteOptions(
                            grace_period_seconds=grace_period
                        )
                    )
                    
                    # Evict pod
                    self.v1.create_namespaced_pod_eviction(
                        pod.metadata.name,
                        pod.metadata.namespace,
                        eviction
                    )
                    
                    evicted_count += 1
                    logger.info(f"✓ Evicted pod {pod.metadata.name} from {node_name}")
                
                except ApiException as e:
                    logger.warning(f"Could not evict pod {pod.metadata.name}: {e}")
            
            logger.info(f"✓ Drained {evicted_count} pods from {node_name}")
            return evicted_count
        
        except Exception as e:
            logger.error(f"Error draining node {node_name}: {e}")
            raise
    
    def get_cluster_info(self):
        """Get general cluster information"""
        try:
            cluster_info = client.client.configuration.Configuration()
            
            return {
                'cluster': cluster_info.host,
                'version': client.VersionApi().get_code().git_version
            }
        except Exception as e:
            logger.warning(f"Could not fetch cluster info: {e}")
            return {'cluster': 'unknown', 'version': 'unknown'}
