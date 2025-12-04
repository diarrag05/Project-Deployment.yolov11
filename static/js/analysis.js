// Analysis-specific JS
// This extends canvas.js for the analysis page

document.addEventListener('DOMContentLoaded', () => {
    loadAnalysisData();
});

async function loadAnalysisData() {
    const imageId = new URLSearchParams(window.location.search).get('image_id');
    
    if (!imageId) {
        showNotification('No image selected', 'error');
        setTimeout(() => window.location.href = '/', 2000);
        return;
    }

    try {
        // Load predictions and segmentation results
        // This would fetch from your server
        
        // For now, set up the UI
        setupAnalysisTabs();
        
    } catch (error) {
        console.error('Error loading analysis data:', error);
        showNotification('Error loading image data', 'error');
    }
}

function setupAnalysisTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active from all
            tabBtns.forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            // Add active to clicked
            btn.classList.add('active');
            const tabId = btn.dataset.tab + '-tab';
            const content = document.getElementById(tabId);
            if (content) content.classList.add('active');
        });
    });
}
