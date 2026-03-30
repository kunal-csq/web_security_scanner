import { useNavigate } from 'react-router-dom';
import { ArrowRight, Play } from 'lucide-react';
import { motion } from 'framer-motion';

export function HeroSection() {
    const navigate = useNavigate();

    return (
        <section className="relative min-h-[92vh] flex items-center overflow-hidden">
            {/* Background effects */}
            <div className="absolute inset-0 cyber-grid-bg" />
            <div className="absolute top-[10%] left-[10%] w-[600px] h-[600px] bg-cyber-purple/[0.04] rounded-full blur-[150px] pointer-events-none" />
            <div className="absolute bottom-[10%] right-[10%] w-[500px] h-[500px] bg-cyber-neon/[0.03] rounded-full blur-[130px] pointer-events-none" />

            {/* Animated gradient wave at bottom */}
            <div className="absolute bottom-0 left-0 right-0 h-[200px] bg-gradient-to-t from-cyber-purple/[0.03] to-transparent pointer-events-none" />

            <div className="relative z-10 max-w-[1320px] mx-auto px-6 w-full">
                <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">

                    {/* LEFT — Copy */}
                    <motion.div
                        initial={{ opacity: 0, x: -40 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.7 }}
                    >
                        {/* Badge */}
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.2 }}
                            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-cyber-purple/10 border border-cyber-purple/25 mb-6"
                        >
                            <span className="w-2 h-2 rounded-full bg-cyber-success animate-pulse" />
                            <span className="text-[12px] text-cyber-glow font-medium tracking-wide">DAST Engine v2.1 — Now Live</span>
                        </motion.div>

                        <h1 className="text-[44px] lg:text-[56px] font-extrabold text-white leading-[1.08] tracking-tight mb-6">
                            Enterprise-Grade{' '}
                            <span className="bg-gradient-to-r from-cyber-purple via-cyber-glow to-cyber-neon bg-clip-text text-transparent">
                                Dynamic Security
                            </span>{' '}
                            Scanning
                        </h1>

                        <p className="text-[17px] lg:text-[19px] text-cyber-text-dim leading-relaxed max-w-[540px] mb-10">
                            Automated DAST, vulnerability detection, and security analytics built for modern web applications. Crawl SPAs, test for SQLi, XSS, CSRF, and more.
                        </p>

                        {/* CTAs */}
                        <div className="flex flex-wrap gap-4">
                            <motion.button
                                whileHover={{ boxShadow: '0 0 40px rgba(139,92,246,0.5)', scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                onClick={() => navigate('/scan')}
                                className="flex items-center gap-2.5 px-7 py-3.5 text-[15px] font-semibold text-white bg-gradient-to-r from-cyber-purple to-cyber-neon rounded-xl shadow-[0_0_25px_rgba(139,92,246,0.35)] transition-all duration-300"
                            >
                                Start Free Scan
                                <ArrowRight className="w-4 h-4" />
                            </motion.button>

                            <motion.button
                                whileHover={{ scale: 1.02, borderColor: 'rgba(192,132,252,0.5)' }}
                                whileTap={{ scale: 0.98 }}
                                className="flex items-center gap-2.5 px-7 py-3.5 text-[15px] font-medium text-cyber-neon border border-cyber-neon/30 rounded-xl hover:bg-cyber-neon/5 transition-all duration-300"
                            >
                                <Play className="w-4 h-4" />
                                View Demo
                            </motion.button>
                        </div>

                        {/* Trust indicators */}
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.8 }}
                            className="flex items-center gap-6 mt-10"
                        >
                            {[
                                { value: '7', label: 'Scan Modules' },
                                { value: '<30s', label: 'Quick Scan' },
                                { value: '0', label: 'False Positives' },
                            ].map(stat => (
                                <div key={stat.label} className="text-center">
                                    <div className="text-[20px] font-bold text-cyber-glow">{stat.value}</div>
                                    <div className="text-[11px] text-cyber-text-muted uppercase tracking-wider">{stat.label}</div>
                                </div>
                            ))}
                        </motion.div>
                    </motion.div>

                    {/* RIGHT — Dashboard Preview Card */}
                    <motion.div
                        initial={{ opacity: 0, x: 40, rotateY: -5 }}
                        animate={{ opacity: 1, x: 0, rotateY: 0 }}
                        transition={{ duration: 0.8, delay: 0.3 }}
                        className="hidden lg:block"
                    >
                        <div className="relative">
                            {/* Glow behind card */}
                            <div className="absolute -inset-4 bg-gradient-to-br from-cyber-purple/20 via-transparent to-cyber-neon/10 rounded-3xl blur-2xl pointer-events-none" />

                            <div className="relative glass-card rounded-2xl p-6 border border-cyber-purple/20">
                                {/* Fake title bar */}
                                <div className="flex items-center gap-2 mb-5">
                                    <div className="w-3 h-3 rounded-full bg-red-500/60" />
                                    <div className="w-3 h-3 rounded-full bg-yellow-500/60" />
                                    <div className="w-3 h-3 rounded-full bg-green-500/60" />
                                    <span className="ml-3 text-[11px] text-cyber-text-muted font-mono">WebSec AI — Dashboard</span>
                                </div>

                                {/* Score + stats row */}
                                <div className="grid grid-cols-3 gap-3 mb-4">
                                    <div className="bg-cyber-surface rounded-xl p-4 flex flex-col items-center">
                                        <div className="w-16 h-16 rounded-full p-[3px] mb-2"
                                            style={{ background: 'conic-gradient(#10B981 288deg, #1E1E30 0deg)' }}>
                                            <div className="w-full h-full rounded-full bg-cyber-card flex items-center justify-center">
                                                <span className="text-[18px] font-bold text-emerald-400">80</span>
                                            </div>
                                        </div>
                                        <span className="text-[10px] text-cyber-text-muted">Score</span>
                                    </div>
                                    <div className="bg-cyber-surface rounded-xl p-4 text-center">
                                        <div className="text-[22px] font-bold text-red-400 mb-1">2</div>
                                        <span className="text-[10px] text-cyber-text-muted">Critical</span>
                                    </div>
                                    <div className="bg-cyber-surface rounded-xl p-4 text-center">
                                        <div className="text-[22px] font-bold text-cyber-purple mb-1">5</div>
                                        <span className="text-[10px] text-cyber-text-muted">High</span>
                                    </div>
                                </div>

                                {/* Fake vulnerability rows */}
                                {[
                                    { name: 'SQL Injection (Error-Based)', sev: 'Critical', color: '#EF4444' },
                                    { name: 'Reflected XSS', sev: 'High', color: '#8B5CF6' },
                                    { name: 'Missing CSP Header', sev: 'Medium', color: '#A78BFA' },
                                ].map((row, i) => (
                                    <motion.div
                                        key={row.name}
                                        initial={{ opacity: 0, x: 10 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: 0.8 + i * 0.15 }}
                                        className="flex items-center justify-between px-3 py-2.5 rounded-lg bg-cyber-surface/50 mb-2"
                                    >
                                        <span className="text-[12px] text-cyber-text-dim truncate mr-3">{row.name}</span>
                                        <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full"
                                            style={{ color: row.color, backgroundColor: `${row.color}15` }}>
                                            {row.sev}
                                        </span>
                                    </motion.div>
                                ))}
                            </div>
                        </div>
                    </motion.div>
                </div>
            </div>
        </section>
    );
}
