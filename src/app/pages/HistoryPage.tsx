import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Clock, Globe, ArrowLeft, ExternalLink, Loader2, AlertTriangle } from 'lucide-react';
import { motion } from 'framer-motion';
import API from '../../config/api';
import { isLoggedIn, authHeader } from '../../config/auth';

interface ScanRecord {
  id: number;
  url: string;
  score: number;
  grade: string;
  severity_counts: { critical?: number; high?: number; medium?: number; low?: number };
  depth: string;
  created_at: string;
}

const gradeColor: Record<string, string> = {
  'A+': '#10B981', A: '#10B981',
  'B+': '#34D399', B: '#34D399',
  C: '#F59E0B',
  D: '#EF4444',
  F: '#DC2626',
};

export function HistoryPage() {
  const navigate = useNavigate();
  const [history, setHistory] = useState<ScanRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isLoggedIn()) {
      navigate('/login');
      return;
    }

    const fetchHistory = async () => {
      try {
        const res = await fetch(API.history, {
          headers: { ...authHeader() },
        });
        const data = await res.json();

        if (!res.ok) {
          setError(data.error || 'Failed to load history');
        } else {
          setHistory(data.history || []);
        }
      } catch {
        setError('Network error');
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [navigate]);

  const viewScan = async (id: number) => {
    try {
      const res = await fetch(API.historyDetail(id), {
        headers: { ...authHeader() },
      });
      const data = await res.json();
      if (res.ok) {
        localStorage.setItem('scanResults', JSON.stringify(data));
        navigate('/results');
      }
    } catch {
      // ignore
    }
  };

  return (
    <div className="min-h-screen bg-cyber-dark cyber-grid-bg relative">
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-cyber-purple/[0.03] rounded-full blur-[150px] pointer-events-none" />

      <div className="relative z-10 py-8 px-6">
        <div className="max-w-[1000px] mx-auto">

          {/* Header */}
          <motion.button
            initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}
            onClick={() => navigate('/scan')}
            className="flex items-center gap-2 text-[13px] text-cyber-text-muted hover:text-cyber-purple transition-colors mb-6"
          >
            <ArrowLeft className="w-4 h-4" /> Back to Scan
          </motion.button>

          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
            <div className="flex items-center gap-3 mb-2">
              <Clock className="w-6 h-6 text-cyber-purple" />
              <h1 className="text-[28px] font-bold text-white">Scan History</h1>
            </div>
            <p className="text-[14px] text-cyber-text-muted">Your past security assessments</p>
          </motion.div>

          {/* Content */}
          {loading ? (
            <div className="flex items-center justify-center py-20">
              <Loader2 className="w-8 h-8 text-cyber-purple animate-spin" />
            </div>
          ) : error ? (
            <div className="glass-card rounded-2xl p-8 text-center">
              <AlertTriangle className="w-10 h-10 text-red-400 mx-auto mb-3" />
              <p className="text-[14px] text-red-400">{error}</p>
            </div>
          ) : history.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
              className="glass-card rounded-2xl p-12 text-center"
            >
              <Shield className="w-14 h-14 text-cyber-purple/30 mx-auto mb-4" />
              <h2 className="text-[20px] font-bold text-white mb-2">No Scans Yet</h2>
              <p className="text-[14px] text-cyber-text-muted mb-6">
                Run your first security scan to see results here.
              </p>
              <button
                onClick={() => navigate('/scan')}
                className="px-6 py-2.5 bg-gradient-to-r from-cyber-purple to-cyber-neon rounded-xl text-[14px] font-semibold text-white shadow-[0_0_20px_rgba(139,92,246,0.3)]"
              >
                Start Scanning
              </button>
            </motion.div>
          ) : (
            <div className="space-y-3">
              {history.map((scan, i) => {
                const totalVulns =
                  (scan.severity_counts?.critical || 0) +
                  (scan.severity_counts?.high || 0) +
                  (scan.severity_counts?.medium || 0) +
                  (scan.severity_counts?.low || 0);

                return (
                  <motion.div
                    key={scan.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.05 }}
                    onClick={() => viewScan(scan.id)}
                    className="glass-card rounded-xl p-5 cursor-pointer hover:border-cyber-purple/30 transition-all duration-200 group"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4 flex-1 min-w-0">
                        {/* Score */}
                        <div className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0"
                          style={{ backgroundColor: `${gradeColor[scan.grade] || '#8B5CF6'}15` }}>
                          <span className="text-[18px] font-bold" style={{ color: gradeColor[scan.grade] || '#8B5CF6' }}>
                            {scan.score}
                          </span>
                        </div>

                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-0.5">
                            <Globe className="w-3.5 h-3.5 text-cyber-text-muted flex-shrink-0" />
                            <span className="text-[14px] text-white font-medium truncate">{scan.url}</span>
                          </div>
                          <div className="flex items-center gap-3">
                            <span className="text-[11px] text-cyber-text-muted">
                              {new Date(scan.created_at).toLocaleDateString('en-US', {
                                month: 'short', day: 'numeric', year: 'numeric',
                                hour: '2-digit', minute: '2-digit',
                              })}
                            </span>
                            <span className="text-[11px] text-cyber-purple font-medium uppercase">{scan.depth}</span>
                            <span className="text-[11px] text-cyber-text-muted">{totalVulns} issues</span>
                          </div>
                        </div>
                      </div>

                      {/* Grade + arrow */}
                      <div className="flex items-center gap-3">
                        <span className="text-[14px] font-bold px-2.5 py-1 rounded-lg"
                          style={{ color: gradeColor[scan.grade] || '#8B5CF6', backgroundColor: `${gradeColor[scan.grade] || '#8B5CF6'}12` }}>
                          {scan.grade}
                        </span>
                        <ExternalLink className="w-4 h-4 text-cyber-text-muted group-hover:text-cyber-purple transition-colors" />
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
