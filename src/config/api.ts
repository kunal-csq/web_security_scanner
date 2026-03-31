// Central API configuration

const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";

export const API = {
  // Scan
  scan: `${API_BASE_URL}/api/scan`,
  stressTest: `${API_BASE_URL}/api/stress-test`,
  health: `${API_BASE_URL}/api/health`,
  scanners: `${API_BASE_URL}/api/scanners`,

  // Auth
  register: `${API_BASE_URL}/api/auth/register`,
  login: `${API_BASE_URL}/api/auth/login`,
  me: `${API_BASE_URL}/api/auth/me`,

  // History
  history: `${API_BASE_URL}/api/history`,
  historyDetail: (id: number) => `${API_BASE_URL}/api/history/${id}`,
};

export default API;
