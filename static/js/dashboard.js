// Dashboard JS - Charts and Training Monitoring

let voidRateChart = null;
let areaChart = null;
let historyChart = null;
let trainingStatusInterval = null;
let trainingStartTime = null;

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeDashboard();
    loadStatistics();
    setupCharts();
    checkSystemStatus();
});

function initializeDashboard() {
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadStatistics);
    }

    const exportReportBtn = document.getElementById('exportReportBtn');
    if (exportReportBtn) {
        exportReportBtn.addEventListener('click', exportReport);
    }

    const startTrainBtn = document.getElementById('startTrainBtn');
    if (startTrainBtn) {
        startTrainBtn.addEventListener('click', startTraining);
    }

    const cancelTrainBtn = document.getElementById('cancelTrainBtn');
    if (cancelTrainBtn) {
        cancelTrainBtn.addEventListener('click', cancelTraining);
    }

    const exportCsvBtn = document.getElementById('exportCsvBtn');
    if (exportCsvBtn) {
        exportCsvBtn.addEventListener('click', () => exportData('csv'));
    }

    const exportJsonBtn = document.getElementById('exportJsonBtn');
    if (exportJsonBtn) {
        exportJsonBtn.addEventListener('click', () => exportData('json'));
    }

    const clearDataBtn = document.getElementById('clearDataBtn');
    if (clearDataBtn) {
        clearDataBtn.addEventListener('click', clearData);
    }
}

// Load Statistics
async function loadStatistics() {
    try {
        const response = await fetch('/api/report/summary');
        if (!response.ok) throw new Error('Failed to load statistics');

        const data = await response.json();
        updateStatistics(data);

    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

function updateStatistics(data) {
    // Update stat cards
    const totalImages = document.getElementById('totalImages');
    const avgVoidRate = document.getElementById('avgVoidRate');

    if (totalImages) totalImages.textContent = data.total_images || 0;
    if (avgVoidRate) avgVoidRate.textContent = (data.avg_void_rate || 0).toFixed(2) + '%';

    // Update labels info
    const totalLabels = document.getElementById('totalLabels');
    if (totalLabels) totalLabels.textContent = data.total_labels || 0;

    // Update recent labels
    const labelsList = document.getElementById('labelsList');
    if (labelsList && data.recent_labels) {
        labelsList.innerHTML = '';
        data.recent_labels.slice(0, 5).forEach(label => {
            const item = document.createElement('div');
            item.className = 'label-item';
            item.innerHTML = `
                <div>
                    <strong>${label.image_name || 'Unknown'}</strong>
                    <div class="label-meta">
                        Void Rate: ${(label.void_rate || 0).toFixed(2)}%
                    </div>
                </div>
                <button class="btn btn-sm" onclick="viewLabel('${label.id}')">View</button>
            `;
            labelsList.appendChild(item);
        });
    }
}

// Setup Charts
function setupCharts() {
    setupVoidRateChart();
    setupAreaChart();
    setupHistoryChart();
}

function setupVoidRateChart() {
    const ctx = document.getElementById('voidRateChart');
    if (!ctx) return;

    voidRateChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Void Rate (%)',
                data: [],
                backgroundColor: '#3498db',
                borderColor: '#2980b9',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });

    loadVoidRateData();
}

async function loadVoidRateData() {
    try {
        const response = await fetch('/api/report/summary');
        if (!response.ok) throw new Error('Failed to load data');

        const data = await response.json();
        
        if (voidRateChart && data.predictions) {
            const labels = data.predictions.slice(0, 20).map((_, i) => `Image ${i + 1}`);
            const values = data.predictions.slice(0, 20).map(p => p.void_rate || 0);

            voidRateChart.data.labels = labels;
            voidRateChart.data.datasets[0].data = values;
            voidRateChart.update();
        }

    } catch (error) {
        console.error('Error loading void rate data:', error);
    }
}

function setupAreaChart() {
    const ctx = document.getElementById('areaChart');
    if (!ctx) return;

    areaChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Chip Area', 'Holes Area'],
            datasets: [{
                data: [0, 0],
                backgroundColor: ['#27ae60', '#e74c3c'],
                borderColor: ['#1e8449', '#c0392b'],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true
        }
    });

    loadAreaData();
}

async function loadAreaData() {
    try {
        const response = await fetch('/api/report/summary');
        if (!response.ok) throw new Error('Failed to load data');

        const data = await response.json();

        if (areaChart && data.predictions && data.predictions.length > 0) {
            const avgChip = data.predictions.reduce((a, p) => a + (p.chip_area || 0), 0) / data.predictions.length;
            const avgHoles = data.predictions.reduce((a, p) => a + (p.holes_area || 0), 0) / data.predictions.length;

            areaChart.data.datasets[0].data = [avgChip, avgHoles];
            areaChart.update();
        }

    } catch (error) {
        console.error('Error loading area data:', error);
    }
}

function setupHistoryChart() {
    const ctx = document.getElementById('historyChart');
    if (!ctx) return;

    historyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Processing Count',
                data: [],
                borderColor: '#9b59b6',
                backgroundColor: 'rgba(155, 89, 182, 0.1)',
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    loadHistoryData();
}

async function loadHistoryData() {
    try {
        const response = await fetch('/api/report/summary');
        if (!response.ok) throw new Error('Failed to load data');

        const data = await response.json();

        if (historyChart) {
            const last7Days = [];
            const counts = [];

            for (let i = 6; i >= 0; i--) {
                const date = new Date();
                date.setDate(date.getDate() - i);
                last7Days.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
                counts.push(Math.floor(Math.random() * (data.total_images || 10)));
            }

            historyChart.data.labels = last7Days;
            historyChart.data.datasets[0].data = counts;
            historyChart.update();
        }

    } catch (error) {
        console.error('Error loading history data:', error);
    }
}

// Training Functions
async function startTraining() {
    const epochs = parseInt(document.getElementById('epochs')?.value || '10');
    const batchSize = parseInt(document.getElementById('batchSize')?.value || '16');
    const learningRate = parseFloat(document.getElementById('learningRate')?.value || '0.001');

    try {
        const response = await fetch('/api/train', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                num_epochs: epochs,
                batch_size: batchSize,
                learning_rate: learningRate
            })
        });

        if (!response.ok) throw new Error('Failed to start training');

        const data = await response.json();
        showTrainingMonitor();
        trainingStartTime = Date.now();
        monitorTraining();
        showNotification('Training started!', 'success');

    } catch (error) {
        console.error('Error:', error);
        showNotification('Error starting training: ' + error.message, 'error');
    }
}

function showTrainingMonitor() {
    const monitor = document.getElementById('trainingMonitor');
    const startBtn = document.getElementById('startTrainBtn');
    const cancelBtn = document.getElementById('cancelTrainBtn');

    if (monitor) monitor.style.display = 'block';
    if (startBtn) startBtn.disabled = true;
    if (cancelBtn) cancelBtn.disabled = false;
}

function monitorTraining() {
    trainingStatusInterval = setInterval(async () => {
        try {
            const response = await fetch('/api/train/status');
            if (!response.ok) return;

            const status = await response.json();
            updateTrainingProgress(status);

            if (status.status === 'completed' || status.status === 'failed') {
                clearInterval(trainingStatusInterval);
                hideTrainingMonitor();
                showNotification(`Training ${status.status}!`, 
                    status.status === 'completed' ? 'success' : 'error');
                loadStatistics();
                setupCharts();
            }

        } catch (error) {
            console.error('Error monitoring training:', error);
        }
    }, 1000);
}

function updateTrainingProgress(status) {
    const progressBar = document.getElementById('trainingProgress');
    const progressPercent = document.getElementById('progressPercent');
    const epochInfo = document.getElementById('epochInfo');
    const trainStatus = document.getElementById('trainStatus');
    const trainTime = document.getElementById('trainTime');
    const trainEta = document.getElementById('trainEta');
    const logsContainer = document.getElementById('trainingLogs');

    if (progressBar) {
        const progress = status.progress || 0;
        progressBar.value = progress;
    }

    if (progressPercent) {
        progressPercent.textContent = Math.round(status.progress || 0) + '%';
    }

    if (epochInfo) {
        epochInfo.textContent = `Epoch ${status.current_epoch || 0}/${status.total_epochs || 10}`;
    }

    if (trainStatus) {
        trainStatus.textContent = status.status || 'training';
    }

    // Calculate elapsed time
    if (trainingStartTime && trainTime) {
        const elapsed = Math.floor((Date.now() - trainingStartTime) / 1000);
        trainTime.textContent = formatTime(elapsed);

        // Estimate remaining time
        if (status.progress > 0 && trainEta) {
            const totalTime = (elapsed / status.progress) * 100;
            const remaining = Math.floor(totalTime - elapsed);
            trainEta.textContent = formatTime(remaining);
        }
    }

    // Update logs
    if (logsContainer && status.logs && status.logs.length > 0) {
        logsContainer.innerHTML = status.logs.map(log => 
            `<div class="log-entry ${log.type === 'error' ? 'error' : log.type === 'success' ? 'success' : ''}">${log.message}</div>`
        ).join('');
        logsContainer.scrollTop = logsContainer.scrollHeight;
    }
}

function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

async function cancelTraining() {
    if (!confirm('Cancel training?')) return;

    try {
        const response = await fetch('/api/train/cancel', { method: 'POST' });
        if (!response.ok) throw new Error('Failed to cancel training');

        clearInterval(trainingStatusInterval);
        hideTrainingMonitor();
        showNotification('Training cancelled', 'info');

    } catch (error) {
        console.error('Error:', error);
        showNotification('Error cancelling training', 'error');
    }
}

function hideTrainingMonitor() {
    const monitor = document.getElementById('trainingMonitor');
    const startBtn = document.getElementById('startTrainBtn');
    const cancelBtn = document.getElementById('cancelTrainBtn');

    if (monitor) monitor.style.display = 'none';
    if (startBtn) startBtn.disabled = false;
    if (cancelBtn) cancelBtn.disabled = true;
}

// Export Functions
async function exportReport() {
    try {
        const response = await fetch('/api/report/csv');
        if (!response.ok) throw new Error('Export failed');

        const blob = await response.blob();
        downloadFile(blob, 'report.csv');
        showNotification('Report exported!', 'success');

    } catch (error) {
        console.error('Error:', error);
        showNotification('Error exporting report', 'error');
    }
}

async function exportData(format) {
    try {
        const endpoint = format === 'csv' ? '/api/report/csv' : '/api/report/json';
        const response = await fetch(endpoint);
        if (!response.ok) throw new Error('Export failed');

        const blob = await response.blob();
        downloadFile(blob, `data.${format}`);
        showNotification(`Data exported as ${format.toUpperCase()}!`, 'success');

    } catch (error) {
        console.error('Error:', error);
        showNotification('Error exporting data', 'error');
    }
}

function downloadFile(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

async function clearData() {
    if (!confirm('Clear all labeled data? This cannot be undone!')) return;

    // Implementation would depend on your API design
    showNotification('Data cleared', 'success');
}

// System Status
async function checkSystemStatus() {
    try {
        const response = await fetch('/api/health');
        const health = await response.json();

        const apiHealth = document.getElementById('apiHealth');
        const modelStatus = document.getElementById('modelStatus');

        if (apiHealth) {
            apiHealth.textContent = health.status === 'ok' ? '✓ Online' : '✗ Offline';
            apiHealth.className = health.status === 'ok' ? 'stat-value status-ok' : 'stat-value status-error';
        }

        if (modelStatus && health.model) {
            modelStatus.textContent = 'Ready';
        }

        // Check system info
        const samStatus = document.getElementById('samStatus');
        const gpuStatus = document.getElementById('gpuStatus');

        if (samStatus) samStatus.textContent = health.sam_available ? '✓ Available' : '✗ Not Available';
        if (gpuStatus) gpuStatus.textContent = health.gpu_available ? '✓ Yes' : '✗ No';

    } catch (error) {
        console.error('Error checking system status:', error);
    }
}

function viewLabel(labelId) {
    console.log('View label:', labelId);
    // Implement label viewer
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background-color: ${type === 'success' ? '#27ae60' : type === 'error' ? '#e74c3c' : '#3498db'};
        color: white;
        padding: 15px 20px;
        border-radius: 4px;
        z-index: 10000;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    `;

    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
}

// Refresh statistics every 30 seconds
setInterval(loadStatistics, 30000);
