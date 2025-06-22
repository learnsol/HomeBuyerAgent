# Multi-stage build for React frontend
FROM node:18-alpine as build

# Set working directory
WORKDIR /app

# Copy package files first for better Docker layer caching
COPY package*.json ./

# Install all dependencies (including dev dependencies needed for build)
RUN npm ci

# Copy source code
COPY . .

# Build the React app
RUN npm run build

# Production stage with nginx
FROM nginx:alpine

# Copy built React app from build stage
COPY --from=build /app/build /usr/share/nginx/html

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
