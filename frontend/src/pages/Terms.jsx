import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

export default function Terms() {
    return (
        <div className="min-h-screen bg-background-light dark:bg-background-dark text-slate-900 dark:text-slate-100 flex flex-col">
            <Navbar variant="app" />
            <main className="flex-1 max-w-4xl mx-auto w-full px-4 sm:px-6 py-8 sm:py-10">
                <h1 className="text-3xl sm:text-4xl font-black tracking-tight text-slate-900 dark:text-white">
                    Terms of Service
                </h1>
                <p className="mt-2 text-slate-600 dark:text-slate-400">
                    Effective date: {new Date().toLocaleDateString()}
                </p>

                <div className="mt-8 space-y-6">
                    <section className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 sm:p-6">
                        <h2 className="text-lg font-bold text-slate-900 dark:text-white">Use of Service</h2>
                        <p className="mt-2 text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                            You may use ScholarForm AI for lawful academic and research workflows. You are responsible
                            for the content you upload and for ensuring rights to process that content.
                        </p>
                    </section>

                    <section className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 sm:p-6">
                        <h2 className="text-lg font-bold text-slate-900 dark:text-white">Account Responsibility</h2>
                        <p className="mt-2 text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                            Keep your account credentials secure. You are responsible for activity under your account
                            unless unauthorized access is promptly reported.
                        </p>
                    </section>

                    <section className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 sm:p-6">
                        <h2 className="text-lg font-bold text-slate-900 dark:text-white">Limits and Availability</h2>
                        <p className="mt-2 text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                            We may update features, templates, and limits over time. Service availability and processing
                            speed can vary by workload and upstream provider status.
                        </p>
                    </section>
                </div>
            </main>
            <Footer variant="app" />
        </div>
    );
}
