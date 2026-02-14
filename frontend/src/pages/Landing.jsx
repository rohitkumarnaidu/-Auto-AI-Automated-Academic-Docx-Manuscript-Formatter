import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { Link } from 'react-router-dom';

export default function Landing() {
    return (
        <>
            <Navbar variant="landing" />

            {/* Hero Section */}
            <section className="relative overflow-hidden py-16 lg:py-24">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                        <div className="flex flex-col gap-8">
                            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-bold uppercase tracking-wider w-fit">
                                <span className="material-symbols-outlined text-sm">verified</span>
                                AI-Powered Academic Standard
                            </div>
                            <div className="flex flex-col gap-4">
                                <h1 className="text-4xl md:text-5xl lg:text-6xl font-black text-slate-900 dark:text-white leading-[1.1] tracking-tight">
                                    Write and Rewrite, Validate, structure, and format academic papers <span className="text-primary">automatically.</span>
                                </h1>
                                <p className="text-lg text-slate-600 dark:text-slate-400 max-w-xl leading-relaxed">
                                    Save hours on manual bibliography and style adjustments. Our engine handles APA, IEEE, Springer, and more so you can focus on your research.
                                </p>
                            </div>
                            <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
                                <Link to="/upload" className="flex items-center gap-2 bg-primary text-white px-8 py-4 rounded-xl text-lg font-bold hover:bg-blue-600 shadow-lg shadow-primary/25 transition-all">
                                    <span className="material-symbols-outlined">upload_file</span>
                                    Upload Manuscript
                                </Link>
                                <div className="flex flex-col px-2">
                                    <span className="text-sm font-semibold text-slate-500">Supported formats:</span>
                                    <span class="text-xs text-slate-400">.docx, .pdf, .tex, .txt, .html, .md</span>
                                </div>
                            </div>
                        </div>
                        <div className="relative">
                            <div className="aspect-[4/3] rounded-2xl overflow-hidden bg-white dark:bg-slate-800 shadow-2xl border border-slate-200 dark:border-slate-700" style={{ backgroundImage: "url('https://lh3.googleusercontent.com/aida-public/AB6AXuBgXXWbmsfQm4btwQHfY2tmhYAJTi94XALRDgR4WuRZufgH--9Q1SLvuCe8ruWlFHwQ1mzsT3fTVSDzz8E2DApgPH8HO0MTTjq18apNHSxsXBGSkaSyQyQ9p-7LChh4VRr9yCoo8eA1sq12Tbq8yNHLoVX043i8vZ773Nn6PO8564Ett01CUsFr4PK5s-5zq0cxT6sTSVal-7BfF5uQ_C77GasmEU_6tDVeTRIpuWJ-34fQJWkhzjnVLKAWyU3PN0BVjXqoC0NIhWFd')" }}>
                                {/* Abstract overlay for dashboard preview */}
                                <div className="absolute inset-0 bg-gradient-to-tr from-primary/5 to-transparent flex items-center justify-center p-8">
                                    <div className="w-full h-full bg-white dark:bg-slate-900 rounded-lg shadow-inner p-4 flex flex-col gap-4">
                                        <div className="h-8 w-1/3 bg-slate-100 dark:bg-slate-800 rounded"></div>
                                        <div className="flex gap-4 grow">
                                            <div className="w-2/3 flex flex-col gap-2">
                                                <div className="h-4 w-full bg-slate-50 dark:bg-slate-800 rounded"></div>
                                                <div className="h-4 w-full bg-slate-50 dark:bg-slate-800 rounded"></div>
                                                <div className="h-4 w-3/4 bg-slate-50 dark:bg-slate-800 rounded"></div>
                                                <div className="mt-4 h-40 w-full bg-slate-50 dark:bg-slate-800 rounded flex items-center justify-center">
                                                    <span className="material-symbols-outlined text-slate-300 dark:text-slate-600 text-4xl">bar_chart</span>
                                                </div>
                                            </div>
                                            <div className="w-1/3 flex flex-col gap-4 border-l border-slate-100 dark:border-slate-800 pl-4">
                                                <div className="h-10 w-full bg-primary/10 rounded border border-primary/20"></div>
                                                <div className="h-6 w-full bg-slate-50 dark:bg-slate-800 rounded"></div>
                                                <div className="h-6 w-full bg-slate-50 dark:bg-slate-800 rounded"></div>
                                                <div className="h-6 w-full bg-slate-50 dark:bg-slate-800 rounded"></div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            {/* Stats badge */}
                            <div className="absolute -bottom-6 -left-6 bg-white dark:bg-slate-800 p-6 rounded-xl shadow-xl border border-slate-100 dark:border-slate-700 hidden md:block">
                                <div className="flex items-center gap-4">
                                    <div className="bg-green-100 dark:bg-green-900/30 p-3 rounded-full">
                                        <span className="material-symbols-outlined text-green-600">check_circle</span>
                                    </div>
                                    <div>
                                        <p className="text-sm text-slate-500 dark:text-slate-400">98.4% Precision</p>
                                        <p className="text-xl font-bold text-slate-900 dark:text-white">Validation Rate</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Feature Grid Section */}
            <section className="py-20 bg-white dark:bg-background-dark/50" id="features">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center max-w-3xl mx-auto mb-16">
                        <h2 className="text-primary font-bold text-sm tracking-widest uppercase mb-3">Powerful Capabilities</h2>
                        <h3 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-6 leading-tight">Designed to meet the rigorous standards of global academic publishing.</h3>
                        <p className="text-slate-600 dark:text-slate-400">Our platform combines machine learning with human-grade formatting rules to ensure your research is presented perfectly every time.</p>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {/* Feature 1 */}
                        <div className="group p-8 bg-background-light dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-700 hover:border-primary/50 transition-all hover:shadow-lg hover:-translate-y-1">
                            <div className="size-12 rounded-xl bg-primary text-white flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                                <span className="material-symbols-outlined">file_open</span>
                            </div>
                            <h4 className="text-xl font-bold text-slate-900 dark:text-white mb-3">Multi-format support</h4>
                            <p className="text-slate-600 dark:text-slate-400 leading-relaxed">Export seamlessly to high-fidelity PDF, clean LaTeX source code, and fully editable Word formats for further collaboration.</p>
                        </div>
                        {/* Feature 2 */}
                        <div className="group p-8 bg-background-light dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-700 hover:border-primary/50 transition-all hover:shadow-lg hover:-translate-y-1">
                            <div className="size-12 rounded-xl bg-primary text-white flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                                <span className="material-symbols-outlined">scan</span>
                            </div>
                            <h4 className="text-xl font-bold text-slate-900 dark:text-white mb-3">OCR support</h4>
                            <p className="text-slate-600 dark:text-slate-400 leading-relaxed">Advanced optical character recognition to convert scanned citations, handwritten notes, and image tables into perfectly editable text.</p>
                        </div>
                        {/* Feature 3 */}
                        <div className="group p-8 bg-background-light dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-700 hover:border-primary/50 transition-all hover:shadow-lg hover:-translate-y-1">
                            <div className="size-12 rounded-xl bg-primary text-white flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                                <span className="material-symbols-outlined">verified_user</span>
                            </div>
                            <h4 className="text-xl font-bold text-slate-900 dark:text-white mb-3">Academic validation</h4>
                            <p className="text-slate-600 dark:text-slate-400 leading-relaxed">Automated checks against specific journal-specific requirements including word counts, figure positioning, and reference density.</p>
                        </div>
                        {/* Feature 4 */}
                        <div className="group p-8 bg-background-light dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-700 hover:border-primary/50 transition-all hover:shadow-lg hover:-translate-y-1">
                            <div className="size-12 rounded-xl bg-primary text-white flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                                <span className="material-symbols-outlined">format_list_bulleted</span>
                            </div>
                            <h4 className="text-xl font-bold text-slate-900 dark:text-white mb-3">IEEE/Springer/APA</h4>
                            <p className="text-slate-600 dark:text-slate-400 leading-relaxed">Apply 1000+ citation styles with one click. We maintain up-to-date templates for major publishers and international conferences.</p>
                        </div>
                        {/* Feature 5 */}
                        <div className="group p-8 bg-background-light dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-700 hover:border-primary/50 transition-all hover:shadow-lg hover:-translate-y-1">
                            <div className="size-12 rounded-xl bg-primary text-white flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                                <span className="material-symbols-outlined">auto_awesome</span>
                            </div>
                            <h4 className="text-xl font-bold text-slate-900 dark:text-white mb-3">AI-assisted insights</h4>
                            <p className="text-slate-600 dark:text-slate-400 leading-relaxed">Structural feedback on document flow and writing clarity. Identify passive voice, repetitive phrases, and weak transitions instantly.</p>
                        </div>
                        {/* Feature 6 */}
                        <div className="group p-8 bg-background-light dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-700 hover:border-primary/50 transition-all hover:shadow-lg hover:-translate-y-1">
                            <div className="size-12 rounded-xl bg-primary text-white flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                                <span className="material-symbols-outlined">lock</span>
                            </div>
                            <h4 className="text-xl font-bold text-slate-900 dark:text-white mb-3">IP Protection</h4>
                            <p className="text-slate-600 dark:text-slate-400 leading-relaxed">Enterprise-grade encryption for your intellectual property. Your research stays private, and documents are deleted after processing.</p>
                        </div>
                    </div>
                </div>
            </section>

            {/* Templates Preview Section */}
            <section className="py-20 bg-background-light dark:bg-slate-900/30" id="templates">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center max-w-3xl mx-auto mb-16">
                        <h2 className="text-primary font-bold text-sm tracking-widest uppercase mb-3">Journal Library</h2>
                        <h3 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-6 leading-tight">One-click formatting for 1,000+ journals.</h3>
                        <p className="text-slate-600 dark:text-slate-400">Our library is constantly updated with the latest formatting requirements from major academic publishers.</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
                        {/* IEEE Preview Card */}
                        <Link to="/templates" className="flex flex-col gap-4 p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:shadow-xl hover:border-primary/30 transition-all group">
                            <div className="flex justify-between items-start">
                                <div className="size-10 rounded-lg bg-slate-50 dark:bg-slate-800 flex items-center justify-center text-primary border border-slate-100 dark:border-slate-700">
                                    <span className="material-symbols-outlined text-[24px]">architecture</span>
                                </div>
                                <span className="px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400">Available</span>
                            </div>
                            <div className="flex flex-col gap-1">
                                <h3 className="text-[#0d131b] dark:text-white text-lg font-bold">IEEE Transactions</h3>
                                <p className="text-xs text-[#4c6c9a] dark:text-slate-400 leading-relaxed line-clamp-2">Official format for technical, electrical, and engineering research.</p>
                            </div>
                        </Link>

                        {/* Nature Preview Card */}
                        <Link to="/templates" className="flex flex-col gap-4 p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:shadow-xl hover:border-primary/30 transition-all group">
                            <div className="flex justify-between items-start">
                                <div className="size-10 rounded-lg bg-slate-50 dark:bg-slate-800 flex items-center justify-center text-primary border border-slate-100 dark:border-slate-700">
                                    <span className="material-symbols-outlined text-[24px]">biotech</span>
                                </div>
                                <span className="px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400">Available</span>
                            </div>
                            <div className="flex flex-col gap-1">
                                <h3 className="text-[#0d131b] dark:text-white text-lg font-bold">Nature Portfolio</h3>
                                <p className="text-xs text-[#4c6c9a] dark:text-slate-400 leading-relaxed line-clamp-2">Standard template for submission to all Nature Portfolio journals.</p>
                            </div>
                        </Link>

                        {/* Elsevier Preview Card */}
                        <Link to="/templates" className="flex flex-col gap-4 p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:shadow-xl hover:border-primary/30 transition-all group">
                            <div className="flex justify-between items-start">
                                <div className="size-10 rounded-lg bg-slate-50 dark:bg-slate-800 flex items-center justify-center text-primary border border-slate-100 dark:border-slate-700">
                                    <span className="material-symbols-outlined text-[24px]">description</span>
                                </div>
                                <span className="px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400">Available</span>
                            </div>
                            <div className="flex flex-col gap-1">
                                <h3 className="text-[#0d131b] dark:text-white text-lg font-bold">Elsevier Standard</h3>
                                <p className="text-xs text-[#4c6c9a] dark:text-slate-400 leading-relaxed line-clamp-2">Guidelines compatible with Elsevier's wide range of journals.</p>
                            </div>
                        </Link>

                        {/* APA Preview Card */}
                        <Link to="/templates" className="flex flex-col gap-4 p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:shadow-xl hover:border-primary/30 transition-all group">
                            <div className="flex justify-between items-start">
                                <div className="size-10 rounded-lg bg-slate-50 dark:bg-slate-800 flex items-center justify-center text-primary border border-slate-100 dark:border-slate-700">
                                    <span className="material-symbols-outlined text-[24px]">history_edu</span>
                                </div>
                                <span className="px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400">Available</span>
                            </div>
                            <div className="flex flex-col gap-1">
                                <h3 className="text-[#0d131b] dark:text-white text-lg font-bold">APA 7th Edition</h3>
                                <p className="text-xs text-[#4c6c9a] dark:text-slate-400 leading-relaxed line-clamp-2">Latest standards for social and behavioral sciences research.</p>
                            </div>
                        </Link>
                    </div>

                    <div className="flex justify-center">
                        <Link to="/templates" className="flex items-center gap-2 px-8 py-3 rounded-xl border border-primary text-primary font-bold hover:bg-primary hover:text-white transition-all">
                            <span>View All Templates</span>
                            <span className="material-symbols-outlined text-sm">arrow_forward</span>
                        </Link>
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="py-16" id="pricing">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="relative bg-slate-900 dark:bg-primary/20 rounded-3xl p-8 md:p-16 overflow-hidden">
                        <div className="absolute inset-0 bg-primary opacity-5 mix-blend-overlay"></div>
                        <div className="relative z-10 flex flex-col items-center text-center gap-8">
                            <h2 className="text-3xl md:text-5xl font-black text-white leading-tight max-w-2xl">
                                Ready to format your paper for publication?
                            </h2>
                            <p className="text-slate-300 text-lg max-w-xl">
                                Join 25,000+ PhD students and researchers who have reclaimed their time and improved their acceptance rates.
                            </p>
                            <div className="flex flex-col sm:flex-row gap-4">
                                <Link to="/upload" className="bg-primary hover:bg-blue-600 text-white px-10 py-4 rounded-xl font-bold text-lg transition-all shadow-xl shadow-primary/20">
                                    Get Started Free
                                </Link>
                                <Link to="/templates" className="bg-white/10 hover:bg-white/20 text-white border border-white/20 px-10 py-4 rounded-xl font-bold text-lg transition-all backdrop-blur-sm">
                                    View Sample Output
                                </Link>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <div id="about">
                <Footer variant="landing" />
            </div>
        </>
    );
}
