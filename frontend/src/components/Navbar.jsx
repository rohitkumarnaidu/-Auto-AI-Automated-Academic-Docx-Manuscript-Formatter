/* eslint-disable react/prop-types */
import { Link } from 'react-router-dom';

export default function Navbar({ variant = 'app' }) {
    if (variant === 'landing') {
        return (
            <header className="sticky top-0 z-50 w-full border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-background-dark/80 backdrop-blur-md">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex h-16 items-center justify-between">
                        <div className="flex items-center gap-2">
                            <div className="bg-primary text-white p-1.5 rounded-lg flex items-center justify-center">
                                <span className="material-symbols-outlined text-xl">menu_book</span>
                            </div>
                            <span className="text-xl font-bold tracking-tight text-slate-900 dark:text-white">ManuscriptFormatter</span>
                        </div>
                        <nav className="hidden md:flex items-center gap-8">
                            <a href="#" className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-primary transition-colors">Features</a>
                            <a href="#" className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-primary transition-colors">Pricing</a>
                            <a href="#" className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-primary transition-colors">Guidelines</a>
                            <a href="#" className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-primary transition-colors">About</a>
                        </nav>
                        <div className="flex items-center gap-3">
                            <button className="text-sm font-semibold text-slate-700 dark:text-slate-200 px-4 py-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">Sign In</button>
                            <Link to="/upload" className="bg-primary text-white text-sm font-bold px-5 py-2.5 rounded-lg hover:bg-blue-600 shadow-sm transition-all">Get Started</Link>
                        </div>
                    </div>
                </div>
            </header>
        );
    }

    // App Navbar
    return (
        <header className="flex items-center justify-between whitespace-nowrap border-b border-solid border-[#e7ecf3] dark:border-slate-800 bg-white dark:bg-background-dark px-10 py-3 sticky top-0 z-50">
            <div className="flex items-center gap-4 text-primary">
                <div className="size-8 flex items-center justify-center bg-primary rounded-lg text-white">
                    <span className="material-symbols-outlined">auto_stories</span>
                </div>
                <Link to="/" className="text-slate-900 dark:text-white text-lg font-bold leading-tight tracking-[-0.015em]">ScholarForm AI</Link>
            </div>
            <div className="flex flex-1 justify-end gap-8">
                <nav className="flex items-center gap-9">
                    <Link to="/" className="text-slate-600 dark:text-slate-300 text-sm font-medium hover:text-primary transition-colors">Dashboard</Link>
                    <Link to="/upload" className="text-slate-900 dark:text-white text-sm font-bold border-b-2 border-primary py-1">Upload</Link>
                    <Link to="/history" className="text-slate-600 dark:text-slate-300 text-sm font-medium hover:text-primary transition-colors">My Manuscripts</Link>
                    <a href="#" className="text-slate-600 dark:text-slate-300 text-sm font-medium hover:text-primary transition-colors">Templates</a>
                </nav>
                <div className="flex gap-2">
                    <button className="flex items-center justify-center rounded-lg h-10 w-10 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200">
                        <span className="material-symbols-outlined">notifications</span>
                    </button>
                    <button className="flex items-center justify-center rounded-lg h-10 w-10 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200">
                        <span className="material-symbols-outlined">settings</span>
                    </button>
                </div>
                <div className="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-10 border border-slate-200 dark:border-slate-700" style={{ backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuCBAnQke1dGWniClQX7rHZBtni1hbRlIpllATyD41NPPw3Br765F9F0vIWQH7I2SezfqlRBNZW0hgkDJ4Kl-Ekd0MVD60AqnPJe_Q0QkDvG2fqpVzmz_HTsQKFKkBIvfvFH26zii0uK7s11gs1bnXmlnWvG6LS6GTXhY6thfBqwRUWqvuAIMWQfqwnAs0DFEX2j3QBP0F7mG913xvhu2iMMo_MIgxF_nqEmviIbI0G3jFBvWtp3KPkAPAxfc4YVXlrDPh_tJJ5ZgnHP")' }}></div>
            </div>
        </header>
    );
}
