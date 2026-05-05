const API_URL = 'https://ai-fund-tracker.onrender.com';
let deptChartInstance = null;

document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

async function initApp() {
    await fetchDashboardData();
    await fetchTransactions();
    await fetchImpactScores();
    fetchAnalysis(); // Auto run AI checks on load
}

// 1. Fetch KPI & Chart Data
async function fetchDashboardData() {
    const res = await fetch(`${API_URL}/get_dashboard_data`);
    const data = await res.json();
    
    // Update KPI Text
    document.getElementById('total-allocated').innerText = `$${data.total_allocated.toLocaleString()}`;
    document.getElementById('total-utilized').innerText = `$${data.total_utilized.toLocaleString()}`;
    document.getElementById('total-balance').innerText = `$${data.balance.toLocaleString()}`;

    // Populate Project Select Dropdown
    const txSelect = document.getElementById('tx-project');
    txSelect.innerHTML = '<option value="">Select Project...</option>';
    data.projects.forEach(p => {
        const option = document.createElement('option');
        option.value = p.id;
        option.innerText = p.name;
        txSelect.appendChild(option);
    });

    // Render Department Chart
    renderChart(data.dept_spending);
}

// 2. Render Chart.js
function renderChart(deptData) {
    const ctx = document.getElementById('deptChart').getContext('2d');
    if (deptChartInstance) deptChartInstance.destroy();

    deptChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(deptData),
            datasets: [{
                label: 'Utilized Funds ($)',
                data: Object.values(deptData),
                backgroundColor: '#2563eb',
                borderRadius: 4
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });
}

// 3. Fetch Transaction Log
async function fetchTransactions() {
    const res = await fetch(`${API_URL}/get_transactions`);
    const data = await res.json();
    
    const tbody = document.getElementById('tx-table-body');
    tbody.innerHTML = '';
    
    data.transactions.forEach(tx => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${tx.date}</td>
            <td><strong>${tx.project_name}</strong></td>
            <td>${tx.desc}</td>
            <td>${tx.category}</td>
            <td class="text-primary font-bold">$${tx.amount.toLocaleString()}</td>
        `;
        tbody.appendChild(tr);
    });
}

// 4. Fetch Impact Scores
async function fetchImpactScores() {
    const res = await fetch(`${API_URL}/impact_score`);
    const data = await res.json();
    
    const container = document.getElementById('impact-container');
    container.innerHTML = '';
    
    data.impact_scores.forEach(score => {
        container.innerHTML += `
            <div class="impact-item">
                <div>
                    <strong>${score.project_name}</strong><br>
                    <span class="text-muted">${score.metrics}</span>
                </div>
                <div>
                    <span class="badge ${score.label}">${score.label} Efficiency</span>
                </div>
            </div>
        `;
    });
}

// 5. Fetch AI Anomaly Detection
async function fetchAnalysis() {
    const res = await fetch(`${API_URL}/analyze`);
    const data = await res.json();
    
    const alertsContainer = document.getElementById('ai-alerts');
    alertsContainer.innerHTML = data.alerts.map(alert => `<p>${alert}</p>`).join('');
}

// 6. Handle Project Addition
document.getElementById('project-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
        name: document.getElementById('p-name').value,
        department: document.getElementById('p-dept').value,
        allocated: document.getElementById('p-alloc').value,
        output_unit: document.getElementById('p-unit').value
    };

    await fetch(`${API_URL}/add_project`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    document.getElementById('project-form').reset();
    initApp(); // Refresh Data
});

// 7. Handle Transaction Addition
document.getElementById('tx-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
        project_id: document.getElementById('tx-project').value,
        amount: document.getElementById('tx-amount').value,
        category: document.getElementById('tx-category').value,
        desc: document.getElementById('tx-desc').value
    };

    await fetch(`${API_URL}/add_transaction`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    document.getElementById('tx-form').reset();
    initApp(); // Refresh Data
});

// 8. Generate Automated Report (Simulated PDF summary)
function generateReport() {
    const box = document.getElementById('report-output');
    box.style.display = 'block';
    
    const date = new Date().toLocaleString();
    box.innerHTML = `
        <strong>SYSTEM AUDIT REPORT</strong>
        <br>Generated: ${date}
        <br>----------------------------------------
        <br>All subsystems synchronized.
        <br>Impact analysis evaluated successfully.
        <br>AI Anomaly Scanner passed. Review alerts above for exceptions.
        <br><br><em>Status: Ready for Management Review</em>
    `;
}
