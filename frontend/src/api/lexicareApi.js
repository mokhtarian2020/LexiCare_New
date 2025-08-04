// src/api/lexicareApi.js

import axios from "axios";

// Determine API base URL - in production, use relative URL for flexibility
const API_BASE = process.env.NODE_ENV === "production" 
  ? "/api"  // Use relative URL in production
  : "http://localhost:8006/api";  // Direct URL in development

export const analyzeDocuments = async (formData) => {
  const response = await axios.post(`${API_BASE}/analyze/`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
};

export const submitFeedback = async (feedback) => {
  const response = await axios.post(`${API_BASE}/feedback/`, feedback);
  return response.data;
};
