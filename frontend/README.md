# Video Meeting Minutes - Micro Frontend

A modern React.js micro frontend application built with Material-UI for the Video-to-Meeting-Minutes system. This application provides a comprehensive interface for managing video processing, transcription, and meeting minutes generation.

## 🏗️ Architecture

This frontend follows a micro frontend architecture with the following structure:

### Shell Application
- **Main Shell** (`shell/`): The main application shell that orchestrates all micro frontends
- **Routing & Navigation**: Centralized routing and navigation management
- **Shared Services**: API services and common utilities

### Micro Frontend Modules
- **Video Processing** (`modules/video-processing/`): Video upload and processing interface
- **Transcription** (`modules/transcription/`): Transcription viewing and management
- **Meeting Minutes** (`modules/meeting-minutes/`): Meeting minutes generation and viewing
- **Shared Components** (`modules/shared/`): Reusable UI components and utilities

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- npm 8+

### Installation

1. **Install all dependencies:**
   ```bash
   cd frontend
   npm run install:all
   ```

2. **Start development servers:**
   ```bash
   npm run dev
   ```

   This will start:
   - Shell application on `http://localhost:3000`
   - Video processing module on `http://localhost:3001`
   - Transcription module on `http://localhost:3002`
   - Meeting minutes module on `http://localhost:3003`

3. **Build for production:**
   ```bash
   npm run build
   ```

## 📁 Project Structure

```
frontend/
├── shell/                          # Main shell application
│   ├── public/
│   ├── src/
│   │   ├── components/            # Shell-specific components
│   │   ├── pages/                # Main application pages
│   │   ├── services/             # API services
│   │   └── App.js               # Main application component
│   └── package.json
├── modules/
│   ├── shared/                   # Shared components and utilities
│   │   ├── src/
│   │   │   ├── components/      # Reusable UI components
│   │   │   ├── utils/          # Utility functions
│   │   │   └── index.js        # Module exports
│   │   └── package.json
│   ├── video-processing/         # Video processing micro frontend
│   │   ├── src/
│   │   │   ├── VideoProcessingModule.js
│   │   │   └── index.js
│   │   └── package.json
│   ├── transcription/            # Transcription micro frontend
│   │   ├── src/
│   │   │   ├── TranscriptionModule.js
│   │   │   └── index.js
│   │   └── package.json
│   └── meeting-minutes/          # Meeting minutes micro frontend
│       ├── src/
│       │   ├── MeetingMinutesModule.js
│       │   └── index.js
│       └── package.json
└── package.json                  # Root package.json with workspaces
```

## 🎯 Features

### Video Processing Module
- **Drag & Drop Upload**: Intuitive file upload interface
- **Progress Tracking**: Real-time upload and processing progress
- **Format Validation**: Automatic video format validation
- **Meeting Details**: Form for meeting title, date, and language selection
- **Processing Pipeline**: Step-by-step processing workflow

### Transcription Module
- **Transcription Viewer**: Complete transcription text display
- **Segments Table**: Searchable and sortable segments
- **Search Functionality**: Full-text search within transcriptions
- **Download Options**: Export transcriptions in various formats
- **Timeline Navigation**: Jump to specific time segments

### Meeting Minutes Module
- **Structured Minutes**: Professional meeting minutes display
- **Artifact Management**: Epics, action items, risks, dependencies
- **Tabbed Interface**: Organized view of different sections
- **Export Options**: Download in DOCX and HTML formats
- **Sprint Integration**: Agile/TPM specific features

### Shared Components
- **StatusChip**: Consistent status indicators
- **LoadingSpinner**: Loading states
- **ErrorBoundary**: Error handling
- **FileUpload**: Reusable file upload component
- **DataTable**: Advanced data grid with actions

## 🔧 Development

### Adding New Micro Frontends

1. **Create module directory:**
   ```bash
   mkdir modules/new-module
   cd modules/new-module
   ```

2. **Initialize package.json:**
   ```bash
   npm init -y
   ```

3. **Add dependencies:**
   ```bash
   npm install react react-dom @mui/material @emotion/react @emotion/styled
   npm install --save-dev @types/react @types/react-dom typescript rollup
   ```

4. **Create module structure:**
   ```
   src/
   ├── NewModule.js
   └── index.js
   ```

5. **Add to root package.json workspaces:**
   ```json
   "workspaces": [
     "shell",
     "modules/*",
     "modules/new-module"
   ]
   ```

### Building Modules

Each module can be built independently:

```bash
cd modules/shared
npm run build

cd modules/video-processing
npm run build
```

### Development Mode

For development, each module runs on its own port:

- Shell: `http://localhost:3000`
- Video Processing: `http://localhost:3001`
- Transcription: `http://localhost:3002`
- Meeting Minutes: `http://localhost:3003`

## 🎨 UI/UX Features

### Material-UI Integration
- **Consistent Design**: Material Design 3 principles
- **Responsive Layout**: Mobile-first responsive design
- **Theme Customization**: Centralized theme management
- **Accessibility**: WCAG 2.1 compliance

### User Experience
- **Intuitive Navigation**: Clear navigation structure
- **Real-time Feedback**: Loading states and progress indicators
- **Error Handling**: Comprehensive error boundaries
- **Responsive Design**: Works on all device sizes

## 🔌 API Integration

The frontend integrates with the backend API service:

- **Base URL**: `http://localhost:5004` (configurable via environment)
- **RESTful API**: Full CRUD operations for meetings, transcriptions, and minutes
- **File Downloads**: Direct file download support
- **Real-time Updates**: WebSocket support for live updates

### Environment Configuration

Create a `.env` file in the shell directory:

```env
REACT_APP_API_URL=http://localhost:5004
REACT_APP_WS_URL=ws://localhost:5004/ws
```

## 📦 Deployment

### Production Build

```bash
npm run build
```

### Docker Deployment

```dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/shell/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 🧪 Testing

### Running Tests

```bash
# Test shell application
cd shell
npm test

# Test all modules
npm run test:all
```

### Test Coverage

```bash
npm run test:coverage
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the API documentation
3. Open an issue on GitHub

## 🔄 Migration Guide

### From Monolithic to Micro Frontend

If migrating from a monolithic React app:

1. **Extract Components**: Move reusable components to shared module
2. **Create Modules**: Split features into separate micro frontends
3. **Update Imports**: Change import paths to use module references
4. **Configure Build**: Set up rollup/webpack for each module
5. **Update Shell**: Integrate modules into shell application

### Version Compatibility

- React 18+
- Material-UI 5+
- Node.js 18+
- Modern browsers (Chrome, Firefox, Safari, Edge)
