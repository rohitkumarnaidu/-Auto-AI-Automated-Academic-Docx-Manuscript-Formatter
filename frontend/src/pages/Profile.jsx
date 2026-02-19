import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { supabase } from '../lib/supabaseClient';

export default function Profile() {
    const { theme, toggleTheme } = useTheme();
    const [statusUpdates, setStatusUpdates] = useState(true);
    const [newsletter, setNewsletter] = useState(false);
    const [uploading, setUploading] = useState(false);
    const fileInputRef = useRef(null);
    const { user, signOut, refreshSession } = useAuth();
    const navigate = useNavigate();

    const handleAvatarClick = () => {
        fileInputRef.current?.click();
    };

    const handleAvatarChange = async (event) => {
        try {
            setUploading(true);

            if (!event.target.files || event.target.files.length === 0) {
                return;
            }

            const file = event.target.files[0];
            const fileExt = file.name.split('.').pop();
            const fileName = `${user.id}/${Math.random()}.${fileExt}`;
            const filePath = `${fileName}`;

            // 1. Upload to Supabase Storage
            const { error: uploadError } = await supabase.storage
                .from('avatars')
                .upload(filePath, file);

            if (uploadError) {
                throw uploadError;
            }

            // 2. Get Public URL
            const { data: { publicUrl } } = supabase.storage
                .from('avatars')
                .getPublicUrl(filePath);

            // 3. Update User Metadata
            const { error: updateError } = await supabase.auth.updateUser({
                data: { avatar_url: publicUrl }
            });

            if (updateError) {
                throw updateError;
            }

            // 4. Refresh Session to update UI
            await refreshSession();

        } catch (error) {
            console.error('Error uploading avatar:', error);
            alert('Error uploading avatar: ' + error.message);
        } finally {
            setUploading(false);
        }
    };

    // Derived User State or Defaults
    const fullName = user?.user_metadata?.full_name || 'Scholar User';
    const email = user?.email || 'user@example.com';
    const avatarUrl = user?.user_metadata?.avatar_url || user?.user_metadata?.picture ||
        'https://lh3.googleusercontent.com/aida-public/AB6AXuCBAnQke1dGWniClQX7rHZBtni1hbRlIpllATyD41NPPw3Br765F9F0vIWQH7I2SezfqlRBNZW0hgkDJ4Kl-Ekd0MVD60AqnPJe_Q0QkDvG2fqpVzmz_HTsQKFKkBIvfvFH26zii0uK7s11gs1bnXmlnWvG6LS6GTXhY6thfBqwRUWqvuAIMWQfqwnAs0DFEX2j3QBP0F7mG913xvhu2iMMo_MIgxF_nqEmviIbI0G3jFBvWtp3KPkAPAxfc4YVXlrDPh_tJJ5ZgnHP';
    const role = user?.user_metadata?.institution || 'Academic Researcher';

    return (
        <div className="bg-background-light dark:bg-background-dark font-display text-slate-900 dark:text-slate-100 min-h-screen flex flex-col transition-colors duration-300">
            <Navbar activeTab="" />

            <main className="max-w-[960px] mx-auto px-4 py-10 flex flex-col gap-8 w-full">
                {/* Page Heading */}
                <div className="flex flex-col gap-2">
                    <h1 className="text-slate-900 dark:text-white text-4xl font-black leading-tight tracking-tight">Account Settings</h1>
                    <p className="text-slate-500 dark:text-slate-400 text-lg font-normal">Manage your academic profile, subscription details, and personal preferences.</p>
                </div>

                {/* Profile Information Card */}
                <section className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
                    <div className="p-6 md:p-8">
                        <div className="flex flex-col md:flex-row gap-8 items-center md:items-start">
                            <div className="relative group shrink-0">
                                <div
                                    className="bg-center bg-no-repeat aspect-square bg-cover rounded-full h-32 w-32 shadow-inner border-4 border-white dark:border-slate-800 transition-opacity"
                                    style={{ backgroundImage: `url("${avatarUrl}")`, opacity: uploading ? 0.5 : 1 }}
                                >
                                </div>
                                {uploading && (
                                    <div className="absolute inset-0 flex items-center justify-center">
                                        <span className="material-symbols-outlined animate-spin text-white drop-shadow-md">refresh</span>
                                    </div>
                                )}
                                <button
                                    onClick={handleAvatarClick}
                                    disabled={uploading}
                                    className="absolute bottom-0 right-0 bg-primary text-white p-2 rounded-full shadow-lg hover:bg-blue-600 transition-all flex items-center justify-center disabled:opacity-50"
                                >
                                    <span className="material-symbols-outlined text-[18px]">edit</span>
                                </button>
                                <input
                                    type="file"
                                    ref={fileInputRef}
                                    onChange={handleAvatarChange}
                                    accept="image/*"
                                    className="hidden"
                                />
                            </div>
                            <div className="flex-1 flex flex-col gap-4 text-center md:text-left">
                                <div className="flex flex-col gap-1">
                                    <div className="flex flex-wrap items-center justify-center md:justify-start gap-3">
                                        <h3 className="text-slate-900 dark:text-white text-2xl font-bold">{fullName}</h3>
                                        <div className="flex h-7 items-center justify-center gap-x-1.5 rounded-full bg-primary/10 px-3 border border-primary/20">
                                            <span className="material-symbols-outlined text-primary text-[16px] font-bold">star</span>
                                            <p className="text-primary text-xs font-bold uppercase tracking-wider">Free Plan</p>
                                        </div>
                                    </div>
                                    <p className="text-slate-600 dark:text-slate-400 font-medium text-lg">{role}</p>
                                    <p className="text-slate-500 dark:text-slate-500 text-sm">{email}</p>
                                </div>
                                <div className="flex flex-wrap gap-3 justify-center md:justify-start mt-2">
                                    <button className="px-5 py-2.5 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-100 rounded-lg text-sm font-bold hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors">Edit Profile</button>
                                    <button className="px-5 py-2.5 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-100 rounded-lg text-sm font-bold hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors">Verify Institution</button>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="bg-slate-50 dark:bg-slate-800/30 border-t border-slate-200 dark:border-slate-800 px-8 py-4 flex flex-col sm:flex-row justify-between items-center gap-4">
                        <p className="text-sm text-slate-500 dark:text-slate-400">Member since <span className="font-bold text-slate-900 dark:text-slate-200">{new Date(user?.created_at || Date.now()).toLocaleDateString()}</span></p>
                        <a className="text-primary text-sm font-bold hover:underline" href="#">Upgrade Plan</a>
                    </div>
                </section>

                {/* Account Actions */}
                <section className="flex flex-col gap-4">
                    <h2 className="text-slate-900 dark:text-white text-xl font-bold px-1 tracking-tight">Account Actions</h2>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <button className="flex items-center justify-between p-5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl hover:border-primary/50 hover:shadow-md transition-all group text-left">
                            <div className="flex items-center gap-4">
                                <div className="p-2.5 bg-slate-100 dark:bg-slate-800 rounded-xl text-slate-600 dark:text-slate-300 group-hover:bg-primary group-hover:text-white transition-colors">
                                    <span className="material-symbols-outlined">lock</span>
                                </div>
                                <span className="font-bold text-slate-700 dark:text-slate-200">Change Password</span>
                            </div>
                            <span className="material-symbols-outlined text-slate-400 group-hover:text-primary transition-colors">chevron_right</span>
                        </button>
                        <button className="flex items-center justify-between p-5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl hover:border-primary/50 hover:shadow-md transition-all group text-left">
                            <div className="flex items-center gap-4">
                                <div className="p-2.5 bg-primary/10 rounded-xl text-primary group-hover:bg-primary group-hover:text-white transition-colors">
                                    <span className="material-symbols-outlined">payments</span>
                                </div>
                                <span className="font-bold text-slate-700 dark:text-slate-200">Manage Subscription</span>
                            </div>
                            <span className="material-symbols-outlined text-slate-400 group-hover:text-primary transition-colors">chevron_right</span>
                        </button>
                        <button
                            onClick={async () => {
                                await signOut();
                                navigate('/');
                            }}
                            className="flex items-center justify-between p-5 bg-white dark:bg-slate-900 border border-red-100 dark:border-red-900/20 rounded-xl hover:bg-red-50 dark:hover:bg-red-900/10 transition-all group text-left"
                        >
                            <div className="flex items-center gap-4">
                                <div className="p-2.5 bg-red-100 dark:bg-red-900/20 rounded-xl text-red-600 group-hover:bg-red-600 group-hover:text-white transition-colors">
                                    <span className="material-symbols-outlined">logout</span>
                                </div>
                                <span className="font-bold text-red-600">Sign out</span>
                            </div>
                        </button>
                    </div>
                </section>

                {/* Preferences */}
                <section className="flex flex-col gap-4">
                    <h2 className="text-slate-900 dark:text-white text-xl font-bold px-1 tracking-tight">Preferences</h2>
                    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl divide-y divide-slate-100 dark:divide-slate-800 shadow-sm">
                        {/* Toggle: Dark Mode */}
                        <div className="flex items-center justify-between p-6">
                            <div className="flex flex-col gap-1">
                                <p className="font-bold text-slate-800 dark:text-white">Dark Mode</p>
                                <p className="text-sm text-slate-500 dark:text-slate-400">Toggle between light and dark themes</p>
                            </div>
                            <button
                                onClick={toggleTheme}
                                className={`relative inline-flex h-7 w-12 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${theme === 'dark' ? 'bg-primary' : 'bg-slate-200 dark:bg-slate-700'}`}
                            >
                                <span className={`pointer-events-none inline-block h-6 w-6 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${theme === 'dark' ? 'translate-x-5' : 'translate-x-0'}`}></span>
                            </button>
                        </div>
                        {/* Toggle: Email Notifications */}
                        <div className="flex items-center justify-between p-6">
                            <div className="flex flex-col gap-1">
                                <p className="font-bold text-slate-800 dark:text-white">Manuscript Status Updates</p>
                                <p className="text-sm text-slate-500 dark:text-slate-400">Receive emails when your formatting process completes</p>
                            </div>
                            <button
                                onClick={() => setStatusUpdates(!statusUpdates)}
                                className={`relative inline-flex h-7 w-12 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${statusUpdates ? 'bg-primary' : 'bg-slate-200 dark:bg-slate-700'}`}
                            >
                                <span className={`pointer-events-none inline-block h-6 w-6 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${statusUpdates ? 'translate-x-5' : 'translate-x-0'}`}></span>
                            </button>
                        </div>
                        {/* Toggle: Newsletter */}
                        <div className="flex items-center justify-between p-6">
                            <div className="flex flex-col gap-1">
                                <p className="font-bold text-slate-800 dark:text-white">Product Updates & Newsletter</p>
                                <p className="text-sm text-slate-500 dark:text-slate-400">Get notified about new academic templates and formatting features</p>
                            </div>
                            <button
                                onClick={() => setNewsletter(!newsletter)}
                                className={`relative inline-flex h-7 w-12 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${newsletter ? 'bg-primary' : 'bg-slate-200 dark:bg-slate-700'}`}
                            >
                                <span className={`pointer-events-none inline-block h-6 w-6 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${newsletter ? 'translate-x-5' : 'translate-x-0'}`}></span>
                            </button>
                        </div>
                    </div>
                </section>

                {/* Footer Note */}
                <footer className="mt-4 text-center pb-8">
                    <p className="text-sm text-slate-400 font-medium tracking-wide italic">User ID: <span className="font-mono not-italic font-bold">{user?.id?.slice(0, 8) || 'Unknown'}</span> • Join Date: {new Date(user?.created_at || Date.now()).toLocaleDateString()}</p>
                </footer>
            </main>

            <Footer variant="app" />
        </div>
    );
}
