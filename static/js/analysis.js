// Analysis-specific JS
// This extends canvas.js for the analysis page

document.addEventListener('DOMContentLoaded', () => {
    loadAnalysisData();
});

async function loadAnalysisData() {
    const imageId = new URLSearchParams(window.location.search).get('image_id');
    
    if (!imageId) {
        console.log('No image_id in URL, trying to get from template variable');
        // Try to get from template variable if available
        const templateImageId = document.getElementById('imageIdData')?.getAttribute('data-image-id');
        if (!templateImageId) {
            console.error('No image selected');
            setTimeout(() => window.location.href = '/', 2000);
            return;
        }
        loadImageToCanvas(templateImageId);
    } else {
        loadImageToCanvas(imageId);
    }
}

function loadImageToCanvas(imageId) {
    console.log('Loading image:', imageId);
    
    // Load original image
    const originalImg = document.getElementById('originalResult');
    if (originalImg) {
        originalImg.src = `/uploads/${imageId}?t=${Date.now()}`;
        originalImg.onerror = () => console.error('Failed to load original image');
        originalImg.onload = () => {
            console.log('✅ Original image loaded');
            // Draw to canvas
            const canvas = document.getElementById('analysisCanvas');
            if (canvas) {
                const ctx = canvas.getContext('2d');
                const img = new Image();
                img.onload = () => {
                    canvas.width = img.width;
                    canvas.height = img.height;
                    ctx.drawImage(img, 0, 0);
                    console.log('✅ Canvas updated');
                };
                img.src = originalImg.src;
            }
        };
    }
    
    // Load YOLO result (mask)
    const yoloImg = document.getElementById('yoloResult');
    if (yoloImg) {
        const maskUrl = `/uploads/${imageId.replace('.jpg', '').replace('.png', '')}_mask.png`;
        yoloImg.src = maskUrl + `?t=${Date.now()}`;
        yoloImg.onerror = () => console.warn('No YOLO mask found:', maskUrl);
        yoloImg.onload = () => console.log('✅ YOLO mask loaded');
    }
    
    // Set up comparison images
    const yoloCompare = document.getElementById('yoloCompare');
    const samCompare = document.getElementById('samCompare');
    if (yoloCompare) yoloCompare.src = `/uploads/${imageId}?t=${Date.now()}`;
    if (samCompare) samCompare.src = `/uploads/${imageId}?t=${Date.now()}`;
    
    // Set up UI
    setupAnalysisTabs();
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
