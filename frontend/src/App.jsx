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
                            <Route path="/upload" element={<ProtectedRoute><Upload /></ProtectedRoute>} />
                            <Route path="/processing" element={<ProtectedRoute><Processing /></ProtectedRoute>} />
                            <Route path="/results" element={<ProtectedRoute><ValidationResults /></ProtectedRoute>} />
                            <Route path="/download" element={<ProtectedRoute><Download /></ProtectedRoute>} />
                            <Route path="/error" element={<Error />} />
                            <Route path="/compare" element={<ProtectedRoute><Compare /></ProtectedRoute>} />
                            <Route path="/preview" element={<ProtectedRoute><Preview /></ProtectedRoute>} />
                            <Route path="/edit" element={<ProtectedRoute><Edit /></ProtectedRoute>} />
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
                            <Route
                                path="/template-editor"
                                element={
                                    <ProtectedRoute>
                                        <TemplateEditor />
                                    </ProtectedRoute>
                                }
                            />
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
