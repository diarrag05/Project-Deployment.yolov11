// Main App JS - Shared functionality across pages

const API_BASE = '/api';
let selectedFile = null;
let predictionResult = null;
let currentBlobUrl = null; // Track blob URL to revoke it
let lastImageId = null; // Track the last image_id from the API response

// Image Upload
const uploadArea = document.getElementById('uploadArea');
const imageInput = document.getElementById('imageInput');
const previewContainer = document.getElementById('previewContainer');
const preview = document.getElementById('preview');
const predictBtn = document.getElementById('predictBtn');
const resetBtn = document.getElementById('resetBtn');
const confidenceInput = document.getElementById('confidence');
const confidenceValue = document.getElementById('confidenceValue');

if (uploadArea && imageInput) {
    uploadArea.addEventListener('click', () => imageInput.click());

    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.backgroundColor = '#e8f0ff';
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.backgroundColor = '';
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.backgroundColor = '';
        const files = e.dataTransfer.files;
        if (files.length) {
            handleFileSelect(files[0]);
        }
    });

    imageInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFileSelect(e.target.files[0]);
        }
    });

    function handleFileSelect(file) {
        // Cleanup old blob URL
        if (currentBlobUrl) {
            URL.revokeObjectURL(currentBlobUrl);
        }
        
        selectedFile = file;
        predictionResult = null;
        
        const reader = new FileReader();
        reader.onload = (e) => {
            currentBlobUrl = e.target.result;
            preview.src = currentBlobUrl;
            previewContainer.style.display = 'block';
            predictBtn.disabled = false;
            uploadArea.style.display = 'none';
            // Clear previous results
            document.getElementById('resultsSection').style.display = 'none';
        };
        reader.readAsDataURL(file);
    }

    if (predictBtn) {
        predictBtn.addEventListener('click', () => {
            if (selectedFile) {
                runInference(selectedFile);
            }
        });
    }

    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            selectedFile = null;
            predictionResult = null;
            imageInput.value = '';
            previewContainer.style.display = 'none';
            uploadArea.style.display = 'block';
            predictBtn.disabled = true;
            document.getElementById('resultsSection').style.display = 'none';
            
            // Cleanup blob URLs
            if (currentBlobUrl) {
                URL.revokeObjectURL(currentBlobUrl);
                currentBlobUrl = null;
            }
        });
    }
}

// Confidence slider
if (confidenceInput) {
    confidenceInput.addEventListener('change', (e) => {
        confidenceValue.textContent = parseFloat(e.target.value).toFixed(2);
    });
}

// Run Inference
async function runInference(file) {
    const formData = new FormData();
    formData.append('image', file);
    formData.append('confidence', confidenceInput?.value || 0.5);

    try {
        predictBtn.disabled = true;
        predictBtn.textContent = 'Processing...';

        const response = await fetch(`${API_BASE}/predict`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Inference failed');
        }

        const data = await response.json();
        console.log('API Response:', data);
        predictionResult = data.result;
        displayResults(data.result, data);  // Pass full API response with mask_url
        showNotification('Inference completed successfully!', 'success');

    } catch (error) {
        console.error('Error:', error);
        showNotification('Error running inference: ' + error.message, 'error');
    } finally {
        predictBtn.disabled = false;
        predictBtn.textContent = 'Run Inference';
    }
}

// Display Results
function displayResults(result, apiResponse) {
    const resultsSection = document.getElementById('resultsSection');
    
    // Save the image_id for later use (e.g., for SAM relabeling)
    if (apiResponse?.image_id) {
        lastImageId = apiResponse.image_id;
        console.log('💾 Saved image_id:', lastImageId);
    }
    
    // Display original image from uploaded file
    if (document.getElementById('originalImage')) {
        document.getElementById('originalImage').src = currentBlobUrl;
    }
    
    // Display segmentation mask - use mask_url from API response
    if (document.getElementById('maskImage')) {
        const maskUrl = apiResponse?.mask_url || result?.mask_url;
        console.log('🎯 Mask URL from response:', maskUrl);
        console.log('🎯 Full API Response:', apiResponse);
        if (maskUrl) {
            // Generated mask with contours from server
            const fullUrl = maskUrl.startsWith('http') ? maskUrl : maskUrl;
            const urlWithCache = fullUrl + '?t=' + new Date().getTime();
            console.log('🎯 Setting mask image src to:', urlWithCache);
            const imgElement = document.getElementById('maskImage');
            
            // Add error handler
            imgElement.onerror = function() {
                console.error('❌ Failed to load mask image from:', urlWithCache);
                this.src = currentBlobUrl; // Fallback to original image
                console.log('   Fallback to original image');
            };
            
            // Add load handler
            imgElement.onload = function() {
                console.log('✅ Mask image loaded successfully from:', urlWithCache);
            };
            
            imgElement.src = urlWithCache;
            console.log('✓ Displaying mask from:', fullUrl);
        } else {
            // No detections - show original image
            console.log('⚠️  No mask_url provided - showing original image');
            document.getElementById('maskImage').src = currentBlobUrl;
        }
    }

    // Update statistics
    if (document.getElementById('chipArea')) {
        document.getElementById('chipArea').textContent = Math.round(result.chip_area || 0);
    }
    if (document.getElementById('holesArea')) {
        document.getElementById('holesArea').textContent = Math.round(result.holes_area || 0);
    }
    if (document.getElementById('voidRate')) {
        document.getElementById('voidRate').textContent = (result.void_rate || 0).toFixed(2);
    }
    if (document.getElementById('chipPercentage')) {
        document.getElementById('chipPercentage').textContent = (result.chip_percentage || 0).toFixed(2);
    }
    if (document.getElementById('holesPercentage')) {
        document.getElementById('holesPercentage').textContent = (result.holes_percentage || 0).toFixed(2);
    }
    if (document.getElementById('confidence')) {
        document.getElementById('confidence').textContent = (result.confidence || 0).toFixed(3);
    }

    if (resultsSection) {
        resultsSection.style.display = 'block';
    }
}

// Relabel with SAM
const relabelBtn = document.getElementById('relabelBtn');
if (relabelBtn) {
    relabelBtn.addEventListener('click', () => {
        if (lastImageId) {
            console.log('🔄 Opening analysis for:', lastImageId);
            window.location.href = `/analysis?image_id=${lastImageId}`;
        } else {
            alert('Please run inference first');
        }
    });
}

// Validate Labels
const validateBtn = document.getElementById('validateBtn');
if (validateBtn) {
    validateBtn.addEventListener('click', async () => {
        if (!predictionResult) return;

        try {
            validateBtn.disabled = true;
            validateBtn.textContent = 'Saving...';

            // Check if we have prediction results and image_id
            if (!predictionResult || !lastImageId) {
                showNotification('No inference results to save', 'warning');
                validateBtn.disabled = false;
                validateBtn.textContent = 'Save Labels';
                return;
            }

            // Send label save request with image_id and statistics
            const response = await fetch(`${API_BASE}/validate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    image_id: lastImageId,
                    masks: [
                        {
                            label: 'chips',
                            area: predictionResult.chip_area || 0,
                            count: predictionResult.chip_count || 0
                        },
                        {
                            label: 'holes',
                            area: predictionResult.holes_area || 0,
                            count: predictionResult.holes_count || 0
                        }
                    ],
                    void_rate: predictionResult.void_rate || 0,
                    stats: predictionResult
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Validation failed');
            }

            const data = await response.json();
            showNotification(`✅ Labels saved successfully!`, 'success');
            console.log('Labels saved:', data);

        } catch (error) {
            console.error('Error:', error);
            showNotification('Error saving labels: ' + error.message, 'error');
        } finally {
            validateBtn.disabled = false;
            validateBtn.textContent = 'Save Labels';
        }
    });
}

// Export Results
const exportBtn = document.getElementById('exportBtn');
if (exportBtn) {
    exportBtn.addEventListener('click', async () => {
        if (!predictionResult) {
            showNotification('No inference results to export', 'warning');
            return;
        }

        try {
            exportBtn.disabled = true;
            exportBtn.textContent = 'Exporting...';

            // Create CSV content from current prediction
            const csvContent = [
                ['Image Analysis Report', new Date().toLocaleString()],
                [],
                ['Metric', 'Value'],
                ['Chip Area (pixels)', predictionResult.chip_area || 0],
                ['Holes Area (pixels)', predictionResult.holes_area || 0],
                ['Void Rate (%)', predictionResult.void_rate || 0],
                ['Chip %', predictionResult.chip_percent || 0],
                ['Holes %', predictionResult.holes_percent || 0],
                ['Image ID', lastImageId || 'unknown']
            ];

            // Convert to CSV string
            const csvString = csvContent
                .map(row => row.map(cell => `"${cell}"`).join(','))
                .join('\n');

            // Create blob and download
            const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            const url = URL.createObjectURL(blob);
            
            link.setAttribute('href', url);
            link.setAttribute('download', `analysis_${new Date().getTime()}.csv`);
            link.style.visibility = 'hidden';
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            showNotification('✅ Report exported successfully!', 'success');

        } catch (error) {
            console.error('Export error:', error);
            showNotification('Error exporting report: ' + error.message, 'error');
        } finally {
            exportBtn.disabled = false;
            exportBtn.textContent = 'Export';
        }
    });
}

// Batch Processing
const batchSelectBtn = document.getElementById('batchSelectBtn');
const batchInput = document.getElementById('batchInput');
const batchProcessBtn = document.getElementById('batchProcessBtn');
let batchFiles = [];

if (batchSelectBtn && batchInput) {
    batchSelectBtn.addEventListener('click', () => batchInput.click());

    batchInput.addEventListener('change', (e) => {
        batchFiles = Array.from(e.target.files);
        batchProcessBtn.disabled = batchFiles.length === 0;
    });

    if (batchProcessBtn) {
        batchProcessBtn.addEventListener('click', () => {
            if (batchFiles.length > 0) {
                processBatch(batchFiles);
            }
        });
    }
}

async function processBatch(files) {
    const progress = document.getElementById('batchProgress');
    const progressBar = document.getElementById('batchProgressBar');
    const progressText = document.getElementById('batchProgressText');

    if (progress) progress.style.display = 'block';

    for (let i = 0; i < files.length; i++) {
        try {
            const formData = new FormData();
            formData.append('image', files[i]);
            formData.append('confidence', confidenceInput?.value || 0.5);

            await fetch(`${API_BASE}/predict`, {
                method: 'POST',
                body: formData
            });

            const percent = Math.round((i + 1) / files.length * 100);
            if (progressBar) progressBar.value = percent;
            if (progressText) progressText.textContent = percent + '%';

        } catch (error) {
            console.error('Error processing file:', files[i].name, error);
        }
    }

    showNotification('Batch processing completed!', 'success');
    if (progress) progress.style.display = 'none';
}

// Utility Functions
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
        animation: slideIn 0.3s ease-out;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Check API Health
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();
        showNotification(`API Status: ${data.status}`, 'success');
    } catch (error) {
        showNotification('API is offline', 'error');
    }
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
