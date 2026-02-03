import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { useDocument } from '../context/DocumentContext';
import { downloadFile } from '../services/api';

export default function Download() {
    const navigate = useNavigate();
    const { job } = useDocument();

    if (!job) {
        return (
            <div className="min-h-screen flex flex-col items-center justify-center">
                <p className="text-slate-500 mb-4">No completed job found.</p>
                <button onClick={() => navigate('/upload')} className="text-primary font-bold hover:underline">Return to Upload</button>
            </div>
        );
    }

    const handleDownload = async () => {
        try {
            // Use output_path if available from job result, otherwise fallback to a generic name
            const filename = job.outputPath || 'processed_manuscript.docx';
            const url = await downloadFile(filename);

            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', job.originalFileName ? `Formatted_${job.originalFileName}` : 'Manuscript_Formatted.docx');
            document.body.appendChild(link);
            link.click();
            link.parentNode.removeChild(link);
        } catch (error) {
            console.error("Download failed:", error);
            alert("Download failed. Please try again.");
        }
    };

    return (
        <>
            <Navbar variant="app" />

            <main className="px-4 md:px-20 lg:px-40 flex flex-1 justify-center py-12 min-h-[calc(100vh-200px)] animate-in zoom-in-95 duration-500">
                <div className="layout-content-container flex flex-col max-w-[800px] flex-1">
                    {/* Success Header */}
                    <div className="flex flex-col items-center mb-8">
                        <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 shadow-sm">
                            <span className="material-symbols-outlined text-4xl">check_circle</span>
                        </div>
                        <h1 className="text-[#0d131b] dark:text-slate-50 tracking-light text-[32px] font-bold leading-tight px-4 text-center pb-2">Formatting Complete!</h1>
                        <p className="text-[#4c6c9a] dark:text-slate-400 text-base text-center max-w-[500px]">Your manuscript has been successfully processed and is ready for submission.</p>
                    </div>

                    {/* Main Success Card */}
                    <div className="p-4 @container">
                        <div className="flex flex-col items-stretch justify-start rounded-xl @xl:flex-row @xl:items-start shadow-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 overflow-hidden">
                            <div className="w-full md:w-1/3 bg-slate-100 dark:bg-slate-800 flex items-center justify-center aspect-[3/4] group">
                                <span className="material-symbols-outlined text-7xl text-slate-300 dark:text-slate-600 group-hover:scale-110 transition-transform">description</span>
                            </div>
                            <div className="flex w-full min-w-72 grow flex-col items-stretch justify-center gap-6 py-8 px-6 @xl:px-8">
                                <div>
                                    <h3 className="text-[#0d131b] dark:text-slate-50 text-xl font-bold leading-tight tracking-[-0.015em] mb-2 flex items-center gap-2">
                                        <span className="material-symbols-outlined text-primary">description</span>
                                        {job.originalFileName}
                                    </h3>
                                    <div className="flex flex-col gap-2">
                                        <div className="flex items-center gap-2 text-[#4c6c9a] dark:text-slate-400">
                                            <span className="material-symbols-outlined text-sm">auto_awesome</span>
                                            <p className="text-sm font-medium">{job.template?.toUpperCase()} Template Applied</p>
                                        </div>
                                        <div className="flex items-center gap-2 text-[#4c6c9a] dark:text-slate-400">
                                            <span className="material-symbols-outlined text-sm">schedule</span>
                                            <p className="text-sm">Processed on {new Date(job.timestamp).toLocaleString()}</p>
                                        </div>
                                    </div>
                                </div>
                                <div className="flex flex-col gap-3">
                                    <button onClick={handleDownload} className="flex w-full cursor-pointer items-center justify-center gap-2 overflow-hidden rounded-lg h-12 px-6 bg-primary text-white text-base font-bold leading-normal transition-all hover:bg-blue-700 active:scale-[0.98] shadow-lg shadow-primary/20">
                                        <span className="material-symbols-outlined">download</span>
                                        <span className="truncate">Download Formatted Document</span>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Details and Next Steps */}
                    <div className="mt-8 px-4">
                        <h4 className="text-sm font-bold uppercase tracking-wider text-[#4c6c9a] dark:text-slate-500 mb-4 px-1">Processing Summary</h4>
                        <div className="grid grid-cols-1 md:grid-cols-[250px_1fr] gap-x-6 border-t border-slate-200 dark:border-slate-800">
                            <div className="col-span-2 grid grid-cols-subgrid border-b border-slate-200 dark:border-slate-800 py-4 items-center">
                                <p className="text-[#4c6c9a] dark:text-slate-400 text-sm font-semibold uppercase tracking-tight">Output Format</p>
                                <div className="flex items-center gap-2">
                                    <span className="material-symbols-outlined text-blue-500">article</span>
                                    <p className="text-[#0d131b] dark:text-slate-200 text-sm font-medium">Microsoft Word (DOCX)</p>
                                </div>
                            </div>
                            <div className="col-span-2 grid grid-cols-subgrid border-b border-slate-200 dark:border-slate-800 py-4 items-center">
                                <p className="text-[#4c6c9a] dark:text-slate-400 text-sm font-semibold uppercase tracking-tight">Style Guide</p>
                                <p className="text-[#0d131b] dark:text-slate-200 text-sm font-medium uppercase">{job.template} Academic Standard</p>
                            </div>
                            <div className="col-span-2 grid grid-cols-subgrid border-b border-slate-200 dark:border-slate-800 py-4 items-center">
                                <p className="text-[#4c6c9a] dark:text-slate-400 text-sm font-semibold uppercase tracking-tight">AI Enhancement</p>
                                <div className="flex items-center gap-2">
                                    <span className="material-symbols-outlined text-primary text-sm">auto_awesome</span>
                                    <p className="text-[#0d131b] dark:text-slate-200 text-sm">{job.flags?.ai_used ? 'AI Analysis and Correction enabled' : 'Standard formatting only'}</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Secondary Action Button Group */}
                    <div className="mt-10 mb-20 flex justify-center">
                        <div className="flex flex-col sm:flex-row gap-4 px-4 py-3 w-full max-w-[600px] justify-center">
                            <button onClick={() => navigate('/upload')} className="flex min-w-[160px] cursor-pointer items-center justify-center gap-2 overflow-hidden rounded-lg h-12 px-6 bg-slate-200 dark:bg-slate-800 text-[#0d131b] dark:text-slate-50 text-sm font-bold leading-normal tracking-[0.015em] grow transition-colors hover:bg-slate-300 dark:hover:bg-slate-700">
                                <span className="material-symbols-outlined text-xl">upload_file</span>
                                <span className="truncate">Upload Another</span>
                            </button>
                            <button onClick={() => navigate('/results')} className="flex min-w-[160px] cursor-pointer items-center justify-center gap-2 overflow-hidden rounded-lg h-12 px-6 bg-white dark:bg-slate-900 border-2 border-slate-200 dark:border-slate-700 text-[#0d131b] dark:text-slate-50 text-sm font-bold leading-normal tracking-[0.015em] grow transition-colors hover:bg-slate-50 dark:hover:bg-slate-800">
                                <span className="material-symbols-outlined text-xl">fact_check</span>
                                <span className="truncate">Validation Report</span>
                            </button>
                        </div>
                    </div>
                </div>
            </main>

            <Footer variant="app" />
        </>
    );
}

