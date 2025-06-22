# React frontend Dockerfile for Cloud Run
FROM node:18-alpine AS build

# Set working directory
WORKDIR /app

# Copy all files at once (most reliable approach)
COPY . .

# Debug: Check if package files exist
RUN ls -la package* || echo "No package files found"

# Install dependencies (use npm ci if lock file exists, otherwise npm install)
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi

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
