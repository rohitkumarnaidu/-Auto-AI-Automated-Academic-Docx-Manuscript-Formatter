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

import { DocumentProvider } from './context/DocumentContext';

function App() {
    return (
        <DocumentProvider>
            <Router>
                <Routes>
                    <Route path="/" element={<Landing />} />
                    <Route path="/upload" element={<Upload />} />
                    <Route path="/processing" element={<Processing />} />
                    <Route path="/results" element={<ValidationResults />} />
                    <Route path="/download" element={<Download />} />
                    <Route path="/error" element={<Error />} />
                    <Route path="/compare" element={<Compare />} />
                    <Route path="/edit" element={<Edit />} />
                    <Route path="/history" element={<History />} />
                </Routes>
            </Router>
        </DocumentProvider>
    );
}

export default App;
