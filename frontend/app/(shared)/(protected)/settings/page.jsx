'use client';
import usePageTitle from '@/src/hooks/usePageTitle';
import { useEffect, useState } from 'react';
import { useTheme } from '@/src/context/ThemeContext';
import Footer from '@/src/components/Footer';

const SETTINGS_KEY = 'scholarform_settings';

const defaultSettings = {
    defaultTemplate: 'IEEE',
    defaultPageSize: 'Letter',
    defaultFastMode: false,
    defaultExportFormat: 'docx',
    emailNotifications: true,
    darkMode: false,
};

const loadSettings = () => {
    if (typeof window === 'undefined') return { ...defaultSettings };
    try {
        const raw = localStorage.getItem(SETTINGS_KEY);
        return raw ? { ...defaultSettings, ...JSON.parse(raw) } : { ...defaultSettings };
    } catch {
        return { ...defaultSettings };
    }
};

export default function SettingsPage() {
    usePageTitle('Settings');
    const { theme, setTheme } = useTheme();
    const [settings, setSettings] = useState(loadSettings);
    const [saved, setSaved] = useState(false);
    const [error, setError] = useState('');

    const update = (key, value) => {
        setSettings((prev) => ({ ...prev, [key]: value }));
        setSaved(false);
    };

    const handleSave = () => {
        try {
            localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
            setSaved(true);
            setError('');
            setTimeout(() => setSaved(false), 3000);
        } catch (err) {
            setError(err.message || 'Failed to save settings');
            setSaved(false);
            setTimeout(() => setError(''), 3000);
        }
    };

    const handleReset = () => {
        const resetState = { ...defaultSettings, darkMode: theme === 'dark' };
        setSettings(resetState);
        localStorage.removeItem(SETTINGS_KEY);
        setSaved(false);
    };

    useEffect(() => {
        setSettings((prev) => ({ ...prev, darkMode: theme === 'dark' }));
    }, [theme]);

    const Toggle = ({ checked, onChange }) => (
        <button
            role="switch"
            aria-checked={checked}
            onClick={() => onChange(!checked)}
            className={`relative inline-flex h-7 w-12 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 ${checked ? 'bg-primary' : 'bg-slate-200 dark:bg-slate-600'}`}
        >
            <span className={`pointer-events-none inline-block h-6 w-6 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${checked ? 'translate-x-5' : 'translate-x-0'}`} />
        </button>
    );

    return (
        <div className="min-h-screen bg-slate-50 dark:bg-slate-950 animate-in fade-in duration-500 flex flex-col">
            <main className="max-w-3xl mx-auto px-4 py-8">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-slate-900 dark:text-white flex items-center gap-3">
                        <span className="material-symbols-outlined text-primary text-4xl">settings</span>
                        Settings
                    </h1>
                    <p className="text-slate-600 dark:text-slate-400 mt-2">Configure your default preferences for document processing.</p>
                </div>

                {/* Upload Preferences */}
                <section className="bg-glass-surface backdrop-blur-xl border border-glass-border  shadow-xl shadow-primary/5 mb-6">
                    <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
                        <span className="material-symbols-outlined text-primary">upload_file</span>
                        Upload Preferences
                    </h2>
                    <div className="space-y-4">
                        {[
                            { label: 'Default Template', key: 'defaultTemplate', options: ['IEEE', 'Springer', 'APA', 'Nature', 'Vancouver', 'none'] },
                            { label: 'Default Page Size', key: 'defaultPageSize', options: ['Letter', 'A4', 'Legal'] },
                            { label: 'Default Export Format', key: 'defaultExportFormat', options: ['docx', 'pdf'] },
                        ].map(({ label, key, options }) => (
                            <div key={key}>
                                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">{label}</label>
                                <select value={settings[key]} onChange={(e) => update(key, e.target.value)}
                                    className="w-full p-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-primary outline-none transition-colors">
                                    {options.map(o => <option key={o} value={o}>{o === 'none' ? 'None (Auto-detect)' : o}</option>)}
                                </select>
                            </div>
                        ))}

                        <div className="flex items-center justify-between p-3 rounded-lg border border-glass-border bg-white/5 dark:bg-white/5">
                            <div className="flex flex-col">
                                <div className="flex items-center gap-2">
                                    <span className="material-symbols-outlined text-amber-500">bolt</span>
                                    <span className="text-sm font-bold text-slate-900 dark:text-white">Fast Mode Default</span>
                                </div>
                                <span className="text-[10px] text-slate-500 pl-8">Skip AI reasoning for faster processing</span>
                            </div>
                            <Toggle checked={settings.defaultFastMode} onChange={(v) => update('defaultFastMode', v)} />
                        </div>
                    </div>
                </section>

                {/* Account Settings */}
                <section className="bg-glass-surface backdrop-blur-xl border border-glass-border  shadow-xl shadow-primary/5 mb-6">
                    <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
                        <span className="material-symbols-outlined text-primary">person</span>
                        Account
                    </h2>
                    <div className="flex items-center justify-between p-3 rounded-lg border border-glass-border bg-white/5 dark:bg-white/5">
                        <div className="flex items-center gap-2">
                            <span className="material-symbols-outlined text-slate-500">email</span>
                            <span className="text-sm font-bold text-slate-900 dark:text-white">Email Notifications</span>
                        </div>
                        <Toggle checked={settings.emailNotifications} onChange={(v) => update('emailNotifications', v)} />
                    </div>
                    <div className="flex items-center justify-between p-3 rounded-lg border border-glass-border bg-white/5 dark:bg-white/5 mt-3">
                        <div className="flex items-center gap-2">
                            <span className="material-symbols-outlined text-slate-500">dark_mode</span>
                            <span className="text-sm font-bold text-slate-900 dark:text-white">Dark Mode</span>
                        </div>
                        <Toggle
                            checked={settings.darkMode}
                            onChange={(v) => {
                                update('darkMode', v);
                                setTheme(v ? 'dark' : 'light');
                            }}
                        />
                    </div>
                </section>

                {/* API Key (Future) */}
                <section className="bg-glass-surface backdrop-blur-xl border border-glass-border  shadow-xl shadow-primary/5 mb-6 opacity-60 pointer-events-none select-none">
                    <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-2 flex items-center gap-2">
                        <span className="material-symbols-outlined text-primary">key</span>
                        API Key Management
                        <span className="text-xs px-2 py-0.5 bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-400 rounded-full">Coming Soon</span>
                    </h2>
                    <p className="text-sm text-slate-500 dark:text-slate-400">Generate and manage API keys for programmatic access to ScholarForm AI.</p>
                </section>

                {/* Feedback Banners */}
                {saved && (
                    <div className="mb-6 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4 flex items-center text-green-700 dark:text-green-400 animate-in fade-in slide-in-from-bottom-2 duration-300">
                        <span className="material-symbols-outlined mr-2">check_circle</span>
                        <span className="font-medium text-sm">Settings saved ✓</span>
                    </div>
                )}
                {error && (
                    <div className="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 flex items-center text-red-700 dark:text-red-400 animate-in fade-in slide-in-from-bottom-2 duration-300">
                        <span className="material-symbols-outlined mr-2">error</span>
                        <span className="font-medium text-sm">{error}</span>
                    </div>
                )}

                <div className="flex items-center justify-between">
                    <button onClick={handleReset}
                        className="px-4 py-2 text-sm text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors active:scale-95">
                        Reset to Defaults
                    </button>
                    <button onClick={handleSave}
                        className="px-6 py-3 bg-primary hover:bg-primary-hover text-white font-bold rounded-xl shadow-lg shadow-primary/25 transition-all flex items-center gap-2 active:scale-95">
                        <span className="material-symbols-outlined">save</span>
                        Save Settings
                    </button>
                </div>
            </main>
            <Footer />
        </div>
    );
}
