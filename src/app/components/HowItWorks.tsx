import { Globe, ShieldCheck, BarChart3, FileText } from 'lucide-react';
import { motion } from 'framer-motion';

const steps = [
    {
        icon: Globe,
        step: '01',
        title: 'Enter Target URL',
        description: 'Provide your website or store URL and choose General DAST or Ecommerce mode.',
    },
    {
        icon: ShieldCheck,
        step: '02',
        title: 'Select Scan Depth',
        description: 'Quick, Standard, or Deep — scan modules run concurrently for speed.',
    },
    {
        icon: BarChart3,
        step: '03',
        title: 'Get Results',
        description: 'Each vulnerability is scored by severity with evidence and fix recommendations.',
    },
    {
        icon: FileText,
        step: '04',
        title: 'AI Analysis',
        description: 'AI generates a risk summary, priority actions, and security grade for your target.',
    },
];

export function HowItWorks() {
    return (
        <section id="how-it-works" className="relative py-24 bg-cyber-surface/30">
            <div className="absolute inset-0 cyber-grid-bg opacity-50" />

            <div className="relative z-10 max-w-[1320px] mx-auto px-6">

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true, margin: '-100px' }}
                    className="text-center mb-16"
                >
                    <span className="inline-block text-[12px] text-cyber-purple font-semibold uppercase tracking-[0.2em] mb-3">
                        How It Works
                    </span>
                    <h2 className="text-[36px] lg:text-[42px] font-extrabold text-white tracking-tight mb-4">
                        Scan in{' '}
                        <span className="bg-gradient-to-r from-cyber-purple to-cyber-neon bg-clip-text text-transparent">
                            Four Steps
                        </span>
                    </h2>
                </motion.div>

                <div className="relative">
                    <div className="hidden lg:block absolute top-[60px] left-[12.5%] right-[12.5%] h-[2px] bg-gradient-to-r from-cyber-purple/30 via-cyber-glow/20 to-cyber-neon/30" />

                    <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                        {steps.map((step, i) => (
                            <motion.div
                                key={step.step}
                                initial={{ opacity: 0, y: 30 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true }}
                                transition={{ delay: i * 0.15, duration: 0.5 }}
                                className="relative text-center"
                            >
                                <div className="relative inline-flex items-center justify-center mb-6">
                                    <motion.div
                                        whileHover={{ boxShadow: '0 0 30px rgba(139,92,246,0.3)' }}
                                        className="w-[72px] h-[72px] rounded-2xl bg-cyber-card border border-cyber-purple/20 flex items-center justify-center transition-all duration-300"
                                    >
                                        <step.icon className="w-7 h-7 text-cyber-purple" />
                                    </motion.div>
                                    <span className="absolute -top-2 -right-2 w-7 h-7 rounded-full bg-cyber-purple text-white text-[11px] font-bold flex items-center justify-center shadow-[0_0_12px_rgba(139,92,246,0.4)]">
                                        {step.step}
                                    </span>
                                </div>

                                <h3 className="text-[16px] font-bold text-white mb-2">{step.title}</h3>
                                <p className="text-[13px] text-cyber-text-muted leading-relaxed max-w-[250px] mx-auto">
                                    {step.description}
                                </p>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </div>
        </section>
    );
}
