# Frontend Architecture

## Overview

This frontend application follows a micro frontend architecture pattern, providing a scalable and maintainable solution for the Video-to-Meeting-Minutes system.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Browser                                  │
└─────────────────┬───────────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────────┐
│                    Shell Application                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  React Router + Material-UI Theme + Layout              │   │
│  │  - Navigation                                           │   │
│  │  - Routing                                              │   │
│  │  - Global State Management                              │   │
│  │  - API Service Layer                                    │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────┬───────────────────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
┌───▼───┐    ┌───▼───┐    ┌───▼───┐
│ Video │    │Trans- │    │Meeting│
│Process│    │cription│    │Minutes│
│Module │    │Module │    │Module │
└───────┘    └───────┘    └───────┘
    │             │             │
    └─────────────┼─────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────────┐
│                    Shared Module                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  - StatusChip, LoadingSpinner, ErrorBoundary           │   │
│  │  - FileUpload, DataTable                               │   │
│  │  - Date/File Utilities                                 │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────┬───────────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────────┐
│                    Backend API                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  - Meetings CRUD                                       │   │
│  │  - Transcription Management                            │   │
│  │  - Meeting Minutes Generation                          │   │
│  │  - File Upload/Download                                │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Micro Frontend Modules

### 1. Shell Application (`shell/`)
**Purpose**: Main application container that orchestrates all micro frontends

**Key Features**:
- Centralized routing and navigation
- Global state management
- API service layer
- Layout and theming
- Error boundaries

**Components**:
- `Layout.js`: Main application layout with navigation
- `Dashboard.js`: Overview dashboard with statistics
- `App.js`: Main application component with routing

**Dependencies**:
- React Router for navigation
- Material-UI for theming and components
- API service for backend communication

### 2. Video Processing Module (`modules/video-processing/`)
**Purpose**: Handle video upload and processing workflow

**Key Features**:
- Drag & drop file upload
- Progress tracking
- Meeting details form
- Processing pipeline steps
- Format validation

**Components**:
- `VideoProcessingModule.js`: Main module component
- Stepper-based workflow
- File validation and upload

**Dependencies**:
- Shared components for UI consistency
- API service for backend communication

### 3. Transcription Module (`modules/transcription/`)
**Purpose**: Display and manage video transcriptions

**Key Features**:
- Transcription text display
- Segments table with search
- Timeline navigation
- Download functionality
- Search and filter

**Components**:
- `TranscriptionModule.js`: Main module component
- Data table for segments
- Search and filter functionality

**Dependencies**:
- Shared components for UI consistency
- API service for data fetching

### 4. Meeting Minutes Module (`modules/meeting-minutes/`)
**Purpose**: Generate and display structured meeting minutes

**Key Features**:
- Structured minutes display
- Artifact management (epics, action items, risks)
- Tabbed interface
- Export functionality
- Sprint integration

**Components**:
- `MeetingMinutesModule.js`: Main module component
- Tabbed interface for different sections
- Export functionality

**Dependencies**:
- Shared components for UI consistency
- API service for data fetching

### 5. Shared Module (`modules/shared/`)
**Purpose**: Reusable components and utilities

**Key Features**:
- Common UI components
- Utility functions
- Type definitions
- Shared constants

**Components**:
- `StatusChip.js`: Status indicator component
- `LoadingSpinner.js`: Loading state component
- `ErrorBoundary.js`: Error handling component
- `FileUpload.js`: File upload component
- `DataTable.js`: Advanced data grid

**Utilities**:
- `dateUtils.js`: Date formatting utilities
- `fileUtils.js`: File handling utilities

## Data Flow

### 1. User Uploads Video
```
User → Video Processing Module → API Service → Backend → Processing Pipeline
```

### 2. View Transcription
```
User → Transcription Module → API Service → Backend → Display Transcription
```

### 3. Generate Meeting Minutes
```
User → Meeting Minutes Module → API Service → Backend → Display Minutes
```

### 4. Download Files
```
User → Any Module → API Service → Backend → File Download
```

## State Management

### Local State
Each module manages its own local state using React hooks:
- `useState` for component state
- `useEffect` for side effects
- Custom hooks for complex logic

### Global State
The shell application manages global state:
- User preferences
- Authentication state
- Global notifications
- Theme settings

### API State
API service manages:
- Request/response caching
- Loading states
- Error handling
- Retry logic

## Build System

### Development
- Each module runs on its own port
- Hot reloading for development
- Source maps for debugging
- Concurrent development servers

### Production
- Rollup for module bundling
- Tree shaking for optimization
- Code splitting for performance
- Docker containerization

## Deployment

### Docker
- Multi-stage build process
- Nginx for serving static files
- Environment configuration
- Health checks

### Environment Variables
- `REACT_APP_API_URL`: Backend API URL
- `REACT_APP_WS_URL`: WebSocket URL
- `NODE_ENV`: Environment mode

## Security

### Client-Side
- Content Security Policy headers
- XSS protection
- CSRF protection
- Input validation

### API Communication
- HTTPS in production
- Request/response validation
- Error handling
- Rate limiting

## Performance

### Optimization
- Code splitting
- Lazy loading
- Image optimization
- Bundle analysis

### Caching
- Browser caching
- API response caching
- Static asset caching
- Service worker (future)

## Testing

### Unit Tests
- Jest for testing framework
- React Testing Library for components
- Mock API responses
- Coverage reporting

### Integration Tests
- Module integration testing
- API integration testing
- User flow testing
- E2E testing (future)

## Monitoring

### Error Tracking
- Error boundaries
- Console logging
- Error reporting service (future)

### Performance Monitoring
- Bundle size analysis
- Runtime performance
- User experience metrics

## Future Enhancements

### Planned Features
- Real-time updates via WebSocket
- Offline support with service workers
- Advanced search and filtering
- User authentication and authorization
- Multi-language support
- Dark mode theme

### Scalability
- Module federation
- CDN integration
- Microservice communication
- Horizontal scaling
