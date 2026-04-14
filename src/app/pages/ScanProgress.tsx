import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from "react-router-dom";
import { CheckCircle2, Loader2, Circle, ShieldAlert, Terminal, Sparkles } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import API from '../../config/api';
import { authHeader } from '../../config/auth';

const generalSteps = [
  { id: 'crawl', name: 'Crawling endpoints', detail: 'Discovering forms, links, and parameters...' },
  { id: 'headers', name: 'Testing Headers & SSL', detail: 'Checking CSP, HSTS, TLS, certificates...' },
  { id: 'xss', name: 'Testing XSS', detail: 'Injecting reflected and DOM-based payloads...' },
  { id: 'sqli', name: 'Testing SQL Injection', detail: 'Error-based, time-based, and auth bypass...' },
  { id: 'report', name: 'Generating Report', detail: 'AI analysis and score calculation...' },
];

const ecomSteps = [
  { id: 'auth', name: 'Checking Auth & Access', detail: 'Testing login, admin panels, IDOR...' },
  { id: 'session', name: 'Analyzing Sessions', detail: 'Checking cookies, session flags, cache...' },
  { id: 'ecom', name: 'Ecommerce Logic Tests', detail: 'Price fields, cart tampering, coupons...' },
  { id: 'exposure', name: 'Scanning Data Exposure', detail: 'Probing .env, .git, API keys, backups...' },
  { id: 'report', name: 'Generating Report', detail: 'AI analysis and score calculation...' },
];

export function ScanProgress() {
  const navigate = useNavigate();
  const config = sessionStorage.getItem('scanConfig');
  const parsedConfig = config ? JSON.parse(config) : {};
  const isEcom = parsedConfig.scanMode === 'ecommerce';
  const scanSteps = isEcom ? ecomSteps : generalSteps;

  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState(0);
  const [currentDetail, setCurrentDetail] = useState(isEcom ? 'Initializing Ecommerce Scanner...' : 'Initializing DAST engine...');
  const [logEntries, setLogEntries] = useState<string[]>([isEcom ? '[INIT] WebGuard Ecommerce Scanner starting...' : '[INIT] WebGuard DAST Engine v2.1 starting...']);
  const [scanComplete, setScanComplete] = useState(false);
  const [scanError, setScanError] = useState(false);

  const logRef = useRef<HTMLDivElement>(null);
  const cancelledRef = useRef(false);
  const abortControllerRef = useRef<AbortController | null>(null);
  const resultReadyRef = useRef(false);

  // Auto-scroll log
  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [logEntries]);

  const addLog = useCallback((msg: string) => {
    if (!cancelledRef.current) {
      setLogEntries(prev => [...prev, msg]);
    }
  }, []);

  // Main scan effect — single async flow, no artificial timers
  useEffect(() => {
    const config = sessionStorage.getItem("scanConfig");
    if (!config) {
      navigate("/scan", { replace: true });
      return;
    }

    const { targetUrl, selectedVulnerabilities, scanProfile, stressTest, scanMode } = JSON.parse(config);

    const controller = new AbortController();
    abortControllerRef.current = controller;

    async function runScan() {
      try {
        // ---- PHASE 1: Initial probe (0% → 10%) ----
        setProgress(5);
        setCurrentStep(0);
        setCurrentDetail(scanSteps[0].detail);
        if (isEcom) {
          addLog(`[ECOM] Starting ecommerce security scan of ${targetUrl}`);
          addLog('[ECOM] Probing authentication & access control...');
          addLog('[ECOM] Checking admin panels, login forms...');
        } else {
          addLog(`[CRAWL] Starting crawl of ${targetUrl}`);
          addLog(`[CRAWL] Depth: ${scanProfile}`);
          addLog('[CRAWL] Extracting forms, links, buttons...');
        }

        await sleep(300);
        if (cancelledRef.current) return;

        setProgress(10);

        // ---- PHASE 2: Send scan request (10% → 70%) ----
        setCurrentStep(1);
        setCurrentDetail('Sending scan request to backend...');
        if (isEcom) {
          addLog('[ECOM] Session & cookie analyzer started');
          addLog('[ECOM] Checking Set-Cookie flags...');
        } else {
          addLog('[SCAN] Headers scanner started');
          addLog('[SCAN] SSL/TLS scanner started');
        }

        const tickInterval = setInterval(() => {
          if (cancelledRef.current) { clearInterval(tickInterval); return; }
          setProgress(prev => {
            if (prev >= 70) return 70;
            return prev + 1;
          });
        }, 800);

        // Step advancement during the wait
        const ecomStepLogs: Record<number, string[]> = {
          2: ['[ECOM] Ecommerce logic scanner started', '[ECOM] Checking price fields, cart inputs, coupons...'],
          3: ['[ECOM] Data exposure scanner started', '[ECOM] Probing .env, .git, API keys, backups...'],
        };
        const dastStepLogs: Record<number, string[]> = {
          2: ['[SCAN] XSS scanner started', '[SCAN] Testing reflected payloads...'],
          3: ['[SCAN] SQLi scanner started', '[SCAN] Testing error-based injection...'],
        };
        const activeStepLogs = isEcom ? ecomStepLogs : dastStepLogs;

        const stepAdvance = setInterval(() => {
          if (cancelledRef.current) { clearInterval(stepAdvance); return; }
          setCurrentStep(prev => {
            const next = prev + 1;
            if (next < scanSteps.length - 1) {
              setCurrentDetail(scanSteps[next].detail);
              (activeStepLogs[next] || []).forEach(msg => addLog(msg));
              return next;
            }
            return prev;
          });
        }, 5000);

        // ---- THE ACTUAL BACKEND CALL ----
        const response = await fetch(API.scan, {
          method: "POST",
          headers: { "Content-Type": "application/json", ...authHeader() },
          body: JSON.stringify({
            url: targetUrl,
            scans: selectedVulnerabilities,
            depth: scanProfile,
            stress_test: stressTest || false,
            scan_mode: scanMode || 'general',
          }),
          signal: controller.signal,
        });

        // Stop the waiting tickers immediately
        clearInterval(tickInterval);
        clearInterval(stepAdvance);

        if (cancelledRef.current) return;

        // ---- PHASE 3: Parse response (70% → 90%) ----
        setProgress(75);
        setCurrentStep(scanSteps.length - 1); // "Generating Report"
        setCurrentDetail('Processing scan results...');
        addLog('[AI] Generating security analysis...');

        const result = await response.json();

        if (cancelledRef.current) return;

        setProgress(85);
        addLog('[SCORE] Calculating severity weights...');

        // Store results
        localStorage.setItem("scanResults", JSON.stringify(result));
        resultReadyRef.current = true;

        // Merge backend scan_log
        if (result.scan_log && Array.isArray(result.scan_log)) {
          const backendLogs = result.scan_log.map(
            (entry: { timestamp: string; phase: string; message: string }) =>
              `[${entry.timestamp}] [${entry.phase}] ${entry.message}`
          );
          setLogEntries(prev => [...prev, ...backendLogs]);
        }

        setProgress(95);
        addLog('[DONE] All scanners finished.');

        // ---- PHASE 4: Finalize (95% → 100%) ----
        await sleep(400); // brief pause for the 95→100 visual
        if (cancelledRef.current) return;

        setProgress(100);
        setCurrentDetail('Finalizing Report...');
        addLog('[DONE] Redirecting to results dashboard...');
        setScanComplete(true);

        // Navigate after 800ms for smooth transition
        await sleep(800);
        if (!cancelledRef.current) {
          navigate("/results", { replace: true });
        }

      } catch (err: any) {
        if (err?.name === 'AbortError') {
          // User cancelled — do nothing
          return;
        }
        console.error("SCAN FAILED:", err);
        addLog(`[ERROR] Scan failed: ${err}`);
        setScanError(true);
        setCurrentDetail('Scan failed. Redirecting...');

        // Fallback: if we already got results before the error, navigate anyway
        if (resultReadyRef.current && !cancelledRef.current) {
          await sleep(1500);
          if (!cancelledRef.current) navigate("/results", { replace: true });
        } else {
          await sleep(3000);
          if (!cancelledRef.current) navigate("/scan", { replace: true });
        }
      }
    }

    runScan();

    // ---- SAFETY FALLBACK ----
    // If nothing happens after 90 seconds, force navigation
    const safetyTimeout = setTimeout(() => {
      if (!cancelledRef.current) {
        if (resultReadyRef.current) {
          navigate("/results", { replace: true });
        } else {
          navigate("/scan", { replace: true });
        }
      }
    }, 90000);

    // ---- CLEANUP ----
    return () => {
      cancelledRef.current = true;
      controller.abort();
      clearTimeout(safetyTimeout);
    };
  }, [navigate, addLog]);

  const handleCancel = () => {
    cancelledRef.current = true;
    abortControllerRef.current?.abort();
    navigate('/scan');
  };

  const getStepStatus = (index: number) => {
    if (scanComplete) return 'complete';
    if (index < currentStep) return 'complete';
    if (index === currentStep) return 'active';
    return 'pending';
  };

  return (
    <div className="min-h-screen bg-cyber-dark cyber-grid-bg relative overflow-hidden">
      <div className="scan-line" />

      <motion.div
        className="absolute top-1/3 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-cyber-purple/5 rounded-full blur-[150px] pointer-events-none"
        animate={{ scale: [1, 1.2, 1], opacity: [0.3, 0.6, 0.3] }}
        transition={{ duration: 4, repeat: Infinity }}
      />

      <div className="relative z-10 flex items-center justify-center min-h-screen p-6">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="w-full max-w-[600px]"
        >
          <div className="glass-card-strong rounded-2xl p-8 shadow-[var(--shadow-card)]">

            {/* Header */}
            <div className="flex flex-col items-center mb-8">
              <motion.div
                className="w-18 h-18 rounded-2xl bg-cyber-purple/10 border border-cyber-purple/30 flex items-center justify-center mb-5"
                animate={{
                  boxShadow: scanComplete
                    ? ['0 0 30px rgba(16,185,129,0.3)', '0 0 60px rgba(16,185,129,0.5)', '0 0 30px rgba(16,185,129,0.3)']
                    : ['0 0 20px rgba(139,92,246,0.2)', '0 0 50px rgba(139,92,246,0.5)', '0 0 20px rgba(139,92,246,0.2)'],
                }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                {scanComplete ? (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: 'spring', stiffness: 300 }}
                  >
                    <Sparkles className="w-9 h-9 text-cyber-success" />
                  </motion.div>
                ) : (
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                  >
                    <ShieldAlert className="w-9 h-9 text-cyber-purple" />
                  </motion.div>
                )}
              </motion.div>

              <h1 className="text-[24px] font-bold text-white mb-1">
                {scanComplete ? 'Scan Complete!' : scanError ? 'Scan Error' : 'Scanning in Progress'}
              </h1>
              <p className="text-[13px] text-cyber-text-dim text-center">
                {scanComplete ? 'Redirecting to results...' : 'DAST engine is analyzing your target'}
              </p>
            </div>

            {/* Progress Ring */}
            <div className="flex justify-center mb-6">
              <div className="relative w-24 h-24">
                <svg className="transform -rotate-90" width="96" height="96">
                  <circle cx="48" cy="48" r="40" fill="none" stroke="#1E1E30" strokeWidth="5" />
                  <motion.circle
                    cx="48" cy="48" r="40"
                    fill="none"
                    stroke={scanComplete ? '#10B981' : 'url(#progressGradient)'}
                    strokeWidth="5"
                    strokeLinecap="round"
                    strokeDasharray={251.3}
                    animate={{ strokeDashoffset: 251.3 - (251.3 * progress) / 100 }}
                    transition={{ duration: 0.5, ease: 'easeOut' }}
                  />
                  <defs>
                    <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" stopColor="#8B5CF6" />
                      <stop offset="100%" stopColor="#C084FC" />
                    </linearGradient>
                  </defs>
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className={`text-[22px] font-bold ${scanComplete ? 'text-cyber-success' : 'text-white'}`}>
                    {progress}%
                  </span>
                </div>
              </div>
            </div>

            {/* Progress bar */}
            <div className="w-full h-1 bg-cyber-surface rounded-full overflow-hidden mb-6">
              <motion.div
                className={`h-full rounded-full ${scanComplete
                  ? 'bg-gradient-to-r from-emerald-500 to-emerald-400'
                  : 'bg-gradient-to-r from-cyber-purple to-cyber-neon'
                  }`}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
                style={{ boxShadow: scanComplete ? '0 0 8px rgba(16,185,129,0.5)' : '0 0 8px rgba(139,92,246,0.5)' }}
              />
            </div>

            {/* 5-Step Indicator */}
            <div className="space-y-2 mb-6">
              {scanSteps.map((step, index) => {
                const status = getStepStatus(index);
                return (
                  <motion.div
                    key={step.id}
                    initial={{ opacity: 0, x: -15 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.08 }}
                    className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-300 ${status === 'active' ? 'bg-cyber-purple/10 border border-cyber-purple/20' : ''
                      }`}
                  >
                    <div className="flex-shrink-0">
                      {status === 'complete' && <CheckCircle2 className="w-4 h-4 text-cyber-success" />}
                      {status === 'active' && <Loader2 className="w-4 h-4 text-cyber-purple animate-spin" />}
                      {status === 'pending' && <Circle className="w-4 h-4 text-cyber-text-muted" />}
                    </div>
                    <span className={`text-[13px] font-medium ${status === 'active' ? 'text-cyber-purple'
                      : status === 'complete' ? 'text-cyber-text-dim'
                        : 'text-cyber-text-muted'
                      }`}>
                      {step.name}
                    </span>
                  </motion.div>
                );
              })}
            </div>

            {/* Log Stream */}
            <div className="mb-5">
              <div className="flex items-center gap-2 mb-2">
                <Terminal className="w-3.5 h-3.5 text-cyber-text-muted" />
                <span className="text-[11px] text-cyber-text-muted uppercase tracking-wider font-medium">Scan Log</span>
              </div>
              <div
                ref={logRef}
                className="bg-cyber-dark rounded-lg border border-cyber-border p-3 h-[130px] overflow-y-auto font-mono"
              >
                {logEntries.map((entry, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -5 }}
                    animate={{ opacity: 1, x: 0 }}
                    className={`text-[11px] leading-relaxed ${entry.includes('[ERROR]') ? 'text-cyber-danger'
                      : entry.includes('[DONE]') ? 'text-cyber-success'
                        : entry.includes('[SCAN]') ? 'text-cyber-glow'
                          : entry.includes('[CRAWL]') ? 'text-cyber-neon'
                            : entry.includes('[AI]') || entry.includes('[SCORE]') ? 'text-cyber-purple'
                              : 'text-cyber-text-muted'
                      }`}
                  >
                    {entry}
                  </motion.div>
                ))}
                {!scanComplete && (
                  <motion.span
                    animate={{ opacity: [1, 0] }}
                    transition={{ duration: 0.8, repeat: Infinity }}
                    className="text-cyber-purple text-[11px]"
                  >
                    ▌
                  </motion.span>
                )}
              </div>
            </div>

            {/* Current Detail */}
            <AnimatePresence mode="wait">
              <motion.div
                key={currentDetail}
                initial={{ opacity: 0, y: 5 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -5 }}
                className="text-center mb-4"
              >
                <p className={`text-[12px] ${scanComplete ? 'text-cyber-success font-medium' : 'text-cyber-text-muted'}`}>
                  {currentDetail}
                </p>
              </motion.div>
            </AnimatePresence>

            {/* Cancel (hidden when complete) */}
            {!scanComplete && (
              <div className="flex justify-center">
                <button
                  onClick={handleCancel}
                  className="text-[12px] text-cyber-text-muted hover:text-cyber-danger transition-colors duration-200"
                >
                  Cancel Scan
                </button>
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  );
}

/** Non-blocking sleep helper */
function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}
