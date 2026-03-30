import { useState } from 'react';
import { useNavigate } from "react-router-dom";
import { Shield, CheckCircle2, Loader2, Zap, Scan, Radar, ShieldCheck, Lock, Globe, Activity } from 'lucide-react';
import { motion } from 'framer-motion';

const vulnerabilities = [
  { id: 'sqli', name: 'SQL Injection', icon: '💉' },
  { id: 'xss', name: 'XSS', icon: '⚡' },
  { id: 'csrf', name: 'CSRF', icon: '🔄' },
  { id: 'headers', name: 'Security Headers', icon: '🛡️' },
  { id: 'ssl', name: 'SSL/TLS', icon: '🔒' },
  { id: 'auth', name: 'Auth Flaws', icon: '🔑' },
];

const scanProfiles = [
  { id: 'quick', name: 'Quick', time: '~15s', icon: Zap, description: 'Surface scan' },
  { id: 'standard', name: 'Standard', time: '~40s', icon: Scan, description: 'Balanced depth' },
  { id: 'deep', name: 'Deep', time: '~60s', icon: Radar, description: 'Full pentest' },
];

const featureCards = [
  {
    icon: ShieldCheck,
    title: 'DAST Engine',
    description: 'Crawl SPAs, detect endpoints, test for real-world vulnerabilities',
    color: '#8B5CF6',
  },
  {
    icon: Globe,
    title: 'Headers & SSL',
    description: 'Analyze security headers, TLS configuration, and certificate health',
    color: '#A78BFA',
  },
  {
    icon: Lock,
    title: 'Auth & Session',
    description: 'Check cookie flags, session rotation, JWT leakage in storage',
    color: '#C084FC',
  },
  {
    icon: Activity,
    title: 'Load Testing',
    description: 'Controlled stress test with response time and stability metrics',
    color: '#818CF8',
  },
];

export function ScanSetup() {
  const navigate = useNavigate();
  const [targetUrl, setTargetUrl] = useState('');
  const [selectedVulnerabilities, setSelectedVulnerabilities] = useState<string[]>(
    vulnerabilities.map(v => v.id)
  );
  const [scanProfile, setScanProfile] = useState('standard');
  const [authorized, setAuthorized] = useState(false);
  const [stressTest, setStressTest] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const toggleVulnerability = (id: string) => {
    setSelectedVulnerabilities(prev =>
      prev.includes(id) ? prev.filter(v => v !== id) : [...prev, id]
    );
  };

  const handleStartScan = () => {
    if (!authorized || !targetUrl) return;

    sessionStorage.setItem(
      "scanConfig",
      JSON.stringify({
        targetUrl,
        selectedVulnerabilities,
        scanProfile,
        stressTest,
      })
    );

    navigate("/scanning");
  };

  return (
    <div className="min-h-screen bg-cyber-dark cyber-grid-bg relative overflow-hidden">
      <div className="scan-line" />

      {/* Ambient glow orbs */}
      <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-cyber-purple/5 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] bg-cyber-neon/5 rounded-full blur-[100px] pointer-events-none" />

      <div className="relative z-10 flex flex-col items-center min-h-screen py-12 px-6">

        {/* ============================== */}
        {/* HERO SECTION */}
        {/* ============================== */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
          className="text-center mb-10 max-w-[700px]"
        >
          <motion.div
            className="w-20 h-20 rounded-2xl bg-cyber-purple/10 border border-cyber-purple/30 flex items-center justify-center mb-6 mx-auto"
            animate={{ boxShadow: ['0 0 20px rgba(139,92,246,0.2)', '0 0 40px rgba(139,92,246,0.4)', '0 0 20px rgba(139,92,246,0.2)'] }}
            transition={{ duration: 3, repeat: Infinity }}
          >
            <Shield className="w-10 h-10 text-cyber-purple" />
          </motion.div>

          <h1 className="text-[40px] font-extrabold text-white mb-3 tracking-tight leading-tight">
            WebGuard <span className="bg-gradient-to-r from-cyber-purple to-cyber-neon bg-clip-text text-transparent">DAST</span>
          </h1>
          <p className="text-[17px] text-cyber-text-dim leading-relaxed">
            Enterprise Web Security Scanning — Powered by AI Analysis
          </p>
        </motion.div>

        {/* ============================== */}
        {/* FEATURE CARDS */}
        {/* ============================== */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="grid grid-cols-2 lg:grid-cols-4 gap-3 max-w-[800px] w-full mb-10"
        >
          {featureCards.map((card, i) => (
            <motion.div
              key={card.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 + i * 0.1 }}
              whileHover={{ y: -4, boxShadow: `0 0 25px ${card.color}20` }}
              className="glass-card rounded-xl p-4 text-center cursor-default"
            >
              <div
                className="w-10 h-10 rounded-lg flex items-center justify-center mx-auto mb-3"
                style={{ backgroundColor: `${card.color}15` }}
              >
                <card.icon className="w-5 h-5" style={{ color: card.color }} />
              </div>
              <h3 className="text-[13px] font-semibold text-white mb-1">{card.title}</h3>
              <p className="text-[11px] text-cyber-text-muted leading-relaxed">{card.description}</p>
            </motion.div>
          ))}
        </motion.div>

        {/* ============================== */}
        {/* MAIN SCAN CONFIG CARD */}
        {/* ============================== */}
        <motion.div
          initial={{ opacity: 0, y: 30, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="w-full max-w-[640px]"
        >
          <div className="glass-card rounded-2xl p-8 shadow-[var(--shadow-card)]">

            {/* URL Input */}
            <div className="mb-7">
              <label className="block text-[13px] font-medium text-cyber-text-dim mb-2 uppercase tracking-wider">
                Target URL
              </label>
              <div className="relative">
                <input
                  type="url"
                  value={targetUrl}
                  onChange={(e) => setTargetUrl(e.target.value)}
                  placeholder="https://target-application.com"
                  className="w-full h-13 px-5 bg-cyber-surface border border-cyber-border rounded-xl text-white placeholder-cyber-text-muted focus:outline-none focus:border-cyber-purple focus:shadow-[0_0_20px_rgba(139,92,246,0.2)] transition-all duration-300"
                />
                <div className="absolute right-4 top-1/2 -translate-y-1/2">
                  <div className={`w-2 h-2 rounded-full ${targetUrl ? 'bg-cyber-success' : 'bg-cyber-text-muted'} transition-colors duration-300`} />
                </div>
              </div>
            </div>

            {/* Scan Modules */}
            <div className="mb-7">
              <label className="block text-[13px] font-medium text-cyber-text-dim mb-3 uppercase tracking-wider">
                Scan Modules
              </label>
              <div className="grid grid-cols-2 gap-2">
                {vulnerabilities.map((vuln) => {
                  const isSelected = selectedVulnerabilities.includes(vuln.id);
                  return (
                    <motion.button
                      key={vuln.id}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => toggleVulnerability(vuln.id)}
                      className={`flex items-center gap-3 p-3 rounded-xl border transition-all duration-300 text-left ${isSelected
                          ? 'border-cyber-purple/50 bg-cyber-purple/10 shadow-[0_0_15px_rgba(139,92,246,0.15)]'
                          : 'border-cyber-border bg-cyber-surface hover:border-cyber-border-bright'
                        }`}
                    >
                      <div className={`w-4.5 h-4.5 rounded-md border-2 flex items-center justify-center transition-all duration-200 ${isSelected ? 'bg-cyber-purple border-cyber-purple' : 'border-cyber-text-muted'
                        }`}>
                        {isSelected && <CheckCircle2 className="w-3 h-3 text-white" />}
                      </div>
                      <span className="text-[12px]">{vuln.icon}</span>
                      <span className={`text-[12px] font-medium ${isSelected ? 'text-white' : 'text-cyber-text-dim'}`}>
                        {vuln.name}
                      </span>
                    </motion.button>
                  );
                })}
              </div>
            </div>

            {/* Scan Depth */}
            <div className="mb-7">
              <label className="block text-[13px] font-medium text-cyber-text-dim mb-3 uppercase tracking-wider">
                Scan Depth
              </label>
              <div className="flex gap-2">
                {scanProfiles.map(profile => {
                  const Icon = profile.icon;
                  const isActive = scanProfile === profile.id;
                  return (
                    <motion.button
                      key={profile.id}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => setScanProfile(profile.id)}
                      className={`flex-1 p-3.5 rounded-xl border transition-all duration-300 ${isActive
                          ? 'border-cyber-purple/50 bg-cyber-purple/10 shadow-[0_0_15px_rgba(139,92,246,0.15)]'
                          : 'border-cyber-border bg-cyber-surface hover:border-cyber-border-bright'
                        }`}
                    >
                      <Icon className={`w-5 h-5 mb-1.5 mx-auto ${isActive ? 'text-cyber-purple' : 'text-cyber-text-muted'}`} />
                      <div className={`text-[13px] font-semibold ${isActive ? 'text-white' : 'text-cyber-text-dim'}`}>
                        {profile.name}
                      </div>
                      <div className={`text-[10px] mt-0.5 ${isActive ? 'text-cyber-glow' : 'text-cyber-text-muted'}`}>
                        {profile.time}
                      </div>
                    </motion.button>
                  );
                })}
              </div>
            </div>

            {/* Stress Test Toggle */}
            <motion.div
              className="mb-7 p-4 rounded-xl border border-cyber-border bg-cyber-surface"
              whileHover={{ borderColor: 'rgba(139,92,246,0.3)' }}
            >
              <label className="flex items-center justify-between cursor-pointer group">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-cyber-info/15 flex items-center justify-center">
                    <Activity className="w-4 h-4 text-cyber-info" />
                  </div>
                  <div>
                    <span className="text-[13px] font-medium text-white block">Load Test</span>
                    <span className="text-[11px] text-cyber-text-muted">Controlled stress test (safe, throttled)</span>
                  </div>
                </div>
                <div
                  onClick={() => setStressTest(!stressTest)}
                  className={`w-11 h-6 rounded-full relative transition-all duration-300 cursor-pointer ${stressTest ? 'bg-cyber-purple' : 'bg-cyber-card'
                    }`}
                >
                  <div className={`w-5 h-5 rounded-full bg-white absolute top-0.5 transition-all duration-300 ${stressTest ? 'left-5.5' : 'left-0.5'
                    }`} />
                </div>
              </label>
            </motion.div>

            {/* Authorization */}
            <div className="mb-6">
              <label className="flex items-center gap-3 cursor-pointer group">
                <div
                  onClick={() => setAuthorized(!authorized)}
                  className={`w-5 h-5 rounded-md border-2 flex items-center justify-center transition-all duration-200 ${authorized ? 'bg-cyber-purple border-cyber-purple' : 'border-cyber-text-muted group-hover:border-cyber-glow'
                    }`}
                >
                  {authorized && <CheckCircle2 className="w-3.5 h-3.5 text-white" />}
                </div>
                <span className="text-[12px] text-cyber-text-dim group-hover:text-cyber-text transition-colors">
                  I confirm I have authorization to scan this target
                </span>
              </label>
            </div>

            {/* Error */}
            {error && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="mb-4 p-3 rounded-lg bg-cyber-danger/10 border border-cyber-danger/30 text-cyber-danger text-sm"
              >
                {error}
              </motion.div>
            )}

            {/* CTA Button */}
            <motion.button
              whileHover={authorized && targetUrl ? { scale: 1.01, boxShadow: '0 0 40px rgba(139,92,246,0.5)' } : {}}
              whileTap={authorized && targetUrl ? { scale: 0.99 } : {}}
              onClick={handleStartScan}
              disabled={!authorized || !targetUrl || loading}
              className={`w-full h-[54px] rounded-xl font-semibold text-[15px] flex items-center justify-center gap-2.5 transition-all duration-300 ${authorized && targetUrl
                  ? 'bg-gradient-to-r from-cyber-purple to-cyber-neon text-white shadow-[0_0_30px_rgba(139,92,246,0.4)] hover:shadow-[0_0_50px_rgba(139,92,246,0.6)]'
                  : 'bg-cyber-surface border border-cyber-border text-cyber-text-muted cursor-not-allowed'
                }`}
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Initializing...
                </>
              ) : (
                <>
                  <Scan className="w-5 h-5" />
                  Launch Security Scan
                </>
              )}
            </motion.button>
          </div>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="text-center text-[11px] text-cyber-text-muted mt-5"
          >
            WebGuard DAST Engine v2.1 — Enterprise Security Scanner
          </motion.p>
        </motion.div>
      </div>
    </div>
  );
}
