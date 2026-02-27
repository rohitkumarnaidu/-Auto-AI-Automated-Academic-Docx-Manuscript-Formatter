import { lazy, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import { DocumentProvider } from './context/DocumentContext';
import { AuthProvider } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import { ToastProvider } from './context/ToastContext';
import ProtectedRoute from './components/ProtectedRoute';
import ErrorBoundary from './components/ErrorBoundary';
import ScrollManager from './components/ScrollManager';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

/* ── Route-based code splitting: each page loads on demand ── */
const Landing = lazy(() => import('./pages/Landing'));
const Upload = lazy(() => import('./pages/Upload'));
const Processing = lazy(() => import('./pages/Processing'));
const ValidationResults = lazy(() => import('./pages/ValidationResults'));
const Download = lazy(() => import('./pages/Download'));
const Error = lazy(() => import('./pages/Error'));
const Compare = lazy(() => import('./pages/Compare'));
const Edit = lazy(() => import('./pages/Edit'));
const History = lazy(() => import('./pages/History'));
const Login = lazy(() => import('./pages/Login'));
const Signup = lazy(() => import('./pages/Signup'));
const Templates = lazy(() => import('./pages/Templates'));
const ForgotPassword = lazy(() => import('./pages/ForgotPassword'));
const VerifyOTP = lazy(() => import('./pages/VerifyOTP'));
const ResetPassword = lazy(() => import('./pages/ResetPassword'));
const Preview = lazy(() => import('./pages/Preview'));
const TemplateEditor = lazy(() => import('./pages/TemplateEditor'));
const AuthCallback = lazy(() => import('./pages/AuthCallback'));
const FeedbackPage = lazy(() => import('./pages/FeedbackPage'));
const AdminDashboard = lazy(() => import('./pages/AdminDashboard'));
const BatchUpload = lazy(() => import('./pages/BatchUpload'));
const NotificationsPage = lazy(() => import('./pages/NotificationsPage'));
const SettingsPage = lazy(() => import('./pages/SettingsPage'));
const Terms = lazy(() => import('./pages/Terms'));
const Privacy = lazy(() => import('./pages/Privacy'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Profile = lazy(() => import('./pages/Profile'));

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            staleTime: 10000,
            refetchOnWindowFocus: false,
            retry: 1,
        },
    },
});

/* ── Suspense fallback shown while lazy chunks load ── */
const PageLoader = () => (
    <div className="min-h-screen flex items-center justify-center bg-background-light dark:bg-background-dark">
        <div className="flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-3 border-primary border-t-transparent rounded-full animate-spin" />
            <p className="text-sm text-slate-500 dark:text-slate-400 font-medium">Loading…</p>
        </div>
    </div>
);

function App() {
    const withBoundary = (element) => <ErrorBoundary>{element}</ErrorBoundary>;

    return (
        <QueryClientProvider client={queryClient}>
            <ThemeProvider>
                <AuthProvider>
                    <ToastProvider>
                        <DocumentProvider>
                            <Router>
                                <ScrollManager />
                                <Suspense fallback={<PageLoader />}>
                                    <Routes>
                                        <Route path="/" element={withBoundary(<Landing />)} />

                                        {/* ── Guest + User: full pipeline flow (no login required) ── */}
                                        <Route path="/upload" element={withBoundary(<Upload />)} />
                                        <Route path="/processing" element={withBoundary(<Processing />)} />
                                        <Route path="/results" element={withBoundary(<ValidationResults />)} />
                                        <Route path="/download" element={withBoundary(<Download />)} />
                                        <Route path="/compare" element={withBoundary(<Compare />)} />
                                        <Route path="/preview" element={withBoundary(<Preview />)} />
                                        <Route path="/edit" element={withBoundary(<Edit />)} />
                                        <Route path="/jobs/:jobId/download" element={withBoundary(<Download />)} />
                                        <Route path="/jobs/:jobId/compare" element={withBoundary(<Compare />)} />
                                        <Route path="/jobs/:jobId/edit" element={withBoundary(<Edit />)} />
                                        <Route path="/jobs/:jobId/results" element={withBoundary(<ValidationResults />)} />
                                        <Route path="/jobs/:jobId/preview" element={withBoundary(<Preview />)} />
                                        <Route
                                            path="/error"
                                            element={withBoundary(
                                                <Error
                                                    error={{
                                                        title: 'Processing Error',
                                                        message: "Unsupported file type or corrupted metadata detected. We couldn't parse your manuscript for formatting. Please check your file format and try again.",
                                                    }}
                                                />,
                                            )}
                                        />
                                        <Route path="/templates" element={withBoundary(<Templates />)} />
                                        <Route path="/terms" element={withBoundary(<Terms />)} />
                                        <Route path="/privacy" element={withBoundary(<Privacy />)} />

                                        {/* ── Login required: account-specific (needs persistent data) ── */}
                                        <Route
                                            path="/dashboard"
                                            element={withBoundary(
                                                <ProtectedRoute>
                                                    <Dashboard />
                                                </ProtectedRoute>,
                                            )}
                                        />
                                        <Route
                                            path="/history"
                                            element={withBoundary(
                                                <ProtectedRoute>
                                                    <History />
                                                </ProtectedRoute>,
                                            )}
                                        />
                                        <Route
                                            path="/template-editor"
                                            element={withBoundary(
                                                <ProtectedRoute>
                                                    <TemplateEditor />
                                                </ProtectedRoute>,
                                            )}
                                        />
                                        <Route
                                            path="/profile"
                                            element={withBoundary(
                                                <ProtectedRoute>
                                                    <Profile />
                                                </ProtectedRoute>,
                                            )}
                                        />
                                        <Route
                                            path="/feedback"
                                            element={withBoundary(
                                                <ProtectedRoute>
                                                    <FeedbackPage />
                                                </ProtectedRoute>,
                                            )}
                                        />
                                        <Route
                                            path="/admin-dashboard"
                                            element={withBoundary(
                                                <ProtectedRoute>
                                                    <AdminDashboard />
                                                </ProtectedRoute>,
                                            )}
                                        />
                                        <Route
                                            path="/batch-upload"
                                            element={withBoundary(
                                                <ProtectedRoute>
                                                    <BatchUpload />
                                                </ProtectedRoute>,
                                            )}
                                        />
                                        <Route
                                            path="/notifications"
                                            element={withBoundary(
                                                <ProtectedRoute>
                                                    <NotificationsPage />
                                                </ProtectedRoute>,
                                            )}
                                        />
                                        <Route
                                            path="/settings"
                                            element={withBoundary(
                                                <ProtectedRoute>
                                                    <SettingsPage />
                                                </ProtectedRoute>,
                                            )}
                                        />

                                        {/* ── Auth pages (always accessible) ── */}
                                        <Route path="/login" element={withBoundary(<Login />)} />
                                        <Route path="/signup" element={withBoundary(<Signup />)} />
                                        <Route path="/auth/callback" element={withBoundary(<AuthCallback />)} />
                                        <Route path="/forgot-password" element={withBoundary(<ForgotPassword />)} />
                                        <Route path="/verify-otp" element={withBoundary(<VerifyOTP />)} />
                                        <Route path="/reset-password" element={withBoundary(<ResetPassword />)} />
                                        <Route path="*" element={withBoundary(<Error />)} />
                                    </Routes>
                                </Suspense>
                            </Router>
                        </DocumentProvider>
                    </ToastProvider>
                </AuthProvider>
            </ThemeProvider>
        </QueryClientProvider>
    );
}

export default App;
