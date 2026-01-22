// Main JavaScript for Fund Analysis System

let allFunds = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadFunds();
    loadStats();
    loadTopPerformers('month');
});

// Tab switching
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    
    // Activate button
    event.target.classList.add('active');
}

// Load all funds
async function loadFunds() {
    try {
        const response = await fetch('/api/funds');
        allFunds = await response.json();
        
        displayFundList(allFunds);
        updateHotFunds(allFunds.slice(0, 5));
    } catch (error) {
        console.error('Error loading funds:', error);
    }
}

// Load statistics
async function loadStats() {
    try {
        const response = await fetch('/api/funds');
        const funds = await response.json();
        
        document.getElementById('total-funds').textContent = funds.length;
        document.getElementById('last-update').textContent = new Date().toLocaleDateString('zh-CN');
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Display fund list
function displayFundList(funds) {
    const fundList = document.getElementById('fund-list');
    
    if (funds.length === 0) {
        fundList.innerHTML = '<p>未找到基金数据</p>';
        return;
    }
    
    fundList.innerHTML = funds.map(fund => `
        <div class="fund-item" onclick="showFundDetail('${fund.code}')">
            <div class="fund-code">${fund.code}</div>
            <div class="fund-name">${fund.name}</div>
            <div class="fund-type">${fund.type || ''} | ${fund.company || ''}</div>
        </div>
    `).join('');
}

// Update hot funds
function updateHotFunds(funds) {
    const hotFunds = document.getElementById('hot-funds');
    
    hotFunds.innerHTML = funds.map(fund => `
        <div style="margin: 10px 0;">
            <strong>${fund.code}</strong> - ${fund.name}
        </div>
    `).join('');
}

// Search fund
function searchFund() {
    const query = document.getElementById('search-input').value.toLowerCase();
    
    if (!query) {
        displayFundList(allFunds);
        return;
    }
    
    const filtered = allFunds.filter(fund => 
        fund.code.toLowerCase().includes(query) || 
        fund.name.toLowerCase().includes(query)
    );
    
    displayFundList(filtered);
}

// Show fund detail
async function showFundDetail(fundCode) {
    try {
        // Load fund info
        const fundResponse = await fetch(`/api/fund/${fundCode}`);
        const fund = await fundResponse.json();
        
        // Load fund values
        const valuesResponse = await fetch(`/api/fund/${fundCode}/values?days=180`);
        const values = await valuesResponse.json();
        
        // Load performance
        const perfResponse = await fetch(`/api/fund/${fundCode}/performance`);
        const performance = await perfResponse.json();
        
        // Display info
        const detailDiv = document.getElementById('fund-detail');
        const titleDiv = document.getElementById('fund-detail-title');
        const infoDiv = document.getElementById('fund-detail-info');
        
        titleDiv.textContent = `${fund.name} (${fund.code})`;
        infoDiv.innerHTML = `
            <p><strong>类型:</strong> ${fund.type || 'N/A'}</p>
            <p><strong>公司:</strong> ${fund.company || 'N/A'}</p>
            <p><strong>基金经理:</strong> ${fund.manager || 'N/A'}</p>
        `;
        
        detailDiv.style.display = 'block';
        
        // Display chart
        if (values.length > 0) {
            displayChart(values);
        }
        
        // Display performance
        if (!performance.error) {
            displayPerformance(performance);
        }
        
    } catch (error) {
        console.error('Error loading fund detail:', error);
        alert('加载基金详情失败');
    }
}

// Display chart
function displayChart(values) {
    const dates = values.map(v => v.date);
    const netValues = values.map(v => v.net_value);
    
    const trace = {
        x: dates,
        y: netValues,
        type: 'scatter',
        mode: 'lines',
        name: '净值',
        line: {
            color: '#667eea',
            width: 2
        }
    };
    
    const layout = {
        title: '净值走势',
        xaxis: { title: '日期' },
        yaxis: { title: '净值' },
        height: 400
    };
    
    Plotly.newPlot('fund-chart', [trace], layout);
}

// Display performance
function displayPerformance(perf) {
    const perfDiv = document.getElementById('fund-performance-data');
    
    perfDiv.innerHTML = `
        <h4>业绩表现</h4>
        <table class="performance-table">
            <tr>
                <th>周期</th>
                <th>收益率</th>
            </tr>
            <tr>
                <td>近一周</td>
                <td class="${perf.week_return >= 0 ? 'positive' : 'negative'}">${perf.week_return}%</td>
            </tr>
            <tr>
                <td>近一月</td>
                <td class="${perf.month_return >= 0 ? 'positive' : 'negative'}">${perf.month_return}%</td>
            </tr>
            <tr>
                <td>近一季度</td>
                <td class="${perf.quarter_return >= 0 ? 'positive' : 'negative'}">${perf.quarter_return}%</td>
            </tr>
            <tr>
                <td>近半年</td>
                <td class="${perf.half_year_return >= 0 ? 'positive' : 'negative'}">${perf.half_year_return}%</td>
            </tr>
            <tr>
                <td>近一年</td>
                <td class="${perf.year_return >= 0 ? 'positive' : 'negative'}">${perf.year_return}%</td>
            </tr>
            <tr>
                <td>近三年</td>
                <td class="${perf.three_year_return >= 0 ? 'positive' : 'negative'}">${perf.three_year_return}%</td>
            </tr>
        </table>
    `;
}

// Analyze fund
async function analyzeFund() {
    const fundCode = document.getElementById('analysis-fund-code').value;
    
    if (!fundCode) {
        alert('请输入基金代码');
        return;
    }
    
    try {
        // Get analysis
        const analysisResponse = await fetch(`/api/fund/${fundCode}/analysis`);
        const analysis = await analysisResponse.json();
        
        // Get backtest
        const backtestResponse = await fetch(`/api/fund/${fundCode}/backtest`);
        const backtest = await backtestResponse.json();
        
        displayAnalysis(analysis);
        displayBacktest(backtest);
        
    } catch (error) {
        console.error('Error analyzing fund:', error);
        alert('分析失败，请检查基金代码');
    }
}

// Display analysis
function displayAnalysis(analysis) {
    const resultDiv = document.getElementById('analysis-result');
    
    const signalClass = `signal-${analysis.overall_signal.toLowerCase()}`;
    
    let strategiesHTML = '';
    for (const [name, result] of Object.entries(analysis.strategy_signals)) {
        const strategyClass = `signal-${result.signal.toLowerCase()}`;
        strategiesHTML += `
            <div class="strategy-card">
                <h4>${name}</h4>
                <div class="signal-box ${strategyClass}">${result.signal}</div>
                <p>置信度: ${result.confidence}%</p>
            </div>
        `;
    }
    
    resultDiv.innerHTML = `
        <h4>综合信号</h4>
        <div class="signal-box ${signalClass}">${analysis.overall_signal}</div>
        <p>综合置信度: ${analysis.confidence}%</p>
        
        <h4 style="margin-top: 30px;">各策略信号</h4>
        <div class="strategy-grid">
            ${strategiesHTML}
        </div>
    `;
}

// Display backtest
function displayBacktest(backtest) {
    const resultDiv = document.getElementById('backtest-result');
    
    if (backtest.error) {
        resultDiv.innerHTML = `<p>回测数据不足</p>`;
        return;
    }
    
    const returnClass = backtest.total_return >= 0 ? 'positive' : 'negative';
    
    resultDiv.innerHTML = `
        <h4>回测结果</h4>
        <p>初始资金: ¥${backtest.initial_capital.toFixed(2)}</p>
        <p>最终资金: ¥${backtest.final_value.toFixed(2)}</p>
        <p class="${returnClass}">总收益率: ${backtest.total_return.toFixed(2)}%</p>
        <p>交易次数: ${backtest.num_trades}</p>
    `;
}

// Load top performers
async function loadTopPerformers(period) {
    try {
        const response = await fetch(`/api/top-performers?period=${period}&limit=10`);
        const performers = await response.json();
        
        const resultDiv = document.getElementById('top-performers');
        
        if (performers.length === 0) {
            resultDiv.innerHTML = '<p>暂无数据</p>';
            return;
        }
        
        resultDiv.innerHTML = `
            <table class="performance-table">
                <tr>
                    <th>排名</th>
                    <th>代码</th>
                    <th>名称</th>
                    <th>类型</th>
                    <th>收益率</th>
                </tr>
                ${performers.map((p, idx) => `
                    <tr>
                        <td>${idx + 1}</td>
                        <td>${p.fund_code}</td>
                        <td>${p.fund_name}</td>
                        <td>${p.fund_type || 'N/A'}</td>
                        <td class="${p.return >= 0 ? 'positive' : 'negative'}">${p.return}%</td>
                    </tr>
                `).join('')}
            </table>
        `;
        
        // Update button states
        document.querySelectorAll('.period-selector button').forEach(btn => {
            btn.classList.remove('active');
        });
        event.target.classList.add('active');
        
    } catch (error) {
        console.error('Error loading top performers:', error);
    }
}
