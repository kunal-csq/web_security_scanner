import { useState, useEffect } from 'react';
import { useNavigate } from "react-router-dom";
import { Sparkles, ArrowLeft, Globe, ShieldCheck, AlertTriangle, ShieldAlert, Info, Clock, Activity, Zap } from 'lucide-react';
import { motion } from 'framer-motion';
import { VulnerabilityCard } from '../components/VulnerabilityCard';
import { VulnerabilityChart } from '../components/VulnerabilityChart';

// -----------------------------------------------
// EVIDENCE NORMALIZATION UTILITY
// -----------------------------------------------
function normalizeEvidence(evidence: unknown): string[] {
  if (!evidence) return [];
  if (Array.isArray(evidence)) return evidence.map(e => String(e));
  if (typeof evidence === 'string') return [evidence];
  return [];
}

interface Vulnerability {
  name: string;
  severity: string;
  description: string;
  confidence?: string;
  location: string;
  parameter: string;
  impact: string;
  recommendation: string;
  evidence: string[];
}

interface StressTestResult {
  avg_response_time: string;
  max_response_time: string;
  min_response_time: string;
  p95_response_time?: string;
  error_rate: string;
  timeout_rate: string;
  stability_score: number;
  request_count: number;
  successful_requests: number;
  failed_requests: number;
  status_codes: Record<string, number>;
  aborted: boolean;
  aborted_reason?: string | null;
}

interface ScanResponse {
  url: string;
  score: number;
  grade?: string;
  severity_counts?: { critical: number; high: number; medium: number; low: number };
  results: Vulnerability[];
  ai_analysis?: { summary: string; why_it_matters: string; priority_actions: string[] };
  crawl_info?: { pages_crawled: number; total_forms: number; total_links: number; endpoints_found: number };
  stress_test?: StressTestResult;
  timing?: { crawl_time: number; total_time: number; scanner_timings: Record<string, number> };
}

export function ScanResults() {
  const navigate = useNavigate();
  const [expandedVuln, setExpandedVuln] = useState<number | null>(null);
  const [data, setData] = useState<ScanResponse | null>(null);

  useEffect(() => {
    const stored = localStorage.getItem('scanResults');
    if (!stored) { navigate('/scan'); return; }
    setData(JSON.parse(stored));
  }, [navigate]);

  if (!data) {
    return (
      <div className="min-h-screen bg-cyber-dark flex items-center justify-center">
        <div className="text-cyber-text-muted">Loading results...</div>
      </div>
    );
  }

  const normalizedResults: Vulnerability[] = (data.results || []).map((v) => ({
    ...v,
    severity: v.severity ? v.severity.charAt(0).toUpperCase() + v.severity.slice(1).toLowerCase() : 'Low',
    evidence: normalizeEvidence(v.evidence),
  }));

  const score = data.score ?? 0;
  const grade = data.grade || getGradeFromScore(score);
  const counts = data.severity_counts || {
    critical: normalizedResults.filter(r => r.severity === 'Critical').length,
    high: normalizedResults.filter(r => r.severity === 'High').length,
    medium: normalizedResults.filter(r => r.severity === 'Medium').length,
    low: normalizedResults.filter(r => r.severity === 'Low').length,
  };

  function getGradeFromScore(s: number): string {
    if (s >= 95) return 'A+'; if (s >= 85) return 'A'; if (s >= 70) return 'B';
    if (s >= 50) return 'C'; if (s >= 30) return 'D'; return 'F';
  }

  function getScoreColor(s: number): string {
    if (s >= 80) return '#10B981'; if (s >= 50) return '#F59E0B'; return '#EF4444';
  }

  const scoreColor = getScoreColor(score);
  const total = counts.critical + counts.high + counts.medium + counts.low;

  // Pie chart segments
  function buildPieGradient() {
    if (total === 0) return '#1E1E30';
    const segments = [
      { count: counts.critical, color: '#EF4444' },
      { count: counts.high, color: '#8B5CF6' },
      { count: counts.medium, color: '#A78BFA' },
      { count: counts.low, color: '#818CF8' },
    ];
    let cumulative = 0;
    const parts: string[] = [];
    segments.forEach(seg => {
      if (seg.count > 0) {
        const pct = (seg.count / total) * 100;
        parts.push(`${seg.color} ${cumulative}% ${cumulative + pct}%`);
        cumulative += pct;
      }
    });
    return `conic-gradient(${parts.join(', ')})`;
  }

  return (
    <div className="min-h-screen bg-cyber-dark cyber-grid-bg relative">
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-cyber-purple/3 rounded-full blur-[150px] pointer-events-none" />

      <div className="relative z-10 py-8 px-6">
        <div className="max-w-[1280px] mx-auto">

          {/* Back button */}
          <motion.button
            initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}
            onClick={() => navigate('/scan')}
            className="flex items-center gap-2 text-[13px] text-cyber-text-muted hover:text-cyber-purple transition-colors mb-6"
          >
            <ArrowLeft className="w-4 h-4" /> New Scan
          </motion.button>

          {/* ============================================ */}
          {/* SCORE + STATS + PIE */}
          {/* ============================================ */}
          <div className="grid grid-cols-1 lg:grid-cols-5 gap-4 mb-8">

            {/* Score Card */}
            <motion.div
              initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
              className="lg:col-span-1 glass-card rounded-2xl p-6 flex flex-col items-center justify-center"
            >
              <div className="relative w-32 h-32 mb-3">
                <div className="w-full h-full rounded-full p-[5px]" style={{ background: `conic-gradient(${scoreColor} ${score * 3.6}deg, #1E1E30 0deg)` }}>
                  <div className="w-full h-full rounded-full bg-cyber-card flex items-center justify-center">
                    <div className="text-center">
                      <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }}
                        className="text-[42px] font-bold block leading-none" style={{ color: scoreColor }}>{score}</motion.span>
                      <span className="text-[12px] text-cyber-text-muted">/100</span>
                    </div>
                  </div>
                </div>
                <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ delay: 0.7, type: 'spring' }}
                  className="absolute -bottom-1 left-1/2 -translate-x-1/2 px-3 py-0.5 rounded-full text-[11px] font-bold border"
                  style={{ backgroundColor: `${scoreColor}20`, borderColor: `${scoreColor}40`, color: scoreColor }}>
                  {grade}
                </motion.div>
              </div>
              <p className="text-[12px] text-cyber-text-muted mt-2">Security Score</p>
              <div className="flex items-center gap-1.5 mt-1">
                <Globe className="w-3 h-3 text-cyber-text-muted" />
                <p className="text-[10px] text-cyber-text-muted font-mono truncate max-w-[150px]">{data.url}</p>
              </div>
            </motion.div>

            {/* Severity Stats */}
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}
              className="lg:col-span-3 grid grid-cols-2 lg:grid-cols-4 gap-3">
              {[
                { label: 'Critical', count: counts.critical, color: '#EF4444', icon: ShieldAlert },
                { label: 'High', count: counts.high, color: '#8B5CF6', icon: AlertTriangle },
                { label: 'Medium', count: counts.medium, color: '#A78BFA', icon: Info },
                { label: 'Low', count: counts.low, color: '#818CF8', icon: ShieldCheck },
              ].map((stat, i) => (
                <div key={stat.label} className="glass-card rounded-xl p-4 flex flex-col">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${stat.color}15` }}>
                      <stat.icon className="w-3.5 h-3.5" style={{ color: stat.color }} />
                    </div>
                    <span className="text-[11px] text-cyber-text-muted uppercase tracking-wider">{stat.label}</span>
                  </div>
                  <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 + i * 0.1 }}
                    className="text-[28px] font-bold" style={{ color: stat.color }}>{stat.count}</motion.span>
                </div>
              ))}
            </motion.div>

            {/* Severity Pie Chart */}
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
              className="lg:col-span-1 glass-card rounded-2xl p-5 flex flex-col items-center justify-center">
              <div className="w-24 h-24 rounded-full p-[4px] mb-3" style={{ background: buildPieGradient() }}>
                <div className="w-full h-full rounded-full bg-cyber-card flex items-center justify-center">
                  <span className="text-[20px] font-bold text-white">{total}</span>
                </div>
              </div>
              <p className="text-[11px] text-cyber-text-muted">Total Issues</p>
              {/* Legend */}
              <div className="flex flex-wrap justify-center gap-x-3 gap-y-1 mt-2">
                {[
                  { label: 'C', color: '#EF4444' }, { label: 'H', color: '#8B5CF6' },
                  { label: 'M', color: '#A78BFA' }, { label: 'L', color: '#818CF8' },
                ].map(item => (
                  <div key={item.label} className="flex items-center gap-1">
                    <div className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }} />
                    <span className="text-[9px] text-cyber-text-muted">{item.label}</span>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>

          {/* ============================================ */}
          {/* STRESS TEST RESULTS (if present) */}
          {/* ============================================ */}
          {data.stress_test && (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}
              className="glass-card rounded-2xl p-6 mb-8">
              <div className="flex items-center gap-2.5 mb-4">
                <div className="w-8 h-8 rounded-lg bg-cyber-info/15 flex items-center justify-center">
                  <Activity className="w-4 h-4 text-cyber-info" />
                </div>
                <div>
                  <h3 className="font-bold text-white text-[15px]">Load Test Results</h3>
                  <p className="text-[11px] text-cyber-text-muted">Controlled stress test — {data.stress_test.request_count} requests</p>
                </div>
                {data.stress_test.aborted && (
                  <span className="ml-auto px-2 py-0.5 rounded-full text-[10px] font-medium bg-cyber-warning/15 text-cyber-warning border border-cyber-warning/30">
                    Aborted
                  </span>
                )}
              </div>

              <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
                {[
                  { label: 'Avg Response', value: data.stress_test.avg_response_time, icon: Clock, color: '#A78BFA' },
                  { label: 'Max Response', value: data.stress_test.max_response_time, icon: Zap, color: '#C084FC' },
                  { label: 'P95 Response', value: data.stress_test.p95_response_time || 'N/A', icon: Activity, color: '#818CF8' },
                  {
                    label: 'Error Rate', value: data.stress_test.error_rate, icon: AlertTriangle,
                    color: parseFloat(data.stress_test.error_rate) > 5 ? '#EF4444' : '#10B981'
                  },
                  {
                    label: 'Stability', value: `${data.stress_test.stability_score}/100`, icon: ShieldCheck,
                    color: data.stress_test.stability_score >= 80 ? '#10B981' : data.stress_test.stability_score >= 50 ? '#F59E0B' : '#EF4444'
                  },
                ].map(metric => (
                  <div key={metric.label} className="bg-cyber-surface rounded-xl p-4 border border-cyber-border">
                    <div className="flex items-center gap-1.5 mb-2">
                      <metric.icon className="w-3.5 h-3.5" style={{ color: metric.color }} />
                      <span className="text-[10px] text-cyber-text-muted uppercase tracking-wider">{metric.label}</span>
                    </div>
                    <div className="text-[18px] font-bold" style={{ color: metric.color }}>{metric.value}</div>
                  </div>
                ))}
              </div>

              {data.stress_test.aborted_reason && (
                <p className="text-[11px] text-cyber-warning mt-3 font-mono">⚠ {data.stress_test.aborted_reason}</p>
              )}
            </motion.div>
          )}

          {/* ============================================ */}
          {/* TIMING INFO */}
          {/* ============================================ */}
          {data.timing && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}
              className="flex flex-wrap gap-3 mb-6">
              <div className="glass-card rounded-lg px-4 py-2 flex items-center gap-2">
                <Clock className="w-3.5 h-3.5 text-cyber-text-muted" />
                <span className="text-[11px] text-cyber-text-dim">Total: <span className="text-cyber-glow font-semibold">{data.timing.total_time}s</span></span>
              </div>
              <div className="glass-card rounded-lg px-4 py-2 flex items-center gap-2">
                <Globe className="w-3.5 h-3.5 text-cyber-text-muted" />
                <span className="text-[11px] text-cyber-text-dim">Crawl: <span className="text-cyber-neon font-semibold">{data.timing.crawl_time}s</span></span>
              </div>
              {Object.entries(data.timing.scanner_timings || {}).map(([name, time]) => (
                <div key={name} className="glass-card rounded-lg px-3 py-2">
                  <span className="text-[10px] text-cyber-text-muted">{name}: <span className="text-cyber-text-dim font-medium">{time}s</span></span>
                </div>
              ))}
            </motion.div>
          )}

          {/* ============================================ */}
          {/* MAIN CONTENT: VULNS + AI */}
          {/* ============================================ */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

            {/* Vulnerabilities */}
            <div className="lg:col-span-2">
              <h2 className="text-[18px] font-bold text-white mb-4 flex items-center gap-2">
                <ShieldAlert className="w-5 h-5 text-cyber-purple" />
                Vulnerabilities
                <span className="text-[12px] text-cyber-text-muted font-normal ml-1">({normalizedResults.length} found)</span>
              </h2>

              <div className="space-y-3">
                {normalizedResults.length > 0 ? (
                  normalizedResults.map((vuln, index) => (
                    <VulnerabilityCard key={index} vuln={vuln} index={index}
                      isExpanded={expandedVuln === index}
                      onToggle={() => setExpandedVuln(expandedVuln === index ? null : index)} />
                  ))
                ) : (
                  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card rounded-xl p-8 text-center">
                    <ShieldCheck className="w-12 h-12 text-cyber-success mx-auto mb-3" />
                    <p className="text-cyber-text font-medium">No vulnerabilities detected</p>
                    <p className="text-[12px] text-cyber-text-muted mt-1">Your application passed all security tests</p>
                  </motion.div>
                )}
              </div>

              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} className="mt-6">
                <VulnerabilityChart vulnerabilities={normalizedResults} />
              </motion.div>
            </div>

            {/* AI Analysis */}
            <div>
              {data.ai_analysis && (
                <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 }}
                  className="glass-card rounded-2xl p-6 sticky top-6">
                  <div className="flex items-center gap-2.5 mb-5">
                    <div className="w-9 h-9 rounded-xl bg-cyber-purple/15 flex items-center justify-center">
                      <Sparkles className="w-5 h-5 text-cyber-purple" />
                    </div>
                    <div>
                      <h3 className="font-bold text-white text-[14px]">AI Analysis</h3>
                      <p className="text-[10px] text-cyber-text-muted">Powered by AI Engine</p>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <p className="text-[10px] text-cyber-text-muted uppercase tracking-wider font-medium mb-1.5">Summary</p>
                      <p className="text-[12px] text-cyber-text leading-relaxed">{data.ai_analysis.summary}</p>
                    </div>
                    <div>
                      <p className="text-[10px] text-cyber-text-muted uppercase tracking-wider font-medium mb-1.5">Why It Matters</p>
                      <p className="text-[12px] text-cyber-text leading-relaxed">{data.ai_analysis.why_it_matters}</p>
                    </div>
                    <div>
                      <p className="text-[10px] text-cyber-text-muted uppercase tracking-wider font-medium mb-1.5">Fix Priority</p>
                      <div className="space-y-1.5">
                        {(data.ai_analysis.priority_actions || []).map((action, i) => (
                          <div key={i} className="flex items-start gap-2 p-2 rounded-lg bg-cyber-surface border border-cyber-border">
                            <span className="text-[11px] text-cyber-purple font-bold flex-shrink-0 mt-0.5">{i + 1}.</span>
                            <p className="text-[11px] text-cyber-text-dim leading-relaxed">{action}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Crawl Info */}
                  {data.crawl_info && (
                    <div className="mt-4 pt-4 border-t border-cyber-border">
                      <p className="text-[10px] text-cyber-text-muted uppercase tracking-wider font-medium mb-2">Crawl Summary</p>
                      <div className="grid grid-cols-2 gap-1.5">
                        {[
                          { label: 'Pages', value: data.crawl_info.pages_crawled },
                          { label: 'Endpoints', value: data.crawl_info.endpoints_found },
                          { label: 'Forms', value: data.crawl_info.total_forms },
                          { label: 'Links', value: data.crawl_info.total_links },
                        ].map(item => (
                          <div key={item.label} className="p-2 rounded-lg bg-cyber-surface text-center">
                            <div className="text-[16px] font-bold text-cyber-glow">{item.value}</div>
                            <div className="text-[9px] text-cyber-text-muted uppercase">{item.label}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </motion.div>
              )}
            </div>
          </div>

          {/* Scan Again */}
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.6 }} className="flex justify-center mt-10 mb-6">
            <button onClick={() => navigate('/scan')}
              className="px-8 py-3 rounded-xl bg-gradient-to-r from-cyber-purple to-cyber-neon text-white font-semibold shadow-[0_0_30px_rgba(139,92,246,0.3)] hover:shadow-[0_0_50px_rgba(139,92,246,0.5)] transition-all duration-300">
              Start New Scan
            </button>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
