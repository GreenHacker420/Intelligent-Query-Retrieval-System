# 🌐 Frontend - Intelligent Query Retrieval System

A modern, responsive web interface for the AI-powered document analysis system.

## 🎯 Features

- **📱 Responsive Design**: Works on desktop, tablet, and mobile devices
- **🎨 Modern UI**: Clean, professional interface with smooth animations
- **📄 Document Upload**: Easy URL input with validation and sample documents
- **❓ Multi-Question Support**: Add multiple questions with sample suggestions
- **📊 Rich Results Display**: Comprehensive analysis results with visual indicators
- **💾 Export Functionality**: Download results as JSON
- **🔔 Toast Notifications**: Real-time feedback for user actions
- **⚡ Real-time API Integration**: Connects to FastAPI backend

## 🚀 Quick Start

### Option 1: Python Server (Recommended)

1. **Start the backend** (in main project directory):
   ```bash
   source venv/bin/activate
   python main.py
   ```

2. **Start the frontend server**:
   ```bash
   cd frontend
   python3 server.py
   ```

3. **Open your browser**: http://localhost:3000

### Option 2: Direct File Access

1. **Start the backend** (in main project directory):
   ```bash
   source venv/bin/activate
   python main.py
   ```

2. **Open the frontend**:
   - Simply open `frontend/index.html` in your browser
   - Or use any local web server (Live Server extension in VS Code, etc.)

## 📋 Usage Guide

### 1. Document Input
- Enter a direct URL to your PDF or DOCX document
- Use the sample document buttons for testing
- URL validation ensures proper format

### 2. Questions
- Add one or more questions about your document
- Use sample question buttons for common queries
- Support for up to 10 questions per analysis

### 3. Analysis
- Click "Analyze Document" to start processing
- Real-time loading indicators show progress
- Results appear automatically when complete

### 4. Results
- **Coverage Status**: Visual indicators for covered/not covered
- **Confidence Scores**: Progress bars showing AI confidence
- **Conditions**: List of requirements and limitations
- **Rationale**: Detailed explanations for decisions
- **Source References**: Page numbers and clause titles
- **Export**: Download results as JSON file

## 🎨 UI Components

### Header
- Branding and system title
- Subtitle with event information

### Input Section
- Document URL input with validation
- Dynamic question management
- Sample data for quick testing
- Form validation and error handling

### Results Section
- Processing summary with key metrics
- Individual answer cards with rich formatting
- Visual confidence indicators
- Structured condition lists
- Source reference information

### Interactive Elements
- Toast notifications for feedback
- Loading states during processing
- Error handling with retry options
- Responsive design for all devices

## 🔧 Technical Details

### Frontend Stack
- **HTML5**: Semantic markup with accessibility features
- **CSS3**: Modern styling with flexbox/grid, animations, and responsive design
- **Vanilla JavaScript**: No frameworks, pure ES6+ for maximum compatibility
- **Font Awesome**: Icons for enhanced visual experience
- **Google Fonts**: Inter font family for professional typography

### API Integration
- **Endpoint**: `POST http://localhost:8000/api/v1/hackrx/run`
- **CORS**: Configured for cross-origin requests
- **Error Handling**: Comprehensive error catching and user feedback
- **Response Processing**: Structured display of complex API responses

### Browser Compatibility
- **Modern Browsers**: Chrome 80+, Firefox 75+, Safari 13+, Edge 80+
- **Mobile Support**: iOS Safari, Chrome Mobile, Samsung Internet
- **Progressive Enhancement**: Graceful degradation for older browsers

## 📱 Responsive Breakpoints

- **Desktop**: 1200px+ (Full layout with sidebar)
- **Tablet**: 768px - 1199px (Stacked layout)
- **Mobile**: 480px - 767px (Single column)
- **Small Mobile**: <480px (Compact layout)

## 🎯 Sample Data

### Sample Documents
- Dummy PDF for basic testing
- Example documents with various content types

### Sample Questions
- Insurance coverage queries
- Policy condition questions
- Exclusion and limitation inquiries
- General document analysis questions

## 🔍 Features in Detail

### Form Validation
- URL format validation
- Required field checking
- Question count limits (1-10)
- Real-time feedback

### Loading States
- Button loading animations
- Spinner indicators
- Disabled states during processing
- Progress feedback

### Error Handling
- Network error detection
- API error message display
- Retry functionality
- User-friendly error messages

### Results Display
- Color-coded coverage status
- Animated confidence bars
- Structured condition lists
- Expandable rationale sections
- Source reference highlighting

## 🚀 Deployment Options

### Development
```bash
# Using Python server
python3 frontend/server.py

# Using Node.js (if available)
npx http-server frontend -p 3000

# Using PHP (if available)
php -S localhost:3000 -t frontend
```

### Production
- Deploy to any static hosting service
- Configure CORS on the backend for your domain
- Update API endpoint in `script.js` if needed

## 🔧 Customization

### Styling
- Modify `styles.css` for visual changes
- CSS custom properties for easy theming
- Responsive design utilities

### Functionality
- Update `script.js` for behavior changes
- Modular class-based architecture
- Easy to extend with new features

### Configuration
- API endpoint in `script.js` (line 4)
- Sample data in HTML and JavaScript
- Toast notification timing and styles

## 📊 Performance

- **Lightweight**: ~50KB total (HTML + CSS + JS)
- **Fast Loading**: Optimized assets and minimal dependencies
- **Efficient**: Vanilla JavaScript for maximum performance
- **Responsive**: Smooth animations and interactions

## 🛠️ Development

### File Structure
```
frontend/
├── index.html          # Main HTML file
├── styles.css          # All CSS styles
├── script.js           # JavaScript functionality
├── server.py           # Python development server
└── README.md           # This file
```

### Adding Features
1. Update HTML structure in `index.html`
2. Add styles in `styles.css`
3. Implement functionality in `script.js`
4. Test with the development server

## 🎉 Ready to Use!

The frontend is now fully functional and ready to use with your Intelligent Query Retrieval System. Simply start both the backend and frontend servers, and you'll have a complete document analysis solution with a professional web interface.

**Happy analyzing! 🚀**
