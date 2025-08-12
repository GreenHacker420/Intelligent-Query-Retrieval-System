// Intelligent Query Retrieval System - Frontend JavaScript
class DocumentAnalyzer {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000';
        this.currentResults = null;
        this.currentFile = null;
        this.uploadMethod = 'upload'; // 'upload' or 'url'
        this.init();
    }

    init() {
        this.bindEvents();
        this.setupSampleData();
    }

    bindEvents() {
        // Main analyze button
        document.getElementById('analyzeBtn').addEventListener('click', () => this.analyzeDocument());

        // Add question button
        document.getElementById('addQuestion').addEventListener('click', () => this.addQuestionField());

        // Export button
        document.getElementById('exportBtn').addEventListener('click', () => this.exportResults());

        // Retry button
        document.getElementById('retryBtn').addEventListener('click', () => this.hideError());

        // Upload method tabs
        document.querySelectorAll('.upload-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const method = e.target.getAttribute('data-method');
                this.switchUploadMethod(method);
            });
        });

        // File upload events
        this.setupFileUpload();

        // Sample URL buttons
        document.querySelectorAll('.sample-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const url = e.target.getAttribute('data-url');
                document.getElementById('documentUrl').value = url;
                this.showToast('Sample URL loaded', 'success');
            });
        });

        // Sample question buttons
        document.querySelectorAll('.sample-question-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.addSampleQuestion(e.target.textContent.trim());
            });
        });

        // Enter key support for questions
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.target.classList.contains('question-field')) {
                e.preventDefault();
                this.analyzeDocument();
            }
        });
    }

    setupSampleData() {
        // Add initial question field event listeners
        this.updateQuestionFieldEvents();
    }

    switchUploadMethod(method) {
        this.uploadMethod = method;

        // Update tab appearance
        document.querySelectorAll('.upload-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-method="${method}"]`).classList.add('active');

        // Show/hide sections
        if (method === 'upload') {
            document.getElementById('uploadSection').style.display = 'block';
            document.getElementById('urlSection').style.display = 'none';
        } else {
            document.getElementById('uploadSection').style.display = 'none';
            document.getElementById('urlSection').style.display = 'block';
        }

        // Clear current file/URL
        this.clearCurrentDocument();
    }

    setupFileUpload() {
        const dropZone = document.getElementById('fileDropZone');
        const fileInput = document.getElementById('fileInput');
        const browseBtn = document.getElementById('browseBtn');
        const removeFileBtn = document.getElementById('removeFileBtn');

        // Browse button click
        browseBtn.addEventListener('click', () => {
            fileInput.click();
        });

        // Drop zone click
        dropZone.addEventListener('click', () => {
            fileInput.click();
        });

        // File input change
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFileSelect(e.target.files[0]);
            }
        });

        // Remove file button
        removeFileBtn.addEventListener('click', () => {
            this.clearCurrentDocument();
        });

        // Drag and drop events
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('drag-over');
        });

        dropZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            dropZone.classList.remove('drag-over');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('drag-over');

            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileSelect(files[0]);
            }
        });
    }

    handleFileSelect(file) {
        // Validate file type
        const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword', 'text/plain'];
        const allowedExtensions = ['.pdf', '.docx', '.doc', '.txt'];

        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();

        if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
            this.showToast('Please select a PDF, DOCX, DOC, or TXT file', 'error');
            return;
        }

        // Validate file size (10MB limit)
        const maxSize = 10 * 1024 * 1024; // 10MB
        if (file.size > maxSize) {
            this.showToast('File size must be less than 10MB', 'error');
            return;
        }

        this.currentFile = file;
        this.displayFilePreview(file);
        this.showToast('File selected successfully', 'success');
    }

    displayFilePreview(file) {
        const preview = document.getElementById('filePreview');
        const fileName = document.getElementById('fileName');
        const fileSize = document.getElementById('fileSize');
        const fileIcon = preview.querySelector('.file-icon i');
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');

        // Set file info
        fileName.textContent = file.name;
        fileSize.textContent = this.formatFileSize(file.size);

        // Set file icon based on type
        const extension = file.name.split('.').pop().toLowerCase();
        fileIcon.className = this.getFileIcon(extension);
        preview.querySelector('.file-icon').className = `file-icon ${extension}`;

        // Show preview and hide drop zone
        document.getElementById('fileDropZone').style.display = 'none';
        preview.style.display = 'block';

        // Set progress
        progressFill.style.width = '100%';
        progressText.textContent = 'Ready to analyze';
    }

    clearCurrentDocument() {
        this.currentFile = null;

        // Reset file input
        document.getElementById('fileInput').value = '';

        // Reset URL input
        document.getElementById('documentUrl').value = '';

        // Hide file preview and show drop zone
        document.getElementById('filePreview').style.display = 'none';
        document.getElementById('fileDropZone').style.display = 'block';

        // Reset progress
        document.getElementById('progressFill').style.width = '0%';
        document.getElementById('progressText').textContent = 'Ready to analyze';
    }

    getFileIcon(extension) {
        switch (extension) {
            case 'pdf':
                return 'fas fa-file-pdf';
            case 'docx':
            case 'doc':
                return 'fas fa-file-word';
            case 'txt':
                return 'fas fa-file-alt';
            default:
                return 'fas fa-file';
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    addQuestionField() {
        const container = document.querySelector('.questions-container');
        const questionDiv = document.createElement('div');
        questionDiv.className = 'question-input';
        
        questionDiv.innerHTML = `
            <input 
                type="text" 
                placeholder="Enter your question about the document..."
                class="question-field"
            >
            <button type="button" class="remove-question">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        container.appendChild(questionDiv);
        this.updateQuestionFieldEvents();
        
        // Focus on the new input
        questionDiv.querySelector('.question-field').focus();
    }

    updateQuestionFieldEvents() {
        // Update remove button visibility and events
        const questionInputs = document.querySelectorAll('.question-input');
        
        questionInputs.forEach((input, index) => {
            const removeBtn = input.querySelector('.remove-question');
            
            if (questionInputs.length > 1) {
                removeBtn.style.display = 'flex';
                removeBtn.onclick = () => this.removeQuestionField(input);
            } else {
                removeBtn.style.display = 'none';
            }
        });
    }

    removeQuestionField(questionDiv) {
        questionDiv.remove();
        this.updateQuestionFieldEvents();
    }

    addSampleQuestion(questionText) {
        // Find first empty question field or add new one
        const questionFields = document.querySelectorAll('.question-field');
        let emptyField = null;
        
        for (let field of questionFields) {
            if (!field.value.trim()) {
                emptyField = field;
                break;
            }
        }
        
        if (!emptyField) {
            this.addQuestionField();
            const newFields = document.querySelectorAll('.question-field');
            emptyField = newFields[newFields.length - 1];
        }
        
        emptyField.value = questionText;
        this.showToast('Sample question added', 'success');
    }

    validateForm() {
        const questionFields = document.querySelectorAll('.question-field');

        // Validate document input based on method
        let documentSource = null;

        if (this.uploadMethod === 'upload') {
            if (!this.currentFile) {
                this.showToast('Please select a document file', 'error');
                return false;
            }
            documentSource = { type: 'file', data: this.currentFile };
        } else {
            const documentUrl = document.getElementById('documentUrl').value.trim();

            if (!documentUrl) {
                this.showToast('Please enter a document URL', 'error');
                return false;
            }

            try {
                new URL(documentUrl);
            } catch {
                this.showToast('Please enter a valid URL', 'error');
                return false;
            }

            documentSource = { type: 'url', data: documentUrl };
        }

        // Validate questions
        const questions = Array.from(questionFields)
            .map(field => field.value.trim())
            .filter(q => q.length > 0);

        if (questions.length === 0) {
            this.showToast('Please enter at least one question', 'error');
            return false;
        }

        if (questions.length > 10) {
            this.showToast('Maximum 10 questions allowed', 'error');
            return false;
        }

        return { documentSource, questions };
    }

    async analyzeDocument() {
        const formData = this.validateForm();
        if (!formData) return;

        this.setLoading(true);
        this.hideError();
        this.hideResults();

        try {
            let documentUrl;

            if (formData.documentSource.type === 'file') {
                // For file uploads, we need to upload the file first
                documentUrl = await this.uploadFile(formData.documentSource.data);
            } else {
                // For URL input, use the URL directly
                documentUrl = formData.documentSource.data;
            }

            const response = await fetch(`${this.apiBaseUrl}/api/v1/hackrx/run`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    documents: documentUrl,
                    questions: formData.questions
                })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
            }

            const results = await response.json();
            this.currentResults = results;
            this.displayResults(results);
            this.showToast('Analysis completed successfully!', 'success');

        } catch (error) {
            console.error('Analysis error:', error);
            this.showError(error.message);
            this.showToast('Analysis failed. Please try again.', 'error');
        } finally {
            this.setLoading(false);
        }
    }

    async uploadFile(file) {
        try {
            // Update progress
            this.updateUploadProgress(0, 'Uploading...');

            // Create FormData for file upload
            const formData = new FormData();
            formData.append('file', file);

            // Upload file to backend
            const response = await fetch(`${this.apiBaseUrl}/api/v1/hackrx/upload`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Upload failed: HTTP ${response.status}`);
            }

            const result = await response.json();

            // Update progress
            this.updateUploadProgress(100, 'Upload complete');

            this.showToast('File uploaded successfully', 'success');
            return result.file_url;

        } catch (error) {
            this.updateUploadProgress(0, 'Upload failed');
            throw new Error(`File upload failed: ${error.message}`);
        }
    }

    updateUploadProgress(percentage, text) {
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');

        if (progressFill) {
            progressFill.style.width = `${percentage}%`;
        }

        if (progressText) {
            progressText.textContent = text;
        }
    }

    setLoading(isLoading) {
        const btn = document.getElementById('analyzeBtn');
        const btnText = btn.querySelector('.btn-text');
        const spinner = btn.querySelector('.loading-spinner');
        
        btn.disabled = isLoading;
        
        if (isLoading) {
            btnText.style.display = 'none';
            spinner.style.display = 'block';
        } else {
            btnText.style.display = 'block';
            spinner.style.display = 'none';
        }
    }

    displayResults(results) {
        this.displayProcessingSummary(results.processing_summary);
        this.displayAnswers(results.answers);
        this.showResults();
    }

    displayProcessingSummary(summary) {
        const container = document.getElementById('processingSummary');
        
        container.innerHTML = `
            <div class="summary-grid">
                <div class="summary-item">
                    <span class="summary-value">${summary.total_questions}</span>
                    <span class="summary-label">Total Questions</span>
                </div>
                <div class="summary-item">
                    <span class="summary-value">${summary.successful_responses}</span>
                    <span class="summary-label">Successful Responses</span>
                </div>
                <div class="summary-item">
                    <span class="summary-value">${summary.total_processing_time}</span>
                    <span class="summary-label">Processing Time</span>
                </div>
                <div class="summary-item">
                    <span class="summary-value">${summary.document_pages_processed || 'N/A'}</span>
                    <span class="summary-label">Pages Processed</span>
                </div>
            </div>
        `;
    }

    displayAnswers(answers) {
        const container = document.getElementById('resultsContainer');
        
        container.innerHTML = answers.map((answer, index) => `
            <div class="answer-card">
                <div class="question-text">
                    <i class="fas fa-question-circle question-icon"></i>
                    <span>${this.escapeHtml(answer.question)}</span>
                </div>
                
                <div class="coverage-status ${answer.isCovered ? 'coverage-covered' : 'coverage-not-covered'}">
                    <i class="fas ${answer.isCovered ? 'fa-check-circle' : 'fa-times-circle'}"></i>
                    <span>${answer.isCovered ? 'Covered' : 'Not Covered'}</span>
                </div>
                
                <div class="confidence-score">
                    <div class="confidence-label">Confidence Score</div>
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: ${(answer.confidence_score * 100).toFixed(1)}%"></div>
                    </div>
                    <div class="confidence-value">${(answer.confidence_score * 100).toFixed(1)}%</div>
                </div>
                
                ${answer.conditions && answer.conditions.length > 0 ? `
                    <div class="conditions-section">
                        <div class="section-title">
                            <i class="fas fa-list-ul"></i>
                            <span>Conditions & Requirements</span>
                        </div>
                        <ul class="conditions-list">
                            ${answer.conditions.map(condition => `
                                <li>${this.escapeHtml(condition)}</li>
                            `).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                <div class="rationale-section">
                    <div class="section-title">
                        <i class="fas fa-lightbulb"></i>
                        <span>Rationale</span>
                    </div>
                    <div class="rationale-text">${this.escapeHtml(answer.rationale)}</div>
                </div>
                
                ${answer.clause_reference && (answer.clause_reference.page || answer.clause_reference.clause_title) ? `
                    <div class="reference-section">
                        <div class="section-title">
                            <i class="fas fa-bookmark"></i>
                            <span>Source Reference</span>
                        </div>
                        <div class="reference-info">
                            ${answer.clause_reference.page ? `Page: ${answer.clause_reference.page}` : ''}
                            ${answer.clause_reference.page && answer.clause_reference.clause_title ? ' | ' : ''}
                            ${answer.clause_reference.clause_title ? `Section: ${this.escapeHtml(answer.clause_reference.clause_title)}` : ''}
                        </div>
                    </div>
                ` : ''}
            </div>
        `).join('');
    }

    showResults() {
        document.getElementById('resultsSection').style.display = 'block';
        document.getElementById('resultsSection').scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }

    hideResults() {
        document.getElementById('resultsSection').style.display = 'none';
    }

    showError(message) {
        document.getElementById('errorMessage').textContent = message;
        document.getElementById('errorSection').style.display = 'block';
        document.getElementById('errorSection').scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }

    hideError() {
        document.getElementById('errorSection').style.display = 'none';
    }

    exportResults() {
        if (!this.currentResults) {
            this.showToast('No results to export', 'warning');
            return;
        }
        
        const dataStr = JSON.stringify(this.currentResults, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `document-analysis-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        
        this.showToast('Results exported successfully', 'success');
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        container.appendChild(toast);
        
        // Trigger animation
        setTimeout(() => toast.classList.add('show'), 100);
        
        // Remove after 3 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => container.removeChild(toast), 300);
        }, 3000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new DocumentAnalyzer();
});
