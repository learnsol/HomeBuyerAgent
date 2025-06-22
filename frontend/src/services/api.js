import axios from 'axios';

// API base URL - will use proxy in development, environment variable in production
const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes timeout for long-running analysis
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.status, error.message);
    
    if (error.response?.status === 500) {
      throw new Error('Server error occurred. Please try again later.');
    } else if (error.response?.status === 404) {
      throw new Error('Service not found. Please check your connection.');
    } else if (error.code === 'NETWORK_ERROR') {
      throw new Error('Network error. Please check your internet connection.');
    } else if (error.code === 'ECONNABORTED') {
      throw new Error('Request timed out. The analysis is taking longer than expected.');
    }
    
    throw error;
  }
);

/**
 * Main API function to analyze home buying request
 * @param {Object} searchData - User search criteria and preferences
 * @returns {Promise<Object>} Analysis results with recommendations
 */
export const analyzeHomeBuyingRequest = async (searchData) => {
  try {
    console.log('Sending search data:', searchData);
    
    const response = await apiClient.post('/analyze', searchData);
    
    if (response.data.error) {
      throw new Error(response.data.error);
    }
    
    return response.data;
  } catch (error) {
    console.error('Home buying analysis error:', error);
    
    // Re-throw with user-friendly message
    if (error.response?.data?.error) {
      throw new Error(error.response.data.error);
    }
    
    throw error;
  }
};

/**
 * Health check endpoint
 * @returns {Promise<Object>} Health status
 */
export const healthCheck = async () => {
  try {
    const response = await apiClient.get('/health');
    return response.data;
  } catch (error) {
    console.error('Health check error:', error);
    throw error;
  }
};

export default apiClient;
