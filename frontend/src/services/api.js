import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const analyzeArticles = async (keyword, articleCount, timeRangeYears) => {
  try {
    const response = await api.post('/api/analyze_articles', {
      keyword,
      article_count: articleCount,
      time_range_years: timeRangeYears || null,
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};

export default api;


