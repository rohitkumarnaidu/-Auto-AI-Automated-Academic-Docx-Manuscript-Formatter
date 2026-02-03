import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

export default function Templates() {
    return (
        <div className="bg-background-light dark:bg-background-dark font-display text-[#0d131b] dark:text-slate-200 min-h-screen flex flex-col">
            <Navbar variant="app" />

            <main className="px-10 lg:px-40 flex flex-1 justify-center py-10">
                <div className="layout-content-container flex flex-col max-w-[1200px] flex-1">
                    {/* Header Section */}
                    <div className="flex flex-col gap-6 p-4">
                        <div className="flex flex-wrap justify-between items-end gap-3">
                            <div className="flex min-w-72 flex-col gap-3">
                                <p className="text-[#0d131b] dark:text-white text-4xl font-black leading-tight tracking-[-0.033em]">Journal Template Library</p>
                                <p className="text-[#4c6c9a] dark:text-slate-400 text-base font-normal leading-normal">Browse and select official academic formatting templates for your manuscript.</p>
                            </div>
                        </div>
                        {/* Search Bar */}
                        <div className="py-3">
                            <label className="flex flex-col min-w-40 h-14 w-full">
                                <div className="flex w-full flex-1 items-stretch rounded-xl h-full shadow-sm">
                                    <div className="text-[#4c6c9a] flex border-none bg-white dark:bg-slate-800 items-center justify-center pl-5 rounded-l-xl border-r-0">
                                        <span className="material-symbols-outlined text-[24px]">search</span>
                                    </div>
                                    <input
                                        className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d131b] dark:text-white focus:outline-0 focus:ring-0 border-none bg-white dark:bg-slate-800 focus:border-none h-full placeholder:text-[#4c6c9a] dark:placeholder:text-slate-500 px-4 rounded-l-none border-l-0 pl-3 text-lg font-normal leading-normal"
                                        placeholder="Search for journal (e.g., IEEE, Nature, Elsevier)..."
                                    />
                                </div>
                            </label>
                        </div>
                        {/* Filters/Chips */}
                        <div className="flex gap-3 py-2 flex-wrap">
                            <button className="flex h-10 shrink-0 items-center justify-center gap-x-2 rounded-lg bg-primary text-white pl-4 pr-3 shadow-md transition-all">
                                <p className="text-sm font-semibold leading-normal">All Publishers</p>
                                <span className="material-symbols-outlined text-[20px]">keyboard_arrow_down</span>
                            </button>
                            <button className="flex h-10 shrink-0 items-center justify-center gap-x-2 rounded-lg bg-white dark:bg-slate-800 border border-[#e7ecf3] dark:border-slate-700 pl-4 pr-3 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">
                                <p className="text-[#0d131b] dark:text-slate-300 text-sm font-medium leading-normal">Engineering</p>
                                <span className="material-symbols-outlined text-[20px]">keyboard_arrow_down</span>
                            </button>
                            <button className="flex h-10 shrink-0 items-center justify-center gap-x-2 rounded-lg bg-white dark:bg-slate-800 border border-[#e7ecf3] dark:border-slate-700 pl-4 pr-3 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">
                                <p className="text-[#0d131b] dark:text-slate-300 text-sm font-medium leading-normal">Life Sciences</p>
                                <span className="material-symbols-outlined text-[20px]">keyboard_arrow_down</span>
                            </button>
                            <button className="flex h-10 shrink-0 items-center justify-center gap-x-2 rounded-lg bg-white dark:bg-slate-800 border border-[#e7ecf3] dark:border-slate-700 pl-4 pr-3 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">
                                <p className="text-[#0d131b] dark:text-slate-300 text-sm font-medium leading-normal">Social Sciences</p>
                                <span className="material-symbols-outlined text-[20px]">keyboard_arrow_down</span>
                            </button>
                        </div>
                    </div>

                    {/* Template Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-4">
                        {/* IEEE Card */}
                        <div className="flex flex-col gap-4 p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:shadow-xl hover:border-primary/30 transition-all group">
                            <div className="flex justify-between items-start">
                                <div className="size-12 rounded-lg bg-slate-50 dark:bg-slate-800 flex items-center justify-center text-primary border border-slate-100 dark:border-slate-700">
                                    <span className="material-symbols-outlined text-[32px]">architecture</span>
                                </div>
                                <span className="px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400">Available</span>
                            </div>
                            <div className="flex flex-col gap-1">
                                <h3 className="text-[#0d131b] dark:text-white text-xl font-bold">IEEE Transactions</h3>
                                <p className="text-sm text-[#4c6c9a] dark:text-slate-400 leading-relaxed min-h-[40px] line-clamp-2">Official IEEE format for technical, electrical, and engineering research papers.</p>
                            </div>
                            <div className="flex flex-col gap-3 mt-2">
                                <button className="w-full bg-primary text-white py-2.5 rounded-lg font-semibold text-sm hover:bg-primary/90 transition-colors">Select Template</button>
                                <button className="w-full bg-slate-100 dark:bg-slate-800 text-[#0d131b] dark:text-slate-300 py-2.5 rounded-lg font-semibold text-sm hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors">Preview Guidelines</button>
                            </div>
                        </div>

                        {/* Nature Card */}
                        <div className="flex flex-col gap-4 p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:shadow-xl hover:border-primary/30 transition-all group">
                            <div className="flex justify-between items-start">
                                <div className="size-12 rounded-lg bg-slate-50 dark:bg-slate-800 flex items-center justify-center text-primary border border-slate-100 dark:border-slate-700">
                                    <span className="material-symbols-outlined text-[32px]">biotech</span>
                                </div>
                                <span className="px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400">Available</span>
                            </div>
                            <div className="flex flex-col gap-1">
                                <h3 className="text-[#0d131b] dark:text-white text-xl font-bold">Nature Portfolio</h3>
                                <p className="text-sm text-[#4c6c9a] dark:text-slate-400 leading-relaxed min-h-[40px] line-clamp-2">Standard formatting template for submission to all Nature Portfolio journals.</p>
                            </div>
                            <div className="flex flex-col gap-3 mt-2">
                                <button className="w-full bg-primary text-white py-2.5 rounded-lg font-semibold text-sm hover:bg-primary/90 transition-colors">Select Template</button>
                                <button className="w-full bg-slate-100 dark:bg-slate-800 text-[#0d131b] dark:text-slate-300 py-2.5 rounded-lg font-semibold text-sm hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors">Preview Guidelines</button>
                            </div>
                        </div>

                        {/* Elsevier Card */}
                        <div className="flex flex-col gap-4 p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:shadow-xl hover:border-primary/30 transition-all group">
                            <div className="flex justify-between items-start">
                                <div className="size-12 rounded-lg bg-slate-50 dark:bg-slate-800 flex items-center justify-center text-primary border border-slate-100 dark:border-slate-700">
                                    <span className="material-symbols-outlined text-[32px]">description</span>
                                </div>
                                <span className="px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400">Available</span>
                            </div>
                            <div className="flex flex-col gap-1">
                                <h3 className="text-[#0d131b] dark:text-white text-xl font-bold">Elsevier Standard</h3>
                                <p className="text-sm text-[#4c6c9a] dark:text-slate-400 leading-relaxed min-h-[40px] line-clamp-2">General formatting guidelines compatible with Elsevier's wide range of journals.</p>
                            </div>
                            <div className="flex flex-col gap-3 mt-2">
                                <button className="w-full bg-primary text-white py-2.5 rounded-lg font-semibold text-sm hover:bg-primary/90 transition-colors">Select Template</button>
                                <button className="w-full bg-slate-100 dark:bg-slate-800 text-[#0d131b] dark:text-slate-300 py-2.5 rounded-lg font-semibold text-sm hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors">Preview Guidelines</button>
                            </div>
                        </div>

                        {/* Springer Card */}
                        <div className="flex flex-col gap-4 p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:shadow-xl transition-all opacity-80 group grayscale">
                            <div className="flex justify-between items-start">
                                <div className="size-12 rounded-lg bg-slate-50 dark:bg-slate-800 flex items-center justify-center text-slate-400 border border-slate-100 dark:border-slate-700">
                                    <span className="material-symbols-outlined text-[32px]">science</span>
                                </div>
                                <span className="px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-slate-200 text-slate-600 dark:bg-slate-700 dark:text-slate-300">Coming Soon</span>
                            </div>
                            <div className="flex flex-col gap-1">
                                <h3 className="text-[#0d131b] dark:text-white text-xl font-bold">Springer LNCS</h3>
                                <p className="text-sm text-[#4c6c9a] dark:text-slate-400 leading-relaxed min-h-[40px] line-clamp-2">Multi-column layouts and specific LNCS styles for Computer Science.</p>
                            </div>
                            <div className="flex flex-col gap-3 mt-2">
                                <button className="w-full bg-slate-200 dark:bg-slate-800 text-slate-500 py-2.5 rounded-lg font-semibold text-sm cursor-not-allowed">Select Template</button>
                                <button className="w-full bg-slate-100 dark:bg-slate-800 text-[#0d131b] dark:text-slate-300 py-2.5 rounded-lg font-semibold text-sm hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors">Preview Guidelines</button>
                            </div>
                        </div>

                        {/* APA Card */}
                        <div className="flex flex-col gap-4 p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:shadow-xl hover:border-primary/30 transition-all group">
                            <div className="flex justify-between items-start">
                                <div className="size-12 rounded-lg bg-slate-50 dark:bg-slate-800 flex items-center justify-center text-primary border border-slate-100 dark:border-slate-700">
                                    <span className="material-symbols-outlined text-[32px]">history_edu</span>
                                </div>
                                <span className="px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400">Available</span>
                            </div>
                            <div className="flex flex-col gap-1">
                                <h3 className="text-[#0d131b] dark:text-white text-xl font-bold">APA 7th Edition</h3>
                                <p className="text-sm text-[#4c6c9a] dark:text-slate-400 leading-relaxed min-h-[40px] line-clamp-2">Latest APA formatting standards for social and behavioral sciences research.</p>
                            </div>
                            <div className="flex flex-col gap-3 mt-2">
                                <button className="w-full bg-primary text-white py-2.5 rounded-lg font-semibold text-sm hover:bg-primary/90 transition-colors">Select Template</button>
                                <button className="w-full bg-slate-100 dark:bg-slate-800 text-[#0d131b] dark:text-slate-300 py-2.5 rounded-lg font-semibold text-sm hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors">Preview Guidelines</button>
                            </div>
                        </div>

                        {/* Request Template Card */}
                        <div className="flex flex-col items-center justify-center gap-4 p-5 rounded-xl bg-slate-50/50 dark:bg-slate-800/20 border-2 border-dashed border-slate-200 dark:border-slate-700 hover:border-primary/50 transition-all cursor-pointer group">
                            <div className="size-14 rounded-full bg-white dark:bg-slate-800 flex items-center justify-center text-slate-400 group-hover:text-primary shadow-sm transition-colors">
                                <span className="material-symbols-outlined text-[32px]">add_circle</span>
                            </div>
                            <div className="text-center">
                                <h3 className="text-[#0d131b] dark:text-white text-lg font-bold">Missing a journal?</h3>
                                <p className="text-sm text-[#4c6c9a] dark:text-slate-400 px-4">Request a new formatting template and our team will add it within 48 hours.</p>
                            </div>
                            <a className="text-primary text-sm font-bold hover:underline" href="#">Request Template</a>
                        </div>
                    </div>

                    {/* Pagination */}
                    <div className="flex items-center justify-center gap-4 mt-12 py-6 border-t border-slate-200 dark:border-slate-800">
                        <button className="p-2 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-white dark:hover:bg-slate-800 transition-colors">
                            <span className="material-symbols-outlined">chevron_left</span>
                        </button>
                        <div className="flex gap-2">
                            <button className="w-10 h-10 rounded-lg bg-primary text-white font-bold">1</button>
                            <button className="w-10 h-10 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">2</button>
                            <button className="w-10 h-10 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">3</button>
                            <span className="flex items-end px-2">...</span>
                            <button className="w-10 h-10 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">12</button>
                        </div>
                        <button className="p-2 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-white dark:hover:bg-slate-800 transition-colors">
                            <span className="material-symbols-outlined">chevron_right</span>
                        </button>
                    </div>
                </div>
            </main>

            <Footer variant="app" />
        </div>
    );
}
