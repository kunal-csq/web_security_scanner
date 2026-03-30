import { ShieldCheck, Database, Code, Activity } from 'lucide-react';
import { motion } from 'framer-motion';

const features = [
    {
        icon: ShieldCheck,
        title: 'Dynamic Application Testing',
        description: 'Crawl SPAs built with React, Angular, and Vue. Detect forms, inputs, query parameters, and build a comprehensive endpoint map automatically.',
        color: '#8B5CF6',
    },
    {
        icon: Database,
        title: 'SQL Injection Detection',
        description: 'Error-based, time-based blind, and authentication bypass SQL injection scanning across all discovered endpoints and parameters.',
        color: '#A78BFA',
    },
    {
        icon: Code,
        title: 'XSS Detection',
        description: 'Reflected, DOM-based, and context-aware Cross-Site Scripting detection with intelligent payload selection and output encoding analysis.',
        color: '#C084FC',
    },
    {
        icon: Activity,
        title: 'Load & Stability Testing',
        description: 'Controlled concurrent load testing measuring response times, error rates, and application stability with built-in safety throttling.',
        color: '#818CF8',
    },
];

export function FeatureSection() {
    return (
        <section id="features" className="relative py-28">
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
                        Everything You Need to{' '}
                        <span className="bg-gradient-to-r from-cyber-purple to-cyber-neon bg-clip-text text-transparent">
                            Secure Your App
                        </span>
                    </h2>
                    <p className="text-[16px] text-cyber-text-dim max-w-[560px] mx-auto leading-relaxed">
                        Seven scanner modules running concurrently, powered by an async engine with configurable depth and intelligent crawling.
                    </p>
                </motion.div>

                {/* Cards */}
                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-5">
                    {features.map((feature, i) => (
                        <motion.div
                            key={feature.title}
                            initial={{ opacity: 0, y: 30 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true, margin: '-50px' }}
                            transition={{ delay: i * 0.1, duration: 0.5 }}
                            whileHover={{ y: -6, boxShadow: `0 0 30px ${feature.color}18` }}
                            className="group glass-card rounded-2xl p-7 cursor-default transition-all duration-300 hover:border-cyber-purple/30"
                        >
                            <div
                                className="w-12 h-12 rounded-xl flex items-center justify-center mb-5 transition-all duration-300 group-hover:shadow-[0_0_20px_rgba(139,92,246,0.2)]"
                                style={{ backgroundColor: `${feature.color}12` }}
                            >
                                <feature.icon className="w-6 h-6" style={{ color: feature.color }} />
                            </div>

                            <h3 className="text-[17px] font-bold text-white mb-2.5 group-hover:text-cyber-glow transition-colors">
                                {feature.title}
                            </h3>

                            <p className="text-[13px] text-cyber-text-muted leading-relaxed">
                                {feature.description}
                            </p>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}
