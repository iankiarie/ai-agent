"""
Enhanced Admin Dashboard with Professional Design
"""

from performance_monitor import performance_monitor, optimization_analyzer

def create_enhanced_dashboard_html():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ketha AI - Command Center</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', sans-serif;
                background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #1e1b4b 100%);
                color: #e2e8f0;
                min-height: 100vh;
                position: relative;
            }
            
            body::before {
                content: '';
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: radial-gradient(circle at 20% 50%, rgba(139, 92, 246, 0.1) 0%, transparent 50%),
                           radial-gradient(circle at 80% 20%, rgba(99, 102, 241, 0.1) 0%, transparent 50%);
                pointer-events: none;
                z-index: -1;
            }
            
            .login-container {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.9);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 1000;
            }
            
            .login-form {
                background: rgba(30, 27, 75, 0.9);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(139, 92, 246, 0.3);
                border-radius: 16px;
                padding: 3rem;
                text-align: center;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            }
            
            .login-form h2 {
                color: #a78bfa;
                margin-bottom: 2rem;
                font-size: 1.5rem;
                font-weight: 600;
            }
            
            .login-form input {
                width: 300px;
                padding: 1rem;
                border: 1px solid rgba(139, 92, 246, 0.3);
                border-radius: 8px;
                background: rgba(0, 0, 0, 0.3);
                color: #e2e8f0;
                margin-bottom: 1rem;
                font-size: 1rem;
            }
            
            .login-form input:focus {
                outline: none;
                border-color: #8b5cf6;
                box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
            }
            
            .login-form button {
                background: linear-gradient(135deg, #8b5cf6, #6366f1);
                color: white;
                border: none;
                padding: 1rem 2rem;
                border-radius: 8px;
                cursor: pointer;
                font-size: 1rem;
                font-weight: 600;
                transition: transform 0.2s;
            }
            
            .login-form button:hover {
                transform: translateY(-2px);
            }
            
            .error-message {
                color: #f87171;
                margin-top: 1rem;
                display: none;
            }
            
            .dashboard-content {
                display: none;
            }
            
            .header {
                background: rgba(30, 27, 75, 0.8);
                backdrop-filter: blur(20px);
                border-bottom: 1px solid rgba(139, 92, 246, 0.2);
                padding: 1.5rem 2rem;
                position: sticky;
                top: 0;
                z-index: 100;
            }
            
            .header-content {
                display: flex;
                justify-content: space-between;
                align-items: center;
                max-width: 1400px;
                margin: 0 auto;
            }
            
            .header h1 {
                font-size: 1.8rem;
                font-weight: 700;
                color: #a78bfa;
                display: flex;
                align-items: center;
                gap: 0.75rem;
            }
            
            .status-dot {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #10b981;
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            
            .header-controls {
                display: flex;
                gap: 1rem;
                align-items: center;
            }
            
            .btn {
                background: rgba(139, 92, 246, 0.1);
                border: 1px solid rgba(139, 92, 246, 0.3);
                color: #a78bfa;
                padding: 0.5rem 1rem;
                border-radius: 8px;
                cursor: pointer;
                font-size: 0.875rem;
                font-weight: 500;
                transition: all 0.2s;
                text-decoration: none;
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
            }
            
            .btn:hover {
                background: rgba(139, 92, 246, 0.2);
                border-color: #8b5cf6;
            }
            
            .logout-btn {
                background: rgba(239, 68, 68, 0.1);
                border-color: rgba(239, 68, 68, 0.3);
                color: #fca5a5;
            }
            
            .logout-btn:hover {
                background: rgba(239, 68, 68, 0.2);
                border-color: #ef4444;
            }
            
            .container {
                max-width: 1400px;
                margin: 0 auto;
                padding: 2rem;
            }
            
            .metrics-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
                gap: 1.5rem;
                margin-bottom: 2rem;
            }
            
            .metric-card {
                background: rgba(30, 27, 75, 0.6);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(139, 92, 246, 0.2);
                border-radius: 12px;
                padding: 1.5rem;
                transition: all 0.3s ease;
            }
            
            .metric-card:hover {
                transform: translateY(-4px);
                border-color: rgba(139, 92, 246, 0.4);
                box-shadow: 0 10px 30px rgba(139, 92, 246, 0.1);
            }
            
            .metric-value {
                font-size: 2rem;
                font-weight: 700;
                color: #f8fafc;
                margin-bottom: 0.5rem;
            }
            
            .metric-label {
                font-size: 0.875rem;
                color: #94a3b8;
                text-transform: uppercase;
                font-weight: 500;
                letter-spacing: 0.5px;
            }
            
            .metric-change {
                display: flex;
                align-items: center;
                gap: 0.25rem;
                margin-top: 0.5rem;
                font-size: 0.875rem;
            }
            
            .change-positive { color: #10b981; }
            .change-negative { color: #ef4444; }
            .change-neutral { color: #94a3b8; }
            
            .tabs {
                display: flex;
                background: rgba(30, 27, 75, 0.6);
                border-radius: 12px;
                padding: 0.5rem;
                margin-bottom: 2rem;
                gap: 0.5rem;
            }
            
            .tab {
                flex: 1;
                padding: 0.75rem 1rem;
                text-align: center;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.2s;
                font-weight: 500;
                font-size: 0.875rem;
                color: #94a3b8;
            }
            
            .tab.active {
                background: linear-gradient(135deg, #8b5cf6, #6366f1);
                color: white;
            }
            
            .tab-content {
                display: none;
            }
            
            .tab-content.active {
                display: block;
            }
            
            .charts-section {
                display: grid;
                grid-template-columns: 2fr 1fr;
                gap: 2rem;
                margin-bottom: 2rem;
            }
            
            .chart-container {
                background: rgba(30, 27, 75, 0.6);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(139, 92, 246, 0.2);
                border-radius: 12px;
                padding: 1.5rem;
            }
            
            .chart-title {
                font-size: 1.125rem;
                font-weight: 600;
                color: #f8fafc;
                margin-bottom: 1.5rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            
            .performance-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 2rem;
                margin-bottom: 2rem;
            }
            
            .performance-card {
                background: rgba(30, 27, 75, 0.6);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(139, 92, 246, 0.2);
                border-radius: 12px;
                padding: 1.5rem;
            }
            
            .performance-title {
                font-size: 1.125rem;
                font-weight: 600;
                color: #f8fafc;
                margin-bottom: 1rem;
            }
            
            .performance-stats {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 1rem;
            }
            
            .stat-item {
                text-align: center;
                padding: 1rem;
                background: rgba(0, 0, 0, 0.2);
                border-radius: 8px;
            }
            
            .stat-value {
                font-size: 1.25rem;
                font-weight: 600;
                color: #f8fafc;
            }
            
            .stat-label {
                font-size: 0.75rem;
                color: #94a3b8;
                margin-top: 0.25rem;
            }
            
            .optimization-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                gap: 1.5rem;
            }
            
            .optimization-card {
                background: rgba(30, 27, 75, 0.6);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(139, 92, 246, 0.2);
                border-radius: 12px;
                padding: 1.5rem;
                transition: all 0.3s ease;
            }
            
            .optimization-card:hover {
                transform: translateY(-2px);
                border-color: rgba(139, 92, 246, 0.4);
            }
            
            .optimization-title {
                font-size: 1.125rem;
                font-weight: 600;
                color: #f8fafc;
                margin-bottom: 1rem;
            }
            
            .optimization-desc {
                color: #cbd5e1;
                line-height: 1.6;
                margin-bottom: 1rem;
            }
            
            .optimization-actions {
                list-style: none;
                padding: 0;
            }
            
            .optimization-actions li {
                padding: 0.5rem 0;
                color: #94a3b8;
                position: relative;
                padding-left: 1.5rem;
            }
            
            .optimization-actions li::before {
                content: '→';
                position: absolute;
                left: 0;
                color: #8b5cf6;
            }
            
            .data-table {
                background: rgba(30, 27, 75, 0.6);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(139, 92, 246, 0.2);
                border-radius: 12px;
                padding: 1.5rem;
                overflow: hidden;
            }
            
            .table-responsive {
                overflow-x: auto;
            }
            
            table {
                width: 100%;
                border-collapse: collapse;
            }
            
            th, td {
                padding: 0.75rem 1rem;
                text-align: left;
                border-bottom: 1px solid rgba(139, 92, 246, 0.1);
            }
            
            th {
                background: rgba(139, 92, 246, 0.1);
                color: #a78bfa;
                font-weight: 600;
                font-size: 0.875rem;
            }
            
            td {
                color: #cbd5e1;
            }
            
            tr:hover {
                background: rgba(139, 92, 246, 0.05);
            }
            
            .status-badge {
                padding: 0.25rem 0.5rem;
                border-radius: 4px;
                font-size: 0.75rem;
                font-weight: 500;
            }
            
            .status-success { 
                background: rgba(16, 185, 129, 0.2); 
                color: #6ee7b7;
            }
            
            .status-error { 
                background: rgba(239, 68, 68, 0.2); 
                color: #fca5a5;
            }
            
            .route-badge {
                padding: 0.25rem 0.5rem;
                border-radius: 4px;
                font-size: 0.75rem;
                font-weight: 500;
            }
            
            .route-database { 
                background: rgba(59, 130, 246, 0.2); 
                color: #93c5fd;
            }
            
            .route-bedrock { 
                background: rgba(139, 92, 246, 0.2); 
                color: #c4b5fd;
            }
            
            @media (max-width: 1200px) {
                .charts-section {
                    grid-template-columns: 1fr;
                }
            }
            
            @media (max-width: 768px) {
                .container {
                    padding: 1rem;
                }
                
                .metrics-grid {
                    grid-template-columns: 1fr;
                }
                
                .header-content {
                    flex-direction: column;
                    gap: 1rem;
                }
            }
        </style>
    </head>
    <body>
        <!-- Login Screen -->
        <div id="login-container" class="login-container">
            <form class="login-form" onsubmit="return login(event)">
                <h2>Admin Access Required</h2>
                <input type="password" id="password" placeholder="Enter admin password" required>
                <br>
                <button type="submit">Access Dashboard</button>
                <div id="error-message" class="error-message">Invalid password. Please try again.</div>
            </form>
        </div>

        <!-- Dashboard Content -->
        <div id="dashboard-content" class="dashboard-content">
            <div class="header">
                <div class="header-content">
                    <h1>
                        <div class="status-dot"></div>
                        Ketha AI Command Center
                    </h1>
                    <div class="header-controls">
                        <button class="btn" onclick="exportMetrics()">Export Data</button>
                        <button class="btn" onclick="forceCleanup()">System Cleanup</button>
                        <button class="btn" onclick="refreshData()">Refresh</button>
                        <button class="logout-btn btn" onclick="logout()">Logout</button>
                    </div>
                </div>
            </div>
            
            <div class="container">
                <div class="tabs">
                    <div class="tab active" onclick="switchTab('overview')">Overview</div>
                    <div class="tab" onclick="switchTab('performance')">Performance</div>
                    <div class="tab" onclick="switchTab('optimization')">Optimization</div>
                    <div class="tab" onclick="switchTab('activity')">Activity Log</div>
                </div>
                
                <!-- Overview Tab -->
                <div id="overview-tab" class="tab-content active">
                    <div class="metrics-grid" id="metrics-grid">
                        <!-- Metrics populated by JavaScript -->
                    </div>
                    
                    <div class="charts-section">
                        <div class="chart-container">
                            <div class="chart-title">System Performance</div>
                            <canvas id="systemChart" width="800" height="300"></canvas>
                        </div>
                        <div class="chart-container">
                            <div class="chart-title">Query Distribution</div>
                            <canvas id="queryDistChart" width="300" height="200"></canvas>
                        </div>
                    </div>
                </div>
                
                <!-- Performance Tab -->
                <div id="performance-tab" class="tab-content">
                    <div class="performance-grid" id="performance-grid">
                        <!-- Performance metrics populated by JavaScript -->
                    </div>
                    
                    <div class="chart-container">
                        <div class="chart-title">Performance Analytics</div>
                        <canvas id="performanceChart" width="800" height="400"></canvas>
                    </div>
                </div>
                
                <!-- Optimization Tab -->
                <div id="optimization-tab" class="tab-content">
                    <div class="optimization-grid" id="optimization-grid">
                        <!-- Optimization suggestions populated by JavaScript -->
                    </div>
                </div>
                
                <!-- Activity Tab -->
                <div id="activity-tab" class="tab-content">
                    <div class="data-table">
                        <div class="chart-title">System Activity Log</div>
                        <div class="table-responsive">
                            <table id="activity-table">
                                <thead>
                                    <tr>
                                        <th>Timestamp</th>
                                        <th>User ID</th>
                                        <th>Query</th>
                                        <th>Route</th>
                                        <th>Response Time</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <!-- Populated by JavaScript -->
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            let charts = {};
            let currentTab = 'overview';
            const ADMIN_PASSWORD = 'kethaadmin12345679';
            
            function login(event) {
                event.preventDefault();
                const password = document.getElementById('password').value;
                const errorMessage = document.getElementById('error-message');
                
                if (password === ADMIN_PASSWORD) {
                    document.getElementById('login-container').style.display = 'none';
                    document.getElementById('dashboard-content').style.display = 'block';
                    sessionStorage.setItem('authenticated', 'true');
                    refreshData();
                    return false;
                } else {
                    errorMessage.style.display = 'block';
                    document.getElementById('password').value = '';
                    return false;
                }
            }
            
            function logout() {
                sessionStorage.removeItem('authenticated');
                document.getElementById('login-container').style.display = 'flex';
                document.getElementById('dashboard-content').style.display = 'none';
            }
            
            // Check if already authenticated
            if (sessionStorage.getItem('authenticated') === 'true') {
                document.getElementById('login-container').style.display = 'none';
                document.getElementById('dashboard-content').style.display = 'block';
            }
            
            function switchTab(tabName) {
                document.querySelectorAll('.tab-content').forEach(tab => {
                    tab.classList.remove('active');
                });
                document.querySelectorAll('.tab').forEach(tab => {
                    tab.classList.remove('active');
                });
                
                document.getElementById(tabName + '-tab').classList.add('active');
                event.target.classList.add('active');
                currentTab = tabName;
                
                refreshData();
            }
            
            async function fetchData() {
                try {
                    const [metricsResponse, performanceResponse] = await Promise.all([
                        fetch('/admin/metrics'),
                        fetch('/admin/performance')
                    ]);
                    
                    const metrics = await metricsResponse.json();
                    const performance = await performanceResponse.json();
                    
                    return { metrics, performance };
                } catch (error) {
                    console.error('Failed to fetch data:', error);
                    return { 
                        metrics: { stats: {}, memory_history: [], query_history: [] }, 
                        performance: { performance: {}, bottlenecks: [], optimizations: [] } 
                    };
                }
            }
            
            function updateOverviewTab(data) {
                updateMetrics(data.metrics);
                updateSystemChart(data.metrics);
                updateQueryDistributionChart(data.metrics);
            }
            
            function updatePerformanceTab(data) {
                updatePerformanceMetrics(data.performance);
                updatePerformanceChart(data.performance);
            }
            
            function updateOptimizationTab(data) {
                updateOptimizationSuggestions(data.performance);
            }
            
            function updateActivityTab(data) {
                updateActivityTable(data.metrics);
            }
            
            function updateMetrics(data) {
                const metricsGrid = document.getElementById('metrics-grid');
                const stats = data.stats || {};
                
                const metrics = [
                    {
                        value: Math.round(stats.current_memory || 0),
                        unit: 'MB',
                        label: 'Memory Usage',
                        change: stats.current_memory > 400 ? 'High' : 'Normal',
                        changeType: stats.current_memory > 400 ? 'negative' : 'positive'
                    },
                    {
                        value: Math.round((stats.uptime_hours || 0) * 10) / 10,
                        unit: 'hrs',
                        label: 'System Uptime',
                        change: 'Online',
                        changeType: 'positive'
                    },
                    {
                        value: stats.total_queries || 0,
                        unit: '',
                        label: 'Total Queries',
                        change: '+' + (stats.queries_per_hour || 0).toFixed(1) + '/hr',
                        changeType: 'positive'
                    },
                    {
                        value: Math.round((stats.avg_response_time || 0) * 1000),
                        unit: 'ms',
                        label: 'Avg Response',
                        change: stats.avg_response_time < 2 ? 'Fast' : 'Slow',
                        changeType: stats.avg_response_time < 2 ? 'positive' : 'negative'
                    },
                    {
                        value: Math.round((stats.error_rate || 0) * 10) / 10,
                        unit: '%',
                        label: 'Error Rate',
                        change: stats.error_rate < 5 ? 'Low' : 'High',
                        changeType: stats.error_rate < 5 ? 'positive' : 'negative'
                    },
                    {
                        value: stats.active_users || 0,
                        unit: '',
                        label: 'Active Users',
                        change: stats.unique_users + ' total',
                        changeType: 'neutral'
                    }
                ];
                
                metricsGrid.innerHTML = metrics.map(metric => `
                    <div class="metric-card">
                        <div class="metric-value">${metric.value}<span style="font-size: 1rem; opacity: 0.7; margin-left: 4px;">${metric.unit}</span></div>
                        <div class="metric-label">${metric.label}</div>
                        <div class="metric-change change-${metric.changeType}">${metric.change}</div>
                    </div>
                `).join('');
            }
            
            function updateSystemChart(data) {
                const ctx = document.getElementById('systemChart').getContext('2d');
                
                if (charts.systemChart) {
                    charts.systemChart.destroy();
                }
                
                const memoryData = (data.memory_history || []).slice(-30);
                
                charts.systemChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: memoryData.map(m => new Date(m.timestamp).toLocaleTimeString()),
                        datasets: [{
                            label: 'Memory Usage (MB)',
                            data: memoryData.map(m => m.memory_mb),
                            borderColor: '#8b5cf6',
                            backgroundColor: 'rgba(139, 92, 246, 0.1)',
                            tension: 0.4,
                            fill: true,
                            pointRadius: 2,
                            borderWidth: 2
                        }, {
                            label: 'Memory Limit',
                            data: new Array(memoryData.length).fill(512),
                            borderColor: '#ef4444',
                            borderDash: [5, 5],
                            pointRadius: 0,
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { 
                                position: 'top',
                                labels: { color: '#e2e8f0' }
                            }
                        },
                        scales: {
                            x: { 
                                grid: { color: 'rgba(139, 92, 246, 0.1)' },
                                ticks: { color: '#94a3b8' }
                            },
                            y: { 
                                beginAtZero: true, 
                                max: 600,
                                grid: { color: 'rgba(139, 92, 246, 0.1)' },
                                ticks: { color: '#94a3b8' }
                            }
                        }
                    }
                });
            }
            
            function updateQueryDistributionChart(data) {
                const ctx = document.getElementById('queryDistChart').getContext('2d');
                
                if (charts.queryDistChart) {
                    charts.queryDistChart.destroy();
                }
                
                charts.queryDistChart = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Database Queries', 'AI Queries'],
                        datasets: [{
                            data: [data.stats.db_queries, data.stats.bedrock_queries],
                            backgroundColor: ['#3b82f6', '#8b5cf6'],
                            borderWidth: 0
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { 
                                position: 'bottom',
                                labels: { color: '#e2e8f0' }
                            }
                        }
                    }
                });
            }
            
            function updatePerformanceMetrics(data) {
                const performanceGrid = document.getElementById('performance-grid');
                const perf = data.performance || {};
                
                const dbPerf = perf.database_performance || {};
                const bedrockPerf = perf.bedrock_performance || {};
                const userActivity = perf.user_activity || {};
                
                performanceGrid.innerHTML = `
                    <div class="performance-card">
                        <div class="performance-title">Database Performance</div>
                        <div class="performance-stats">
                            <div class="stat-item">
                                <div class="stat-value">${Math.round((dbPerf.avg_response_time || 0) * 1000)}ms</div>
                                <div class="stat-label">Avg Response</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">${Math.round(dbPerf.success_rate || 100)}%</div>
                                <div class="stat-label">Success Rate</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">${dbPerf.total_queries || 0}</div>
                                <div class="stat-label">Total Queries</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">${Object.keys(dbPerf.query_types || {}).length}</div>
                                <div class="stat-label">Query Types</div>
                            </div>
                        </div>
                    </div>
                    <div class="performance-card">
                        <div class="performance-title">AI Performance</div>
                        <div class="performance-stats">
                            <div class="stat-item">
                                <div class="stat-value">${Math.round((bedrockPerf.avg_response_time || 0) * 1000)}ms</div>
                                <div class="stat-label">Avg Response</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">${Math.round(bedrockPerf.success_rate || 100)}%</div>
                                <div class="stat-label">Success Rate</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">${bedrockPerf.total_queries || 0}</div>
                                <div class="stat-label">Total Queries</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">Claude 3</div>
                                <div class="stat-label">Model</div>
                            </div>
                        </div>
                    </div>
                    <div class="performance-card">
                        <div class="performance-title">User Metrics</div>
                        <div class="performance-stats">
                            <div class="stat-item">
                                <div class="stat-value">${userActivity.active_users || 0}</div>
                                <div class="stat-label">Active Users</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">${userActivity.peak_concurrent || 0}</div>
                                <div class="stat-label">Peak Concurrent</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">${userActivity.total_unique_users || 0}</div>
                                <div class="stat-label">Total Users</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-value">Online</div>
                                <div class="stat-label">Status</div>
                            </div>
                        </div>
                    </div>
                `;
            }
            
            function updatePerformanceChart(data) {
                const ctx = document.getElementById('performanceChart').getContext('2d');
                
                if (charts.performanceChart) {
                    charts.performanceChart.destroy();
                }
                
                const perf = data.performance || {};
                const queryPatterns = perf.query_patterns || {};
                
                charts.performanceChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: Object.keys(queryPatterns).slice(0, 10),
                        datasets: [{
                            label: 'Query Frequency',
                            data: Object.values(queryPatterns).slice(0, 10),
                            backgroundColor: 'rgba(139, 92, 246, 0.6)',
                            borderColor: '#8b5cf6',
                            borderWidth: 1,
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { 
                                position: 'top',
                                labels: { color: '#e2e8f0' }
                            }
                        },
                        scales: {
                            x: { 
                                grid: { color: 'rgba(139, 92, 246, 0.1)' },
                                ticks: { color: '#94a3b8' }
                            },
                            y: { 
                                beginAtZero: true,
                                grid: { color: 'rgba(139, 92, 246, 0.1)' },
                                ticks: { color: '#94a3b8' }
                            }
                        }
                    }
                });
            }
            
            function updateOptimizationSuggestions(data) {
                const optimizationGrid = document.getElementById('optimization-grid');
                const optimizations = data.optimizations || [];
                const bottlenecks = data.bottlenecks || [];
                
                const allSuggestions = [
                    ...optimizations.map(opt => ({
                        title: opt.title || 'Optimization Suggestion',
                        desc: opt.description || 'No description available',
                        actions: opt.implementation || ['No actions specified'],
                        type: 'optimization'
                    })),
                    ...bottlenecks.map(bot => ({
                        title: bot.issue || 'Performance Issue',
                        desc: bot.description || 'No description available',
                        actions: bot.suggestions || ['No suggestions available'],
                        type: 'bottleneck'
                    }))
                ];
                
                if (allSuggestions.length === 0) {
                    allSuggestions.push({
                        title: 'System Operating Optimally',
                        desc: 'All performance metrics are within acceptable ranges. No immediate optimizations required.',
                        actions: ['Continue monitoring system performance', 'Maintain current configuration'],
                        type: 'status'
                    });
                }
                
                optimizationGrid.innerHTML = allSuggestions.map(suggestion => `
                    <div class="optimization-card">
                        <div class="optimization-title">${suggestion.title}</div>
                        <div class="optimization-desc">${suggestion.desc}</div>
                        <ul class="optimization-actions">
                            ${suggestion.actions.map(action => `<li>${action}</li>`).join('')}
                        </ul>
                    </div>
                `).join('');
            }
            
            function updateActivityTable(data) {
                const tbody = document.querySelector('#activity-table tbody');
                tbody.innerHTML = data.query_history.slice(-20).reverse().map(activity => `
                    <tr>
                        <td>${new Date(activity.timestamp).toLocaleString()}</td>
                        <td>${activity.user_id}</td>
                        <td title="${activity.query}">${activity.query.length > 50 ? activity.query.substring(0, 50) + '...' : activity.query}</td>
                        <td><span class="route-badge route-${activity.route}">${activity.route}</span></td>
                        <td>${Math.round(activity.response_time * 1000)}ms</td>
                        <td><span class="status-badge status-${activity.success ? 'success' : 'error'}">${activity.success ? 'Success' : 'Error'}</span></td>
                    </tr>
                `).join('');
            }
            
            async function refreshData() {
                const data = await fetchData();
                if (data) {
                    switch(currentTab) {
                        case 'overview':
                            updateOverviewTab(data);
                            break;
                        case 'performance':
                            updatePerformanceTab(data);
                            break;
                        case 'optimization':
                            updateOptimizationTab(data);
                            break;
                        case 'activity':
                            updateActivityTab(data);
                            break;
                    }
                }
            }
            
            async function exportMetrics() {
                try {
                    const response = await fetch('/admin/export');
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.style.display = 'none';
                    a.href = url;
                    a.download = `ketha-ai-metrics-${Date.now()}.json`;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                } catch (error) {
                    console.error('Export failed:', error);
                }
            }
            
            async function forceCleanup() {
                try {
                    const response = await fetch('/cleanup', { method: 'POST' });
                    const result = await response.json();
                    console.log('Cleanup result:', result);
                    setTimeout(refreshData, 1000);
                } catch (error) {
                    console.error('Cleanup failed:', error);
                }
            }
            
            // Initialize if authenticated
            if (sessionStorage.getItem('authenticated') === 'true') {
                refreshData();
                setInterval(refreshData, 30000); // Refresh every 30 seconds
            }
        </script>
    </body>
    </html>
    """
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ketha AI Agent - Command Center</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Exo+2:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Exo 2', sans-serif;
                background: radial-gradient(ellipse at center, #0f1419 0%, #020512 100%);
                color: #00d4ff;
                min-height: 100vh;
                overflow-x: hidden;
                position: relative;
            }
            
            body::before {
                content: '';
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: 
                    radial-gradient(circle at 20% 50%, rgba(0, 212, 255, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(0, 255, 157, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 40% 80%, rgba(138, 43, 226, 0.1) 0%, transparent 50%),
                    repeating-linear-gradient(
                        0deg,
                        transparent,
                        transparent 2px,
                        rgba(0, 212, 255, 0.03) 2px,
                        rgba(0, 212, 255, 0.03) 4px
                    );
                z-index: -1;
            }
            
            .header {
                background: linear-gradient(135deg, rgba(15, 20, 25, 0.95) 0%, rgba(2, 5, 18, 0.98) 100%);
                backdrop-filter: blur(20px);
                border-bottom: 2px solid rgba(0, 212, 255, 0.3);
                padding: 1rem 2rem;
                box-shadow: 0 4px 30px rgba(0, 212, 255, 0.2);
                position: sticky;
                top: 0;
                z-index: 100;
            }
            
            .header-content {
                display: flex;
                justify-content: space-between;
                align-items: center;
                max-width: 1400px;
                margin: 0 auto;
            }
            
            .header h1 {
                font-family: 'Orbitron', monospace;
                font-size: 2.2rem;
                font-weight: 900;
                display: flex;
                align-items: center;
                gap: 1rem;
                background: linear-gradient(45deg, #00d4ff, #00ff9d, #8a2be2);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
                letter-spacing: 2px;
            }
            
            .status-indicator {
                width: 16px;
                height: 16px;
                border-radius: 50%;
                background: radial-gradient(circle, #00ff9d 0%, #00d4ff 100%);
                animation: pulse 2s infinite;
                box-shadow: 0 0 20px rgba(0, 255, 157, 0.8);
            }
            
            @keyframes pulse {
                0% { 
                    box-shadow: 0 0 20px rgba(0, 255, 157, 0.8);
                    transform: scale(1);
                }
                50% { 
                    box-shadow: 0 0 30px rgba(0, 255, 157, 1);
                    transform: scale(1.1);
                }
                100% { 
                    box-shadow: 0 0 20px rgba(0, 255, 157, 0.8);
                    transform: scale(1);
                }
            }
            
            .header-controls {
                display: flex;
                gap: 1rem;
                align-items: center;
            }
            
            .refresh-btn, .export-btn {
                background: linear-gradient(135deg, rgba(0, 212, 255, 0.2) 0%, rgba(138, 43, 226, 0.2) 100%);
                border: 1px solid rgba(0, 212, 255, 0.5);
                color: #00d4ff;
                padding: 0.75rem 1.5rem;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 600;
                font-family: 'Orbitron', monospace;
                transition: all 0.3s ease;
                backdrop-filter: blur(10px);
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            .refresh-btn:hover, .export-btn:hover {
                background: linear-gradient(135deg, rgba(0, 212, 255, 0.4) 0%, rgba(138, 43, 226, 0.4) 100%);
                box-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
                transform: translateY(-2px);
            }
            
            .container {
                max-width: 1400px;
                margin: 0 auto;
                padding: 2rem;
            }
            
            .alert-banner {
                background: linear-gradient(135deg, rgba(255, 107, 107, 0.2) 0%, rgba(254, 202, 87, 0.2) 100%);
                border: 1px solid rgba(255, 107, 107, 0.5);
                color: #ff6b6b;
                padding: 1rem 2rem;
                border-radius: 12px;
                margin-bottom: 2rem;
                display: none;
                animation: slideIn 0.5s ease;
                backdrop-filter: blur(10px);
            }
            
            @keyframes slideIn {
                from { transform: translateY(-20px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }
            
            .tabs {
                display: flex;
                background: rgba(15, 20, 25, 0.4);
                border: 1px solid rgba(0, 212, 255, 0.3);
                border-radius: 12px;
                padding: 0.5rem;
                margin-bottom: 2rem;
                backdrop-filter: blur(20px);
            }
            
            .tab {
                flex: 1;
                padding: 1rem;
                text-align: center;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.3s ease;
                font-weight: 600;
                font-family: 'Orbitron', monospace;
                position: relative;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            .tab.active {
                background: linear-gradient(135deg, rgba(0, 212, 255, 0.3) 0%, rgba(138, 43, 226, 0.3) 100%);
                color: #00d4ff;
                box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
            }
            
            .tab:not(.active) {
                color: rgba(0, 212, 255, 0.6);
            }
            
            .tab:not(.active):hover {
                background: rgba(0, 212, 255, 0.1);
                color: #00d4ff;
            }
            
            .tab-content {
                display: none;
            }
            
            .tab-content.active {
                display: block;
                animation: fadeIn 0.3s ease;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .metrics-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 1.5rem;
                margin-bottom: 2rem;
            }
            
            .metric-card {
                background: linear-gradient(135deg, rgba(15, 20, 25, 0.8) 0%, rgba(2, 5, 18, 0.9) 100%);
                border: 1px solid rgba(0, 212, 255, 0.3);
                border-radius: 16px;
                padding: 2rem;
                backdrop-filter: blur(20px);
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }
            
            .metric-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 2px;
                background: linear-gradient(90deg, #00d4ff, #00ff9d, #8a2be2);
            }
            
            .metric-card:hover {
                transform: translateY(-8px);
                box-shadow: 0 15px 40px rgba(0, 212, 255, 0.2);
                border-color: rgba(0, 212, 255, 0.6);
            }
            
            .metric-header {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 1rem;
            }
            
            .metric-icon {
                font-size: 2.5rem;
                opacity: 0.8;
                filter: drop-shadow(0 0 10px currentColor);
            }
            
            .metric-value {
                font-size: 3rem;
                font-weight: 900;
                font-family: 'Orbitron', monospace;
                margin-bottom: 0.5rem;
                background: linear-gradient(45deg, #00d4ff, #00ff9d);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
            }
            
            .metric-label {
                color: rgba(0, 212, 255, 0.8);
                font-size: 1rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            .metric-trend {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                font-size: 0.9rem;
                margin-top: 1rem;
                padding: 0.5rem;
                border-radius: 8px;
                background: rgba(0, 0, 0, 0.2);
                font-family: 'Orbitron', monospace;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .trend-up { color: #00ff9d; }
            .trend-down { color: #ff6b6b; }
            .trend-stable { color: #feca57; }
            
            .charts-section {
                display: grid;
                grid-template-columns: 2fr 1fr;
                gap: 2rem;
                margin-bottom: 2rem;
            }
            
            .chart-container {
                background: linear-gradient(135deg, rgba(15, 20, 25, 0.8) 0%, rgba(2, 5, 18, 0.9) 100%);
                border: 1px solid rgba(0, 212, 255, 0.3);
                border-radius: 16px;
                padding: 2rem;
                backdrop-filter: blur(20px);
                position: relative;
                overflow: hidden;
            }
            
            .chart-container::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 2px;
                background: linear-gradient(90deg, #00d4ff, #00ff9d, #8a2be2);
            }
            
            .chart-title {
                font-size: 1.3rem;
                font-weight: 700;
                font-family: 'Orbitron', monospace;
                margin-bottom: 1.5rem;
                color: #00d4ff;
                display: flex;
                align-items: center;
                gap: 0.5rem;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            .performance-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 2rem;
                margin-bottom: 2rem;
            }
            
            .bottleneck-card {
                background: linear-gradient(135deg, rgba(15, 20, 25, 0.8) 0%, rgba(2, 5, 18, 0.9) 100%);
                border: 1px solid rgba(0, 212, 255, 0.3);
                border-radius: 16px;
                padding: 2rem;
                backdrop-filter: blur(20px);
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }
            
            .bottleneck-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 2px;
                background: linear-gradient(90deg, #00d4ff, #00ff9d, #8a2be2);
            }
            
            .bottleneck-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 30px rgba(0, 212, 255, 0.2);
            }
            
            .bottleneck-card h3 {
                font-family: 'Orbitron', monospace;
                font-size: 1.2rem;
                font-weight: 700;
                color: #00d4ff;
                margin-bottom: 1rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            .optimization-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                gap: 1.5rem;
            }
            
            .optimization-card {
                background: linear-gradient(135deg, rgba(138, 43, 226, 0.2) 0%, rgba(0, 212, 255, 0.2) 100%);
                border: 1px solid rgba(138, 43, 226, 0.5);
                padding: 2rem;
                border-radius: 16px;
                transition: all 0.3s ease;
                backdrop-filter: blur(20px);
                color: #00d4ff;
            }
            
            .optimization-card:hover {
                transform: scale(1.02);
                box-shadow: 0 10px 30px rgba(138, 43, 226, 0.3);
            }
            
            .data-table {
                background: linear-gradient(135deg, rgba(15, 20, 25, 0.8) 0%, rgba(2, 5, 18, 0.9) 100%);
                border: 1px solid rgba(0, 212, 255, 0.3);
                border-radius: 16px;
                padding: 2rem;
                backdrop-filter: blur(20px);
                overflow: hidden;
                position: relative;
            }
            
            .data-table::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 2px;
                background: linear-gradient(90deg, #00d4ff, #00ff9d, #8a2be2);
            }
            
            .table-responsive {
                overflow-x: auto;
                border-radius: 12px;
            }
            
            table {
                width: 100%;
                border-collapse: collapse;
                background: rgba(0, 0, 0, 0.2);
            }
            
            th, td {
                padding: 1rem 1.5rem;
                text-align: left;
                border-bottom: 1px solid rgba(0, 212, 255, 0.2);
            }
            
            th {
                background: linear-gradient(135deg, rgba(0, 212, 255, 0.3) 0%, rgba(138, 43, 226, 0.3) 100%);
                color: #00d4ff;
                font-weight: 700;
                font-family: 'Orbitron', monospace;
                font-size: 0.9rem;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            td {
                color: rgba(0, 212, 255, 0.9);
            }
            
            tr:hover {
                background: rgba(0, 212, 255, 0.05);
            }
            
            .status-badge {
                padding: 0.25rem 0.75rem;
                border-radius: 20px;
                font-size: 0.8rem;
                font-weight: 600;
                text-transform: uppercase;
                font-family: 'Orbitron', monospace;
            }
            
            .status-success { 
                background: rgba(0, 255, 157, 0.2); 
                color: #00ff9d;
                border: 1px solid rgba(0, 255, 157, 0.5);
            }
            .status-error { 
                background: rgba(255, 107, 107, 0.2); 
                color: #ff6b6b;
                border: 1px solid rgba(255, 107, 107, 0.5);
            }
            
            .route-badge {
                padding: 0.4rem 0.8rem;
                border-radius: 8px;
                font-size: 0.8rem;
                font-weight: 600;
                font-family: 'Orbitron', monospace;
                text-transform: uppercase;
            }
            
            .route-database { 
                background: rgba(52, 152, 219, 0.2); 
                color: #3498db;
                border: 1px solid rgba(52, 152, 219, 0.5);
            }
            .route-bedrock { 
                background: rgba(155, 89, 182, 0.2); 
                color: #9b59b6;
                border: 1px solid rgba(155, 89, 182, 0.5);
            }
            
            @media (max-width: 1200px) {
                .charts-section {
                    grid-template-columns: 1fr;
                }
            }
            
            @media (max-width: 768px) {
                .header-content {
                    flex-direction: column;
                    gap: 1rem;
                }
                
                .tabs {
                    flex-direction: column;
                }
                
                .metrics-grid {
                    grid-template-columns: 1fr;
                }
                
                .performance-grid {
                    grid-template-columns: 1fr;
                }
                
                .optimization-grid {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-content">
                <h1>
                    <div class="status-indicator"></div>
                    KETHA AI COMMAND CENTER
                </h1>
                <div class="header-controls">
                    <button class="export-btn" onclick="exportMetrics()">📊 EXPORT DATA</button>
                    <button class="refresh-btn" onclick="forceCleanup()">🧹 CLEANUP</button>
                    <button class="refresh-btn" onclick="refreshData()">🔄 REFRESH</button>
                </div>
            </div>
        </div>
        
        <div class="container">
            <div id="alert-banner" class="alert-banner">
                <strong>⚠️ Alert:</strong> <span id="alert-message"></span>
            </div>
            
            <div class="tabs">
                <div class="tab active" onclick="switchTab('overview')">📊 OVERVIEW</div>
                <div class="tab" onclick="switchTab('performance')">⚡ PERFORMANCE</div>
                <div class="tab" onclick="switchTab('optimization')">🚀 OPTIMIZATION</div>
                <div class="tab" onclick="switchTab('activity')">👥 ACTIVITY LOG</div>
            </div>
            
            <!-- Overview Tab -->
            <div id="overview-tab" class="tab-content active">
                <div class="metrics-grid" id="metrics-grid">
                    <!-- Metrics populated by JavaScript -->
                </div>
                
                <div class="charts-section">
                    <div class="chart-container">
                        <div class="chart-title">📈 SYSTEM METRICS ANALYSIS</div>
                        <canvas id="memoryChart" width="400" height="200"></canvas>
                    </div>
                    <div class="chart-container">
                        <div class="chart-title">📊 QUERY DISTRIBUTION</div>
                        <canvas id="queryDistChart" width="300" height="200"></canvas>
                    </div>
                </div>
            </div>
            
            <!-- Performance Tab -->
            <div id="performance-tab" class="tab-content">
                <div class="performance-grid" id="performance-grid">
                    <!-- Performance metrics populated by JavaScript -->
                </div>
                
                <div class="chart-container">
                    <div class="chart-title">⚡ PERFORMANCE ANALYTICS</div>
                    <canvas id="responseTimeChart" width="800" height="300"></canvas>
                </div>
            </div>
            
            <!-- Optimization Tab -->
            <div id="optimization-tab" class="tab-content">
                <div class="optimization-grid" id="optimization-grid">
                    <!-- Optimization suggestions populated by JavaScript -->
                </div>
            </div>
            
            <!-- Activity Tab -->
            <div id="activity-tab" class="tab-content">
                <div class="data-table">
                    <div class="chart-title">👥 SYSTEM ACTIVITY LOG</div>
                    <div class="table-responsive">
                        <table id="activity-table">
                            <thead>
                                <tr>
                                    <th>TIMESTAMP</th>
                                    <th>USER ID</th>
                                    <th>QUERY</th>
                                    <th>ROUTE</th>
                                    <th>RESPONSE TIME</th>
                                    <th>STATUS</th>
                                </tr>
                            </thead>
                            <tbody>
                                <!-- Populated by JavaScript -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            let charts = {};
            let currentTab = 'overview';
            
            function switchTab(tabName) {
                // Hide all tabs
                document.querySelectorAll('.tab-content').forEach(tab => {
                    tab.classList.remove('active');
                });
                document.querySelectorAll('.tab').forEach(tab => {
                    tab.classList.remove('active');
                });
                
                // Show selected tab
                document.getElementById(tabName + '-tab').classList.add('active');
                event.target.classList.add('active');
                currentTab = tabName;
                
                // Refresh data for the new tab
                refreshData();
            }
            
            async function fetchData() {
                try {
                    const [metricsResponse, performanceResponse] = await Promise.all([
                        fetch('/admin/metrics'),
                        fetch('/admin/performance')
                    ]);
                    
                    const metrics = await metricsResponse.json();
                    const performance = await performanceResponse.json();
                    
                    return { metrics, performance };
                } catch (error) {
                    console.error('Failed to fetch data:', error);
                    return null;
                }
            }
            
            function updateOverviewTab(data) {
                updateMetrics(data.metrics);
                updateMemoryChart(data.metrics);
                updateQueryDistributionChart(data.metrics);
            }
            
            function updatePerformanceTab(data) {
                updatePerformanceMetrics(data.performance);
                updateResponseTimeChart(data.performance);
            }
            
            function updateOptimizationTab(data) {
                updateOptimizationSuggestions(data.performance);
            }
            
            function updateActivityTab(data) {
                updateActivityTable(data.metrics);
            }
            
            function updateMetrics(data) {
                const metricsGrid = document.getElementById('metrics-grid');
                const stats = data.stats;
                
                const metrics = [
                    {
                        icon: '🧠',
                        value: Math.round(stats.current_memory),
                        unit: 'MB',
                        label: 'Memory Usage',
                        trend: stats.current_memory > 400 ? 'critical' : stats.current_memory > 300 ? 'warning' : 'good'
                    },
                    {
                        icon: '⏱️',
                        value: Math.round(stats.uptime_hours * 10) / 10,
                        unit: 'hrs',
                        label: 'System Uptime',
                        trend: 'good'
                    },
                    {
                        icon: '📝',
                        value: stats.total_queries,
                        unit: '',
                        label: 'Total Queries',
                        trend: 'good'
                    },
                    {
                        icon: '⚡',
                        value: Math.round(stats.avg_response_time * 1000),
                        unit: 'ms',
                        label: 'Avg Response',
                        trend: stats.avg_response_time < 2 ? 'good' : stats.avg_response_time < 5 ? 'warning' : 'critical'
                    },
                    {
                        icon: '❌',
                        value: Math.round(stats.error_rate * 10) / 10,
                        unit: '%',
                        label: 'Error Rate',
                        trend: stats.error_rate < 5 ? 'good' : stats.error_rate < 10 ? 'warning' : 'critical'
                    },
                    {
                        icon: '👥',
                        value: stats.active_users,
                        unit: '',
                        label: 'Active Users',
                        trend: 'good'
                    }
                ];
                
                metricsGrid.innerHTML = metrics.map(metric => `
                    <div class="metric-card">
                        <div class="metric-header">
                            <div class="metric-icon">${metric.icon}</div>
                        </div>
                        <div class="metric-value">${metric.value}<span style="font-size: 1rem; opacity: 0.7;">${metric.unit}</span></div>
                        <div class="metric-label">${metric.label}</div>
                        <div class="metric-trend trend-${metric.trend === 'good' ? 'down' : metric.trend === 'warning' ? 'stable' : 'up'}">
                            ${metric.trend === 'good' ? '✅ Optimal' : metric.trend === 'warning' ? '⚠️ Monitor' : '🚨 Action Required'}
                        </div>
                    </div>
                `).join('');
                
                // Update alert banner
                const alertBanner = document.getElementById('alert-banner');
                const alertMessage = document.getElementById('alert-message');
                
                if (stats.current_memory > 450) {
                    alertMessage.textContent = 'Critical memory usage detected! Immediate action required.';
                    alertBanner.style.display = 'block';
                } else if (stats.error_rate > 10) {
                    alertMessage.textContent = 'High error rate detected. Check system logs.';
                    alertBanner.style.display = 'block';
                } else {
                    alertBanner.style.display = 'none';
                }
            }
            
            function updateMemoryChart(data) {
                const ctx = document.getElementById('memoryChart').getContext('2d');
                
                if (charts.memoryChart) {
                    charts.memoryChart.destroy();
                }
                
                charts.memoryChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: data.memory_history.slice(-30).map(m => new Date(m.timestamp).toLocaleTimeString()),
                        datasets: [{
                            label: 'Memory Usage (MB)',
                            data: data.memory_history.slice(-30).map(m => m.memory_mb),
                            borderColor: '#667eea',
                            backgroundColor: 'rgba(102, 126, 234, 0.1)',
                            tension: 0.4,
                            fill: true,
                            pointRadius: 2,
                            borderWidth: 3
                        }, {
                            label: 'Memory Limit',
                            data: new Array(data.memory_history.slice(-30).length).fill(512),
                            borderColor: '#e74c3c',
                            borderDash: [5, 5],
                            pointRadius: 0,
                            borderWidth: 2
                        }]
                    },
                    options: {
                        responsive: true,
                        interaction: { intersect: false },
                        plugins: {
                            legend: { position: 'top' }
                        },
                        scales: {
                            y: { beginAtZero: true, max: 600 }
                        }
                    }
                });
            }
            
            function updateQueryDistributionChart(data) {
                const ctx = document.getElementById('queryDistChart').getContext('2d');
                
                if (charts.queryDistChart) {
                    charts.queryDistChart.destroy();
                }
                
                charts.queryDistChart = new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Database Queries', 'Bedrock Queries'],
                        datasets: [{
                            data: [data.stats.db_queries, data.stats.bedrock_queries],
                            backgroundColor: ['#3498db', '#9b59b6'],
                            borderWidth: 0
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { position: 'bottom' }
                        }
                    }
                });
            }
            
            function updatePerformanceMetrics(data) {
                const performanceGrid = document.getElementById('performance-grid');
                const perf = data.performance || {};
                
                const dbPerf = perf.database_performance || {};
                const bedrockPerf = perf.bedrock_performance || {};
                const userActivity = perf.user_activity || {};
                
                performanceGrid.innerHTML = `
                    <div class="bottleneck-card medium">
                        <h3>🗃️ Database Performance</h3>
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-top: 1rem;">
                            <div style="text-align: center; padding: 1rem; background: rgba(0,0,0,0.05); border-radius: 8px;">
                                <div style="font-size: 1.5rem; font-weight: bold; color: #3498db;">${Math.round((dbPerf.avg_response_time || 0) * 1000)}ms</div>
                                <div style="font-size: 0.8rem; color: #666;">Avg Response Time</div>
                            </div>
                            <div style="text-align: center; padding: 1rem; background: rgba(0,0,0,0.05); border-radius: 8px;">
                                <div style="font-size: 1.5rem; font-weight: bold; color: #27ae60;">${Math.round(dbPerf.success_rate || 100)}%</div>
                                <div style="font-size: 0.8rem; color: #666;">Success Rate</div>
                            </div>
                            <div style="text-align: center; padding: 1rem; background: rgba(0,0,0,0.05); border-radius: 8px;">
                                <div style="font-size: 1.5rem; font-weight: bold; color: #667eea;">${dbPerf.total_queries || 0}</div>
                                <div style="font-size: 0.8rem; color: #666;">Total Queries</div>
                            </div>
                            <div style="text-align: center; padding: 1rem; background: rgba(0,0,0,0.05); border-radius: 8px;">
                                <div style="font-size: 1.5rem; font-weight: bold; color: #9b59b6;">${Object.keys(dbPerf.query_types || {}).length}</div>
                                <div style="font-size: 0.8rem; color: #666;">Query Types</div>
                            </div>
                        </div>
                    </div>
                    <div class="bottleneck-card medium">
                        <h3>🤖 Bedrock AI Performance</h3>
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-top: 1rem;">
                            <div style="text-align: center; padding: 1rem; background: rgba(0,0,0,0.05); border-radius: 8px;">
                                <div style="font-size: 1.5rem; font-weight: bold; color: #9b59b6;">${Math.round((bedrockPerf.avg_response_time || 0) * 1000)}ms</div>
                                <div style="font-size: 0.8rem; color: #666;">Avg Response Time</div>
                            </div>
                            <div style="text-align: center; padding: 1rem; background: rgba(0,0,0,0.05); border-radius: 8px;">
                                <div style="font-size: 1.5rem; font-weight: bold; color: #27ae60;">${Math.round(bedrockPerf.success_rate || 100)}%</div>
                                <div style="font-size: 0.8rem; color: #666;">Success Rate</div>
                            </div>
                            <div style="text-align: center; padding: 1rem; background: rgba(0,0,0,0.05); border-radius: 8px;">
                                <div style="font-size: 1.5rem; font-weight: bold; color: #667eea;">${bedrockPerf.total_queries || 0}</div>
                                <div style="font-size: 0.8rem; color: #666;">Total Queries</div>
                            </div>
                            <div style="text-align: center; padding: 1rem; background: rgba(0,0,0,0.05); border-radius: 8px;">
                                <div style="font-size: 1.5rem; font-weight: bold; color: #e74c3c;">Claude 3</div>
                                <div style="font-size: 0.8rem; color: #666;">AI Model</div>
                            </div>
                        </div>
                    </div>
                    <div class="bottleneck-card medium">
                        <h3>👥 User Activity</h3>
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-top: 1rem;">
                            <div style="text-align: center; padding: 1rem; background: rgba(0,0,0,0.05); border-radius: 8px;">
                                <div style="font-size: 1.5rem; font-weight: bold; color: #27ae60;">${userActivity.active_users || 0}</div>
                                <div style="font-size: 0.8rem; color: #666;">Active Users</div>
                            </div>
                            <div style="text-align: center; padding: 1rem; background: rgba(0,0,0,0.05); border-radius: 8px;">
                                <div style="font-size: 1.5rem; font-weight: bold; color: #f39c12;">${userActivity.peak_concurrent || 0}</div>
                                <div style="font-size: 0.8rem; color: #666;">Peak Concurrent</div>
                            </div>
                            <div style="text-align: center; padding: 1rem; background: rgba(0,0,0,0.05); border-radius: 8px;">
                                <div style="font-size: 1.5rem; font-weight: bold; color: #3498db;">${userActivity.total_unique_users || 0}</div>
                                <div style="font-size: 0.8rem; color: #666;">Total Users</div>
                            </div>
                            <div style="text-align: center; padding: 1rem; background: rgba(0,0,0,0.05); border-radius: 8px;">
                                <div style="font-size: 1.5rem; font-weight: bold; color: #27ae60;">●</div>
                                <div style="font-size: 0.8rem; color: #666;">System Online</div>
                            </div>
                        </div>
                    </div>
                `;
            }
            
            function updateResponseTimeChart(data) {
                const ctx = document.getElementById('responseTimeChart').getContext('2d');
                
                if (charts.responseTimeChart) {
                    charts.responseTimeChart.destroy();
                }
                
                const perf = data.performance || {};
                const queryPatterns = perf.query_patterns || {};
                
                charts.responseTimeChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: Object.keys(queryPatterns).slice(0, 10),
                        datasets: [{
                            label: 'Query Frequency',
                            data: Object.values(queryPatterns).slice(0, 10),
                            backgroundColor: 'rgba(102, 126, 234, 0.6)',
                            borderColor: '#667eea',
                            borderWidth: 2,
                            borderRadius: 4,
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { position: 'top' }
                        },
                        scales: {
                            y: { beginAtZero: true }
                        }
                    }
                });
            }
            
            function updateOptimizationSuggestions(data) {
                const optimizationGrid = document.getElementById('optimization-grid');
                const optimizations = data.optimizations || [];
                const bottlenecks = data.bottlenecks || [];
                
                // Combine optimizations and bottlenecks
                const allSuggestions = [
                    ...optimizations.map(opt => ({
                        title: opt.title || 'Optimization Suggestion',
                        desc: opt.description || 'No description available',
                        actions: opt.implementation || ['No actions specified'],
                        priority: opt.priority || 'medium',
                        type: 'optimization'
                    })),
                    ...bottlenecks.map(bot => ({
                        title: bot.issue || 'Performance Issue',
                        desc: bot.description || 'No description available',
                        actions: bot.suggestions || ['No suggestions available'],
                        priority: bot.severity || 'medium',
                        type: 'bottleneck'
                    }))
                ];
                
                if (allSuggestions.length === 0) {
                    allSuggestions.push({
                        title: '✅ System Operating Optimally',
                        desc: 'All performance metrics are within acceptable ranges. No immediate optimizations required.',
                        actions: ['Continue monitoring system performance', 'Maintain current configuration', 'Regular maintenance schedule'],
                        priority: 'info',
                        type: 'status'
                    });
                }
                
                optimizationGrid.innerHTML = allSuggestions.map(suggestion => `
                    <div class="optimization-card">
                        <h3 style="margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
                            ${suggestion.type === 'bottleneck' ? '⚠️' : suggestion.type === 'optimization' ? '🚀' : '✅'} 
                            ${suggestion.title}
                            <span style="font-size: 0.7rem; padding: 0.2rem 0.5rem; background: rgba(255,255,255,0.2); border-radius: 12px; text-transform: uppercase;">${suggestion.priority}</span>
                        </h3>
                        <p style="margin-bottom: 1rem; opacity: 0.9;">${suggestion.desc}</p>
                        <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px;">
                            <strong style="margin-bottom: 0.5rem; display: block;">Recommended Actions:</strong>
                            <ul style="margin: 0; padding-left: 1.5rem;">
                                ${suggestion.actions.map(action => `<li style="margin-bottom: 0.5rem;">${action}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                `).join('');
            }
            
            function updateActivityTable(data) {
                const tbody = document.querySelector('#activity-table tbody');
                tbody.innerHTML = data.query_history.slice(-20).reverse().map(activity => `
                    <tr>
                        <td>${new Date(activity.timestamp).toLocaleString()}</td>
                        <td><strong>${activity.user_id}</strong></td>
                        <td title="${activity.query}">${activity.query.length > 50 ? activity.query.substring(0, 50) + '...' : activity.query}</td>
                        <td><span class="route-badge route-${activity.route}">${activity.route}</span></td>
                        <td>${Math.round(activity.response_time * 1000)}ms</td>
                        <td><span class="status-badge status-${activity.success ? 'success' : 'error'}">${activity.success ? 'Success' : 'Error'}</span></td>
                    </tr>
                `).join('');
            }
            
            async function refreshData() {
                const data = await fetchData();
                if (data) {
                    switch(currentTab) {
                        case 'overview':
                            updateOverviewTab(data);
                            break;
                        case 'performance':
                            updatePerformanceTab(data);
                            break;
                        case 'optimization':
                            updateOptimizationTab(data);
                            break;
                        case 'activity':
                            updateActivityTab(data);
                            break;
                    }
                }
            }
            
            function exportMetrics() {
                // Export functionality
                window.open('/admin/export', '_blank');
            }
            
            async function forceCleanup() {
                try {
                    const response = await fetch('/cleanup', { method: 'POST' });
                    const result = await response.json();
                    console.log('Cleanup result:', result);
                    setTimeout(refreshData, 1000); // Refresh after cleanup
                } catch (error) {
                    console.error('Cleanup failed:', error);
                }
            }
            
            // Initialize
            refreshData();
            setInterval(refreshData, 10000); // Refresh every 10 seconds
        </script>
    </body>
    </html>
    """
