import { useNavigate } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';

export function CTASection() {
    const navigate = useNavigate();

    return (
        <section className="relative py-24 overflow-hidden">
            {/* Background gradient */}
            <div className="absolute inset-0 bg-gradient-to-br from-cyber-purple/15 via-cyber-dark to-cyber-neon/10" />
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
                        Secure Your Application{' '}
                        <span className="bg-gradient-to-r from-cyber-purple to-cyber-neon bg-clip-text text-transparent">Today</span>
                    </h2>

                    <p className="text-[16px] text-cyber-text-dim leading-relaxed mb-10 max-w-[480px] mx-auto">
                        Start scanning in seconds. No installation required. Get actionable security insights with AI-powered analysis.
                    </p>

                    <motion.button
                        whileHover={{ scale: 1.03, boxShadow: '0 0 50px rgba(139,92,246,0.5)' }}
                        whileTap={{ scale: 0.97 }}
                        onClick={() => navigate('/scan')}
                        className="inline-flex items-center gap-2.5 px-8 py-4 text-[16px] font-bold text-white bg-gradient-to-r from-cyber-purple to-cyber-neon rounded-xl shadow-[0_0_30px_rgba(139,92,246,0.4)] transition-all duration-300"
                    >
                        Start Free Scan
                        <ArrowRight className="w-5 h-5" />
                    </motion.button>
                </motion.div>
            </div>
        </section>
    );
}
