// src/api/lexicareApi.js

import axios from "axios";

const API_BASE = "http://localhost:8006/api";

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
