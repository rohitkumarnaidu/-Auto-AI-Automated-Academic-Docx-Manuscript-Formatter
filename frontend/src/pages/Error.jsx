import Navbar from '../components/Navbar';
import { Link } from 'react-router-dom';

export default function Error() {
    return (
        <div className="flex flex-col min-h-screen">
            <Navbar variant="app" />

            {/* Main Content Container */}
            <main className="flex-1 flex flex-col items-center justify-center px-4 py-12">
                <div className="max-w-[640px] w-full bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-[#e7ecf3] dark:border-slate-800 overflow-hidden">
                    {/* EmptyState / Error Hero Section */}
                    <div className="flex flex-col items-center gap-6 px-8 pt-10 pb-6">
                        <div className="flex items-center justify-center w-24 h-24 rounded-full bg-red-50 dark:bg-red-900/20 text-red-500">
                            <span className="material-symbols-outlined text-6xl" style={{ fontVariationSettings: "'FILL' 1" }}>error</span>
                        </div>
                        <div className="flex flex-col items-center gap-3 text-center">
                            <h1 className="text-[#0d131b] dark:text-white text-3xl font-bold leading-tight tracking-tight">Processing Error</h1>
                            <p className="text-slate-600 dark:text-slate-400 text-base leading-relaxed max-w-[480px]">
                                Unsupported file type or corrupted metadata detected. We couldn't parse your manuscript for formatting. Please check your file format and try again.
                            </p>
                        </div>
                    </div>

                    {/* Divider */}
                    <div className="px-8">
                        <div className="h-px bg-[#e7ecf3] dark:bg-slate-800 w-full"></div>
                    </div>

                    {/* Headline & Checklist Section */}
                    <div className="px-8 py-6">
                        <h3 className="text-[#0d131b] dark:text-white text-lg font-bold leading-tight mb-4">Recommended Next Steps</h3>
                        <div className="space-y-1">
                            <label className="flex gap-x-4 py-3 px-3 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors cursor-pointer group">
                                <div className="relative flex items-center">
                                    <input className="h-5 w-5 rounded border-[#cfd9e7] dark:border-slate-700 border-2 bg-transparent text-primary checked:bg-primary checked:border-primary focus:ring-0 focus:ring-offset-0 transition-all" type="checkbox" />
                                </div>
                                <p className="text-slate-700 dark:text-slate-300 text-base font-normal leading-normal">Check if your file is in <span className="font-semibold text-[#0d131b] dark:text-white">.docx, .pdf, .tex, .txt, .html</span> or <span className="font-semibold text-[#0d131b] dark:text-white">.md</span> format</p>
                            </label>
                            <label className="flex gap-x-4 py-3 px-3 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors cursor-pointer group">
                                <div className="relative flex items-center">
                                    <input className="h-5 w-5 rounded border-[#cfd9e7] dark:border-slate-700 border-2 bg-transparent text-primary checked:bg-primary checked:border-primary focus:ring-0 focus:ring-offset-0 transition-all" type="checkbox" />
                                </div>
                                <p className="text-slate-700 dark:text-slate-300 text-base font-normal leading-normal">Ensure the file is not password protected or encrypted</p>
                            </label>
                            <label className="flex gap-x-4 py-3 px-3 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors cursor-pointer group">
                                <div className="relative flex items-center">
                                    <input className="h-5 w-5 rounded border-[#cfd9e7] dark:border-slate-700 border-2 bg-transparent text-primary checked:bg-primary checked:border-primary focus:ring-0 focus:ring-offset-0 transition-all" type="checkbox" />
                                </div>
                                <p className="text-slate-700 dark:text-slate-300 text-base font-normal leading-normal">Rename the file to remove special characters and retry</p>
                            </label>
                        </div>
                    </div>

                    {/* Button Group / Actions */}
                    <div className="bg-slate-50 dark:bg-slate-800/30 px-8 py-6 flex flex-col sm:flex-row gap-3 justify-center">
                        <Link to="/upload" className="flex-1 flex min-w-[160px] cursor-pointer items-center justify-center rounded-lg h-12 px-6 bg-primary text-white text-sm font-bold leading-normal tracking-wide transition-opacity hover:opacity-90 active:scale-95 duration-150">
                            <span className="material-symbols-outlined mr-2">upload_file</span>
                            <span className="truncate">Return to Upload</span>
                        </Link>
                        <button className="flex-1 flex min-w-[160px] cursor-pointer items-center justify-center rounded-lg h-12 px-6 bg-white dark:bg-slate-800 border border-[#cfd9e7] dark:border-slate-700 text-[#0d131b] dark:text-white text-sm font-bold leading-normal tracking-wide transition-all hover:bg-slate-50 dark:hover:bg-slate-700 active:scale-95 duration-150">
                            <span className="material-symbols-outlined mr-2">support_agent</span>
                            <span className="truncate">Contact Support</span>
                        </button>
                    </div>
                </div>

                {/* System Status Footer */}
                <div className="mt-8 flex items-center gap-2 text-slate-500 dark:text-slate-400 text-sm">
                    <span className="flex h-2 w-2 rounded-full bg-green-500"></span>
                    <p>All other systems are operational. <a href="#" className="text-primary hover:underline underline-offset-4 ml-1">View status page</a></p>
                </div>
            </main>

            <footer className="w-full py-8 px-10 text-center border-t border-[#e7ecf3] dark:border-slate-800 text-slate-400 text-xs">
                <p>© 2024 ManuscriptFormatter. Professional Academic Tools for Researchers.</p>
            </footer>
        </div>
    );
}
