# React frontend Dockerfile for Cloud Run
FROM node:18-alpine AS build

# Set working directory
WORKDIR /app

# Copy all files at once (most reliable approach)
COPY . .

# Install dependencies
RUN npm ci

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
