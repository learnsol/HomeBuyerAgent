# React frontend Dockerfile for Cloud Run
FROM node:18-alpine AS build

# Set working directory
WORKDIR /app

# Copy all files (this ensures we get everything)
COPY . .

# Debug: Show what files we have
RUN echo "=== Files in /app ===" && ls -la

# Install dependencies
RUN npm ci

# Build the app
RUN npm run build

# Debug: Show build output
RUN echo "=== Build output ===" && ls -la build/

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
