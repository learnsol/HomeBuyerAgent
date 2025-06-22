# React frontend Dockerfile for Cloud Run
FROM node:20-alpine AS build

# Set working directory
WORKDIR /app

# Copy package files explicitly first
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy remaining source files
COPY src ./src
COPY public ./public

# Set the API URL environment variable for build time
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=$REACT_APP_API_URL

# Build the React app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
