import { useNavigate } from 'react-router-dom';
import { ArrowRight, Shield, ShoppingCart } from 'lucide-react';
import { motion } from 'framer-motion';

export function HeroSection() {
    const navigate = useNavigate();

    return (
        <section className="relative min-h-[92vh] flex items-center overflow-hidden">
            <div className="absolute inset-0 cyber-grid-bg" />
            <div className="absolute top-[10%] left-[10%] w-[600px] h-[600px] bg-cyber-purple/[0.04] rounded-full blur-[150px] pointer-events-none" />
            <div className="absolute bottom-[10%] right-[10%] w-[500px] h-[500px] bg-amber-500/[0.03] rounded-full blur-[130px] pointer-events-none" />
            <div className="absolute bottom-0 left-0 right-0 h-[200px] bg-gradient-to-t from-cyber-purple/[0.03] to-transparent pointer-events-none" />

            <div className="relative z-10 max-w-[1320px] mx-auto px-6 w-full">
                <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">

                    {/* LEFT — Copy */}
                    <motion.div
                        initial={{ opacity: 0, x: -40 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.7 }}
                    >
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.2 }}
                            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-cyber-purple/10 border border-cyber-purple/25 mb-6"
                        >
                            <span className="w-2 h-2 rounded-full bg-cyber-success animate-pulse" />
                            <span className="text-[12px] text-cyber-glow font-medium tracking-wide">DAST + Ecommerce Scanner — Live</span>
                        </motion.div>

                        <h1 className="text-[44px] lg:text-[56px] font-extrabold text-white leading-[1.08] tracking-tight mb-6">
                            Web Security{' '}
                            <span className="bg-gradient-to-r from-cyber-purple via-cyber-glow to-cyber-neon bg-clip-text text-transparent">
                                Testing Platform
                            </span>
                        </h1>

                        <p className="text-[17px] lg:text-[19px] text-cyber-text-dim leading-relaxed max-w-[540px] mb-10">
                            Two scanning engines in one platform. Run DAST security audits on any web app, or specialized ecommerce security assessments on online stores.
                        </p>

                        {/* CTAs */}
                        <div className="flex flex-wrap gap-3">
                            <motion.button
                                whileHover={{ boxShadow: '0 0 40px rgba(139,92,246,0.5)', scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                onClick={() => navigate('/scan?mode=general')}
                                className="flex items-center gap-2.5 px-7 py-3.5 text-[15px] font-semibold text-white bg-gradient-to-r from-cyber-purple to-cyber-neon rounded-xl shadow-[0_0_25px_rgba(139,92,246,0.35)] transition-all duration-300"
                            >
                                <Shield className="w-4 h-4" />
                                DAST Scan
                                <ArrowRight className="w-4 h-4" />
                            </motion.button>

                            <motion.button
                                whileHover={{ boxShadow: '0 0 40px rgba(245,158,11,0.5)', scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                onClick={() => navigate('/scan?mode=ecommerce')}
                                className="flex items-center gap-2.5 px-7 py-3.5 text-[15px] font-semibold text-white bg-gradient-to-r from-amber-500 to-orange-500 rounded-xl shadow-[0_0_25px_rgba(245,158,11,0.35)] transition-all duration-300"
                            >
                                <ShoppingCart className="w-4 h-4" />
                                Ecommerce Scan
                                <ArrowRight className="w-4 h-4" />
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
                                { value: '15+', label: 'Scan Modules' },
                                { value: '<30s', label: 'Quick Scan' },
                                { value: '2', label: 'Engine Modes' },
                            ].map(stat => (
                                <div key={stat.label} className="text-center">
                                    <div className="text-[20px] font-bold text-cyber-glow">{stat.value}</div>
                                    <div className="text-[11px] text-cyber-text-muted uppercase tracking-wider">{stat.label}</div>
                                </div>
                            ))}
                        </motion.div>
                    </motion.div>

                    {/* RIGHT — Two mode cards */}
                    <motion.div
                        initial={{ opacity: 0, x: 40 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.8, delay: 0.3 }}
                        className="hidden lg:flex flex-col gap-4"
                    >
                        {/* DAST Card */}
                        <motion.div
                            whileHover={{ borderColor: 'rgba(139,92,246,0.4)', y: -3 }}
                            className="glass-card-strong rounded-2xl p-5 border border-cyber-purple/15 transition-all duration-300 cursor-pointer hover:shadow-[0_0_30px_rgba(139,92,246,0.08)]"
                            onClick={() => navigate('/scan?mode=general')}
                        >
                            <div className="flex items-center gap-3 mb-3">
                                <div className="w-10 h-10 rounded-xl bg-cyber-purple/10 border border-cyber-purple/30 flex items-center justify-center">
                                    <Shield className="w-5 h-5 text-cyber-purple" />
                                </div>
                                <div>
                                    <div className="text-[15px] font-bold text-white">General DAST</div>
                                    <div className="text-[11px] text-cyber-text-muted">Web Application Security</div>
                                </div>
                            </div>
                            <div className="grid grid-cols-3 gap-2">
                                {['SQL Injection', 'XSS', 'CSRF', 'SSL/TLS', 'Headers', 'Auth Flaws'].map(m => (
                                    <div key={m} className="px-2 py-1.5 rounded-lg bg-cyber-surface text-[10px] text-cyber-text-dim text-center">
                                        {m}
                                    </div>
                                ))}
                            </div>
                        </motion.div>

                        {/* Ecommerce Card */}
                        <motion.div
                            whileHover={{ borderColor: 'rgba(245,158,11,0.4)', y: -3 }}
                            className="glass-card-strong rounded-2xl p-5 border border-amber-500/15 transition-all duration-300 cursor-pointer hover:shadow-[0_0_30px_rgba(245,158,11,0.08)]"
                            onClick={() => navigate('/scan?mode=ecommerce')}
                        >
                            <div className="flex items-center gap-3 mb-3">
                                <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center">
                                    <ShoppingCart className="w-5 h-5 text-amber-400" />
                                </div>
                                <div>
                                    <div className="text-[15px] font-bold text-white">Ecommerce Scanner</div>
                                    <div className="text-[11px] text-cyber-text-muted">Online Store Security</div>
                                </div>
                            </div>
                            <div className="grid grid-cols-4 gap-2">
                                {['Price Tamper', 'Cart Security', 'Coupon Abuse', 'IDOR', 'API Security', 'Bot Defense', 'Data Leak', 'Admin Exposed'].map(m => (
                                    <div key={m} className="px-2 py-1.5 rounded-lg bg-cyber-surface text-[10px] text-cyber-text-dim text-center">
                                        {m}
                                    </div>
                                ))}
                            </div>
                        </motion.div>
                    </motion.div>
                </div>
            </div>
        </section>
    );
}
