import usePageTitle from '../hooks/usePageTitle';
import { useState } from 'react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

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
    try {
        const raw = localStorage.getItem(SETTINGS_KEY);
        return raw ? { ...defaultSettings, ...JSON.parse(raw) } : { ...defaultSettings };
    } catch {
        return { ...defaultSettings };
    }
};

export default function SettingsPage() {
    usePageTitle('Settings');
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
        setSettings({ ...defaultSettings });
        localStorage.removeItem(SETTINGS_KEY);
        setSaved(false);
    };

    return (
        <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
            <Navbar />
            <main className="max-w-3xl mx-auto px-4 py-8">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-slate-900 dark:text-white flex items-center gap-3">
                        <span className="material-symbols-outlined text-primary text-4xl">settings</span>
                        Settings
                    </h1>
                    <p className="text-slate-600 dark:text-slate-400 mt-2">
                        Configure your default preferences for document processing.
                    </p>
                </div>

                {/* Upload Preferences */}
                <section className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm mb-6">
                    <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
                        <span className="material-symbols-outlined text-primary">upload_file</span>
                        Upload Preferences
                    </h2>
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                                Default Template
                            </label>
                            <select
                                value={settings.defaultTemplate}
                                onChange={(e) => update('defaultTemplate', e.target.value)}
                                className="w-full p-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-primary outline-none"
                            >
                                <option value="IEEE">IEEE</option>
                                <option value="Springer">Springer</option>
                                <option value="APA">APA</option>
                                <option value="Nature">Nature</option>
                                <option value="Vancouver">Vancouver</option>
                                <option value="none">None (Auto-detect)</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                                Default Page Size
                            </label>
                            <select
                                value={settings.defaultPageSize}
                                onChange={(e) => update('defaultPageSize', e.target.value)}
                                className="w-full p-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-primary outline-none"
                            >
                                <option value="Letter">Letter (US Default)</option>
                                <option value="A4">A4 (International)</option>
                                <option value="Legal">Legal</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                                Default Export Format
                            </label>
                            <select
                                value={settings.defaultExportFormat}
                                onChange={(e) => update('defaultExportFormat', e.target.value)}
                                className="w-full p-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-primary outline-none"
                            >
                                <option value="docx">DOCX</option>
                                <option value="pdf">PDF</option>
                            </select>
                        </div>

                        <div className="flex items-center justify-between p-3 rounded-lg border border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50">
                            <div className="flex flex-col">
                                <div className="flex items-center gap-2">
                                    <span className="material-symbols-outlined text-amber-500">bolt</span>
                                    <span className="text-sm font-bold text-slate-900 dark:text-white">Fast Mode Default</span>
                                </div>
                                <span className="text-[10px] text-slate-500 pl-8">Skip AI reasoning for faster processing</span>
                            </div>
                            <div className="relative inline-block w-10 align-middle select-none">
                                <input
                                    checked={settings.defaultFastMode}
                                    onChange={(e) => update('defaultFastMode', e.target.checked)}
                                    className="toggle-checkbox absolute block w-5 h-5 rounded-full bg-white border-4 appearance-none cursor-pointer transition-all duration-300"
                                    id="default_fast_mode"
                                    type="checkbox"
                                    style={{ top: 0, right: settings.defaultFastMode ? '0px' : '20px' }}
                                />
                                <label
                                    className={`toggle-label block overflow-hidden h-5 rounded-full cursor-pointer transition-colors duration-300 ${settings.defaultFastMode ? 'bg-amber-500' : 'bg-slate-300'}`}
                                    htmlFor="default_fast_mode"
                                />
                            </div>
                        </div>
                    </div>
                </section>

                {/* Account Settings */}
                <section className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm mb-6">
                    <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
                        <span className="material-symbols-outlined text-primary">person</span>
                        Account
                    </h2>
                    <div className="space-y-4">
                        <div className="flex items-center justify-between p-3 rounded-lg border border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50">
                            <div className="flex items-center gap-2">
                                <span className="material-symbols-outlined text-slate-500">email</span>
                                <span className="text-sm font-bold text-slate-900 dark:text-white">Email Notifications</span>
                            </div>
                            <div className="relative inline-block w-10 align-middle select-none">
                                <input
                                    checked={settings.emailNotifications}
                                    onChange={(e) => update('emailNotifications', e.target.checked)}
                                    className="toggle-checkbox absolute block w-5 h-5 rounded-full bg-white border-4 appearance-none cursor-pointer transition-all duration-300"
                                    id="email_notifications"
                                    type="checkbox"
                                    style={{ top: 0, right: settings.emailNotifications ? '0px' : '20px' }}
                                />
                                <label
                                    className={`toggle-label block overflow-hidden h-5 rounded-full cursor-pointer transition-colors duration-300 ${settings.emailNotifications ? 'bg-primary' : 'bg-slate-300'}`}
                                    htmlFor="email_notifications"
                                />
                            </div>
                        </div>
                    </div>
                </section>

                {/* API Key (Future) */}
                <section className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm mb-6 opacity-60">
                    <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-2 flex items-center gap-2">
                        <span className="material-symbols-outlined text-primary">key</span>
                        API Key Management
                        <span className="text-xs px-2 py-0.5 bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-400 rounded-full">Coming Soon</span>
                    </h2>
                    <p className="text-sm text-slate-500 dark:text-slate-400">
                        Generate and manage API keys for programmatic access to ScholarForm AI.
                    </p>
                </section>

                {/* Toast Banners */}
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

                {/* Action Buttons */}
                <div className="flex items-center justify-between">
                    <button
                        onClick={handleReset}
                        className="px-4 py-2 text-sm text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
                    >
                        Reset to Defaults
                    </button>
                    <div className="flex items-center gap-3">
                        <button
                            onClick={handleSave}
                            className="px-6 py-3 bg-primary hover:bg-blue-700 text-white font-bold rounded-xl shadow-lg shadow-primary/25 transition-all flex items-center gap-2"
                        >
                            <span className="material-symbols-outlined">save</span>
                            Save Settings
                        </button>
                    </div>
                </div>
            </main>
            <Footer />
        </div>
    );
}
