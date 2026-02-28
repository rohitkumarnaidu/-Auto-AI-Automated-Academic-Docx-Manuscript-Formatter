import usePageTitle from '../hooks/usePageTitle';
import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { supabase } from '../lib/supabaseClient';

export default function Profile() {
    usePageTitle('Profile');
    const { theme, toggleTheme } = useTheme();
    const [statusUpdates, setStatusUpdates] = useState(true);
    const [newsletter, setNewsletter] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [isEditing, setIsEditing] = useState(false);
    const [editName, setEditName] = useState('');
    const [editInstitution, setEditInstitution] = useState('');
    const [editSaving, setEditSaving] = useState(false);
    const [editSuccess, setEditSuccess] = useState('');
    const [editError, setEditError] = useState('');
    const [showPasswordForm, setShowPasswordForm] = useState(false);
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [passwordSaving, setPasswordSaving] = useState(false);
    const [passwordMessage, setPasswordMessage] = useState('');
    const [verifyStatus, setVerifyStatus] = useState('');
    const [cropImage, setCropImage] = useState(null);
    const canvasRef = useRef(null);
    const fileInputRef = useRef(null);
    const { user, signOut, refreshSession } = useAuth();
    const navigate = useNavigate();

    const handleAvatarClick = () => {
        if (fileInputRef.current) fileInputRef.current.value = '';
        fileInputRef.current?.click();
    };

    const handleAvatarChange = (event) => {
        if (!event.target.files || event.target.files.length === 0) return;
        const file = event.target.files[0];
        const reader = new FileReader();
        reader.onload = (e) => setCropImage({ src: e.target.result, fileExt: file.name.split('.').pop() });
        reader.readAsDataURL(file);
    };

    useEffect(() => {
        if (cropImage && canvasRef.current) {
            const img = new Image();
            img.onload = () => {
                const canvas = canvasRef.current;
                const ctx = canvas.getContext('2d');
                const size = Math.min(img.width, img.height);
                const startX = (img.width - size) / 2;
                const startY = (img.height - size) / 2;
                canvas.width = 300;
                canvas.height = 300;
                ctx.clearRect(0, 0, 300, 300);
                ctx.drawImage(img, startX, startY, size, size, 0, 0, 300, 300);
            };
            img.src = cropImage.src;
        }
    }, [cropImage]);

    const handleCropUpload = () => {
        if (!canvasRef.current || !cropImage) return;
        canvasRef.current.toBlob(async (blob) => {
            try {
                setUploading(true);
                setCropImage(null);

                const fileName = `${user.id}/${Math.random()}.${cropImage.fileExt}`;
                const { error: uploadError } = await supabase.storage
                    .from('avatars')
                    .upload(fileName, blob, { contentType: `image/${cropImage.fileExt}` });

                if (uploadError) throw uploadError;

                const { data: { publicUrl } } = supabase.storage
                    .from('avatars')
                    .getPublicUrl(fileName);

                const { error: updateError } = await supabase.auth.updateUser({
                    data: { avatar_url: publicUrl }
                });

                if (updateError) throw updateError;
                await refreshSession();
            } catch (error) {
                console.error('Error uploading avatar:', error);
                alert('Error uploading avatar: ' + error.message);
            } finally {
                setUploading(false);
            }
        });
    };

    const fullName = user?.user_metadata?.full_name || 'Scholar User';
    const email = user?.email || 'user@example.com';
    const avatarUrl = user?.user_metadata?.avatar_url || user?.user_metadata?.picture ||
        'https://lh3.googleusercontent.com/aida-public/AB6AXuCBAnQke1dGWniClQX7rHZBtni1hbRlIpllATyD41NPPw3Br765F9F0vIWQH7I2SezfqlRBNZW0hgkDJ4Kl-Ekd0MVD60AqnPJe_Q0QkDvG2fqpVzmz_HTsQKFKkBIvfvFH26zii0uK7s11gs1bnXmlnWvG6LS6GTXhY6thfBqwRUWqvuAIMWQfqwnAs0DFEX2j3QBP0F7mG913xvhu2iMMo_MIgxF_nqEmviIbI0G3jFBvWtp3KPkAPAxfc4YVXlrDPh_tJJ5ZgnHP';
    const role = user?.user_metadata?.institution || 'Academic Researcher';

    const handleEditProfile = () => {
        setEditName(fullName);
        setEditInstitution(user?.user_metadata?.institution || '');
        setEditSuccess('');
        setEditError('');
        setIsEditing(true);
    };

    const handleSaveProfile = async () => {
        setEditSaving(true);
        setEditError('');
        setEditSuccess('');
        try {
            const { error } = await supabase.auth.updateUser({
                data: {
                    full_name: editName,
                    institution: editInstitution,
                }
            });
            if (error) throw error;
            await refreshSession();
            setEditSuccess('Profile updated successfully!');
            setTimeout(() => {
                setIsEditing(false);
                setEditSuccess('');
            }, 1500);
        } catch (err) {
            setEditError(err.message || 'Failed to update profile');
        } finally {
            setEditSaving(false);
        }
    };

    const handleVerifyInstitution = async () => {
        setVerifyStatus('sending');
        try {
            // Send a verification email for the institution
            const { error } = await supabase.auth.updateUser({
                data: { institution_verified: false, institution_verify_requested: true }
            });
            if (error) throw error;
            setVerifyStatus('sent');
            setTimeout(() => setVerifyStatus(''), 3000);
        } catch (err) {
            console.error('Verify institution error:', err);
            setVerifyStatus('error');
            setTimeout(() => setVerifyStatus(''), 3000);
        }
    };

    const handleChangePassword = async () => {
        if (newPassword.length < 8) {
            setPasswordMessage('Password must be at least 8 characters');
            return;
        }
        if (newPassword !== confirmPassword) {
            setPasswordMessage('Passwords do not match');
            return;
        }
        setPasswordSaving(true);
        setPasswordMessage('');
        try {
            const { error } = await supabase.auth.updateUser({ password: newPassword });
            if (error) throw error;
            setPasswordMessage('Password updated successfully!');
            setNewPassword('');
            setConfirmPassword('');
            setTimeout(() => {
                setShowPasswordForm(false);
                setPasswordMessage('');
            }, 2000);
        } catch (err) {
            setPasswordMessage(err.message || 'Failed to update password');
        } finally {
            setPasswordSaving(false);
        }
    };

    return (
        <div className="bg-background-light dark:bg-background-dark font-display text-slate-900 dark:text-slate-100 min-h-screen flex flex-col transition-colors duration-300">
            <Navbar activeTab="" />

            <main className="max-w-[960px] mx-auto px-4 sm:px-6 py-8 sm:py-10 flex flex-col gap-8 w-full">
                <div className="flex flex-col gap-2">
                    <h1 className="text-slate-900 dark:text-white text-3xl sm:text-4xl font-black leading-tight tracking-tight">Account Settings</h1>
                    <p className="text-slate-500 dark:text-slate-400 text-base sm:text-lg font-normal">Manage your academic profile, subscription details, and personal preferences.</p>
                </div>

                <section className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
                    <div className="p-6 md:p-8">
                        <div className="flex flex-col md:flex-row gap-8 items-center md:items-start">
                            <div className="relative group shrink-0">
                                <div
                                    className="bg-center bg-no-repeat aspect-square bg-cover rounded-full h-32 w-32 shadow-inner border-4 border-white dark:border-slate-800 transition-opacity"
                                    style={{ backgroundImage: `url("${avatarUrl}")`, opacity: uploading ? 0.5 : 1 }}
                                />
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
                                {isEditing ? (
                                    <div className="flex flex-col gap-3">
                                        <div>
                                            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Full Name</label>
                                            <input
                                                type="text"
                                                value={editName}
                                                onChange={(e) => setEditName(e.target.value)}
                                                className="w-full mt-1 px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:border-primary focus:ring-1 focus:ring-primary"
                                            />
                                        </div>
                                        <div>
                                            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Institution</label>
                                            <input
                                                type="text"
                                                value={editInstitution}
                                                onChange={(e) => setEditInstitution(e.target.value)}
                                                className="w-full mt-1 px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:border-primary focus:ring-1 focus:ring-primary"
                                            />
                                        </div>
                                        {editError && <p className="text-sm text-red-500">{editError}</p>}
                                        {editSuccess && <p className="text-sm text-green-500">{editSuccess}</p>}
                                        <div className="flex gap-3">
                                            <button
                                                onClick={handleSaveProfile}
                                                disabled={editSaving}
                                                className="px-5 py-2.5 bg-primary text-white rounded-lg text-sm font-bold hover:bg-blue-600 transition-colors disabled:opacity-50"
                                            >
                                                {editSaving ? 'Saving...' : 'Save Changes'}
                                            </button>
                                            <button
                                                onClick={() => setIsEditing(false)}
                                                className="px-5 py-2.5 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-100 rounded-lg text-sm font-bold hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
                                            >
                                                Cancel
                                            </button>
                                        </div>
                                    </div>
                                ) : (
                                    <>
                                        <div className="flex flex-col gap-1">
                                            <div className="flex flex-wrap items-center justify-center md:justify-start gap-3">
                                                <h3 className="text-slate-900 dark:text-white text-2xl font-bold">{fullName}</h3>
                                                <div className="flex h-7 items-center justify-center gap-x-1.5 rounded-full bg-primary/10 px-3 border border-primary/20">
                                                    <span className="material-symbols-outlined text-primary text-[16px] font-bold">star</span>
                                                    <p className="text-primary text-xs font-bold uppercase tracking-wider">Free Plan</p>
                                                </div>
                                            </div>
                                            <p className="text-slate-600 dark:text-slate-400 font-medium text-lg">{role}</p>
                                            <p className="text-slate-500 dark:text-slate-500 text-sm break-all">{email}</p>
                                        </div>
                                        <div className="flex flex-wrap gap-3 justify-center md:justify-start mt-2">
                                            <button
                                                onClick={handleEditProfile}
                                                className="px-5 py-2.5 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-100 rounded-lg text-sm font-bold hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
                                            >
                                                Edit Profile
                                            </button>
                                            <button
                                                onClick={handleVerifyInstitution}
                                                disabled={verifyStatus === 'sending'}
                                                className="px-5 py-2.5 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-100 rounded-lg text-sm font-bold hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors disabled:opacity-50"
                                            >
                                                {verifyStatus === 'sending' ? 'Sending...' : verifyStatus === 'sent' ? '✓ Verification Requested' : verifyStatus === 'error' ? 'Failed — Retry' : 'Verify Institution'}
                                            </button>
                                        </div>
                                    </>
                                )}
                            </div>
                        </div>
                    </div>
                    <div className="bg-slate-50 dark:bg-slate-800/30 border-t border-slate-200 dark:border-slate-800 px-4 sm:px-8 py-4 flex flex-col sm:flex-row justify-between items-center gap-4">
                        <p className="text-sm text-slate-500 dark:text-slate-400">Member since <span className="font-bold text-slate-900 dark:text-slate-200">{new Date(user?.created_at || Date.now()).toLocaleDateString()}</span></p>
                        <button onClick={() => navigate('/settings')} className="text-primary text-sm font-bold hover:underline">Upgrade Plan</button>
                    </div>
                </section>

                <section className="flex flex-col gap-4">
                    <h2 className="text-slate-900 dark:text-white text-xl font-bold px-1 tracking-tight">Account Actions</h2>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <button
                            onClick={() => setShowPasswordForm(!showPasswordForm)}
                            className="flex items-center justify-between p-5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl hover:border-primary/50 hover:shadow-md transition-all group text-left"
                        >
                            <div className="flex items-center gap-4">
                                <div className="p-2.5 bg-slate-100 dark:bg-slate-800 rounded-xl text-slate-600 dark:text-slate-300 group-hover:bg-primary group-hover:text-white transition-colors">
                                    <span className="material-symbols-outlined">lock</span>
                                </div>
                                <span className="font-bold text-slate-700 dark:text-slate-200">Change Password</span>
                            </div>
                            <span className="material-symbols-outlined text-slate-400 group-hover:text-primary transition-colors">chevron_right</span>
                        </button>
                        <button
                            onClick={() => navigate('/settings')}
                            className="flex items-center justify-between p-5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl hover:border-primary/50 hover:shadow-md transition-all group text-left"
                        >
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

                    {/* Inline Change Password Form */}
                    {showPasswordForm && (
                        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm animate-in fade-in slide-in-from-top-2 duration-300">
                            <h3 className="text-slate-900 dark:text-white font-bold text-lg mb-4">Change Password</h3>
                            <div className="flex flex-col gap-3 max-w-md">
                                <input
                                    type="password"
                                    placeholder="New Password (min 8 chars)"
                                    value={newPassword}
                                    onChange={(e) => setNewPassword(e.target.value)}
                                    className="w-full px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:border-primary focus:ring-1 focus:ring-primary"
                                />
                                <input
                                    type="password"
                                    placeholder="Confirm New Password"
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                    className="w-full px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:border-primary focus:ring-1 focus:ring-primary"
                                />
                                {passwordMessage && (
                                    <p className={`text-sm ${passwordMessage.includes('success') ? 'text-green-500' : 'text-red-500'}`}>
                                        {passwordMessage}
                                    </p>
                                )}
                                <div className="flex gap-3">
                                    <button
                                        onClick={handleChangePassword}
                                        disabled={passwordSaving}
                                        className="px-5 py-2.5 bg-primary text-white rounded-lg text-sm font-bold hover:bg-blue-600 transition-colors disabled:opacity-50"
                                    >
                                        {passwordSaving ? 'Updating...' : 'Update Password'}
                                    </button>
                                    <button
                                        onClick={() => { setShowPasswordForm(false); setPasswordMessage(''); setNewPassword(''); setConfirmPassword(''); }}
                                        className="px-5 py-2.5 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-100 rounded-lg text-sm font-bold hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
                                    >
                                        Cancel
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}
                </section>

                <section className="flex flex-col gap-4">
                    <h2 className="text-slate-900 dark:text-white text-xl font-bold px-1 tracking-tight">Preferences</h2>
                    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl divide-y divide-slate-100 dark:divide-slate-800 shadow-sm">
                        <div className="flex items-center justify-between p-6">
                            <div className="flex flex-col gap-1">
                                <p className="font-bold text-slate-800 dark:text-white">Dark Mode</p>
                                <p className="text-sm text-slate-500 dark:text-slate-400">Toggle between light and dark themes</p>
                            </div>
                            <button
                                onClick={toggleTheme}
                                className={`relative inline-flex h-7 w-12 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${theme === 'dark' ? 'bg-primary' : 'bg-slate-200 dark:bg-slate-700'}`}
                            >
                                <span className={`pointer-events-none inline-block h-6 w-6 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${theme === 'dark' ? 'translate-x-5' : 'translate-x-0'}`} />
                            </button>
                        </div>
                        <div className="flex items-center justify-between p-6">
                            <div className="flex flex-col gap-1">
                                <p className="font-bold text-slate-800 dark:text-white">Manuscript Status Updates</p>
                                <p className="text-sm text-slate-500 dark:text-slate-400">Receive emails when your formatting process completes</p>
                            </div>
                            <button
                                onClick={() => setStatusUpdates(!statusUpdates)}
                                className={`relative inline-flex h-7 w-12 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${statusUpdates ? 'bg-primary' : 'bg-slate-200 dark:bg-slate-700'}`}
                            >
                                <span className={`pointer-events-none inline-block h-6 w-6 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${statusUpdates ? 'translate-x-5' : 'translate-x-0'}`} />
                            </button>
                        </div>
                        <div className="flex items-center justify-between p-6">
                            <div className="flex flex-col gap-1">
                                <p className="font-bold text-slate-800 dark:text-white">Product Updates & Newsletter</p>
                                <p className="text-sm text-slate-500 dark:text-slate-400">Get notified about new academic templates and formatting features</p>
                            </div>
                            <button
                                onClick={() => setNewsletter(!newsletter)}
                                className={`relative inline-flex h-7 w-12 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${newsletter ? 'bg-primary' : 'bg-slate-200 dark:bg-slate-700'}`}
                            >
                                <span className={`pointer-events-none inline-block h-6 w-6 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${newsletter ? 'translate-x-5' : 'translate-x-0'}`} />
                            </button>
                        </div>
                    </div>
                </section>

                <footer className="mt-4 text-center pb-8">
                    <p className="text-xs sm:text-sm text-slate-400 font-medium tracking-wide italic break-words">User ID: <span className="font-mono not-italic font-bold">{user?.id?.slice(0, 8) || 'Unknown'}</span> | Join Date: {new Date(user?.created_at || Date.now()).toLocaleDateString()}</p>
                </footer>
            </main>

            {cropImage && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4">
                    <div className="bg-white dark:bg-slate-900 rounded-xl shadow-xl w-full max-w-sm overflow-hidden border border-slate-200 dark:border-slate-800 animate-in zoom-in-95 duration-200">
                        <div className="p-4 border-b border-slate-100 dark:border-slate-800 flex justify-between items-center bg-slate-50 dark:bg-slate-800/50">
                            <h3 className="font-bold text-slate-800 dark:text-slate-100">Adjust Avatar</h3>
                            <button onClick={() => setCropImage(null)} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
                                <span className="material-symbols-outlined text-xl">close</span>
                            </button>
                        </div>
                        <div className="p-6 flex flex-col items-center gap-4">
                            <p className="text-sm text-center text-slate-500 dark:text-slate-400">1:1 square crop from center</p>
                            <div className="rounded-full overflow-hidden border-4 border-slate-100 dark:border-slate-800 shadow-inner w-[200px] h-[200px] flex items-center justify-center bg-slate-50 dark:bg-slate-950">
                                <canvas ref={canvasRef} className="w-full h-full object-cover" />
                            </div>
                            <button
                                onClick={handleCropUpload}
                                className="w-full mt-4 py-2.5 bg-primary text-white rounded-lg font-bold hover:bg-blue-600 transition-colors"
                            >
                                Upload Avatar
                            </button>
                        </div>
                    </div>
                </div>
            )}

            <Footer variant="app" />
        </div>
    );
}
