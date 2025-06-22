# React frontend Dockerfile for Cloud Run
FROM node:18-alpine AS build

# Set working directory
WORKDIR /app

# Copy package files explicitly first
COPY frontend/package.json frontend/package-lock.json ./

# Verify package files were copied

# Install dependencies
RUN npm ci

# Copy remaining source files
COPY frontend/src ./src
COPY frontend/public ./public
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx config (override main config if intended)
COPY ./nginx/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
