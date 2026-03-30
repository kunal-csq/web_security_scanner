import { Shield } from 'lucide-react';

const footerColumns = [
    {
        title: 'Product',
        links: ['DAST Scanner', 'Load Tester', 'API Security', 'CI/CD Integration'],
    },
    {
        title: 'Company',
        links: ['About Us', 'Careers', 'Blog', 'Contact'],
    },
    {
        title: 'Resources',
        links: ['Documentation', 'API Reference', 'Security Reports', 'Changelog'],
    },
    {
        title: 'Legal',
        links: ['Privacy Policy', 'Terms of Service', 'Cookie Policy', 'GDPR'],
    },
];

export function Footer() {
    return (
        <footer className="bg-cyber-surface border-t border-cyber-border">
            <div className="max-w-[1320px] mx-auto px-6 py-16">
                <div className="grid md:grid-cols-2 lg:grid-cols-5 gap-10 lg:gap-8">

                    {/* Brand column */}
                    <div className="lg:col-span-1">
                        <div className="flex items-center gap-2.5 mb-4">
                            <div className="w-8 h-8 rounded-lg bg-cyber-purple/15 border border-cyber-purple/30 flex items-center justify-center">
                                <Shield className="w-4 h-4 text-cyber-purple" />
                            </div>
                            <span className="text-[16px] font-bold text-white">
                                Web<span className="text-cyber-purple">Sec</span> AI
                            </span>
                        </div>
                        <p className="text-[13px] text-cyber-text-muted leading-relaxed mb-4">
                            Enterprise-grade dynamic web application security testing platform.
                        </p>
                        <div className="flex gap-3">
                            {['X', 'GH', 'LI'].map(social => (
                                <a key={social} href="#"
                                    className="w-8 h-8 rounded-lg bg-cyber-card border border-cyber-border flex items-center justify-center text-[11px] text-cyber-text-muted hover:text-cyber-purple hover:border-cyber-purple/30 transition-all">
                                    {social}
                                </a>
                            ))}
                        </div>
                    </div>

                    {/* Link columns */}
                    {footerColumns.map(col => (
                        <div key={col.title}>
                            <h4 className="text-[13px] font-semibold text-white uppercase tracking-wider mb-4">{col.title}</h4>
                            <ul className="space-y-2.5">
                                {col.links.map(link => (
                                    <li key={link}>
                                        <a href="#" className="text-[13px] text-cyber-text-muted hover:text-cyber-glow transition-colors duration-200">
                                            {link}
                                        </a>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ))}
                </div>

                {/* Bottom bar */}
                <div className="mt-14 pt-6 border-t border-cyber-border flex flex-col md:flex-row items-center justify-between gap-4">
                    <p className="text-[12px] text-cyber-text-muted">
                        © 2026 WebSec AI. All rights reserved.
                    </p>
                    <p className="text-[12px] text-cyber-text-muted">
                        Built with ❤️ for application security
                    </p>
                </div>
            </div>
        </footer>
    );
}
