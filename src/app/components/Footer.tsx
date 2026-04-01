import { Shield } from 'lucide-react';

const footerColumns = [
    {
        title: 'Scanners',
        links: ['DAST Scanner', 'Ecommerce Scanner', 'Load Tester', 'API Security'],
    },
    {
        title: 'Platform',
        links: ['Scan History', 'AI Analysis', 'Security Reports', 'User Dashboard'],
    },
    {
        title: 'Resources',
        links: ['Documentation', 'OWASP Top 10', 'Changelog', 'Contact'],
    },
];

export function Footer() {
    return (
        <footer className="bg-cyber-surface border-t border-cyber-border">
            <div className="max-w-[1320px] mx-auto px-6 py-14">
                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-10 lg:gap-8">

                    {/* Brand */}
                    <div>
                        <div className="flex items-center gap-2.5 mb-4">
                            <div className="w-8 h-8 rounded-lg bg-cyber-purple/15 border border-cyber-purple/30 flex items-center justify-center">
                                <Shield className="w-4 h-4 text-cyber-purple" />
                            </div>
                            <span className="text-[16px] font-bold text-white">
                                Web<span className="text-cyber-purple">Sec</span> AI
                            </span>
                        </div>
                        <p className="text-[13px] text-cyber-text-muted leading-relaxed">
                            Web application and ecommerce security testing platform with AI-powered analysis.
                        </p>
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

                <div className="mt-12 pt-6 border-t border-cyber-border flex flex-col md:flex-row items-center justify-between gap-4">
                    <p className="text-[12px] text-cyber-text-muted">
                        © 2026 WebSec AI. All rights reserved.
                    </p>
                    <p className="text-[12px] text-cyber-text-muted">
                        DAST + Ecommerce Security Platform
                    </p>
                </div>
            </div>
        </footer>
    );
}
