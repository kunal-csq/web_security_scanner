import { useNavigate } from 'react-router-dom';
import { ArrowRight, Shield, ShoppingCart } from 'lucide-react';
import { motion } from 'framer-motion';

export function CTASection() {
    const navigate = useNavigate();

    return (
        <section className="relative py-24 overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-cyber-purple/15 via-cyber-dark to-amber-500/8" />
            <div className="absolute inset-0 cyber-grid-bg" />
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[300px] bg-cyber-purple/10 rounded-full blur-[120px] pointer-events-none" />

            <div className="relative z-10 max-w-[700px] mx-auto px-6 text-center">
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6 }}
                >
                    <h2 className="text-[36px] lg:text-[44px] font-extrabold text-white tracking-tight mb-5 leading-tight">
                        Start Scanning{' '}
                        <span className="bg-gradient-to-r from-cyber-purple to-cyber-neon bg-clip-text text-transparent">Today</span>
                    </h2>

                    <p className="text-[16px] text-cyber-text-dim leading-relaxed mb-10 max-w-[480px] mx-auto">
                        No installation. No setup. Pick a mode, enter a URL, and get actionable security insights in seconds.
                    </p>

                    <div className="flex flex-wrap justify-center gap-3">
                        <motion.button
                            whileHover={{ scale: 1.03, boxShadow: '0 0 50px rgba(139,92,246,0.5)' }}
                            whileTap={{ scale: 0.97 }}
                            onClick={() => navigate('/scan?mode=general')}
                            className="inline-flex items-center gap-2.5 px-8 py-4 text-[15px] font-bold text-white bg-gradient-to-r from-cyber-purple to-cyber-neon rounded-xl shadow-[0_0_30px_rgba(139,92,246,0.4)] transition-all duration-300"
                        >
                            <Shield className="w-5 h-5" />
                            DAST Scan
                            <ArrowRight className="w-4 h-4" />
                        </motion.button>

                        <motion.button
                            whileHover={{ scale: 1.03, boxShadow: '0 0 50px rgba(245,158,11,0.5)' }}
                            whileTap={{ scale: 0.97 }}
                            onClick={() => navigate('/scan?mode=ecommerce')}
                            className="inline-flex items-center gap-2.5 px-8 py-4 text-[15px] font-bold text-white bg-gradient-to-r from-amber-500 to-orange-500 rounded-xl shadow-[0_0_30px_rgba(245,158,11,0.4)] transition-all duration-300"
                        >
                            <ShoppingCart className="w-5 h-5" />
                            Ecommerce Scan
                            <ArrowRight className="w-4 h-4" />
                        </motion.button>
                    </div>
                </motion.div>
            </div>
        </section>
    );
}
