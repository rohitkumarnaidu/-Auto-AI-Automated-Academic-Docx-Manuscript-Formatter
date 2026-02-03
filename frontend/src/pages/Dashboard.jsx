import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

export default function Dashboard() {
    return (
        <div className="bg-background-light dark:bg-background-dark font-display text-slate-900 dark:text-slate-100 min-h-screen flex flex-col transition-colors duration-300">
            <Navbar variant="app" activeTab="dashboard" />

            <main className="flex-1 max-w-[1280px] mx-auto w-full px-6 py-8">
                {/* PageHeading Component */}
                <div className="mb-10">
                    <div className="flex flex-col gap-2">
                        <h1 className="text-slate-900 dark:text-white text-4xl font-black leading-tight tracking-tight">Welcome back, Dr. Smith</h1>
                        <p className="text-slate-500 dark:text-slate-400 text-lg font-normal leading-normal max-w-2xl">Manage your academic manuscripts, track validation status, and ensure formatting compliance for upcoming publications.</p>
                    </div>
                </div>

                {/* ImageGrid / Quick Actions */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
                    {/* Action Card 1: Upload */}
                    <Link to="/upload" className="group flex flex-col bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden hover:shadow-lg transition-all cursor-pointer">
                        <div className="h-48 w-full bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                            <span className="material-symbols-outlined text-primary text-5xl">cloud_upload</span>
                        </div>
                        <div className="p-6">
                            <h3 className="text-slate-900 dark:text-white text-lg font-bold mb-2">Upload New Manuscript</h3>
                            <p className="text-slate-500 dark:text-slate-400 text-sm leading-relaxed mb-4">Start a new submission and formatting check. Supports .docx and LaTeX files.</p>
                            <div className="w-full bg-primary text-white py-2.5 px-4 rounded-lg font-bold text-sm hover:bg-blue-700 transition-colors flex items-center justify-center gap-2 text-center">
                                <span className="material-symbols-outlined text-sm">add</span>
                                New Submission
                            </div>
                        </div>
                    </Link>

                    {/* Action Card 2: History */}
                    <Link to="/history" className="group flex flex-col bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden hover:shadow-lg transition-all cursor-pointer">
                        <div className="h-48 w-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center group-hover:bg-slate-200 dark:group-hover:bg-slate-700 transition-colors">
                            <span className="material-symbols-outlined text-slate-400 text-5xl">description</span>
                        </div>
                        <div className="p-6">
                            <div className="flex justify-between items-start mb-2">
                                <h3 className="text-slate-900 dark:text-white text-lg font-bold">My Manuscripts</h3>
                                <span className="bg-primary/20 text-primary text-[10px] font-bold px-2 py-1 rounded-full uppercase tracking-wider">12 Active</span>
                            </div>
                            <p className="text-slate-500 dark:text-slate-400 text-sm leading-relaxed mb-4">Track progress of ongoing projects. Last update was 2 hours ago.</p>
                            <div className="w-full bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white py-2.5 px-4 rounded-lg font-bold text-sm hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors text-center">
                                View All Projects
                            </div>
                        </div>
                    </Link>

                    {/* Action Card 3: Results */}
                    <div className="group flex flex-col bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden hover:shadow-lg transition-all cursor-pointer">
                        <div className="h-48 w-full bg-green-50 dark:bg-green-900/10 flex items-center justify-center group-hover:bg-green-100 dark:group-hover:bg-green-900/20 transition-colors">
                            <span className="material-symbols-outlined text-green-600 text-5xl">fact_check</span>
                        </div>
                        <div className="p-6">
                            <div className="flex justify-between items-start mb-2">
                                <h3 className="text-slate-900 dark:text-white text-lg font-bold">Validation Results</h3>
                                <span className="bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-[10px] font-bold px-2 py-1 rounded-full uppercase tracking-wider">3 Ready</span>
                            </div>
                            <p className="text-slate-500 dark:text-slate-400 text-sm leading-relaxed mb-4">Detailed formatting compliance reports and export-ready files.</p>
                            <button className="w-full bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-white py-2.5 px-4 rounded-lg font-bold text-sm hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors">
                                Download Results
                            </button>
                        </div>
                    </div>
                </div>

                {/* SectionHeader Component */}
                <div className="flex items-center justify-between mb-4 px-1">
                    <h2 className="text-slate-900 dark:text-white text-2xl font-bold tracking-tight">Recent Activity</h2>
                    <Link className="text-primary text-sm font-semibold hover:underline flex items-center gap-1" to="/history">
                        View full history
                        <span className="material-symbols-outlined text-sm">arrow_forward</span>
                    </Link>
                </div>

                {/* Table Component */}
                <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-sm">
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="bg-slate-50 dark:bg-slate-800/50 border-b border-slate-200 dark:border-slate-800">
                                    <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Manuscript Title</th>
                                    <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Status</th>
                                    <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Last Modified</th>
                                    <th className="px-6 py-4 text-right text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                                <tr className="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors">
                                    <td className="px-6 py-5">
                                        <div className="flex items-center gap-3">
                                            <span className="material-symbols-outlined text-slate-400">article</span>
                                            <span className="text-slate-900 dark:text-white font-medium">Quantum Physics Draft v2.4</span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-5">
                                        <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
                                            <span className="w-1.5 h-1.5 rounded-full bg-green-600 dark:bg-green-400 mr-2"></span>
                                            Validated
                                        </span>
                                    </td>
                                    <td className="px-6 py-5 text-slate-500 dark:text-slate-400 text-sm">Oct 24, 2023 14:32</td>
                                    <td className="px-6 py-5 text-right">
                                        <button className="text-primary hover:text-primary/80 font-bold text-sm transition-colors">Download</button>
                                    </td>
                                </tr>
                                <tr className="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors">
                                    <td className="px-6 py-5">
                                        <div className="flex items-center gap-3">
                                            <span className="material-symbols-outlined text-slate-400">article</span>
                                            <span className="text-slate-900 dark:text-white font-medium">Neural Networks Study - Final</span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-5">
                                        <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-primary/10 text-primary dark:bg-primary/20 dark:text-primary">
                                            <span className="w-1.5 h-1.5 rounded-full bg-primary mr-2 animate-pulse"></span>
                                            In Progress
                                        </span>
                                    </td>
                                    <td className="px-6 py-5 text-slate-500 dark:text-slate-400 text-sm">Oct 22, 2023 09:15</td>
                                    <td className="px-6 py-5 text-right">
                                        <button className="text-primary hover:text-primary/80 font-bold text-sm transition-colors">Edit</button>
                                    </td>
                                </tr>
                                <tr className="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors">
                                    <td className="px-6 py-5">
                                        <div className="flex items-center gap-3">
                                            <span className="material-symbols-outlined text-slate-400">article</span>
                                            <span className="text-slate-900 dark:text-white font-medium">Climate Change Analysis</span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-5">
                                        <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400">
                                            <span className="w-1.5 h-1.5 rounded-full bg-amber-600 dark:bg-amber-400 mr-2"></span>
                                            Formatting Needed
                                        </span>
                                    </td>
                                    <td className="px-6 py-5 text-slate-500 dark:text-slate-400 text-sm">Oct 20, 2023 18:45</td>
                                    <td className="px-6 py-5 text-right">
                                        <button className="text-primary hover:text-primary/80 font-bold text-sm transition-colors">Fix Errors</button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </main>

            <Footer variant="app" />
        </div>
    );
}
