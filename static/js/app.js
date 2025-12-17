// GovInsight Query UI - JavaScript

// API Configuration
const API_BASE_URL = 'http://127.0.0.1:8000';

// DOM Elements
let queryInput, submitBtn, resultsSection, answerCard, sourcesContainer;
let loadingState, errorState, emptyState;
let queryStartTime;

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initializeElements();
    attachEventListeners();
    checkBackendHealth();
});

// Initialize DOM element references
function initializeElements() {
    queryInput = document.getElementById('queryInput');
    submitBtn = document.getElementById('submitBtn');
    resultsSection = document.getElementById('resultsSection');
    answerCard = document.getElementById('answerCard');
    sourcesContainer = document.getElementById('sourcesContainer');
    loadingState = document.getElementById('loadingState');
    errorState = document.getElementById('errorState');
    emptyState = document.getElementById('emptyState');
}

// Attach event listeners
function attachEventListeners() {
    // Submit button click
    submitBtn.addEventListener('click', handleSubmit);

    // Enter key in query input
    queryInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    });

    // Quick query buttons
    document.querySelectorAll('.quick-query-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            queryInput.value = btn.getAttribute('data-query');
            queryInput.focus();
            // Auto-submit after a short delay
            setTimeout(() => handleSubmit(), 150);
        });
    });
}

// Check backend health
async function checkBackendHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            console.log('✓ Backend is healthy');
        } else {
            showError('Backend is not responding properly. Please check if the server is running.');
        }
    } catch (error) {
        console.warn('Backend health check failed:', error);
        // Don't show error immediately - backend might start later
    }
}

// Handle query submission
async function handleSubmit() {
    const query = queryInput.value.trim();

    if (!query) {
        showError('Please enter a query');
        return;
    }

    // Show loading state
    showLoading();

    // Build request payload
    const payload = {
        query: query,
        temperature: 0.1,
        filters: {
            top_k: 5
        }
    };

    try {
        // Make API request
        const response = await fetch(`${API_BASE_URL}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to get response from server');
        }

        const data = await response.json();

        // Display results
        displayResults(data);

    } catch (error) {
        console.error('Query error:', error);

        // Handle specific errors
        if (error.message.includes('Vector store not found')) {
            showError('⚠️ PDFs have not been indexed yet. Please run: python app/rag_pipeline.py --index');
        } else if (error.message.includes('Failed to fetch')) {
            showError('❌ Cannot connect to backend. Please ensure the server is running at http://127.0.0.1:8000');
        } else {
            showError(`Error: ${error.message}`);
        }
    }
}

// Show loading state
function showLoading() {
    resultsSection.classList.remove('hidden');
    loadingState.classList.remove('hidden');
    answerCard.classList.add('hidden');
    errorState.classList.add('hidden');
    emptyState.classList.add('hidden');

    // Disable submit button and show loading state
    submitBtn.disabled = true;
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoading = submitBtn.querySelector('.btn-loading');
    if (btnText) btnText.classList.add('hidden');
    if (btnLoading) btnLoading.classList.remove('hidden');
    
    // Record start time
    queryStartTime = Date.now();
}

// Display results
function displayResults(data) {
    // Calculate response time
    const responseTime = ((Date.now() - queryStartTime) / 1000).toFixed(1);
    
    // Hide loading, show answer
    loadingState.classList.add('hidden');
    answerCard.classList.remove('hidden');
    errorState.classList.add('hidden');
    emptyState.classList.add('hidden');
    
    // Reset button state
    submitBtn.disabled = false;
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoading = submitBtn.querySelector('.btn-loading');
    if (btnText) btnText.classList.remove('hidden');
    if (btnLoading) btnLoading.classList.add('hidden');

    // Parse markdown-style answer for better display
    const formattedAnswer = formatAnswer(data.answer);

    // Display answer
    const answerContent = answerCard.querySelector('.answer-content');
    answerContent.innerHTML = formattedAnswer;

    // Display response time
    const responseTimeEl = document.getElementById('responseTime');
    if (responseTimeEl) {
        responseTimeEl.textContent = `⚡ ${responseTime}s`;
    }

    // Display sources
    displaySources(data.sources, data.num_chunks_used);

    // Update results count
    const resultsCount = document.querySelector('.results-count');
    if (resultsCount) {
        resultsCount.textContent = `Using ${data.num_chunks_used} source${data.num_chunks_used !== 1 ? 's' : ''}`;
    }
}

// Format answer with markdown-like styling
function formatAnswer(answer) {
    // Convert markdown tables to HTML
    let formatted = answer;

    // Handle tables
    const tableRegex = /\|(.+)\|[\r\n]+\|[-:\s|]+\|[\r\n]+((?:\|.+\|[\r\n]*)+)/g;
    formatted = formatted.replace(tableRegex, (match, headers, rows) => {
        const headerCells = headers.split('|').filter(cell => cell.trim()).map(cell =>
            `<th>${escapeHtml(cell.trim())}</th>`
        ).join('');

        const rowCells = rows.trim().split('\n').map(row => {
            const cells = row.split('|').filter(cell => cell.trim()).map(cell =>
                `<td>${escapeHtml(cell.trim())}</td>`
            ).join('');
            return `<tr>${cells}</tr>`;
        }).join('');

        return `<table><thead><tr>${headerCells}</tr></thead><tbody>${rowCells}</tbody></table>`;
    });

    // Convert bold text
    formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

    // Convert line breaks to paragraphs
    formatted = formatted.split('\n\n').map(para =>
        para.trim() ? `<p>${para.replace(/\n/g, '<br>')}</p>` : ''
    ).join('');

    return formatted;
}

// Display sources with download buttons
function displaySources(sources, count) {
    if (!sources || sources.length === 0) {
        sourcesContainer.innerHTML = '<p class="text-muted">No sources available</p>';
        return;
    }

    // Remove duplicates based on year, ministry, page, and document_name
    const uniqueSources = [];
    const seen = new Set();

    sources.forEach(source => {
        const key = `${source.year}-${source.ministry}-${source.page_number}-${source.document_name || ''}`;
        if (!seen.has(key)) {
            seen.add(key);
            uniqueSources.push(source);
        }
    });

    const sourcesHTML = uniqueSources.map((source, index) => {
        const hasDocument = source.document_name && source.document_name.trim() !== '';
        const displayDocName = hasDocument 
            ? (source.document_name.length > 35 
                ? source.document_name.substring(0, 32) + '...' 
                : source.document_name)
            : `${source.ministry} - ${source.year}`;
        
        return `
        <div class="source-item ${hasDocument ? 'source-clickable' : ''}" 
             ${hasDocument ? `data-document="${escapeHtml(source.document_name)}" data-page="${source.page_number}"` : ''}
             title="${hasDocument ? 'Click to download: ' + source.document_name : 'Document not available for download'}">
            <div class="source-title">
                📄 ${escapeHtml(displayDocName)}
                ${hasDocument ? '<span class="download-icon">⬇️</span>' : ''}
            </div>
            <div class="source-meta">
                <span class="source-meta-item">📖 Page ${escapeHtml(String(source.page_number))}</span>
                <span class="source-meta-item">📅 ${escapeHtml(source.year)}</span>
                <span class="source-meta-item">🏛️ ${escapeHtml(source.ministry)}</span>
            </div>
        </div>
        `;
    }).join('');

    sourcesContainer.innerHTML = `
        <div class="sources-title">📚 Sources (${uniqueSources.length}) - Click to download</div>
        <div class="sources-grid">${sourcesHTML}</div>
    `;
    
    // Attach click handlers for download
    document.querySelectorAll('.source-item.source-clickable').forEach(item => {
        item.addEventListener('click', function() {
            const docName = this.getAttribute('data-document');
            const pageNum = this.getAttribute('data-page');
            if (docName) {
                downloadSourcePDF(docName, pageNum);
            }
        });
    });
}

// Download source PDF
function downloadSourcePDF(documentName, pageNumber) {
    const downloadUrl = `${API_BASE_URL}/download/${encodeURIComponent(documentName)}`;
    console.log(`Downloading: ${documentName} (Page ${pageNumber})`);
    
    // Open in new tab or trigger download
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = documentName;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Show error message
function showError(message) {
    resultsSection.classList.remove('hidden');
    loadingState.classList.add('hidden');
    answerCard.classList.add('hidden');
    errorState.classList.remove('hidden');
    emptyState.classList.add('hidden');
    
    // Reset button state
    submitBtn.disabled = false;
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoading = submitBtn.querySelector('.btn-loading');
    if (btnText) btnText.classList.remove('hidden');
    if (btnLoading) btnLoading.classList.add('hidden');

    const errorTitle = errorState.querySelector('.error-title');
    const errorDetails = errorState.querySelector('.error-details');
    
    if (errorTitle) {
        errorTitle.textContent = message;
    }
    if (errorDetails) {
        if (message.includes('not indexed')) {
            errorDetails.textContent = 'Run: python app/rag_pipeline.py --index';
        } else if (message.includes('Cannot connect')) {
            errorDetails.textContent = 'Make sure the server is running on port 8000';
        } else {
            errorDetails.textContent = '';
        }
    }
}

// Utility: Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Auto-resize textarea
if (queryInput) {
    queryInput.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 300) + 'px';
    });
}
