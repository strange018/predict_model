// Backend API Configuration
const API_BASE = '/api';

// ─── Chart Manager ──────────────────────────────────────────────────────────
class ChartManager {
    constructor() {
        this.charts = {};
        this.maxPoints = 20; // rolling window
        this.healthHistory = [];  // [{time, value}]
        this.riskHistory = [];  // [{time, value}]
        this.eventCounts = { risk: 0, action: 0, info: 0 };
        this.currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        this._initCharts();
    }

    updateTheme(theme) {
        this.currentTheme = theme;
        const isDark = theme === 'dark';
        const gridColor = isDark ? 'rgba(148,163,184,0.1)' : 'rgba(148,163,184,0.12)';
        const tickColor = isDark ? '#94a3b8' : '#64748b';

        Object.values(this.charts).forEach(chart => {
            if (chart.options.scales.x) {
                chart.options.scales.x.ticks.color = tickColor;
            }
            if (chart.options.scales.y) {
                chart.options.scales.y.grid.color = gridColor;
                chart.options.scales.y.ticks.color = tickColor;
            }
            chart.update();
        });

        // Special handling for distribution chart (doughnut) - update scales if they exist
        const distChart = this.charts.distribution;
        if (distChart) {
            distChart.update();
        }

    }

    _initCharts() {
        const gridColor = 'rgba(148,163,184,0.12)';
        const tickColor = '#94a3b8';
        const fontFamily = "'Inter','Segoe UI',sans-serif";

        const baseScales = {
            x: {
                grid: { display: false, drawBorder: false }, // Minimal grid
                ticks: { maxRotation: 0, autoSkip: true, maxTicksLimit: 6 }
            },
            y: {
                grid: { color: gridColor, drawBorder: false, borderDash: [4, 4] },
                beginAtZero: true,
                max: 100,
                ticks: { stepSize: 25, callback: val => `${val}%` }
            }
        };

        // 1. Unified Health Timeline
        const hCtx = document.getElementById('health-chart');
        if (hCtx) {
            this.charts.health = new Chart(hCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: 'Historical Health Index',
                            data: [],
                            borderColor: '#3b82f6', // Primary Blue
                            backgroundColor: 'rgba(59, 130, 246, 0.1)',
                            borderWidth: 2,
                            tension: 0.4,
                            fill: true,
                            pointRadius: 0,      // Hide points unless hovered
                            pointHoverRadius: 6
                        },
                        {
                            label: 'ML Forecast',
                            data: [],
                            borderColor: '#8b5cf6', // Indigo Warning
                            borderWidth: 2,
                            borderDash: [5, 5], // Dashed line for forecast
                            tension: 0.4,
                            fill: false,
                            pointRadius: 0,
                            hidden: false // Controlled by toggles later
                        }
                    ]
                },
                options: {
                    animation: { duration: 1000, easing: 'easeOutQuart' }, // Smooth animation
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: { mode: 'index', intersect: false },
                    plugins: {
                        legend: { position: 'top', align: 'end', labels: { usePointStyle: true, boxWidth: 8, font: { family: fontFamily } } },
                        tooltip: { backgroundColor: 'rgba(15, 23, 42, 0.9)', padding: 12, cornerRadius: 4 }
                    },
                    scales: baseScales
                }
            });
        }

        // 2. Focused Highest Risk Utilization (Bar)
        const rCtx = document.getElementById('resource-chart');
        if (rCtx) {
            this.charts.resource = new Chart(rCtx, {
                type: 'bar',
                data: {
                    labels: [], // Top nodes
                    datasets: [
                        {
                            label: 'CPU',
                            data: [],
                            backgroundColor: 'rgba(59, 130, 246, 0.8)', // Solid blue
                            borderRadius: 4,
                            barPercentage: 0.7
                        },
                        {
                            label: 'Memory',
                            data: [],
                            backgroundColor: 'rgba(16, 185, 129, 0.8)', // Solid green
                            borderRadius: 4,
                            barPercentage: 0.7
                        }
                    ]
                },
                options: {
                    animation: { duration: 800 },
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'top', labels: { usePointStyle: true, boxWidth: 8, font: { family: fontFamily } } }
                    },
                    scales: baseScales
                }
            });
            // 3. Node Health Distribution (Doughnut)
            const dCtx = document.getElementById('distribution-chart');
            if (dCtx) {
                this.charts.distribution = new Chart(dCtx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Healthy', 'Degraded', 'Critical'],
                        datasets: [{
                            data: [0, 0, 0],
                            backgroundColor: [
                                'rgba(16, 185, 129, 0.8)', // Green
                                'rgba(245, 158, 11, 0.8)', // Orange
                                'rgba(239, 68, 68, 0.8)'   // Red
                            ],
                            borderWidth: 0,
                            hoverOffset: 4
                        }]
                    },
                    options: {
                        cutout: '70%',
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                display: true,
                                position: 'bottom',
                                labels: {
                                    padding: 10,
                                    usePointStyle: true,
                                    boxWidth: 8,
                                    font: { family: fontFamily, size: 10 }
                                }
                            }
                        }
                    }
                });
            }
        }

    }

    /** Called every analytics poll with cluster analytics data */
    updateHealthChart(clusterHealthScore) {
        const chart = this.charts.health;
        if (!chart) return;
        const label = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

        // Add actual point
        chart.data.labels.push(label);
        chart.data.datasets[0].data.push(Math.round(clusterHealthScore || 0));

        // Add fake ML forecast connecting point (slightly drifting)
        let forecastDrift = (clusterHealthScore || 100) - (Math.random() * 5);
        chart.data.datasets[1].data.push(Math.round(Math.max(0, forecastDrift)));

        if (chart.data.labels.length > this.maxPoints) {
            chart.data.labels.shift();
            chart.data.datasets[0].data.shift();
            chart.data.datasets[1].data.shift();
        }
        chart.update('none'); // Update without full animation for smooth polling
    }

    /** Called every nodes poll to update the focused resource chart */
    updateResourceChart(nodes) {
        const chart = this.charts.resource;
        if (!chart || !nodes || nodes.length === 0) return;

        // Sort nodes by risk score to show the most stressed nodes first
        const sortedNodes = [...nodes].sort((a, b) => (b.risk_score || 0) - (a.risk_score || 0)).slice(0, 5); // Top 5

        chart.data.labels = sortedNodes.map(n => n.node_name || n.node_id);
        chart.data.datasets[0].data = sortedNodes.map(n => +(n.cpu_usage || 0).toFixed(1));
        chart.data.datasets[1].data = sortedNodes.map(n => +(n.memory_usage || 0).toFixed(1));

        // Dynamically color bars based on severity threshold
        chart.data.datasets[0].backgroundColor = sortedNodes.map(n =>
            (n.cpu_usage || 0) > 85 ? 'rgba(239, 68, 68, 0.85)' : // Red
                (n.cpu_usage || 0) > 70 ? 'rgba(245, 158, 11, 0.85)' : // Orange
                    'rgba(59, 130, 246, 0.8)' // Blue
        );

        chart.data.datasets[1].backgroundColor = sortedNodes.map(n =>
            (n.memory_usage || 0) > 85 ? 'rgba(239, 68, 68, 0.85)' :
                (n.memory_usage || 0) > 70 ? 'rgba(245, 158, 11, 0.85)' :
                    'rgba(16, 185, 129, 0.8)' // Green
        );

        chart.update('none'); // Update without full animation
    }

    /** Called every analytics poll to update the distribution doughnut */
    updateDistributionChart(data) {
        const chart = this.charts.distribution;
        if (!chart) return;

        chart.data.datasets[0].data = [
            data.healthy_nodes || 0,
            data.degraded_nodes || 0,
            data.critical_nodes || 0
        ];

        chart.update('active'); // Use active for subtle expansion effect
    }
}


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
        this.chartManager = new ChartManager();
        this.currentTheme = 'light';

        // Register progressive disclosure Chart overlays
        const toggleForecastBtn = document.getElementById('toggle-forecast');
        if (toggleForecastBtn) {
            toggleForecastBtn.addEventListener('click', () => {
                if (!this.chartManager.charts.health) return;
                const dataset = this.chartManager.charts.health.data.datasets[1]; // ML Forecast dataset
                dataset.hidden = !dataset.hidden;
                this.chartManager.charts.health.update('none');
                toggleForecastBtn.style.opacity = dataset.hidden ? '0.5' : '1';
            });
            toggleForecastBtn.style.opacity = '0.5'; // Default off
        }

        const toggleAnomaliesBtn = document.getElementById('toggle-anomalies');
        if (toggleAnomaliesBtn) {
            toggleAnomaliesBtn.addEventListener('click', () => {
                if (!this.chartManager.charts.health) return;
                const dataset = this.chartManager.charts.health.data.datasets[0];

                // Toggle showing points vs bare line
                dataset.pointRadius = dataset.pointRadius === 0 ? 4 : 0;

                // Color points based on the value to show anomalies
                if (dataset.pointRadius > 0) {
                    dataset.pointBackgroundColor = dataset.data.map(val =>
                        val < 60 ? 'rgba(239, 68, 68, 1)' :   // Red (Risk)
                            val < 80 ? 'rgba(245, 158, 11, 1)' :  // Orange (Warning)
                                'rgba(59, 130, 246, 0.2)'             // Blue (Normal)
                    );
                }
                this.chartManager.charts.health.update('none');
                toggleAnomaliesBtn.style.opacity = dataset.pointRadius === 0 ? '0.5' : '1';
            });
            toggleAnomaliesBtn.style.opacity = '0.5'; // Default off
        }

        // Add delegated listener for recommendations
        const recList = document.getElementById('recommendations-list');
        if (recList) {
            recList.addEventListener('click', async (e) => {
                if (e.target.classList.contains('action-btn')) {
                    const card = e.target.closest('.node-card');
                    if (!card) return;

                    const type = card.querySelector('.node-name span:not([style*="font-size"])').textContent;
                    const target = card.querySelector('.metric-row .metric-value').textContent;

                    await this.applyRecommendation(type, target, e.target);
                }
            });
        }
    }

    async _fetchWithErrorHandling(url, options = {}) {
        try {
            const response = await fetch(url, options);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (e) {
            console.error(`Fetch error for ${url}:`, e);
            return null;
        }
    }

    async initialize() {
        console.log('🚀 Initializing Monitoring System...');
        this.initTheme();
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
        await this.fetchRecommendations();

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
        const recommendationsPollId = setInterval(() => {
            console.log('💡 Polling recommendations...');
            this.fetchRecommendations();
        }, 5000);

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
            console.log('🔄 Fetching cluster status...');
            const data = await this._fetchWithErrorHandling(`${API_BASE}/cluster/status`);
            if (!data) return;

            // Update stats with real data from backend
            const nodesVal = data.nodes_monitored || 0;
            const nodesElem = document.getElementById('nodes-monitored');
            if (nodesElem) {
                const oldVal = parseInt(nodesElem.textContent) || 0;
                nodesElem.textContent = nodesVal;
                if (oldVal !== nodesVal) {
                    this.highlightStatChange('nodes-monitored', oldVal, nodesVal);
                }
            }

            // Average Health as percentage
            const avgHealth = Math.round(data.average_health || 100);
            const healthEl = document.getElementById('avg-health-display');
            if (healthEl) {
                const oldVal = parseInt(healthEl.textContent) || 100;
                healthEl.textContent = avgHealth + '%';

                // Color code the health
                if (avgHealth >= 80) {
                    healthEl.style.color = '#38A169'; // success
                } else if (avgHealth >= 60) {
                    healthEl.style.color = '#DD6B20'; // warning
                } else {
                    healthEl.style.color = '#E53E3E'; // risk
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
                healthyEl.style.color = '#38A169';
            }

            // Degraded Nodes
            const degradedNodes = data.nodes_degraded || 0;
            const degradedEl = document.getElementById('nodes-degraded');
            if (degradedEl) {
                degradedEl.textContent = degradedNodes;
                degradedEl.style.color = degradedNodes > 0 ? '#E53E3E' : '#4A5568';
            }

            // GreenOps Eco-Score
            const avgEcoScore = Math.round(data.average_eco_score || 100);
            const ecoScoreEl = document.getElementById('avg-eco-score');
            if (ecoScoreEl) {
                const oldEcoVal = parseInt(ecoScoreEl.textContent) || 100;
                ecoScoreEl.textContent = avgEcoScore + '%';

                if (avgEcoScore >= 80) ecoScoreEl.style.color = '#38A169'; // success
                else if (avgEcoScore >= 60) ecoScoreEl.style.color = '#DD6B20'; // warning
                else ecoScoreEl.style.color = '#E53E3E'; // risk

                if (oldEcoVal !== avgEcoScore) {
                    ecoScoreEl.classList.add('stat-updated');
                    setTimeout(() => ecoScoreEl.classList.remove('stat-updated'), 600);
                }
            }

            // Capacity Warnings (Forecast)
            const warningsVal = data.nodes_with_warnings || 0;
            const warningsEl = document.getElementById('capacity-warnings');
            if (warningsEl) {
                const oldWarnings = parseInt(warningsEl.textContent) || 0;
                warningsEl.textContent = warningsVal;
                warningsEl.style.color = warningsVal > 0 ? '#E53E3E' : '#4A5568';

                if (oldWarnings !== warningsVal) {
                    this.highlightStatChange('capacity-warnings', oldWarnings, warningsVal);
                }
            }

            // Risks Detected
            const risksVal = data.risks_detected || 0;
            const risksEl = document.getElementById('risks-detected');
            if (risksEl) {
                const oldRisks = parseInt(risksEl.textContent) || 0;
                risksEl.textContent = risksVal;
                risksEl.style.color = risksVal > 0 ? '#E53E3E' : '#4A5568';

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
                workloadsEl.style.color = '#38A169';

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
            const nodes = await this._fetchWithErrorHandling(`${API_BASE}/nodes`);
            if (!nodes) return;
            console.log(`✓ Received ${nodes.length} nodes:`, nodes.map(n => `${n.node_name}(taints:${n.taints?.length || 0})`).join(', '));
            this.renderNodeMetrics(nodes);
            // Update resource usage chart in real-time
            this.chartManager.updateResourceChart(nodes);
        } catch (e) {
            console.error('❌ Error fetching nodes:', e);
        }
    }

    async fetchEvents() {
        try {
            const events = await this._fetchWithErrorHandling(`${API_BASE}/events`);
            if (!events) return;
            this.renderEvents(events);
        } catch (e) {
            console.error('Error fetching events:', e);
        }
    }

    async fetchAnalytics() {
        try {
            console.log('📊 Fetching cluster health analytics...');
            const data = await this._fetchWithErrorHandling(`${API_BASE}/cluster/health`);
            if (!data) return;

            this.renderAnalytics(data);

            // Fetch AI Insights separately (modular)
            const insightData = await this._fetchWithErrorHandling(`${API_BASE}/analytics/ai-insights`);
            if (insightData) {
                this.displayAiInsight(insightData);
            }
        } catch (e) {
            console.error('Error fetching analytics:', e);
        }
    }

    async fetchRecommendations() {
        try {
            console.log('💡 Fetching recommendations...');
            const data = await this._fetchWithErrorHandling(`${API_BASE}/workload/recommendations`);
            if (!data || !data.recommendations) return;

            this.renderRecommendations(data.recommendations);
        } catch (e) {
            console.error('Error fetching recommendations:', e);
        }
    }

    renderRecommendations(recommendations) {
        const listEl = document.getElementById('recommendations-list');
        if (!listEl) return;

        if (recommendations.length === 0) {
            listEl.innerHTML = '<div class="empty-state"><p>All infrastructure is optimally sized! 🌱</p></div>';
            return;
        }

        // Keep existing scroll position
        const scr = listEl.scrollTop;
        listEl.innerHTML = '';

        recommendations.forEach(rec => {
            const card = document.createElement('div');
            card.className = 'node-card recommendation-card';

            let icon = '💡';
            let colorClass = 'primary';
            if (rec.type === 'Scale Down') { icon = '📉'; colorClass = 'accent'; }
            else if (rec.type === 'Scale Up') { icon = '📈'; colorClass = 'warning'; }
            else if (rec.type === 'Right-Size Pod') { icon = '⚖️'; colorClass = 'success'; }

            card.innerHTML = `
                <div class="node-name">
                    <span class="rec-icon">${icon}</span>
                    <span class="rec-type color-${colorClass}">${rec.type}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Target:</span>
                    <span class="metric-value">${rec.target}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label reason-text">${rec.reason}</span>
                </div>
                <div class="metric-row impact-row">
                    <span class="metric-label">Est. Impact:</span>
                    <span class="metric-value savings-value">${rec.savings_estimate}</span>
                </div>
                <div class="rec-actions">
                    <button class="action-btn apply-rec-btn">Apply Recommendation</button>
                </div>
            `;
            listEl.appendChild(card);
        });
        listEl.scrollTop = scr;
    }

    async applyRecommendation(type, target, button) {
        console.log(`🚀 Applying recommendation: ${type} for ${target}`);

        if (button) {
            button.disabled = true;
            button.textContent = 'Applying...';
            button.classList.add('loading');
        }

        try {
            const data = await this._fetchWithErrorHandling(`${API_BASE}/recommendations/apply`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type, target })
            });

            if (data && data.success) {
                console.log('✓ Recommendation applied successfully');
                if (button) {
                    button.textContent = '✓ Applied';
                    button.style.background = 'var(--success-color)';
                }

                // Refresh data to show the new 'action' event and updated stats
                setTimeout(() => {
                    this.fetchEvents();
                    this.fetchStats();
                    this.fetchRecommendations(); // Refresh the list
                }, 1000);
            } else {
                throw new Error(data?.error || 'Failed to apply recommendation');
            }
        } catch (e) {
            console.error('❌ Error applying recommendation:', e);
            if (button) {
                button.disabled = false;
                button.textContent = 'Retry Apply';
                button.style.background = 'var(--risk-color)';
            }
            alert(`Failed to apply recommendation: ${e.message}`);
        }
    }

    renderAnalytics(data) {
        try {
            // Update real-time charts
            this.chartManager.updateHealthChart(data.cluster_health_score);
            this.chartManager.updateDistributionChart(data);


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

            // The generateAiInsight is now handled via backend calls to /api/analytics/ai-insights
            // This method remains for compatibility or can be removed if strictly following the new flow.
            // this.generateAiInsight(clusterHealth, nodesAtRisk, data.cluster_health_trend);

        } catch (e) {
            console.error('Error rendering analytics:', e);
        }
    }

    displayAiInsight(data) {
        const insightEl = document.getElementById('ai-insight-text');
        if (!insightEl) return;

        insightEl.innerHTML = data.text;
        insightEl.style.color = data.color || 'var(--text-secondary)';
    }

    // Deprecated: Migrated to backend /api/analytics/ai-insights
    generateAiInsight(clusterHealth, nodesAtRisk, trend) {
        // No longer used, logic moved to Python
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
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ taint: 'degradation=true:NoSchedule' })
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
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ key: 'degradation' })
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
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ grace_period: 30, slo_aware: true })
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

    // ─── Theme Management ──────────────────────────────────────────────────
    initTheme() {
        const savedTheme = localStorage.getItem('theme');
        const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

        const theme = savedTheme || (systemPrefersDark ? 'dark' : 'light');
        this._applyTheme(theme);
    }

    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this._applyTheme(newTheme);
        localStorage.setItem('theme', newTheme);
    }

    _applyTheme(theme) {
        this.currentTheme = theme;
        document.documentElement.setAttribute('data-theme', theme);

        // Update toggle icon
        const icon = document.querySelector('.theme-icon');
        if (icon) {
            icon.textContent = theme === 'dark' ? '☀️' : '🌙';
        }

        // Update charts
        if (this.chartManager) {
            this.chartManager.updateTheme(theme);
        }
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

    // Theme toggle setup
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => monitor.toggleTheme());
    }
});
