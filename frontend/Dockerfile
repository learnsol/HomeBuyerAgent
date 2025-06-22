# Simple, reliable Dockerfile for React + nginx
FROM node:18-alpine AS build

WORKDIR /app

# Copy all files (ensures nothing is missed)
COPY . .

# Install dependencies and build
RUN npm install && npm run build

# Production image with nginx
FROM nginx:alpine

# Copy built app
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx config  
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
