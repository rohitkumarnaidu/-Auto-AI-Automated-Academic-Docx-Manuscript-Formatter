/* eslint-disable react/prop-types */

export default function Footer({ variant = 'app' }) {
    if (variant === 'landing') {
        return (
            <footer className="bg-slate-50 dark:bg-background-dark border-t border-slate-200 dark:border-slate-800 pt-16 pb-8">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-12 mb-12">
                        <div className="col-span-2 md:col-span-1">
                            <div className="flex items-center gap-2 mb-6">
                                <div className="bg-primary text-white p-1 rounded-md flex items-center justify-center">
                                    <span className="material-symbols-outlined text-sm">auto_stories</span>
                                </div>
                                <span className="text-lg font-bold tracking-tight text-slate-900 dark:text-white">ScholarForm AI</span>
                            </div>
                            <p className="text-sm text-slate-500 dark:text-slate-400 leading-relaxed mb-6">
                                Providing specialized technical writing and formatting infrastructure for global academia and scientific institutions since 2021.
                            </p>
                            <div className="flex gap-4">
                                <a href="#" className="text-slate-400 hover:text-primary"><span className="material-symbols-outlined">share</span></a>
                                <a href="#" className="text-slate-400 hover:text-primary"><span className="material-symbols-outlined">mail</span></a>
                            </div>
                        </div>
                        <div>
                            <h5 className="text-slate-900 dark:text-white font-bold text-sm mb-6 uppercase tracking-wider">Resources</h5>
                            <ul className="flex flex-col gap-4">
                                <li><a href="#" className="text-sm text-slate-500 hover:text-primary transition-colors">Style Guides</a></li>
                                <li><a href="#" className="text-sm text-slate-500 hover:text-primary transition-colors">Documentation</a></li>
                                <li><a href="#" className="text-sm text-slate-500 hover:text-primary transition-colors">Video Tutorials</a></li>
                                <li><a href="#" className="text-sm text-slate-500 hover:text-primary transition-colors">LaTeX Templates</a></li>
                            </ul>
                        </div>
                        <div>
                            <h5 className="text-slate-900 dark:text-white font-bold text-sm mb-6 uppercase tracking-wider">Compliance</h5>
                            <ul className="flex flex-col gap-4">
                                <li><a href="#" className="text-sm text-slate-500 hover:text-primary transition-colors">Privacy Policy</a></li>
                                <li><a href="#" className="text-sm text-slate-500 hover:text-primary transition-colors">Academic Integrity</a></li>
                                <li><a href="#" className="text-sm text-slate-500 hover:text-primary transition-colors">Terms of Service</a></li>
                                <li><a href="#" className="text-sm text-slate-500 hover:text-primary transition-colors">Data Security</a></li>
                            </ul>
                        </div>
                        <div>
                            <h5 className="text-slate-900 dark:text-white font-bold text-sm mb-6 uppercase tracking-wider">Support</h5>
                            <ul className="flex flex-col gap-4">
                                <li><a href="#" className="text-sm text-slate-500 hover:text-primary transition-colors">Help Center</a></li>
                                <li><a href="#" className="text-sm text-slate-500 hover:text-primary transition-colors">Institutional Access</a></li>
                                <li><a href="#" className="text-sm text-slate-500 hover:text-primary transition-colors">Contact Expert</a></li>
                                <li><a href="#" className="text-sm text-slate-500 hover:text-primary transition-colors">System Status</a></li>
                            </ul>
                        </div>
                    </div>
                    <div className="pt-8 border-t border-slate-200 dark:border-slate-800 flex flex-col md:flex-row justify-between items-center gap-4 text-center md:text-left">
                        <p className="text-xs text-slate-400">© 2024 ManuscriptFormatter SaaS Platform. All Rights Reserved. ISO 27001 Certified.</p>
                        <div className="flex items-center gap-6">
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

    // App Footer
    return (
        <footer className="max-w-[1280px] mx-auto px-6 py-10 mt-12 border-t border-slate-200 dark:border-slate-800">
            <div className="flex flex-col md:flex-row justify-between items-center gap-6">
                <div className="flex items-center gap-2 text-slate-400">
                    <span className="material-symbols-outlined text-xl">auto_stories</span>
                    <span className="text-sm font-medium">© 2024 ScholarForm AI. Built for Researchers.</span>
                </div>
                <div className="flex gap-6">
                    <a href="#" className="text-sm text-slate-500 hover:text-primary">Terms of Service</a>
                    <a href="#" className="text-sm text-slate-500 hover:text-primary">Privacy Policy</a>
                    <a href="#" className="text-sm text-slate-500 hover:text-primary">Support</a>
                </div>
            </div>
        </footer>
    );
}
