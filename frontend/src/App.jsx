import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Landing from './pages/Landing';
import Upload from './pages/Upload';
import Processing from './pages/Processing';
import ValidationResults from './pages/ValidationResults';
import Download from './pages/Download';
import Error from './pages/Error';

import Compare from './pages/Compare';
import Edit from './pages/Edit';
import History from './pages/History';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Templates from './pages/Templates';
import ForgotPassword from './pages/ForgotPassword';
import VerifyOTP from './pages/VerifyOTP';
import ResetPassword from './pages/ResetPassword';
import Preview from './pages/Preview';
import TemplateEditor from './pages/TemplateEditor';

import { DocumentProvider } from './context/DocumentContext';
import { AuthProvider } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';
import ProtectedRoute from './components/ProtectedRoute';
import ErrorBoundary from './components/ErrorBoundary';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            staleTime: 10000,
            refetchOnWindowFocus: false,
            retry: 1,
        },
    },
});

function App() {
    const withBoundary = (element) => <ErrorBoundary>{element}</ErrorBoundary>;

    return (
        <QueryClientProvider client={queryClient}>
            <ThemeProvider>
                <AuthProvider>
                    <DocumentProvider>
                        <Router>
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

                                {/* ── Auth pages (always accessible) ── */}
                                <Route path="/login" element={withBoundary(<Login />)} />
                                <Route path="/signup" element={withBoundary(<Signup />)} />
                                <Route path="/forgot-password" element={withBoundary(<ForgotPassword />)} />
                                <Route path="/verify-otp" element={withBoundary(<VerifyOTP />)} />
                                <Route path="/reset-password" element={withBoundary(<ResetPassword />)} />
                                <Route path="*" element={withBoundary(<Error />)} />
                            </Routes>
                        </Router>
                    </DocumentProvider>
                </AuthProvider>
            </ThemeProvider>
        </QueryClientProvider>
    );
}

export default App;
