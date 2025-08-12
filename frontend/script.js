// Intelligent Query Retrieval System - Frontend JavaScript
class DocumentAnalyzer {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000';
        this.currentResults = null;
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
        const documentUrl = document.getElementById('documentUrl').value.trim();
        const questionFields = document.querySelectorAll('.question-field');
        
        // Validate URL
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
        
        return { documentUrl, questions };
    }

    async analyzeDocument() {
        const formData = this.validateForm();
        if (!formData) return;
        
        this.setLoading(true);
        this.hideError();
        this.hideResults();
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/v1/hackrx/run`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    documents: formData.documentUrl,
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
