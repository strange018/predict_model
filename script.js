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

        console.log(`✓ Polling started: stats=${statsPollId}, nodes=${nodesPollId}, events=${eventsPollId}`);

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

    async fetchStats() {
        try {
            const response = await fetch(`${API_BASE}/stats`);
            if (!response.ok) throw new Error('Failed to fetch stats');
            
            const data = await response.json();
            
            document.getElementById('nodes-monitored').textContent = data.nodes_monitored || 0;
            document.getElementById('risks-detected').textContent = data.risks_detected || 0;
            document.getElementById('workloads-moved').textContent = data.workloads_moved || 0;
            
            this.updateTimestamp();
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

        nodeCard.classList.toggle('at-risk', isAtRisk);

        const cpuClass = cpu > 70 ? 'warning' : (cpu > 85 ? 'critical' : '');
        const memoryClass = memory > 75 ? 'warning' : (memory > 85 ? 'critical' : '');

        nodeCard.innerHTML = `
            <div class="node-name">
                <span class="node-status-indicator"></span>
                ${node.node_name || 'Unknown'}
                <div class="taint-badges" style="display:inline-block; margin-left:0.5rem;"></div>
            </div>
            
            <div class="metric-row">
                <span class="metric-label">CPU</span>
                <span class="metric-value">${cpu.toFixed(1)}%</span>
            </div>
            <div class="metric-bar">
                <div class="metric-fill ${cpuClass}" style="width: ${Math.min(100, cpu)}%"></div>
            </div>

            <div class="metric-row">
                <span class="metric-label">Memory</span>
                <span class="metric-value">${memory.toFixed(1)}%</span>
            </div>
            <div class="metric-bar">
                <div class="metric-fill ${memoryClass}" style="width: ${Math.min(100, memory)}%"></div>
            </div>

            <div class="metric-row">
                <span class="metric-label">Temperature</span>
                <span class="metric-value">${temp.toFixed(1)}°C</span>
            </div>
            <div class="metric-bar">
                <div class="metric-fill ${temp > 75 ? 'critical' : ''}" style="width: ${Math.min(100, (temp / 90) * 100)}%"></div>
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

            <div class="metric-row" style="margin-top: 0.5rem; font-size: 0.85rem;">
                <span class="metric-label">Pods</span>
                <span class="metric-value">${podCount}</span>
            </div>

            ${isAtRisk ? '<div class="metric-label" style="color: var(--error-color); margin-top: 0.5rem;">⚠️ At Risk</div>' : ''}
            <div class="node-actions" style="margin-top:0.75rem; display:flex; gap:0.5rem;">
                <button class="action-btn taint-btn" data-node-id="${node.node_id}">Taint</button>
                <button class="action-btn drain-btn" data-node-id="${node.node_id}">Drain</button>
                <button class="action-btn remove-taint-btn" data-node-id="${node.node_id}">Remove Taint</button>
            </div>
        `;

        // Attach action listeners
        const taintBtn = nodeCard.querySelector('.taint-btn');
        const drainBtn = nodeCard.querySelector('.drain-btn');
        const removeTaintBtn = nodeCard.querySelector('.remove-taint-btn');

        if (taintBtn) {
            taintBtn.addEventListener('click', async (e) => {
                const id = e.target.getAttribute('data-node-id');
                await this.applyTaint(id);
            });
        }

        if (drainBtn) {
            drainBtn.addEventListener('click', async (e) => {
                const id = e.target.getAttribute('data-node-id');
                await this.drainNode(id);
            });
        }

        if (removeTaintBtn) {
            removeTaintBtn.addEventListener('click', async (e) => {
                const id = e.target.getAttribute('data-node-id');
                await this.removeTaint(id);
            });
        }

        // Update status indicator and taint badges
        const statusDot = nodeCard.querySelector('.node-status-indicator');
        const badgeContainer = nodeCard.querySelector('.taint-badges');
        badgeContainer.innerHTML = '';

        // Show taints if present
        if (node.taints && node.taints.length) {
            node.taints.forEach(t => {
                const b = document.createElement('span');
                b.className = 'taint-badge';
                b.textContent = `${t.key}=${t.value || ''}:${t.effect}`;
                badgeContainer.appendChild(b);
            });
        }

        // Set status color
        if (isAtRisk) {
            statusDot.style.background = 'var(--error-color)';
            statusDot.title = 'At Risk';
        } else if (node.taints && node.taints.length) {
            statusDot.style.background = 'orange';
            statusDot.title = 'Tainted (scheduling prevented)';
        } else if (podCount === 0) {
            statusDot.style.background = 'gray';
            statusDot.title = 'No pods';
        } else {
            statusDot.style.background = 'green';
            statusDot.title = 'Healthy';
        }

        // Disable/enable buttons based on state
        if (taintBtn) {
            taintBtn.disabled = !!(node.taints && node.taints.length);
            taintBtn.textContent = 'Taint';
        }
        if (removeTaintBtn) {
            removeTaintBtn.disabled = !(node.taints && node.taints.length);
            removeTaintBtn.textContent = 'Remove Taint';
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
