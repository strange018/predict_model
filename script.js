// Backend API Configuration
const API_BASE = '/api';

// Infrastructure Monitor - Uses Backend API
class InfrastructureMonitor {
    constructor() {
        this.nodeMetrics = {};
        this.stats = {
            risksDetected: 0,
            workloadsMoved: 0
        };
        this.previousStats = {
            risksDetected: 0,
            workloadsMoved: 0
        };
        this.eventFilter = 'all';
        this.backendConnected = false;
    }

    async initialize() {
        try {
            // Check backend connection
            const health = await fetch(`${API_BASE}/health`);
            if (health.ok) {
                this.backendConnected = true;
                console.log('✓ Connected to backend API');
            }
        } catch (e) {
            console.warn('⚠️ Backend not available, running in demo mode');
            this.backendConnected = false;
        }

        // Start updates
        this.startMonitoring();
    }

    async startMonitoring() {
        // Initial load
        console.log('📊 Starting monitoring...');
        await this.fetchStats();
        await this.fetchNodes();
        await this.fetchEvents();
        await this.fetchAnalytics();

        // Continuous updates - FAST polling for real-time feel
        const statsPollId = setInterval(() => {
            console.log('📈 Polling stats...');
            this.fetchStats();
        }, 1000);
        const nodesPollId = setInterval(() => {
            console.log('🖥️  Polling nodes...');
            this.fetchNodes();
        }, 1500);
        const eventsPollId = setInterval(() => {
            console.log('📋 Polling events...');
            this.fetchEvents();
        }, 800);
        const analyticsPollId = setInterval(() => {
            console.log('📊 Polling analytics...');
            this.fetchAnalytics();
        }, 2000);

        console.log(`✓ Polling started: stats=${statsPollId}, nodes=${nodesPollId}, events=${eventsPollId}, analytics=${analyticsPollId}`);

        // Subscribe to server-sent events for live updates (if supported)
        this._setupEventStream();

        // Start backend monitoring if connected
        if (this.backendConnected) {
            try {
                await fetch(`${API_BASE}/monitoring/start`, { method: 'POST' });
                console.log('✓ Backend monitoring started');
            } catch (e) {
                console.warn('Could not start backend monitoring:', e);
            }
        }
    }

    highlightStatChange(elementId, oldValue, newValue) {
        if (oldValue !== newValue) {
            const element = document.getElementById(elementId);
            if (element) {
                // Add pulse animation
                element.classList.remove('stat-updated');
                void element.offsetWidth; // Trigger reflow
                element.classList.add('stat-updated');
                
                // Add visual indicator
                const badge = element.querySelector('.change-badge');
                if (!badge) {
                    const newBadge = document.createElement('span');
                    newBadge.className = 'change-badge';
                    newBadge.textContent = newValue > oldValue ? `+${newValue - oldValue}` : `${newValue - oldValue}`;
                    newBadge.style.color = newValue > oldValue ? '#dc2626' : '#22c55e';
                    element.parentElement.appendChild(newBadge);
                    setTimeout(() => newBadge.remove(), 1000);
                }
            }
        }
    }

    async fetchStats() {
        try {
            const response = await fetch(`${API_BASE}/stats`);
            if (!response.ok) throw new Error('Failed to fetch stats');
            
            const data = await response.json();
            
            // Nodes Monitored
            const nodesVal = data.nodes_monitored || 0;
            const nodesElem = document.getElementById('nodes-monitored');
            if (nodesElem) {
                nodesElem.textContent = nodesVal;
                nodesElem.classList.add('stat-updated');
                setTimeout(() => nodesElem.classList.remove('stat-updated'), 600);
            }
            
            // Average Health as percentage
            const avgHealth = Math.round(data.average_health || 100);
            const healthEl = document.getElementById('avg-health-display');
            if (healthEl) {
                const oldVal = parseInt(healthEl.textContent) || 100;
                healthEl.textContent = avgHealth + '%';
                
                // Color code the health
                if (avgHealth >= 80) {
                    healthEl.style.color = '#10b981'; // green
                } else if (avgHealth >= 60) {
                    healthEl.style.color = '#f59e0b'; // amber
                } else {
                    healthEl.style.color = '#ef4444'; // red
                }
                
                if (oldVal !== avgHealth) {
                    healthEl.classList.add('stat-updated');
                    setTimeout(() => healthEl.classList.remove('stat-updated'), 600);
                }
            }
            
            // Healthy Nodes
            const healthyNodes = data.nodes_healthy || 0;
            const healthyEl = document.getElementById('nodes-healthy');
            if (healthyEl) {
                healthyEl.textContent = healthyNodes;
                healthyEl.style.color = '#10b981';
            }
            
            // Degraded Nodes
            const degradedNodes = data.nodes_degraded || 0;
            const degradedEl = document.getElementById('nodes-degraded');
            if (degradedEl) {
                degradedEl.textContent = degradedNodes;
                degradedEl.style.color = degradedNodes > 0 ? '#ef4444' : '#64748b';
            }
            
            // Risks Detected
            const risksVal = data.risks_detected || 0;
            const risksEl = document.getElementById('risks-detected');
            if (risksEl) {
                const oldRisks = parseInt(risksEl.textContent) || 0;
                risksEl.textContent = risksVal;
                risksEl.style.color = risksVal > 0 ? '#ef4444' : '#64748b';
                
                if (oldRisks !== risksVal) {
                    this.highlightStatChange('risks-detected', oldRisks, risksVal);
                }
            }
            
            // Workloads Moved
            const workloadsVal = data.workloads_moved || 0;
            const workloadsEl = document.getElementById('workloads-moved');
            if (workloadsEl) {
                const oldWorkloads = parseInt(workloadsEl.textContent) || 0;
                workloadsEl.textContent = workloadsVal;
                workloadsEl.style.color = '#10b981';
                
                if (oldWorkloads !== workloadsVal) {
                    this.highlightStatChange('workloads-moved', oldWorkloads, workloadsVal);
                }
            }
            
            // Last Update
            this.updateTimestamp();
            
            // Log the stats update
            console.log(`✓ Stats updated: ${nodesVal} nodes | Health: ${avgHealth}% | Healthy: ${healthyNodes} | Degraded: ${degradedNodes} | Risks: ${risksVal} | Workloads: ${workloadsVal}`);
        } catch (e) {
            console.error('Error fetching stats:', e);
        }
    }

    async fetchNodes() {
        try {
            console.log('🔄 Fetching nodes...');
            const response = await fetch(`${API_BASE}/nodes`);
            if (!response.ok) throw new Error('Failed to fetch nodes');
            
            const nodes = await response.json();
            console.log(`✓ Received ${nodes.length} nodes:`, nodes.map(n => `${n.node_name}(taints:${n.taints?.length || 0})`).join(', '));
            this.renderNodeMetrics(nodes);
        } catch (e) {
            console.error('❌ Error fetching nodes:', e);
        }
    }

    async fetchEvents() {
        try {
            const response = await fetch(`${API_BASE}/events`);
            if (!response.ok) throw new Error('Failed to fetch events');
            
            const events = await response.json();
            this.renderEvents(events);
        } catch (e) {
            console.error('Error fetching events:', e);
        }
    }

    async fetchAnalytics() {
        try {
            const response = await fetch(`${API_BASE}/analytics/cluster-health`);
            if (!response.ok) throw new Error('Failed to fetch analytics');
            
            const data = await response.json();
            this.renderAnalytics(data);
        } catch (e) {
            console.error('Error fetching analytics:', e);
        }
    }

    renderAnalytics(data) {
        try {
            // Cluster Health Score
            const clusterHealth = Math.round(data.cluster_health_score || 0);
            const clusterHealthEl = document.getElementById('cluster-health');
            if (clusterHealthEl) {
                clusterHealthEl.textContent = clusterHealth + '%';
                clusterHealthEl.style.color = 
                    clusterHealth >= 80 ? '#10b981' :
                    clusterHealth >= 60 ? '#f59e0b' :
                    '#ef4444';
                clusterHealthEl.style.fontWeight = '700';
                
                const barEl = document.getElementById('cluster-health-bar');
                if (barEl) {
                    barEl.style.width = clusterHealth + '%';
                    if (clusterHealth >= 80) {
                        barEl.style.background = 'linear-gradient(90deg, #06b6d4, #10b981)';
                    } else if (clusterHealth >= 60) {
                        barEl.style.background = 'linear-gradient(90deg, #f59e0b, #fbbf24)';
                    } else {
                        barEl.style.background = 'linear-gradient(90deg, #ef4444, #f87171)';
                    }
                }
            }

            // Average Node Health
            const avgHealth = Math.round(data.average_node_health || 0);
            const avgHealthEl = document.getElementById('avg-node-health');
            if (avgHealthEl) {
                avgHealthEl.textContent = avgHealth + '%';
                avgHealthEl.style.color = 
                    avgHealth >= 80 ? '#10b981' :
                    avgHealth >= 60 ? '#f59e0b' :
                    '#ef4444';
                avgHealthEl.style.fontWeight = '700';
                
                const barEl = document.getElementById('avg-health-bar');
                if (barEl) {
                    barEl.style.width = avgHealth + '%';
                    if (avgHealth >= 80) {
                        barEl.style.background = 'linear-gradient(90deg, #06b6d4, #10b981)';
                    } else if (avgHealth >= 60) {
                        barEl.style.background = 'linear-gradient(90deg, #f59e0b, #fbbf24)';
                    } else {
                        barEl.style.background = 'linear-gradient(90deg, #ef4444, #f87171)';
                    }
                }
            }

            // Nodes at Risk
            const nodesAtRisk = data.nodes_at_risk || 0;
            const riskEl = document.getElementById('nodes-at-risk');
            if (riskEl) {
                riskEl.textContent = nodesAtRisk;
                riskEl.style.color = nodesAtRisk > 0 ? '#ef4444' : '#10b981';
                riskEl.style.fontWeight = '700';
            }

            // Trend with detailed breakdown
            const trendEl = document.getElementById('cluster-trend');
            if (trendEl) {
                let trendText = '→ Stable';
                let trendColor = '#06b6d4';
                
                if (data.cluster_health_trend === 'improving') {
                    trendText = '↑ Improving';
                    trendColor = '#10b981';
                } else if (data.cluster_health_trend === 'degrading') {
                    trendText = '↓ Degrading';
                    trendColor = '#ef4444';
                } else if (data.cluster_health_trend === 'volatile') {
                    trendText = '↔ Volatile';
                    trendColor = '#f59e0b';
                }
                
                trendEl.textContent = trendText;
                trendEl.style.color = trendColor;
                trendEl.style.fontWeight = '600';
            }

            // Log comprehensive analytics with node breakdown
            const healthy = data.healthy_nodes || 0;
            const degraded = data.degraded_nodes || 0;
            const critical = data.critical_nodes || 0;
            const total = data.total_nodes || 0;
            
            console.log(`✓ Cluster Analytics Updated:`);
            console.log(`  • Cluster Health: ${clusterHealth}% | Avg Node: ${avgHealth}%`);
            console.log(`  • Node Composition: ${healthy}✓ ${degraded}⚠️ ${critical}🔒 (${total} total)`);
            console.log(`  • Risk Status: ${nodesAtRisk} at risk | Trend: ${data.cluster_health_trend}`);
        } catch (e) {
            console.error('Error rendering analytics:', e);
        }
    }

    renderEvents(events) {
        const eventList = document.getElementById('event-list');
        
        // Filter events
        let filteredEvents = events;
        if (this.eventFilter !== 'all') {
            filteredEvents = events.filter(e => e.type === this.eventFilter);
        }

        // Only show recent events
        filteredEvents = filteredEvents.slice(0, 50);

        // Build set of current event IDs
        const currentIds = new Set(
            Array.from(eventList.querySelectorAll('.event-item')).map(e => e.dataset.eventId)
        );

        const icons = { risk: '⚠️', action: '✓', info: 'ℹ️' };

        // Add new events or update existing
        filteredEvents.forEach((event, index) => {
            const existingEvent = eventList.querySelector(`[data-event-id="${event.id}"]`);
            
            if (!existingEvent) {
                // New event - create it
                const eventHTML = document.createElement('div');
                eventHTML.className = `event-item ${event.type}`;
                eventHTML.setAttribute('data-type', event.type);
                eventHTML.setAttribute('data-event-id', event.id);

                let detailsHTML = '';
                if (event.details && Object.keys(event.details).length > 0) {
                    detailsHTML = '<div class="event-details">';
                    Object.entries(event.details).forEach(([key, value]) => {
                        if (key !== 'factors') {
                            const displayKey = key.replace(/([A-Z])/g, ' $1').trim();
                            const displayValue = Array.isArray(value) ? value.join(', ') : value;
                            detailsHTML += `<div class="event-detail"><strong>${displayKey}:</strong> ${displayValue}</div>`;
                        }
                    });
                    detailsHTML += '</div>';
                }

                const timeString = this.formatTimeString(event.timestamp);

                eventHTML.innerHTML = `
                    <div class="event-icon">${icons[event.type] || 'ℹ️'}</div>
                    <div class="event-content">
                        <div class="event-title">${event.title}</div>
                        <div class="event-description">${event.description}</div>
                        ${detailsHTML}
                    </div>
                    <div class="event-time">${timeString}</div>
                `;

                eventList.insertBefore(eventHTML, eventList.firstChild);
            }
        });

        // Remove empty state if present
        const emptyState = eventList.querySelector('.empty-state');
        if (emptyState && eventList.querySelectorAll('.event-item').length > 0) {
            emptyState.remove();
        }

        // Clean up old events
        const items = eventList.querySelectorAll('.event-item');
        if (items.length > 50) {
            for (let i = 50; i < items.length; i++) {
                items[i].remove();
            }
        }
    }

    renderNodeMetrics(nodes) {
        const nodeGrid = document.getElementById('node-grid');
        console.log(`📦 Rendering ${nodes.length} nodes...`);
        
        if (!nodes || nodes.length === 0) {
            console.warn('⚠️ No nodes to render');
            return;
        }

        // Always update all nodes to ensure changes are visible
        const existingCards = nodeGrid.querySelectorAll('.node-card');
        console.log(`  Current cards: ${existingCards.length}, New nodes: ${nodes.length}`);
        
        // If different number of cards, rebuild
        if (existingCards.length !== nodes.length) {
            console.log('  → Rebuilding node grid (card count mismatch)');
            nodeGrid.innerHTML = '';
            nodes.forEach(node => {
                const nodeCard = document.createElement('div');
                nodeCard.className = 'node-card';
                this.updateNodeCard(nodeCard, node);
                nodeGrid.appendChild(nodeCard);
            });
        } else {
            // Same number of cards - update each one
            console.log('  → Updating existing cards');
            existingCards.forEach((card, i) => {
                if (nodes[i]) {
                    this.updateNodeCard(card, nodes[i]);
                    console.log(`  ✓ Updated card ${i}: ${nodes[i].node_name}`);
                }
            });
        }
    }

    updateNodeCard(nodeCard, node) {
        const cpu = node.cpu_usage || 0;
        const memory = node.memory_usage || 0;
        const temp = node.temperature || 50;
        const latency = node.network_latency || 0;
        const disk = node.disk_io || 0;
        const podCount = node.pods ? node.pods.length : 0;

        const isAtRisk = cpu > 80 || memory > 85 || temp > 75;
        const isTainted = node.taints && node.taints.length > 0;

        nodeCard.classList.toggle('at-risk', isAtRisk);

        const cpuClass = cpu > 85 ? 'critical' : (cpu > 70 ? 'warning' : '');
        const memoryClass = memory > 85 ? 'critical' : (memory > 75 ? 'warning' : '');
        const tempClass = temp > 75 ? 'critical' : (temp > 65 ? 'warning' : '');

        // Calculate status indicator and message
        let statusMsg = '✓ Healthy';
        let statusColor = '#10b981'; // green

        if (isAtRisk) {
            statusMsg = '⚠️ At Risk';
            statusColor = '#ef4444'; // red
        } else if (isTainted) {
            statusMsg = '🔒 Tainted';
            statusColor = '#f59e0b'; // amber
        } else if (podCount === 0) {
            statusMsg = '◯ No Pods';
            statusColor = '#64748b'; // gray
        }

        nodeCard.innerHTML = `
            <div class="node-name">
                <span class="node-status-indicator" style="background: ${statusColor};"></span>
                <span style="font-weight: 700; color: ${statusColor};">${node.node_name || 'Unknown'}</span>
                <span style="color: var(--text-secondary); font-size: 0.8rem; margin-left: 0.5rem;">${statusMsg}</span>
                <div class="taint-badges" style="display:inline-block; margin-left:0.5rem;"></div>
            </div>
            
            <div class="metric-row">
                <span class="metric-label">CPU Usage</span>
                <span class="metric-value" style="color: ${cpu > 85 ? '#ef4444' : (cpu > 70 ? '#f59e0b' : '#64748b')}">${cpu.toFixed(1)}%</span>
            </div>
            <div class="metric-bar">
                <div class="metric-fill ${cpuClass}" style="width: ${Math.min(100, cpu)}%"></div>
            </div>

            <div class="metric-row">
                <span class="metric-label">Memory Usage</span>
                <span class="metric-value" style="color: ${memory > 85 ? '#ef4444' : (memory > 75 ? '#f59e0b' : '#64748b')}">${memory.toFixed(1)}%</span>
            </div>
            <div class="metric-bar">
                <div class="metric-fill ${memoryClass}" style="width: ${Math.min(100, memory)}%"></div>
            </div>

            <div class="metric-row">
                <span class="metric-label">Temperature</span>
                <span class="metric-value" style="color: ${temp > 75 ? '#ef4444' : (temp > 65 ? '#f59e0b' : '#64748b')}">${temp.toFixed(1)}°C</span>
            </div>
            <div class="metric-bar">
                <div class="metric-fill ${tempClass}" style="width: ${Math.min(100, (temp / 85) * 100)}%"></div>
            </div>

            <div class="metric-row">
                <span class="metric-label">Network Latency</span>
                <span class="metric-value">${latency.toFixed(1)}ms</span>
            </div>

            <div class="metric-row">
                <span class="metric-label">Disk I/O</span>
                <span class="metric-value">${disk.toFixed(1)}%</span>
            </div>
            <div class="metric-bar">
                <div class="metric-fill" style="width: ${Math.min(100, disk)}%"></div>
            </div>

            <div class="metric-row" style="margin-top: 0.5rem; font-size: 0.85rem; padding-top: 0.75rem; border-top: 1px solid rgba(6, 182, 212, 0.1);">
                <span class="metric-label">Running Pods</span>
                <span class="metric-value">${podCount}</span>
            </div>

            <div class="node-actions">
                <button class="action-btn taint-btn" data-node-id="${node.node_id}" title="Mark node to prevent new pod scheduling">Taint</button>
                <button class="action-btn drain-btn" data-node-id="${node.node_id}" title="Gracefully evict all pods">Drain</button>
                <button class="action-btn remove-taint-btn" data-node-id="${node.node_id}" title="Allow new pods to be scheduled">Remove</button>
            </div>
        `;

        // Attach action listeners with loading state
        const taintBtn = nodeCard.querySelector('.taint-btn');
        const drainBtn = nodeCard.querySelector('.drain-btn');
        const removeTaintBtn = nodeCard.querySelector('.remove-taint-btn');

        const disableButtons = () => {
            [taintBtn, drainBtn, removeTaintBtn].forEach(btn => btn.disabled = true);
        };

        const enableButtons = () => {
            this.updateButtonStates(nodeCard, node, taintBtn, drainBtn, removeTaintBtn);
        };

        if (taintBtn) {
            taintBtn.addEventListener('click', async (e) => {
                const id = e.target.getAttribute('data-node-id');
                disableButtons();
                e.target.classList.add('loading');
                await this.applyTaint(id);
                e.target.classList.remove('loading');
                enableButtons();
            });
        }

        if (drainBtn) {
            drainBtn.addEventListener('click', async (e) => {
                const id = e.target.getAttribute('data-node-id');
                disableButtons();
                e.target.classList.add('loading');
                await this.drainNode(id);
                e.target.classList.remove('loading');
                enableButtons();
            });
        }

        if (removeTaintBtn) {
            removeTaintBtn.addEventListener('click', async (e) => {
                const id = e.target.getAttribute('data-node-id');
                disableButtons();
                e.target.classList.add('loading');
                await this.removeTaint(id);
                e.target.classList.remove('loading');
                enableButtons();
            });
        }

        // Update status indicator and taint badges
        const badgeContainer = nodeCard.querySelector('.taint-badges');
        badgeContainer.innerHTML = '';

        // Show taints if present
        if (isTainted) {
            const taintCount = node.taints.length;
            const pill = document.createElement('span');
            pill.className = 'taint-badge';
            pill.textContent = `${taintCount} Taint${taintCount > 1 ? 's' : ''}`;
            badgeContainer.appendChild(pill);
        }

        // Set up button states
        this.updateButtonStates(nodeCard, node, taintBtn, drainBtn, removeTaintBtn);
    }

    updateButtonStates(nodeCard, node, taintBtn, drainBtn, removeTaintBtn) {
        const isTainted = node.taints && node.taints.length > 0;

        if (taintBtn) {
            taintBtn.disabled = isTainted;
            taintBtn.textContent = isTainted ? '✓ Tainted' : 'Taint';
        }
        if (removeTaintBtn) {
            removeTaintBtn.disabled = !isTainted;
            removeTaintBtn.textContent = isTainted ? 'Remove' : 'None';
        }
        if (drainBtn) {
            drainBtn.disabled = false;
            drainBtn.textContent = 'Drain';
        }
    }

    async applyTaint(nodeId) {
        console.log('Tainting node:', nodeId);
        const btn = document.querySelector(`.taint-btn[data-node-id="${nodeId}"]`);
        if (btn) { btn.disabled = true; btn.textContent = 'Tainting...'; }
        try {
            const resp = await fetch(`${API_BASE}/nodes/${encodeURIComponent(nodeId)}/taint`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({taint: 'degradation=true:NoSchedule'})
            });
            if (!resp.ok) throw new Error('Taint failed');
            console.log('Taint response OK');
            // Force immediate update
            await this.fetchNodes();
            await this.fetchEvents();
            await this.fetchStats();
        } catch (e) {
            console.error('Taint error', e);
            alert(`Taint failed: ${e.message}`);
        } finally {
            // Force re-fetch to get latest button state
            await this.fetchNodes();
        }
    }

    async removeTaint(nodeId) {
        console.log('Removing taint from node:', nodeId);
        const btn = document.querySelector(`.remove-taint-btn[data-node-id="${nodeId}"]`);
        if (btn) { btn.disabled = true; btn.textContent = 'Removing...'; }
        try {
            const resp = await fetch(`${API_BASE}/nodes/${encodeURIComponent(nodeId)}/remove-taint`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({key: 'degradation'})
            });
            if (!resp.ok) throw new Error('Remove taint failed');
            console.log('Remove taint response OK');
            // Force immediate update
            await this.fetchNodes();
            await this.fetchEvents();
            await this.fetchStats();
        } catch (e) {
            console.error('Remove taint error', e);
            alert(`Remove taint failed: ${e.message}`);
        } finally {
            // Force re-fetch to get latest button state
            await this.fetchNodes();
        }
    }

    async drainNode(nodeId) {
        console.log('Draining node:', nodeId);
        const btn = document.querySelector(`.drain-btn[data-node-id="${nodeId}"]`);
        if (btn) { btn.disabled = true; btn.textContent = 'Draining...'; }
        try {
            const resp = await fetch(`${API_BASE}/nodes/${encodeURIComponent(nodeId)}/drain`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({grace_period: 30})
            });
            if (!resp.ok) throw new Error('Drain failed');
            console.log('Drain response OK');
            // Force immediate update
            await this.fetchNodes();
            await this.fetchEvents();
            await this.fetchStats();
        } catch (e) {
            console.error('Drain error', e);
            alert(`Drain failed: ${e.message}`);
        } finally {
            // Force re-fetch to get latest button state
            await this.fetchNodes();
        }
    }

    _setupEventStream() {
        if (!window.EventSource) {
            console.log('EventSource not supported, relying on polling only');
            return;
        }
        try {
            const es = new EventSource(`${API_BASE}/events/stream`);
            es.onmessage = (msg) => {
                try {
                    const data = JSON.parse(msg.data);
                    console.log('SSE event received:', data.type);
                    // Immediately refresh on any event
                    this.fetchNodes();
                    this.fetchEvents();
                    this.fetchStats();
                } catch (e) {
                    console.warn('Malformed SSE event', e);
                }
            };
            es.onerror = (err) => {
                console.warn('SSE connection error, will use polling only', err);
                es.close();
            };
            console.log('✓ SSE stream established');
        } catch (e) {
            console.log('SSE setup skipped, using polling only', e);
        }
    }

    formatTimeString(isoString) {
        try {
            const date = new Date(isoString);
            const now = new Date();
            const diffMs = now - date;
            const diffSecs = Math.floor(diffMs / 1000);
            
            if (diffSecs < 5) return 'Just now';
            if (diffSecs < 60) return `${diffSecs}s ago`;
            
            const diffMins = Math.floor(diffSecs / 60);
            if (diffMins < 60) return `${diffMins}m ago`;
            
            return date.toLocaleTimeString();
        } catch (e) {
            return 'Recent';
        }
    }

    updateTimestamp() {
        const now = new Date();
        const timeAgo = this.getTimeAgo(now);
        document.getElementById('last-update').textContent = timeAgo;
    }

    getTimeAgo(date) {
        const now = new Date();
        const seconds = Math.floor((now - date) / 1000);
        
        if (seconds < 5) return 'Just now';
        if (seconds < 60) return `${seconds}s ago`;
        
        const minutes = Math.floor(seconds / 60);
        if (minutes < 60) return `${minutes}m ago`;
        
        return 'Recently';
    }
}

// Event filtering
class EventFilter {
    constructor(monitor) {
        this.monitor = monitor;
        this.setupEventListeners();
    }

    setupEventListeners() {
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.monitor.eventFilter = e.target.getAttribute('data-filter');
                // Re-fetch events to apply filter
                this.monitor.fetchEvents();
            });
        });
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    const monitor = new InfrastructureMonitor();
    const filter = new EventFilter(monitor);
    
    // Initialize and start monitoring
    monitor.initialize();
});
