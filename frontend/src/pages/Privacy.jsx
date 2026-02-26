import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

export default function Privacy() {
    return (
        <div className="min-h-screen bg-background-light dark:bg-background-dark text-slate-900 dark:text-slate-100 flex flex-col">
            <Navbar variant="app" />
            <main className="flex-1 max-w-4xl mx-auto w-full px-4 sm:px-6 py-8 sm:py-10">
                <h1 className="text-3xl sm:text-4xl font-black tracking-tight text-slate-900 dark:text-white">
                    Privacy Policy
                </h1>
                <p className="mt-2 text-slate-600 dark:text-slate-400">
                    Effective date: {new Date().toLocaleDateString()}
                </p>

                <div className="mt-8 space-y-6">
                    <section className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 sm:p-6">
                        <h2 className="text-lg font-bold text-slate-900 dark:text-white">Data We Process</h2>
                        <p className="mt-2 text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                            We process account metadata and uploaded manuscript content to provide formatting,
                            validation, and export features.
                        </p>
                    </section>

                    <section className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 sm:p-6">
                        <h2 className="text-lg font-bold text-slate-900 dark:text-white">How Data Is Used</h2>
                        <p className="mt-2 text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                            Data is used to execute document processing workflows, maintain account history, and improve
                            reliability and quality of the service.
                        </p>
                    </section>

                    <section className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 sm:p-6">
                        <h2 className="text-lg font-bold text-slate-900 dark:text-white">Contact</h2>
                        <p className="mt-2 text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                            For privacy requests, contact <a className="text-primary hover:underline" href="mailto:support@scholarform.ai">support@scholarform.ai</a>.
                        </p>
                    </section>
                </div>
            </main>
            <Footer variant="app" />
        </div>
    );
}
