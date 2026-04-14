import { useState } from 'react';
import { useNavigate, Link, useSearchParams } from "react-router-dom";
import { Shield, CheckCircle2, Loader2, Zap, Scan, Radar, ShieldCheck, Lock, Globe, Activity, ShoppingCart, CreditCard, Package, Users, Database, Bug, Bot, Server } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { isLoggedIn } from '../../config/auth';

// ============================================
// GENERAL DAST MODULES
// ============================================
const generalModules = [
  { id: 'sqli', name: 'SQL Injection', icon: '💉' },
  { id: 'xss', name: 'XSS', icon: '⚡' },
  { id: 'csrf', name: 'CSRF', icon: '🔄' },
  { id: 'headers', name: 'Security Headers', icon: '🛡️' },
  { id: 'ssl', name: 'SSL/TLS', icon: '🔒' },
  { id: 'auth', name: 'Auth Flaws', icon: '🔑' },
];

// ============================================
// ECOMMERCE MODULES
// ============================================
const ecomModules = [
  { id: 'auth_account', name: 'Auth & Account', icon: '🔐' },
  { id: 'access_control', name: 'Access Control', icon: '👤' },
  { id: 'session_cookie', name: 'Session & Cookie', icon: '🍪' },
  { id: 'ecom_logic', name: 'Ecommerce Logic', icon: '🛍️' },
  { id: 'sensitive_data', name: 'Data Exposure', icon: '📂' },
  { id: 'security_misconfig', name: 'Misconfig', icon: '⚙️' },
  { id: 'api_security', name: 'API Security', icon: '🔗' },
  { id: 'bot_protection', name: 'Bot Protection', icon: '🚫' },
];

const scanProfiles = [
  { id: 'quick', name: 'Quick', time: '~15s', icon: Zap, description: 'Surface scan' },
  { id: 'standard', name: 'Standard', time: '~40s', icon: Scan, description: 'Balanced depth' },
  { id: 'deep', name: 'Deep', time: '~60s', icon: Radar, description: 'Full pentest' },
];

// ============================================
// FEATURE CARDS PER MODE
// ============================================
const generalFeatures = [
  { icon: ShieldCheck, title: 'DAST Engine', description: 'Crawl SPAs, detect endpoints, test for real-world vulnerabilities', color: '#8B5CF6' },
  { icon: Globe, title: 'Headers & SSL', description: 'Analyze security headers, TLS configuration, and certificate health', color: '#A78BFA' },
  { icon: Lock, title: 'Auth & Session', description: 'Check cookie flags, session rotation, JWT leakage in storage', color: '#C084FC' },
  { icon: Activity, title: 'Load Testing', description: 'Controlled stress test with response time and stability metrics', color: '#818CF8' },
];

const ecomFeatures = [
  { icon: CreditCard, title: 'Payment Security', description: 'Detect price manipulation, cart tampering, and payment flow bypasses', color: '#F59E0B' },
  { icon: Package, title: 'Order Security', description: 'Check for predictable order IDs, coupon abuse, and refund exploits', color: '#EF4444' },
  { icon: Database, title: 'Data Protection', description: 'Find exposed .env files, API keys, database dumps, and backups', color: '#10B981' },
  { icon: Bot, title: 'Bot Defense', description: 'Verify CAPTCHA, rate limiting, and anti-automation protections', color: '#3B82F6' },
];

// Mode config
const modeConfig = {
  general: {
    title: 'WebGuard ',
    titleAccent: 'DAST',
    subtitle: 'Enterprise Web Security Scanning — Powered by AI Analysis',
    modules: generalModules,
    features: generalFeatures,
    accentColor: '#8B5CF6',
    gradientFrom: 'from-cyber-purple',
    gradientTo: 'to-cyber-neon',
    buttonText: 'Launch Security Scan',
    versionText: 'WebGuard DAST Engine v2.2 — Enterprise Security Scanner',
  },
  ecommerce: {
    title: 'WebGuard ',
    titleAccent: 'ECOM',
    subtitle: 'Ecommerce Security Assessment — OWASP Aligned Checks',
    modules: ecomModules,
    features: ecomFeatures,
    accentColor: '#F59E0B',
    gradientFrom: 'from-amber-500',
    gradientTo: 'to-orange-500',
    buttonText: 'Launch Ecommerce Scan',
    versionText: 'WebGuard Ecommerce Scanner v1.0 — 8 Security Categories',
  },
};

type ScanMode = 'general' | 'ecommerce';

export function ScanSetup() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const loggedIn = isLoggedIn();
  const initialMode = searchParams.get('mode') === 'ecommerce' ? 'ecommerce' : 'general';
  const [scanMode, setScanMode] = useState<ScanMode>(initialMode);
  const [targetUrl, setTargetUrl] = useState('');
  const [selectedModules, setSelectedModules] = useState<string[]>(
    (initialMode === 'ecommerce' ? ecomModules : generalModules).map(v => v.id)
  );
  const [scanProfile, setScanProfile] = useState(loggedIn ? 'standard' : 'quick');
  const [authorized, setAuthorized] = useState(false);
  const [stressTest, setStressTest] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const config = modeConfig[scanMode];

  const handleModeSwitch = (mode: ScanMode) => {
    if (mode === scanMode) return;
    setScanMode(mode);
    // Reset modules to new mode's defaults
    const modules = mode === 'general' ? generalModules : ecomModules;
    setSelectedModules(modules.map(m => m.id));
    setStressTest(false);
  };

  const toggleModule = (id: string) => {
    setSelectedModules(prev =>
      prev.includes(id) ? prev.filter(v => v !== id) : [...prev, id]
    );
  };

  const handleStartScan = () => {
    if (!authorized || !targetUrl) return;

    sessionStorage.setItem(
      "scanConfig",
      JSON.stringify({
        targetUrl,
        selectedVulnerabilities: selectedModules,
        scanProfile,
        stressTest,
        scanMode,
      })
    );

    navigate("/scanning");
  };

  return (
    <div className="min-h-screen bg-cyber-dark cyber-grid-bg relative overflow-hidden">
      <div className="scan-line" />

      {/* Ambient glow — changes with mode */}
      <motion.div
        key={scanMode + '-orb1'}
        animate={{ backgroundColor: scanMode === 'ecommerce' ? 'rgba(245,158,11,0.05)' : 'rgba(139,92,246,0.05)' }}
        transition={{ duration: 0.8 }}
        className="absolute top-1/4 left-1/4 w-[500px] h-[500px] rounded-full blur-[120px] pointer-events-none"
      />
      <motion.div
        key={scanMode + '-orb2'}
        animate={{ backgroundColor: scanMode === 'ecommerce' ? 'rgba(239,68,68,0.05)' : 'rgba(192,132,252,0.05)' }}
        transition={{ duration: 0.8 }}
        className="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] rounded-full blur-[100px] pointer-events-none"
      />

      <div className="relative z-10 flex flex-col items-center min-h-screen py-12 px-6">

        {/* Guest banner */}
        {!loggedIn && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="w-full max-w-[600px] mb-4 px-4 py-3 rounded-xl bg-cyber-purple/8 border border-cyber-purple/20 flex items-center justify-between"
          >
            <span className="text-[13px] text-cyber-text-dim">
              🔒 <Link to="/login" className="text-cyber-purple hover:text-cyber-glow font-medium">Login</Link> to unlock all scan depths & save history
            </span>
          </motion.div>
        )}

        {/* ============================================ */}
        {/* MODE TOGGLE SWITCH */}
        {/* ============================================ */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-6"
        >
          <div className="flex items-center gap-1 p-1 rounded-2xl bg-cyber-surface border border-cyber-border">
            {(['general', 'ecommerce'] as ScanMode[]).map(mode => (
              <motion.button
                key={mode}
                onClick={() => handleModeSwitch(mode)}
                className={`relative px-5 py-2.5 rounded-xl text-[13px] font-semibold transition-colors duration-200 flex items-center gap-2 ${
                  scanMode === mode ? 'text-white' : 'text-cyber-text-muted hover:text-cyber-text-dim'
                }`}
              >
                {scanMode === mode && (
                  <motion.div
                    layoutId="mode-pill"
                    className={`absolute inset-0 rounded-xl ${
                      mode === 'ecommerce'
                        ? 'bg-gradient-to-r from-amber-500/20 to-orange-500/20 border border-amber-500/30'
                        : 'bg-gradient-to-r from-cyber-purple/20 to-cyber-neon/20 border border-cyber-purple/30'
                    }`}
                    transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                  />
                )}
                <span className="relative z-10 flex items-center gap-2">
                  {mode === 'general' ? <Shield className="w-4 h-4" /> : <ShoppingCart className="w-4 h-4" />}
                  {mode === 'general' ? 'General DAST' : 'Ecommerce'}
                </span>
              </motion.button>
            ))}
          </div>
        </motion.div>

        {/* ============================================ */}
        {/* HERO — animates on mode change */}
        {/* ============================================ */}
        <AnimatePresence mode="wait">
          <motion.div
            key={scanMode + '-hero'}
            initial={{ opacity: 0, y: 20, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -20, scale: 0.97 }}
            transition={{ duration: 0.4 }}
            className="text-center mb-10 max-w-[700px]"
          >
            <motion.div
              className={`w-20 h-20 rounded-2xl border flex items-center justify-center mb-6 mx-auto ${
                scanMode === 'ecommerce'
                  ? 'bg-amber-500/10 border-amber-500/30'
                  : 'bg-cyber-purple/10 border-cyber-purple/30'
              }`}
              animate={{
                boxShadow: scanMode === 'ecommerce'
                  ? ['0 0 20px rgba(245,158,11,0.2)', '0 0 40px rgba(245,158,11,0.4)', '0 0 20px rgba(245,158,11,0.2)']
                  : ['0 0 20px rgba(139,92,246,0.2)', '0 0 40px rgba(139,92,246,0.4)', '0 0 20px rgba(139,92,246,0.2)']
              }}
              transition={{ duration: 3, repeat: Infinity }}
            >
              {scanMode === 'ecommerce'
                ? <ShoppingCart className="w-10 h-10 text-amber-400" />
                : <Shield className="w-10 h-10 text-cyber-purple" />
              }
            </motion.div>

            <h1 className="text-[40px] font-extrabold text-white mb-3 tracking-tight leading-tight">
              {config.title}
              <span className={`bg-clip-text text-transparent ${
                scanMode === 'ecommerce'
                  ? 'bg-gradient-to-r from-amber-400 to-orange-500'
                  : 'bg-gradient-to-r from-cyber-purple to-cyber-neon'
              }`}>
                {config.titleAccent}
              </span>
            </h1>
            <p className="text-[17px] text-cyber-text-dim leading-relaxed">
              {config.subtitle}
            </p>
          </motion.div>
        </AnimatePresence>

        {/* ============================================ */}
        {/* FEATURE CARDS — animate on mode change */}
        {/* ============================================ */}
        <AnimatePresence mode="wait">
          <motion.div
            key={scanMode + '-features'}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -15 }}
            transition={{ duration: 0.35 }}
            className="grid grid-cols-2 lg:grid-cols-4 gap-3 max-w-[750px] w-full mb-10"
          >
            {config.features.map((card, i) => (
              <motion.div
                key={card.title}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.08 }}
                className="glass-card rounded-xl p-4 text-center"
              >
                <div className="w-10 h-10 rounded-lg mx-auto mb-3 flex items-center justify-center"
                  style={{ backgroundColor: `${card.color}15` }}>
                  <card.icon className="w-5 h-5" style={{ color: card.color }} />
                </div>
                <div className="text-[13px] font-semibold text-white mb-1">{card.title}</div>
                <div className="text-[11px] text-cyber-text-muted leading-relaxed">{card.description}</div>
              </motion.div>
            ))}
          </motion.div>
        </AnimatePresence>

        {/* ============================================ */}
        {/* SCAN FORM CARD */}
        {/* ============================================ */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="w-full max-w-[560px]"
        >
          <div className={`glass-card-strong rounded-2xl p-7 border ${
            scanMode === 'ecommerce' ? 'border-amber-500/10' : 'border-white/[0.06]'
          }`}>

            {/* Target URL */}
            <div className="mb-6">
              <label className="block text-[13px] font-medium text-cyber-text-dim mb-2 uppercase tracking-wider">
                Target URL
              </label>
              <div className="flex items-center gap-2">
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${
                  scanMode === 'ecommerce' ? 'bg-amber-500/10' : 'bg-cyber-purple/10'
                }`}>
                  <Globe className={`w-5 h-5 ${scanMode === 'ecommerce' ? 'text-amber-400' : 'text-cyber-purple'}`} />
                </div>
                <input
                  type="url"
                  placeholder={scanMode === 'ecommerce' ? "https://shop.example.com" : "https://example.com"}
                  value={targetUrl}
                  onChange={e => { setTargetUrl(e.target.value); setError(null); }}
                  className="flex-1 px-4 py-3 bg-cyber-surface border border-cyber-border rounded-xl text-[14px] text-white placeholder:text-cyber-text-muted focus:border-cyber-purple/50 focus:outline-none transition-colors"
                />
              </div>
            </div>

            {/* Scan Modules — animates on mode switch */}
            <div className="mb-6">
              <label className="block text-[13px] font-medium text-cyber-text-dim mb-3 uppercase tracking-wider">
                {scanMode === 'ecommerce' ? 'Ecommerce Checks' : 'Scan Modules'}
              </label>
              <AnimatePresence mode="wait">
                <motion.div
                  key={scanMode + '-modules'}
                  initial={{ opacity: 0, rotateX: -15, scale: 0.95 }}
                  animate={{ opacity: 1, rotateX: 0, scale: 1 }}
                  exit={{ opacity: 0, rotateX: 15, scale: 0.95 }}
                  transition={{ duration: 0.35 }}
                  className="grid grid-cols-2 gap-2"
                >
                  {config.modules.map((mod) => {
                    const isSelected = selectedModules.includes(mod.id);
                    return (
                      <motion.button
                        key={mod.id}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => toggleModule(mod.id)}
                        className={`flex items-center gap-3 p-3 rounded-xl border transition-all duration-300 text-left ${isSelected
                            ? scanMode === 'ecommerce'
                              ? 'border-amber-500/50 bg-amber-500/10 shadow-[0_0_15px_rgba(245,158,11,0.15)]'
                              : 'border-cyber-purple/50 bg-cyber-purple/10 shadow-[0_0_15px_rgba(139,92,246,0.15)]'
                            : 'border-cyber-border bg-cyber-surface hover:border-cyber-border-bright'
                          }`}
                      >
                        <div className={`w-4.5 h-4.5 rounded-md border-2 flex items-center justify-center transition-all duration-200 ${
                          isSelected
                            ? scanMode === 'ecommerce'
                              ? 'bg-amber-500 border-amber-500'
                              : 'bg-cyber-purple border-cyber-purple'
                            : 'border-cyber-text-muted'
                          }`}>
                          {isSelected && <CheckCircle2 className="w-3 h-3 text-white" />}
                        </div>
                        <span className="text-[12px]">{mod.icon}</span>
                        <span className={`text-[12px] font-medium ${isSelected ? 'text-white' : 'text-cyber-text-dim'}`}>
                          {mod.name}
                        </span>
                      </motion.button>
                    );
                  })}
                </motion.div>
              </AnimatePresence>
            </div>

            {/* Scan Depth — only for general mode */}
            {scanMode === 'general' && (
              <div className="mb-7">
                <label className="block text-[13px] font-medium text-cyber-text-dim mb-3 uppercase tracking-wider">
                  Scan Depth
                </label>
                <div className="flex gap-2">
                  {scanProfiles.map(profile => {
                    const Icon = profile.icon;
                    const isActive = scanProfile === profile.id;
                    const isLocked = !loggedIn && profile.id !== 'quick';
                    return (
                      <motion.button
                        key={profile.id}
                        whileHover={isLocked ? {} : { scale: 1.02 }}
                        whileTap={isLocked ? {} : { scale: 0.98 }}
                        onClick={() => !isLocked && setScanProfile(profile.id)}
                        className={`flex-1 p-3.5 rounded-xl border transition-all duration-300 relative ${isLocked
                            ? 'border-cyber-border bg-cyber-surface/50 opacity-50 cursor-not-allowed'
                            : isActive
                              ? 'border-cyber-purple/50 bg-cyber-purple/10 shadow-[0_0_15px_rgba(139,92,246,0.15)]'
                              : 'border-cyber-border bg-cyber-surface hover:border-cyber-border-bright'
                          }`}
                      >
                        {isLocked && (
                          <div className="absolute -top-2 -right-2 px-1.5 py-0.5 bg-cyber-purple/20 border border-cyber-purple/30 rounded text-[8px] text-cyber-glow font-bold">
                            PRO
                          </div>
                        )}
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
            )}

            {/* Stress Test Toggle — only for general mode */}
            {scanMode === 'general' && (
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
                    onClick={() => loggedIn && setStressTest(!stressTest)}
                    className={`w-11 h-6 rounded-full relative transition-all duration-300 ${loggedIn ? 'cursor-pointer' : 'cursor-not-allowed opacity-40'} ${stressTest && loggedIn ? 'bg-cyber-purple' : 'bg-cyber-card'
                      }`}
                  >
                    <div className={`w-5 h-5 rounded-full bg-white absolute top-0.5 transition-all duration-300 ${stressTest ? 'left-5.5' : 'left-0.5'
                      }`} />
                  </div>
                </label>
              </motion.div>
            )}

            {/* Authorization */}
            <div className="mb-6">
              <label className="flex items-center gap-3 cursor-pointer group">
                <div
                  onClick={() => setAuthorized(!authorized)}
                  className={`w-5 h-5 rounded-md border-2 flex items-center justify-center transition-all duration-200 ${authorized
                      ? scanMode === 'ecommerce' ? 'bg-amber-500 border-amber-500' : 'bg-cyber-purple border-cyber-purple'
                      : 'border-cyber-text-muted group-hover:border-cyber-glow'
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
              whileHover={authorized && targetUrl ? { scale: 1.01, boxShadow: scanMode === 'ecommerce' ? '0 0 40px rgba(245,158,11,0.5)' : '0 0 40px rgba(139,92,246,0.5)' } : {}}
              whileTap={authorized && targetUrl ? { scale: 0.99 } : {}}
              onClick={handleStartScan}
              disabled={!authorized || !targetUrl || loading}
              className={`w-full h-[54px] rounded-xl font-semibold text-[15px] flex items-center justify-center gap-2.5 transition-all duration-300 ${authorized && targetUrl
                  ? scanMode === 'ecommerce'
                    ? 'bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-[0_0_30px_rgba(245,158,11,0.4)]'
                    : 'bg-gradient-to-r from-cyber-purple to-cyber-neon text-white shadow-[0_0_30px_rgba(139,92,246,0.4)]'
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
                  {scanMode === 'ecommerce' ? <ShoppingCart className="w-5 h-5" /> : <Scan className="w-5 h-5" />}
                  {config.buttonText}
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
            {config.versionText}
          </motion.p>
        </motion.div>
      </div>
    </div>
  );
}
