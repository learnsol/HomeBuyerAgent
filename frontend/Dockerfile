# React frontend Dockerfile for Cloud Run
FROM node:18-alpine AS build

# Set working directory
WORKDIR /app

# Debug: List files to see what's available
RUN echo "=== Listing root directory ===" && ls -la /

# Copy package files explicitly
COPY package.json ./
COPY package-lock.json ./

# Debug: Verify files were copied
RUN echo "=== Files in /app ===" && ls -la

# Install dependencies
RUN npm ci

# Copy source code
COPY src ./src
COPY public ./public

# Debug: Verify all files
RUN echo "=== All files in /app ===" && ls -la

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
