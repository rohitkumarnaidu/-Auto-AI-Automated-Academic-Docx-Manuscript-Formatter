import usePageTitle from '../hooks/usePageTitle';
import { useState, useRef, useEffect } from 'react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { Link } from 'react-router-dom';
import useScrollReveal from '../hooks/useScrollReveal';

// Lightweight count-up hook — requestAnimationFrame, disconnects on reveal
function useCountUp(target, duration = 1500) {
    const [count, setCount] = useState(0);
    const ref = useRef(null);

    useEffect(() => {
        const el = ref.current;
        if (!el) return;

        let rafId = null;
        let cancelled = false;
        let started = false;

        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            setCount(target);
            return;
        }

        const observer = new IntersectionObserver(([entry]) => {
            if (entry.isIntersecting && !started) {
                started = true;
                let start = 0;
                const step = target / Math.max(duration / 16, 1);

                const tick = () => {
                    if (cancelled) return;
                    start = Math.min(start + step, target);
                    setCount(Math.floor(start));
                    if (start < target) rafId = requestAnimationFrame(tick);
                };

                rafId = requestAnimationFrame(tick);
                observer.disconnect();
            }
        }, { threshold: 0.5 });

        observer.observe(el);
        return () => {
            cancelled = true;
            observer.disconnect();
            if (rafId !== null) {
                cancelAnimationFrame(rafId);
            }
        };
    }, [target, duration]);

    return { count, ref };
}

export default function Landing() {
    usePageTitle('Automated Academic Manuscript Formatter');
    const heroRef = useRef(null);
    const [animateHero, setAnimateHero] = useState(true);
    const [isScrolling, setIsScrolling] = useState(false);
    const featuresRef = useScrollReveal();
    const templatesRef = useScrollReveal();
    const pricingRef = useScrollReveal();
    const ctaRef = useScrollReveal();
    const aboutRef = useScrollReveal();
    const researchers = useCountUp(25000, 1800);
    const templates = useCountUp(1000, 1500);
    const universities = useCountUp(50, 1200);

    useEffect(() => {
        const section = heroRef.current;
        if (!section) return;

        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            setAnimateHero(false);
            return;
        }

        const observer = new IntersectionObserver(
            ([entry]) => setAnimateHero(entry.isIntersecting),
            { threshold: 0.15 }
        );
        observer.observe(section);
        return () => observer.disconnect();
    }, []);

    useEffect(() => {
        let timeoutId = null;
        const onScroll = () => {
            setIsScrolling(true);
            if (timeoutId !== null) {
                clearTimeout(timeoutId);
            }
            timeoutId = setTimeout(() => setIsScrolling(false), 120);
        };

        window.addEventListener('scroll', onScroll, { passive: true });
        return () => {
            window.removeEventListener('scroll', onScroll);
            if (timeoutId !== null) {
                clearTimeout(timeoutId);
            }
        };
    }, []);

    const shouldAnimateHero = animateHero && !isScrolling;

    const heroAnimation = (base, delay) => {
        if (!shouldAnimateHero) return undefined;
        return delay ? { animation: base, animationDelay: delay } : { animation: base };
    };

    return (
        <>
            <Navbar variant="landing" />

            {/* Hero Section */}
            <section ref={heroRef} className="relative overflow-hidden py-16 lg:py-24">
                {/* Gradient depth blobs */}
                <div className="absolute inset-0 -z-10 overflow-hidden pointer-events-none">
                    <div className="absolute -top-40 -right-40 w-[600px] h-[600px] rounded-full bg-primary/5 dark:bg-primary/10 blur-2xl" />
                    <div className="absolute -bottom-40 -left-40 w-[500px] h-[500px] rounded-full bg-violet-500/5 dark:bg-violet-500/10 blur-2xl" />
                </div>
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                        <div className="flex flex-col gap-8 fade-in-up">
                            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-bold uppercase tracking-wider w-fit">
                                <span className="material-symbols-outlined text-sm">verified</span>
                                AI-Powered Academic Standard
                            </div>
                            <div className="flex flex-col gap-4">
                                <h1 className="text-4xl md:text-5xl lg:text-6xl font-black text-slate-900 dark:text-white leading-[1.1] tracking-tight">
                                    Write, validate, structure, and format academic papers <span className="text-primary">automatically.</span>
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
                                    <span className="text-xs text-slate-400">.docx, .pdf, .tex</span>
                                </div>
                            </div>
                        </div>
                        <div className="relative fade-in-up" style={{ animationDelay: '200ms' }}>
                            <div className="aspect-[4/3] rounded-2xl overflow-hidden bg-white dark:bg-slate-800 shadow-2xl border border-slate-200 dark:border-slate-700 relative" style={heroAnimation('hero-pulse-glow 3s ease-in-out infinite')}>
                                {/* Animated scanning line */}
                                <div className="absolute left-0 w-full h-0.5 bg-gradient-to-r from-transparent via-primary to-transparent z-10 pointer-events-none" style={heroAnimation('hero-scan-line 6s ease-in-out infinite')} />

                                <div className="absolute inset-0 flex flex-col">
                                    {/* Title bar */}
                                    <div className="flex items-center gap-2 px-4 py-2.5 border-b border-slate-100 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/50">
                                        <div className="flex gap-1.5">
                                            <div className="w-2.5 h-2.5 rounded-full bg-red-400" />
                                            <div className="w-2.5 h-2.5 rounded-full bg-amber-400" />
                                            <div className="w-2.5 h-2.5 rounded-full bg-green-400" />
                                        </div>
                                        <div className="flex-1 flex justify-center">
                                            <div className="px-3 py-0.5 bg-white dark:bg-slate-800 rounded text-[10px] font-medium text-slate-500 dark:text-slate-400 border border-slate-200 dark:border-slate-700">
                                                research_paper.docx
                                            </div>
                                        </div>
                                    </div>

                                    {/* Document body with animated typing */}
                                    <div className="flex-1 flex">
                                        <div className="flex-1 p-5 flex flex-col gap-3">
                                            {/* Heading */}
                                            <div className="h-5 bg-slate-800 dark:bg-white rounded-sm" style={{ ...heroAnimation('hero-line-type 6s ease-out infinite'), maxWidth: '65%' }} />
                                            {/* Body lines typing in with stagger */}
                                            <div className="h-3 bg-slate-200 dark:bg-slate-600 rounded-sm" style={{ ...heroAnimation('hero-line-type 6s ease-out infinite', '0.3s'), maxWidth: '95%' }} />
                                            <div className="h-3 bg-slate-200 dark:bg-slate-600 rounded-sm" style={{ ...heroAnimation('hero-line-type 6s ease-out infinite', '0.5s'), maxWidth: '88%' }} />
                                            <div className="h-3 bg-slate-200 dark:bg-slate-600 rounded-sm" style={{ ...heroAnimation('hero-line-type 6s ease-out infinite', '0.7s'), maxWidth: '92%' }} />
                                            <div className="h-3 bg-slate-200 dark:bg-slate-600 rounded-sm" style={{ ...heroAnimation('hero-line-type 6s ease-out infinite', '0.9s'), maxWidth: '60%' }} />
                                            {/* Spacer */}
                                            <div className="h-2" />
                                            {/* Sub heading */}
                                            <div className="h-4 bg-slate-700 dark:bg-slate-200 rounded-sm" style={{ ...heroAnimation('hero-line-type 6s ease-out infinite', '1.2s'), maxWidth: '45%' }} />
                                            <div className="h-3 bg-slate-200 dark:bg-slate-600 rounded-sm" style={{ ...heroAnimation('hero-line-type 6s ease-out infinite', '1.4s'), maxWidth: '90%' }} />
                                            <div className="h-3 bg-slate-200 dark:bg-slate-600 rounded-sm" style={{ ...heroAnimation('hero-line-type 6s ease-out infinite', '1.6s'), maxWidth: '85%' }} />
                                        </div>

                                        {/* Right sidebar — validation panel */}
                                        <div className="w-[35%] border-l border-slate-100 dark:border-slate-700 p-3 flex flex-col gap-2.5 bg-slate-50/50 dark:bg-slate-900/30">
                                            <div className="text-[9px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">Formatting</div>
                                            {/* Progress bar */}
                                            <div className="h-1.5 rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden">
                                                <div className="h-full rounded-full bg-primary" style={heroAnimation('hero-progress-fill 6s ease-out infinite')} />
                                            </div>
                                            {/* Checklist items */}
                                            {['Citations', 'Headings', 'Margins', 'Figures'].map((label, i) => (
                                                <div key={label} className="flex items-center gap-1.5">
                                                    <span className="material-symbols-outlined text-green-500 text-xs" style={shouldAnimateHero ? { animation: 'hero-check-pop 6s ease-out infinite', animationDelay: `${2 + i * 0.5}s`, opacity: 0 } : { opacity: 1 }}>check_circle</span>
                                                    <span className="text-[9px] text-slate-500 dark:text-slate-400">{label}</span>
                                                </div>
                                            ))}
                                            {/* Template badge */}
                                            <div className="mt-auto px-2 py-1 rounded bg-primary/10 border border-primary/20 text-[9px] text-primary font-bold text-center" style={shouldAnimateHero ? { animation: 'hero-check-pop 6s ease-out infinite', animationDelay: '4s', opacity: 0 } : { opacity: 1 }}>
                                                IEEE Formatted ✓
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
                                        <p className="text-sm text-slate-500 dark:text-slate-400">~98% Precision*</p>
                                        <p className="text-xl font-bold text-slate-900 dark:text-white">Validation Rate</p>
                                        <p className="text-[9px] text-slate-400 mt-0.5">*Based on internal benchmarks. Actual results may vary.</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Feature Grid Section */}
            <section className="py-20 bg-white dark:bg-background-dark/50 section-texture cv-auto" id="features">
                <div ref={featuresRef} className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 scroll-reveal">
                    <div className="text-center max-w-3xl mx-auto mb-16">
                        <h2 className="text-primary font-bold text-sm tracking-widest uppercase mb-3">Powerful Capabilities</h2>
                        <h3 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-6 leading-tight">Designed to meet the rigorous standards of global academic publishing.</h3>
                        <p className="text-slate-600 dark:text-slate-400">Our platform combines machine learning with human-grade formatting rules to ensure your research is presented perfectly every time.</p>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {/* Feature 1 — Blue */}
                        <div className="group p-8 bg-white dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-700 hover:border-blue-400/50 transition-all duration-300 hover:shadow-xl hover:shadow-blue-500/10 hover:-translate-y-1.5 hover:bg-blue-50/50 dark:hover:bg-blue-950/20 relative overflow-hidden">
                            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-blue-500 to-cyan-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                            <div className="size-12 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 text-white flex items-center justify-center mb-6 group-hover:scale-110 group-hover:shadow-lg group-hover:shadow-blue-500/30 transition-all">
                                <span className="material-symbols-outlined">file_open</span>
                            </div>
                            <h4 className="text-xl font-bold text-slate-900 dark:text-white mb-3">Multi-format support</h4>
                            <p className="text-slate-600 dark:text-slate-400 leading-relaxed">Export seamlessly to high-fidelity PDF, clean LaTeX source code, and fully editable Word formats for further collaboration.</p>
                        </div>
                        {/* Feature 2 — Violet */}
                        <div className="group p-8 bg-white dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-700 hover:border-violet-400/50 transition-all duration-300 hover:shadow-xl hover:shadow-violet-500/10 hover:-translate-y-1.5 hover:bg-violet-50/50 dark:hover:bg-violet-950/20 relative overflow-hidden">
                            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-violet-500 to-purple-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                            <div className="size-12 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 text-white flex items-center justify-center mb-6 group-hover:scale-110 group-hover:shadow-lg group-hover:shadow-violet-500/30 transition-all">
                                <span className="material-symbols-outlined">scan</span>
                            </div>
                            <h4 className="text-xl font-bold text-slate-900 dark:text-white mb-3">OCR support</h4>
                            <p className="text-slate-600 dark:text-slate-400 leading-relaxed">Advanced optical character recognition to convert scanned citations, handwritten notes, and image tables into perfectly editable text.</p>
                        </div>
                        {/* Feature 3 — Emerald */}
                        <div className="group p-8 bg-white dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-700 hover:border-emerald-400/50 transition-all duration-300 hover:shadow-xl hover:shadow-emerald-500/10 hover:-translate-y-1.5 hover:bg-emerald-50/50 dark:hover:bg-emerald-950/20 relative overflow-hidden">
                            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-emerald-500 to-teal-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                            <div className="size-12 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 text-white flex items-center justify-center mb-6 group-hover:scale-110 group-hover:shadow-lg group-hover:shadow-emerald-500/30 transition-all">
                                <span className="material-symbols-outlined">verified_user</span>
                            </div>
                            <h4 className="text-xl font-bold text-slate-900 dark:text-white mb-3">Academic validation</h4>
                            <p className="text-slate-600 dark:text-slate-400 leading-relaxed">Automated checks against specific journal-specific requirements including word counts, figure positioning, and reference density.</p>
                        </div>
                        {/* Feature 4 — Amber */}
                        <div className="group p-8 bg-white dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-700 hover:border-amber-400/50 transition-all duration-300 hover:shadow-xl hover:shadow-amber-500/10 hover:-translate-y-1.5 hover:bg-amber-50/50 dark:hover:bg-amber-950/20 relative overflow-hidden">
                            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-amber-500 to-orange-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                            <div className="size-12 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 text-white flex items-center justify-center mb-6 group-hover:scale-110 group-hover:shadow-lg group-hover:shadow-amber-500/30 transition-all">
                                <span className="material-symbols-outlined">format_list_bulleted</span>
                            </div>
                            <h4 className="text-xl font-bold text-slate-900 dark:text-white mb-3">IEEE/Springer/APA</h4>
                            <p className="text-slate-600 dark:text-slate-400 leading-relaxed">Apply 1000+ citation styles with one click. We maintain up-to-date templates for major publishers and international conferences.</p>
                        </div>
                        {/* Feature 5 — Rose */}
                        <div className="group p-8 bg-white dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-700 hover:border-rose-400/50 transition-all duration-300 hover:shadow-xl hover:shadow-rose-500/10 hover:-translate-y-1.5 hover:bg-rose-50/50 dark:hover:bg-rose-950/20 relative overflow-hidden">
                            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-rose-500 to-pink-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                            <div className="size-12 rounded-xl bg-gradient-to-br from-rose-500 to-pink-600 text-white flex items-center justify-center mb-6 group-hover:scale-110 group-hover:shadow-lg group-hover:shadow-rose-500/30 transition-all">
                                <span className="material-symbols-outlined">auto_awesome</span>
                            </div>
                            <h4 className="text-xl font-bold text-slate-900 dark:text-white mb-3">AI-assisted insights</h4>
                            <p className="text-slate-600 dark:text-slate-400 leading-relaxed">Structural feedback on document flow and writing clarity. Identify passive voice, repetitive phrases, and weak transitions instantly.</p>
                        </div>
                        {/* Feature 6 — Cyan */}
                        <div className="group p-8 bg-white dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-700 hover:border-cyan-400/50 transition-all duration-300 hover:shadow-xl hover:shadow-cyan-500/10 hover:-translate-y-1.5 hover:bg-cyan-50/50 dark:hover:bg-cyan-950/20 relative overflow-hidden">
                            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-cyan-500 to-sky-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                            <div className="size-12 rounded-xl bg-gradient-to-br from-cyan-500 to-sky-600 text-white flex items-center justify-center mb-6 group-hover:scale-110 group-hover:shadow-lg group-hover:shadow-cyan-500/30 transition-all">
                                <span className="material-symbols-outlined">lock</span>
                            </div>
                            <h4 className="text-xl font-bold text-slate-900 dark:text-white mb-3">IP Protection</h4>
                            <p className="text-slate-600 dark:text-slate-400 leading-relaxed">Enterprise-grade encryption for your intellectual property. Your research stays private and securely stored.</p>
                        </div>
                    </div>
                </div>
            </section>

            {/* Templates Preview Section */}
            <section className="py-20 bg-background-light dark:bg-slate-900/30 cv-auto" id="templates">
                <div ref={templatesRef} className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 scroll-reveal">
                    <div className="text-center max-w-3xl mx-auto mb-16">
                        <h2 className="text-primary font-bold text-sm tracking-widest uppercase mb-3">Journal Library</h2>
                        <h3 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-6 leading-tight">One-click formatting for 1,000+ journals.</h3>
                        <p className="text-slate-600 dark:text-slate-400">Our library is constantly updated with the latest formatting requirements from major academic publishers.</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
                        {/* IEEE Preview Card */}
                        <Link to="/templates" className="flex flex-col gap-4 p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:shadow-xl hover:shadow-blue-500/10 hover:border-blue-300 dark:hover:border-blue-500/40 transition-all duration-300 group relative overflow-hidden hover:-translate-y-1">
                            <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-blue-500 to-cyan-400 rounded-l-xl" />
                            <div className="flex justify-between items-start">
                                <div className="size-10 rounded-lg bg-blue-50 dark:bg-blue-900/20 flex items-center justify-center text-blue-600 dark:text-blue-400 border border-blue-100 dark:border-blue-800/30">
                                    <span className="material-symbols-outlined text-[24px]">architecture</span>
                                </div>
                                <span className="px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400">Available</span>
                            </div>
                            <div className="flex flex-col gap-1">
                                <h3 className="text-slate-900 dark:text-white text-lg font-bold group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">IEEE Transactions</h3>
                                <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed line-clamp-2">Official format for technical, electrical, and engineering research.</p>
                            </div>
                        </Link>

                        {/* Nature Preview Card */}
                        <Link to="/templates" className="flex flex-col gap-4 p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:shadow-xl hover:shadow-emerald-500/10 hover:border-emerald-300 dark:hover:border-emerald-500/40 transition-all duration-300 group relative overflow-hidden hover:-translate-y-1">
                            <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-emerald-500 to-teal-400 rounded-l-xl" />
                            <div className="flex justify-between items-start">
                                <div className="size-10 rounded-lg bg-emerald-50 dark:bg-emerald-900/20 flex items-center justify-center text-emerald-600 dark:text-emerald-400 border border-emerald-100 dark:border-emerald-800/30">
                                    <span className="material-symbols-outlined text-[24px]">biotech</span>
                                </div>
                                <span className="px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400">Available</span>
                            </div>
                            <div className="flex flex-col gap-1">
                                <h3 className="text-slate-900 dark:text-white text-lg font-bold group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors">Nature Portfolio</h3>
                                <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed line-clamp-2">Standard template for submission to all Nature Portfolio journals.</p>
                            </div>
                        </Link>

                        {/* Elsevier Preview Card */}
                        <Link to="/templates" className="flex flex-col gap-4 p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:shadow-xl hover:shadow-violet-500/10 hover:border-violet-300 dark:hover:border-violet-500/40 transition-all duration-300 group relative overflow-hidden hover:-translate-y-1">
                            <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-violet-500 to-purple-400 rounded-l-xl" />
                            <div className="flex justify-between items-start">
                                <div className="size-10 rounded-lg bg-violet-50 dark:bg-violet-900/20 flex items-center justify-center text-violet-600 dark:text-violet-400 border border-violet-100 dark:border-violet-800/30">
                                    <span className="material-symbols-outlined text-[24px]">description</span>
                                </div>
                                <span className="px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400">Available</span>
                            </div>
                            <div className="flex flex-col gap-1">
                                <h3 className="text-slate-900 dark:text-white text-lg font-bold group-hover:text-violet-600 dark:group-hover:text-violet-400 transition-colors">Elsevier Standard</h3>
                                <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed line-clamp-2">Guidelines compatible with Elsevier&apos;s wide range of journals.</p>
                            </div>
                        </Link>

                        {/* APA Preview Card */}
                        <Link to="/templates" className="flex flex-col gap-4 p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:shadow-xl hover:shadow-amber-500/10 hover:border-amber-300 dark:hover:border-amber-500/40 transition-all duration-300 group relative overflow-hidden hover:-translate-y-1">
                            <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-amber-500 to-orange-400 rounded-l-xl" />
                            <div className="flex justify-between items-start">
                                <div className="size-10 rounded-lg bg-amber-50 dark:bg-amber-900/20 flex items-center justify-center text-amber-600 dark:text-amber-400 border border-amber-100 dark:border-amber-800/30">
                                    <span className="material-symbols-outlined text-[24px]">history_edu</span>
                                </div>
                                <span className="px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400">Available</span>
                            </div>
                            <div className="flex flex-col gap-1">
                                <h3 className="text-slate-900 dark:text-white text-lg font-bold group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-colors">APA 7th Edition</h3>
                                <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed line-clamp-2">Latest standards for social and behavioral sciences research.</p>
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

            {/* Pricing Section */}
            <section className="py-20 bg-white dark:bg-background-dark/50 section-texture cv-auto" id="pricing">
                <div ref={pricingRef} className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 scroll-reveal">
                    <div className="text-center max-w-3xl mx-auto mb-16">
                        <h2 className="text-primary font-bold text-sm tracking-widest uppercase mb-3">Pricing</h2>
                        <h3 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-6 leading-tight">Simple, transparent pricing for every researcher.</h3>
                        <p className="text-slate-600 dark:text-slate-400">Start for free. Upgrade when you need more power. No hidden fees.</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
                        {/* Free Tier */}
                        <div className="flex flex-col p-8 bg-background-light dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-700 hover:shadow-lg transition-all">
                            <div className="mb-6">
                                <h4 className="text-lg font-bold text-slate-900 dark:text-white mb-1">Starter</h4>
                                <p className="text-sm text-slate-500 dark:text-slate-400">For individual researchers</p>
                            </div>
                            <div className="mb-6">
                                <span className="text-4xl font-black text-slate-900 dark:text-white">Free</span>
                            </div>
                            <ul className="space-y-3 mb-8 flex-1">
                                <li className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
                                    <span className="material-symbols-outlined text-green-500 text-lg mt-0.5">check_circle</span>
                                    3 manuscripts per month
                                </li>
                                <li className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
                                    <span className="material-symbols-outlined text-green-500 text-lg mt-0.5">check_circle</span>
                                    Basic formatting (IEEE, APA)
                                </li>
                                <li className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
                                    <span className="material-symbols-outlined text-green-500 text-lg mt-0.5">check_circle</span>
                                    DOCX export
                                </li>
                                <li className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
                                    <span className="material-symbols-outlined text-green-500 text-lg mt-0.5">check_circle</span>
                                    Community support
                                </li>
                            </ul>
                            <Link to="/signup" className="w-full text-center bg-slate-100 dark:bg-slate-700 text-slate-900 dark:text-white py-3 px-6 rounded-xl font-bold text-sm hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors">
                                Get Started Free
                            </Link>
                        </div>

                        {/* Pro Tier */}
                        <div className="flex flex-col p-8 bg-white dark:bg-slate-900 rounded-2xl border-2 border-primary shadow-xl shadow-primary/10 relative scale-[1.03]">
                            <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-primary text-white text-xs font-bold px-4 py-1 rounded-full uppercase tracking-wider">
                                Most Popular
                            </div>
                            <div className="mb-6">
                                <h4 className="text-lg font-bold text-slate-900 dark:text-white mb-1">Pro</h4>
                                <p className="text-sm text-slate-500 dark:text-slate-400">For active academics</p>
                            </div>
                            <div className="mb-6">
                                <span className="text-4xl font-black text-slate-900 dark:text-white">$12</span>
                                <span className="text-slate-500 dark:text-slate-400 text-sm ml-1">/month</span>
                            </div>
                            <ul className="space-y-3 mb-8 flex-1">
                                <li className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
                                    <span className="material-symbols-outlined text-green-500 text-lg mt-0.5">check_circle</span>
                                    Unlimited manuscripts
                                </li>
                                <li className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
                                    <span className="material-symbols-outlined text-green-500 text-lg mt-0.5">check_circle</span>
                                    All 1,000+ journal templates
                                </li>
                                <li className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
                                    <span className="material-symbols-outlined text-green-500 text-lg mt-0.5">check_circle</span>
                                    PDF, LaTeX, DOCX export
                                </li>
                                <li className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
                                    <span className="material-symbols-outlined text-green-500 text-lg mt-0.5">check_circle</span>
                                    AI writing insights
                                </li>
                                <li className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
                                    <span className="material-symbols-outlined text-green-500 text-lg mt-0.5">check_circle</span>
                                    Priority processing
                                </li>
                            </ul>
                            <Link to="/signup" className="w-full text-center bg-primary text-white py-3 px-6 rounded-xl font-bold text-sm hover:bg-blue-600 transition-colors shadow-lg shadow-primary/25">
                                Start 14-Day Free Trial
                            </Link>
                        </div>

                        {/* Institution Tier */}
                        <div className="flex flex-col p-8 bg-background-light dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-700 hover:shadow-lg transition-all">
                            <div className="mb-6">
                                <h4 className="text-lg font-bold text-slate-900 dark:text-white mb-1">Institution</h4>
                                <p className="text-sm text-slate-500 dark:text-slate-400">For labs &amp; departments</p>
                            </div>
                            <div className="mb-6">
                                <span className="text-4xl font-black text-slate-900 dark:text-white">Custom</span>
                            </div>
                            <ul className="space-y-3 mb-8 flex-1">
                                <li className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
                                    <span className="material-symbols-outlined text-green-500 text-lg mt-0.5">check_circle</span>
                                    Everything in Pro
                                </li>
                                <li className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
                                    <span className="material-symbols-outlined text-green-500 text-lg mt-0.5">check_circle</span>
                                    Unlimited team seats
                                </li>
                                <li className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
                                    <span className="material-symbols-outlined text-green-500 text-lg mt-0.5">check_circle</span>
                                    Custom template builder
                                </li>
                                <li className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
                                    <span className="material-symbols-outlined text-green-500 text-lg mt-0.5">check_circle</span>
                                    SSO &amp; admin dashboard
                                </li>
                                <li className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
                                    <span className="material-symbols-outlined text-green-500 text-lg mt-0.5">check_circle</span>
                                    Dedicated support
                                </li>
                            </ul>
                            <a href="mailto:sales@scholarform.ai" className="w-full text-center bg-slate-100 dark:bg-slate-700 text-slate-900 dark:text-white py-3 px-6 rounded-xl font-bold text-sm hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors">
                                Contact Sales
                            </a>
                        </div>
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="py-16 cv-auto">
                <div ref={ctaRef} className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 scroll-reveal">
                    <div className="relative bg-gradient-to-br from-slate-900 via-blue-950 to-indigo-950 dark:from-slate-950 dark:via-blue-950 dark:to-indigo-950 rounded-3xl p-8 md:p-16 overflow-hidden">
                        <div className="absolute -top-20 -right-20 w-80 h-80 bg-primary/20 rounded-full blur-3xl" />
                        <div className="absolute -bottom-20 -left-20 w-60 h-60 bg-violet-500/15 rounded-full blur-3xl" />
                        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl" />
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

            {/* About Section */}
            <section id="about" className="py-20 bg-background-light dark:bg-slate-900/30 cv-auto">
                <div ref={aboutRef} className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 scroll-reveal">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
                        <div className="flex flex-col gap-6">
                            <h2 className="text-primary font-bold text-sm tracking-widest uppercase">About ScholarForm AI</h2>
                            <h3 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white leading-tight">
                                Built by researchers, for researchers.
                            </h3>
                            <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
                                ScholarForm AI was born from a simple frustration: spending more time formatting papers than writing them. Our team of academic researchers and AI engineers built the tool they wished existed — one that understands the nuances of journal-specific requirements and does the tedious work automatically.
                            </p>
                            <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
                                We combine deep learning models trained on thousands of published papers with rule-based validation engines that catch every formatting detail. From citation styles to figure placement, margin sizes to heading hierarchy — we handle it all so you can focus on what matters: your research.
                            </p>
                            <div className="grid grid-cols-3 gap-6 mt-4">
                                <div ref={researchers.ref} className="text-center">
                                    <p className="text-3xl font-black text-primary">{researchers.count >= 1000 ? `${(researchers.count / 1000).toFixed(researchers.count >= 25000 ? 0 : 1)}k+` : `${researchers.count}+`}</p>
                                    <p className="text-xs text-slate-500 dark:text-slate-400 font-medium mt-1">Researchers</p>
                                </div>
                                <div ref={templates.ref} className="text-center">
                                    <p className="text-3xl font-black text-primary">{templates.count >= 1000 ? `${(templates.count / 1000).toFixed(templates.count >= 1000 ? 0 : 0)},000+` : `${templates.count}+`}</p>
                                    <p className="text-xs text-slate-500 dark:text-slate-400 font-medium mt-1">Journal Templates</p>
                                </div>
                                <div ref={universities.ref} className="text-center">
                                    <p className="text-3xl font-black text-primary">{universities.count}+</p>
                                    <p className="text-xs text-slate-500 dark:text-slate-400 font-medium mt-1">Universities</p>
                                </div>
                            </div>
                        </div>
                        <div className="bg-white dark:bg-slate-800 rounded-2xl p-8 border border-slate-200 dark:border-slate-700 shadow-lg">
                            <div className="flex flex-col gap-6">
                                <div className="flex items-start gap-4">
                                    <div className="size-10 rounded-lg bg-primary/10 text-primary flex items-center justify-center shrink-0">
                                        <span className="material-symbols-outlined">rocket_launch</span>
                                    </div>
                                    <div>
                                        <h4 className="font-bold text-slate-900 dark:text-white mb-1">Our Mission</h4>
                                        <p className="text-sm text-slate-600 dark:text-slate-400">Eliminate formatting as a barrier to academic publishing, so every researcher can present their best work regardless of their technical skills.</p>
                                    </div>
                                </div>
                                <div className="flex items-start gap-4">
                                    <div className="size-10 rounded-lg bg-green-100 dark:bg-green-900/30 text-green-600 flex items-center justify-center shrink-0">
                                        <span className="material-symbols-outlined">security</span>
                                    </div>
                                    <div>
                                        <h4 className="font-bold text-slate-900 dark:text-white mb-1">Privacy First</h4>
                                        <p className="text-sm text-slate-600 dark:text-slate-400">Your intellectual property is encrypted end-to-end. We never train on your manuscripts and you can delete your data anytime.</p>
                                    </div>
                                </div>
                                <div className="flex items-start gap-4">
                                    <div className="size-10 rounded-lg bg-amber-100 dark:bg-amber-900/30 text-amber-600 flex items-center justify-center shrink-0">
                                        <span className="material-symbols-outlined">groups</span>
                                    </div>
                                    <div>
                                        <h4 className="font-bold text-slate-900 dark:text-white mb-1">Open Community</h4>
                                        <p className="text-sm text-slate-600 dark:text-slate-400">Join our community of researchers sharing templates, best practices, and formatting tips for top journals worldwide.</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <Footer variant="landing" />
        </>
    );
}
