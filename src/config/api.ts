// Central API configuration
// In development: uses localhost
// In production: uses your Render backend URL

const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";

export const API = {
  scan: `${API_BASE_URL}/api/scan`,
  stressTest: `${API_BASE_URL}/api/stress-test`,
  health: `${API_BASE_URL}/api/health`,
  scanners: `${API_BASE_URL}/api/scanners`,
};

export default API;
