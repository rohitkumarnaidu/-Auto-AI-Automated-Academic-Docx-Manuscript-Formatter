import { Link } from 'react-router-dom';

export default function Footer({ variant = 'app' }) {
    if (variant === 'landing') {
        return (
            <footer className="bg-slate-50 dark:bg-background-dark border-t border-slate-200 dark:border-slate-800 pt-16 pb-8">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-10 mb-12">
                        <div className="sm:col-span-2 md:col-span-1">
                            <div className="flex items-center gap-2 mb-6">
                                <div className="bg-primary text-white p-1 rounded-md flex items-center justify-center">
                                    <span className="material-symbols-outlined text-sm">auto_stories</span>
                                </div>
                                <span className="text-lg font-bold tracking-tight text-slate-900 dark:text-white">ScholarForm AI</span>
                            </div>
                            <p className="text-sm text-slate-500 dark:text-slate-400 leading-relaxed mb-6">
                                Providing specialized technical writing and formatting.
                            </p>
                            <div className="flex gap-4">
                                <a href="https://twitter.com/intent/tweet?text=Check%20out%20ScholarForm%20AI" target="_blank" rel="noopener noreferrer" className="text-slate-400 hover:text-primary transition-colors"><span className="material-symbols-outlined">share</span></a>
                                <a href="mailto:contact@scholarform.ai" className="text-slate-400 hover:text-primary transition-colors"><span className="material-symbols-outlined">mail</span></a>
                            </div>
                        </div>
                        <div>
                            <h5 className="text-slate-900 dark:text-white font-bold text-sm mb-6 uppercase tracking-wider">Resources</h5>
                            <ul className="flex flex-col gap-4">
                                <li><Link to="/templates" className="text-sm text-slate-500 dark:text-slate-400 hover:text-primary transition-colors">Style Guides</Link></li>
                                <li><span className="text-sm text-slate-400 cursor-default" title="Coming Soon">Documentation</span></li>
                                <li><span className="text-sm text-slate-400 cursor-default" title="Coming Soon">Video Tutorials</span></li>
                                <li><Link to="/templates" className="text-sm text-slate-500 dark:text-slate-400 hover:text-primary transition-colors">LaTeX Templates</Link></li>
                            </ul>
                        </div>
                        <div>
                            <h5 className="text-slate-900 dark:text-white font-bold text-sm mb-6 uppercase tracking-wider">Compliance</h5>
                            <ul className="flex flex-col gap-4">
                                <li><Link to="/privacy" className="text-sm text-slate-500 dark:text-slate-400 hover:text-primary transition-colors">Privacy Policy</Link></li>
                                <li><span className="text-sm text-slate-400 cursor-default" title="Coming Soon">Academic Integrity</span></li>
                                <li><Link to="/terms" className="text-sm text-slate-500 dark:text-slate-400 hover:text-primary transition-colors">Terms of Service</Link></li>
                                <li><span className="text-sm text-slate-400 cursor-default" title="Coming Soon">Data Security</span></li>
                            </ul>
                        </div>
                        <div>
                            <h5 className="text-slate-900 dark:text-white font-bold text-sm mb-6 uppercase tracking-wider">Support</h5>
                            <ul className="flex flex-col gap-4">
                                <li><a href="mailto:support@scholarform.ai" className="text-sm text-slate-500 dark:text-slate-400 hover:text-primary transition-colors">Help Center</a></li>
                                <li><span className="text-sm text-slate-400 cursor-default" title="Coming Soon">Institutional Access</span></li>
                                <li><a href="mailto:support@scholarform.ai" className="text-sm text-slate-500 dark:text-slate-400 hover:text-primary transition-colors">Contact Expert</a></li>
                                <li><Link to="/admin-dashboard" className="text-sm text-slate-500 dark:text-slate-400 hover:text-primary transition-colors">System Status</Link></li>
                            </ul>
                        </div>
                    </div>
                    <div className="pt-8 border-t border-slate-200 dark:border-slate-800 flex flex-col md:flex-row justify-between items-center gap-4 text-center md:text-left">
                        <p className="text-xs text-slate-400">(c) {new Date().getFullYear()} ManuscriptFormatter SaaS Platform. All Rights Reserved.</p>
                        <div className="flex flex-wrap items-center justify-center gap-4 sm:gap-6">
                            <div className="flex items-center gap-1 opacity-50 grayscale">
                                <span className="material-symbols-outlined text-xs">shield</span>
                                <span className="text-[10px] font-bold">GDPR COMPLIANT</span>
                            </div>
                            <div className="flex items-center gap-1 opacity-50 grayscale">
                                <span className="material-symbols-outlined text-xs">verified</span>
                                <span className="text-[10px] font-bold">PUBLISHER PARTNER</span>
                            </div>
                        </div>
                    </div>
                </div>
            </footer>
        );
    }

    return (
        <footer className="max-w-[1280px] mx-auto px-4 sm:px-6 py-8 sm:py-10 mt-10 sm:mt-12 border-t border-slate-200 dark:border-slate-800">
            <div className="flex flex-col md:flex-row justify-between items-center gap-4 sm:gap-6">
                <div className="flex items-center gap-2 text-slate-400">
                    <span className="material-symbols-outlined text-xl">auto_stories</span>
                    <span className="text-sm font-medium text-center md:text-left">(c) {new Date().getFullYear()} ScholarForm AI. Built for Academics.</span>
                </div>
                <div className="flex flex-wrap items-center justify-center gap-x-6 gap-y-2">
                    <Link to="/terms" className="text-sm text-slate-500 dark:text-slate-400 hover:text-primary transition-colors">Terms of Service</Link>
                    <Link to="/privacy" className="text-sm text-slate-500 dark:text-slate-400 hover:text-primary transition-colors">Privacy Policy</Link>
                    <a href="mailto:support@scholarform.ai" className="text-sm text-slate-500 dark:text-slate-400 hover:text-primary transition-colors">Support</a>
                </div>
            </div>
        </footer>
    );
}
