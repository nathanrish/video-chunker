# Multi-stage build for production
FROM node:18-alpine as builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./
COPY shell/package*.json ./shell/
COPY modules/shared/package*.json ./modules/shared/
COPY modules/video-processing/package*.json ./modules/video-processing/
COPY modules/transcription/package*.json ./modules/transcription/
COPY modules/meeting-minutes/package*.json ./modules/meeting-minutes/

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built application
COPY --from=builder /app/shell/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
