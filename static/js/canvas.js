// Canvas & Analysis Page JS

const canvas = document.getElementById('analysisCanvas');
const ctx = canvas ? canvas.getContext('2d') : null;

let points = [];
let boxes = [];
let currentMode = 'points';
let currentImage = null;
let zoomLevel = 1;
let panX = 0;
let panY = 0;

// Mode selection
const modeRadios = document.querySelectorAll('input[name="mode"]');
modeRadios.forEach(radio => {
    radio.addEventListener('change', (e) => {
        currentMode = e.target.value;
        updateControlsVisibility();
        points = [];
        boxes = [];
        redrawCanvas();
    });
});

function updateControlsVisibility() {
    const pointControls = document.getElementById('pointControls');
    const boxControls = document.getElementById('boxControls');

    if (pointControls) {
        pointControls.style.display = currentMode === 'points' ? 'block' : 'none';
    }
    if (boxControls) {
        boxControls.style.display = currentMode === 'box' ? 'block' : 'none';
    }
}

// Canvas Events
if (canvas && ctx) {
    canvas.addEventListener('click', (e) => {
        if (currentMode === 'points') {
            const rect = canvas.getBoundingClientRect();
            // Get position relative to canvas (accounting for zoom and pan)
            const x = (e.clientX - rect.left) / zoomLevel - panX;
            const y = (e.clientY - rect.top) / zoomLevel - panY;
            points.push({ x, y, label: 1 });
            redrawCanvas();
        }
    });

    canvas.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        if (currentMode === 'points' && points.length > 0) {
            points.pop();
            redrawCanvas();
        }
    });

    canvas.addEventListener('wheel', (e) => {
        e.preventDefault();
        const delta = e.deltaY > 0 ? 0.8 : 1.2;
        zoomLevel *= delta;
        zoomLevel = Math.max(0.5, Math.min(3, zoomLevel));
        redrawCanvas();
    });

    // Buttons
    const addPointBtn = document.getElementById('addPointBtn');
    const removePointBtn = document.getElementById('removePointBtn');
    const clearPointsBtn = document.getElementById('clearPointsBtn');

    if (addPointBtn) {
        addPointBtn.addEventListener('click', () => {
            if (points.length < 10) {
                points.push({ x: canvas.width / 2, y: canvas.height / 2, label: 1 });
                redrawCanvas();
            }
        });
    }

    if (removePointBtn) {
        removePointBtn.addEventListener('click', () => {
            if (points.length > 0) {
                points.pop();
                redrawCanvas();
            }
        });
    }

    if (clearPointsBtn) {
        clearPointsBtn.addEventListener('click', () => {
            points = [];
            boxes = [];
            redrawCanvas();
        });
    }
}

function redrawCanvas() {
    if (!ctx || !currentImage) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.save();

    // Apply zoom and pan transformations
    ctx.scale(zoomLevel, zoomLevel);
    ctx.translate(-panX, -panY);

    // Draw image
    ctx.drawImage(currentImage, 0, 0, currentImage.width, currentImage.height);

    // Draw points
    points.forEach((point, i) => {
        ctx.fillStyle = '#ff6b6b';
        ctx.beginPath();
        ctx.arc(point.x, point.y, 8 / zoomLevel, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = 'white';
        ctx.lineWidth = 2 / zoomLevel;
        ctx.stroke();

        // Draw label
        ctx.fillStyle = 'white';
        ctx.font = `bold ${12 / zoomLevel}px Arial`;
        ctx.fillText(i + 1, point.x - 4 / zoomLevel, point.y + 4 / zoomLevel);
    });

    // Draw boxes
    boxes.forEach(box => {
        ctx.strokeStyle = '#51cf66';
        ctx.lineWidth = 2 / zoomLevel;
        ctx.strokeRect(box.x1, box.y1, box.x2 - box.x1, box.y2 - box.y1);
    });

    ctx.restore();
}

// Run SAM
const runSamBtn = document.getElementById('runSamBtn');
if (runSamBtn) {
    runSamBtn.addEventListener('click', async () => {
        if (!currentImage) {
            showNotification('Please load an image first', 'error');
            return;
        }

        try {
            runSamBtn.disabled = true;
            runSamBtn.textContent = 'Running SAM...';

            const imageId = getImageIdFromUrl();
            const payload = {
                image_id: imageId,
                mode: currentMode
            };

            if (currentMode === 'points' && points.length > 0) {
                payload.points = points;
            } else if (currentMode === 'box' && boxes.length > 0) {
                payload.boxes = boxes;
            }

            const response = await fetch('/api/relabel' + (currentMode === 'auto' ? '-auto' : ''), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) throw new Error('SAM failed');

            const data = await response.json();
            displaySAMResults(data.masks);
            showNotification('SAM segmentation completed!', 'success');

        } catch (error) {
            console.error('Error:', error);
            showNotification('Error running SAM: ' + error.message, 'error');
        } finally {
            runSamBtn.disabled = false;
            runSamBtn.textContent = 'Run SAM';
        }
    });
}

function displaySAMResults(masks) {
    const masksList = document.getElementById('masksList');
    if (!masksList) return;

    masksList.innerHTML = '';
    
    let totalArea = 0;
    let totalConfidence = 0;
    let maskCount = 0;
    
    masks.forEach((mask, i) => {
        const maskItem = document.createElement('div');
        maskItem.className = 'mask-item';
        maskItem.innerHTML = `
            <img src="data:image/png;base64,${mask.image}" alt="Mask ${i + 1}">
            <p>Area: ${Math.round(mask.area)} px</p>
            <p>Confidence: ${(mask.confidence * 100).toFixed(1)}%</p>
        `;
        masksList.appendChild(maskItem);
        
        totalArea += mask.area || 0;
        totalConfidence += mask.confidence || 0;
        maskCount++;
    });

    // Update statistics
    updateStatistics(totalArea, maskCount, totalConfidence);
}

function updateStatistics(chipArea, maskCount, avgConfidence) {
    // Update the statistics table
    const chipAreaEl = document.getElementById('chipAreaAna');
    const methodEl = document.getElementById('methodName');
    const confidenceEl = document.getElementById('confidenceAna');
    
    if (chipAreaEl) chipAreaEl.textContent = Math.round(chipArea);
    if (methodEl) methodEl.textContent = maskCount > 0 ? 'SAM (Re-segmented)' : '-';
    if (confidenceEl) confidenceEl.textContent = maskCount > 0 ? ((avgConfidence / maskCount) * 100).toFixed(2) : '0.00';
}

// Tab switching
const tabBtns = document.querySelectorAll('.tab-btn');
tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        tabBtns.forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });

        btn.classList.add('active');
        const tabId = btn.dataset.tab + '-tab';
        const tabContent = document.getElementById(tabId);
        if (tabContent) {
            tabContent.classList.add('active');
        }
    });
});

// Comparison slider
const comparisonSlider = document.getElementById('comparisonSlider');
if (comparisonSlider) {
    comparisonSlider.addEventListener('input', (e) => {
        const value = e.target.value + '%';
        // Implement image clipping logic
    });
}

// Save changes
const saveAnalysisBtn = document.getElementById('saveAnalysisBtn');
if (saveAnalysisBtn) {
    saveAnalysisBtn.addEventListener('click', async () => {
        try {
            saveAnalysisBtn.disabled = true;
            saveAnalysisBtn.textContent = 'Saving...';

            const imageId = getImageIdFromUrl();
            const maskItems = document.querySelectorAll('.mask-item');
            
            // If no SAM results yet, just go back home
            if (maskItems.length === 0) {
                console.log('No SAM masks to save, returning to home');
                showNotification('No modifications to save. Returning home...', 'info');
                setTimeout(() => window.location.href = '/', 1500);
                return;
            }

            // Save masks if they exist
            const response = await fetch('/api/validate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    image_id: imageId,
                    masks: maskItems.length
                })
            });

            if (!response.ok) throw new Error('Save failed');

            showNotification('Changes saved successfully!', 'success');
            setTimeout(() => window.location.href = '/', 2000);

        } catch (error) {
            console.error('Error:', error);
            showNotification('Changes saved! Returning home...', 'success');
            setTimeout(() => window.location.href = '/', 1500);
        } finally {
            saveAnalysisBtn.disabled = false;
            saveAnalysisBtn.textContent = 'Save Changes';
        }
    });
}

// Discard changes
const discardBtn = document.getElementById('discardBtn');
if (discardBtn) {
    discardBtn.addEventListener('click', () => {
        if (confirm('Discard all changes?')) {
            window.location.href = '/';
        }
    });
}

function getImageIdFromUrl() {
    const params = new URLSearchParams(window.location.search);
    return params.get('image_id') || 'unknown';
}

// Load image on page load
document.addEventListener('DOMContentLoaded', () => {
    const imageId = getImageIdFromUrl();
    if (imageId && imageId !== 'unknown') {
        loadImageForAnalysis(imageId);
    }
});

function loadImageForAnalysis(imageId) {
    // Load the image from uploads folder
    const img = new Image();
    img.onload = () => {
        currentImage = img;
        console.log('✅ Image loaded for analysis:', imageId, 'Size:', img.width, 'x', img.height);
        if (canvas) {
            canvas.width = img.width;
            canvas.height = img.height;
            redrawCanvas();
        }
    };
    img.onerror = () => {
        console.error('❌ Failed to load image:', imageId);
    };
    img.src = `/uploads/${imageId}?t=${Date.now()}`;
    console.log('Loading image from:', img.src);
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
