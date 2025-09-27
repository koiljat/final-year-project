// localStorage utilities for managing summary history
const STORAGE_KEY = 'selene_summary_history';

export const summaryStorage = {
  // Save a new summary to localStorage
  saveSummary: (summaryData) => {
    try {
      const history = summaryStorage.getSummaries();
      const newSummary = {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        ...summaryData,
      };
      
      const updatedHistory = [newSummary, ...history];
      // Keep only the last 50 summaries to prevent storage bloat
      const limitedHistory = updatedHistory.slice(0, 50);
      
      localStorage.setItem(STORAGE_KEY, JSON.stringify(limitedHistory));
      return newSummary;
    } catch (error) {
      console.error('Failed to save summary to localStorage:', error);
      return null;
    }
  },

  // Get all summaries from localStorage
  getSummaries: () => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      return stored ? JSON.parse(stored) : [];
    } catch (error) {
      console.error('Failed to retrieve summaries from localStorage:', error);
      return [];
    }
  },

  // Delete a specific summary by ID
  deleteSummary: (id) => {
    try {
      const history = summaryStorage.getSummaries();
      const updatedHistory = history.filter(item => item.id !== id);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedHistory));
      return true;
    } catch (error) {
      console.error('Failed to delete summary:', error);
      return false;
    }
  },

  // Clear all summaries
  clearAll: () => {
    try {
      localStorage.removeItem(STORAGE_KEY);
      return true;
    } catch (error) {
      console.error('Failed to clear summary history:', error);
      return false;
    }
  },

  // Get summary count
  getCount: () => {
    return summaryStorage.getSummaries().length;
  }
};