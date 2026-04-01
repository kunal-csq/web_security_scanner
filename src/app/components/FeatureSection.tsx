import { Shield, ShoppingCart, Database, Code, CreditCard, Package, Lock, Activity, Server, Bot } from 'lucide-react';
import { motion } from 'framer-motion';

const dastFeatures = [
    { icon: Database, title: 'SQL Injection', description: 'Error-based, time-based blind, and auth bypass detection', color: '#8B5CF6' },
    { icon: Code, title: 'XSS Detection', description: 'Reflected, DOM-based, and context-aware payload testing', color: '#A78BFA' },
    { icon: Lock, title: 'Auth & Session', description: 'Cookie flags, session rotation, and JWT leakage checks', color: '#C084FC' },
    { icon: Activity, title: 'Load Testing', description: 'Controlled stress test with stability metrics', color: '#818CF8' },
];

const ecomFeatures = [
    { icon: CreditCard, title: 'Payment Security', description: 'Price manipulation, cart tampering, and payment bypass', color: '#F59E0B' },
    { icon: Package, title: 'Order Security', description: 'Predictable order IDs, coupon abuse, and refund exploits', color: '#EF4444' },
    { icon: Server, title: 'API & Data', description: 'Exposed .env files, API keys, and unauthenticated endpoints', color: '#10B981' },
    { icon: Bot, title: 'Bot Defense', description: 'CAPTCHA, rate limiting, and anti-automation checks', color: '#3B82F6' },
];

export function FeatureSection() {
    return (
        <section id="features" className="relative py-24">
            <div className="absolute inset-0 cyber-grid-bg" />
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] bg-cyber-purple/[0.02] rounded-full blur-[180px] pointer-events-none" />

            <div className="relative z-10 max-w-[1320px] mx-auto px-6">

                {/* Section header */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true, margin: '-100px' }}
                    transition={{ duration: 0.5 }}
                    className="text-center mb-16"
                >
                    <span className="inline-block text-[12px] text-cyber-purple font-semibold uppercase tracking-[0.2em] mb-3">
                        Capabilities
                    </span>
                    <h2 className="text-[36px] lg:text-[42px] font-extrabold text-white tracking-tight mb-4">
                        Two Engines, One{' '}
                        <span className="bg-gradient-to-r from-cyber-purple to-cyber-neon bg-clip-text text-transparent">
                            Platform
                        </span>
                    </h2>
                    <p className="text-[16px] text-cyber-text-dim max-w-[560px] mx-auto leading-relaxed">
                        Choose the scanner that fits your target. General DAST for web apps, Ecommerce scanner for online stores.
                    </p>
                </motion.div>

                {/* Two columns */}
                <div className="grid lg:grid-cols-2 gap-8">

                    {/* DAST Column */}
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.5 }}
                    >
                        <div className="flex items-center gap-3 mb-5">
                            <div className="w-10 h-10 rounded-xl bg-cyber-purple/10 border border-cyber-purple/30 flex items-center justify-center">
                                <Shield className="w-5 h-5 text-cyber-purple" />
                            </div>
                            <div>
                                <h3 className="text-[18px] font-bold text-white">General DAST</h3>
                                <p className="text-[12px] text-cyber-text-muted">6 scanner modules • 3 depth levels</p>
                            </div>
                        </div>
                        <div className="grid grid-cols-2 gap-3">
                            {dastFeatures.map((f, i) => (
                                <motion.div
                                    key={f.title}
                                    initial={{ opacity: 0, y: 20 }}
                                    whileInView={{ opacity: 1, y: 0 }}
                                    viewport={{ once: true }}
                                    transition={{ delay: i * 0.08 }}
                                    whileHover={{ y: -4, boxShadow: `0 0 25px ${f.color}15` }}
                                    className="glass-card rounded-xl p-5 cursor-default transition-all duration-300 hover:border-cyber-purple/25"
                                >
                                    <div className="w-10 h-10 rounded-lg flex items-center justify-center mb-3"
                                        style={{ backgroundColor: `${f.color}12` }}>
                                        <f.icon className="w-5 h-5" style={{ color: f.color }} />
                                    </div>
                                    <h4 className="text-[14px] font-bold text-white mb-1">{f.title}</h4>
                                    <p className="text-[12px] text-cyber-text-muted leading-relaxed">{f.description}</p>
                                </motion.div>
                            ))}
                        </div>
                    </motion.div>

                    {/* Ecommerce Column */}
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.5, delay: 0.15 }}
                    >
                        <div className="flex items-center gap-3 mb-5">
                            <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center">
                                <ShoppingCart className="w-5 h-5 text-amber-400" />
                            </div>
                            <div>
                                <h3 className="text-[18px] font-bold text-white">Ecommerce Scanner</h3>
                                <p className="text-[12px] text-cyber-text-muted">8 check categories • OWASP aligned</p>
                            </div>
                        </div>
                        <div className="grid grid-cols-2 gap-3">
                            {ecomFeatures.map((f, i) => (
                                <motion.div
                                    key={f.title}
                                    initial={{ opacity: 0, y: 20 }}
                                    whileInView={{ opacity: 1, y: 0 }}
                                    viewport={{ once: true }}
                                    transition={{ delay: i * 0.08 }}
                                    whileHover={{ y: -4, boxShadow: `0 0 25px ${f.color}15` }}
                                    className="glass-card rounded-xl p-5 cursor-default transition-all duration-300 hover:border-amber-500/25"
                                >
                                    <div className="w-10 h-10 rounded-lg flex items-center justify-center mb-3"
                                        style={{ backgroundColor: `${f.color}12` }}>
                                        <f.icon className="w-5 h-5" style={{ color: f.color }} />
                                    </div>
                                    <h4 className="text-[14px] font-bold text-white mb-1">{f.title}</h4>
                                    <p className="text-[12px] text-cyber-text-muted leading-relaxed">{f.description}</p>
                                </motion.div>
                            ))}
                        </div>
                    </motion.div>
                </div>
            </div>
        </section>
    );
}
