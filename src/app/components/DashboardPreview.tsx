import { motion } from 'framer-motion';

export function DashboardPreview() {
    return (
        <section id="dashboard" className="relative py-28 overflow-hidden">
            <div className="absolute inset-0 cyber-grid-bg" />
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[900px] h-[500px] bg-cyber-purple/[0.03] rounded-full blur-[200px] pointer-events-none" />

            <div className="relative z-10 max-w-[1320px] mx-auto px-6">

                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true, margin: '-100px' }}
                    className="text-center mb-14"
                >
                    <span className="inline-block text-[12px] text-cyber-purple font-semibold uppercase tracking-[0.2em] mb-3">
                        Dashboard
                    </span>
                    <h2 className="text-[36px] lg:text-[42px] font-extrabold text-white tracking-tight mb-4">
                        Security Intelligence at a{' '}
                        <span className="bg-gradient-to-r from-cyber-purple to-cyber-neon bg-clip-text text-transparent">Glance</span>
                    </h2>
                    <p className="text-[16px] text-cyber-text-dim max-w-[500px] mx-auto">
                        Real-time insights with AI-powered analysis, severity scoring, and actionable recommendations.
                    </p>
                </motion.div>

                {/* Dashboard Mock */}
                <motion.div
                    initial={{ opacity: 0, y: 40 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.7 }}
                    className="relative max-w-[1000px] mx-auto"
                >
                    {/* Glow behind */}
                    <div className="absolute -inset-6 bg-gradient-to-b from-cyber-purple/10 via-transparent to-transparent rounded-3xl blur-2xl pointer-events-none" />

                    <div className="relative glass-card rounded-2xl border border-cyber-purple/15 overflow-hidden">

                        {/* Title bar */}
                        <div className="flex items-center gap-2 px-5 py-3 border-b border-cyber-border">
                            <div className="w-3 h-3 rounded-full bg-red-500/60" />
                            <div className="w-3 h-3 rounded-full bg-yellow-500/60" />
                            <div className="w-3 h-3 rounded-full bg-green-500/60" />
                            <span className="ml-3 text-[11px] text-cyber-text-muted font-mono">WebSec AI — Security Report — example.com</span>
                        </div>

                        <div className="p-6">
                            <div className="grid lg:grid-cols-4 gap-4 mb-5">

                                {/* Score ring */}
                                <div className="bg-cyber-surface rounded-xl p-5 flex flex-col items-center justify-center">
                                    <div className="w-20 h-20 rounded-full p-[4px] mb-2"
                                        style={{ background: 'conic-gradient(#10B981 270deg, #1E1E30 0deg)' }}>
                                        <div className="w-full h-full rounded-full bg-cyber-card flex items-center justify-center">
                                            <span className="text-[24px] font-bold text-emerald-400">75</span>
                                        </div>
                                    </div>
                                    <span className="text-[11px] text-cyber-text-muted">Security Score</span>
                                    <span className="text-[10px] font-bold text-emerald-400 mt-0.5">Grade: B</span>
                                </div>

                                {/* Severity cards */}
                                {[
                                    { label: 'Critical', count: 1, color: '#EF4444' },
                                    { label: 'High', count: 3, color: '#8B5CF6' },
                                    { label: 'Medium', count: 5, color: '#A78BFA' },
                                ].map(sev => (
                                    <div key={sev.label} className="bg-cyber-surface rounded-xl p-5">
                                        <span className="text-[10px] text-cyber-text-muted uppercase tracking-wider">{sev.label}</span>
                                        <div className="text-[28px] font-bold mt-1" style={{ color: sev.color }}>{sev.count}</div>
                                        <div className="w-full h-1 bg-cyber-card rounded-full mt-2">
                                            <div className="h-full rounded-full" style={{ width: `${sev.count * 20}%`, backgroundColor: sev.color }} />
                                        </div>
                                    </div>
                                ))}
                            </div>

                            {/* Vulnerability rows */}
                            <div className="grid lg:grid-cols-2 gap-3">
                                {[
                                    { name: 'SQL Injection (Error-Based)', sev: 'Critical', color: '#EF4444', loc: '/api/login' },
                                    { name: 'Reflected XSS in search', sev: 'High', color: '#8B5CF6', loc: '/search?q=' },
                                    { name: 'Missing Content-Security-Policy', sev: 'Medium', color: '#A78BFA', loc: 'Response Headers' },
                                    { name: 'CSRF Token Missing', sev: 'High', color: '#8B5CF6', loc: '/account/settings' },
                                    { name: 'Insecure Cookie (no HttpOnly)', sev: 'Medium', color: '#A78BFA', loc: 'Set-Cookie header' },
                                    { name: 'TLS 1.0 Supported', sev: 'High', color: '#8B5CF6', loc: 'SSL Configuration' },
                                ].map((vuln, i) => (
                                    <motion.div
                                        key={vuln.name}
                                        initial={{ opacity: 0, x: -10 }}
                                        whileInView={{ opacity: 1, x: 0 }}
                                        viewport={{ once: true }}
                                        transition={{ delay: 0.3 + i * 0.08 }}
                                        className="flex items-center justify-between px-4 py-3 rounded-lg bg-cyber-card/60 border border-cyber-border hover:border-cyber-purple/25 transition-colors"
                                    >
                                        <div className="flex-1 min-w-0 mr-3">
                                            <div className="text-[12px] text-cyber-text truncate">{vuln.name}</div>
                                            <div className="text-[10px] text-cyber-text-muted font-mono truncate">{vuln.loc}</div>
                                        </div>
                                        <span className="text-[10px] font-semibold px-2.5 py-1 rounded-full flex-shrink-0"
                                            style={{ color: vuln.color, backgroundColor: `${vuln.color}12`, border: `1px solid ${vuln.color}25` }}>
                                            {vuln.sev}
                                        </span>
                                    </motion.div>
                                ))}
                            </div>
                        </div>
                    </div>
                </motion.div>
            </div>
        </section>
    );
}
