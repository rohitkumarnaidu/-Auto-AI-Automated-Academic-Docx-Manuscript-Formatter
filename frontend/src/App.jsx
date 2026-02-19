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

import { DocumentProvider } from './context/DocumentContext';
import { AuthProvider } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
    return (
        <ThemeProvider>
            <AuthProvider>
                <DocumentProvider>
                    <Router>
                        <Routes>
                            <Route path="/" element={<Landing />} />
                            <Route
                                path="/dashboard"
                                element={
                                    <ProtectedRoute>
                                        <Dashboard />
                                    </ProtectedRoute>
                                }
                            />
                            <Route path="/upload" element={<Upload />} />
                            <Route path="/processing" element={<Processing />} />
                            <Route path="/results" element={<ValidationResults />} />
                            <Route path="/download" element={<Download />} />
                            <Route path="/error" element={<Error />} />
                            <Route path="/compare" element={<Compare />} />
                            <Route path="/preview" element={<Preview />} />
                            <Route path="/edit" element={<Edit />} />
                            <Route
                                path="/history"
                                element={
                                    <ProtectedRoute>
                                        <History />
                                    </ProtectedRoute>
                                }
                            />
                            <Route path="/login" element={<Login />} />
                            <Route path="/signup" element={<Signup />} />
                            <Route path="/templates" element={<Templates />} />
                            <Route path="/forgot-password" element={<ForgotPassword />} />
                            <Route path="/verify-otp" element={<VerifyOTP />} />
                            <Route path="/reset-password" element={<ResetPassword />} />
                            <Route
                                path="/profile"
                                element={
                                    <ProtectedRoute>
                                        <Profile />
                                    </ProtectedRoute>
                                }
                            />
                        </Routes>
                    </Router>
                </DocumentProvider>
            </AuthProvider>
        </ThemeProvider >
    );
}

export default App;
