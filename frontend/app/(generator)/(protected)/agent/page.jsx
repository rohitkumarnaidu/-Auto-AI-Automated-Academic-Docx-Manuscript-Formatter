'use client';

import React, { useCallback, useEffect, useRef, useState } from 'react';
import dynamic from 'next/dynamic';
import { useSearchParams } from 'next/navigation';
import { Bot, PanelLeftClose, PanelLeft, LayoutTemplate } from 'lucide-react';
import { approveOutline, createAgentSession, getSession, getSessionDocument, getSessionMessages, sendMessage } from '../../../../src/services/api.generator.v1';

const PanelGroup = dynamic(() => import('react-resizable-panels').then(mod => mod.PanelGroup || mod.Group), { ssr: false });
const Panel = dynamic(() => import('react-resizable-panels').then(mod => mod.Panel), { ssr: false });
const PanelResizeHandle = dynamic(() => import('react-resizable-panels').then(mod => mod.PanelResizeHandle || mod.Separator), { ssr: false });
import AgentChatPane from '../../../../src/components/generator/AgentChatPane';
import DocumentBuildPane from '../../../../src/components/generator/DocumentBuildPane';
import SessionHistory from '../../../../src/components/generator/SessionHistory';
import OutlineApproval from '../../../../src/components/generator/OutlineApproval';

const deriveSessionState = (session) => {
  const status = session?.status || '';
  const stage = session?.config?.stage || '';
  if (status === 'completed' || stage === 'done') return 'complete';
  if (status === 'awaiting_approval' || stage === 'awaiting_approval' || stage === 'outline') return 'outline_review';
  if (stage === 'writing' || stage === 'citations' || stage === 'rendering' || stage === 'scoring' || stage === 'rewriting' || stage === 'quality_boost') return 'generating';
  if (status === 'processing' || stage) return 'parsing';
  return 'idle';
};

const detectRewriteSection = (message, sections = []) => {
  const normalized = String(message || '').toLowerCase();
  const triggers = ['rewrite', 're-write', 'revise', 'reword', 'update', 'expand'];
  if (!triggers.some(trigger => normalized.includes(trigger))) return null;

  const aliases = {
    intro: 'Introduction',
    introduction: 'Introduction',
    background: 'Introduction',
    'literature review': 'Literature Review',
    methods: 'Methods',
    methodology: 'Methods',
    results: 'Results',
    discussion: 'Discussion',
    conclusion: 'Conclusion',
    abstract: 'Abstract'
  };
  for (const [alias, canonical] of Object.entries(aliases)) {
    if (normalized.includes(alias)) return canonical;
  }

  for (const section of sections) {
    const title = section?.title || section?.section || section;
    if (title && normalized.includes(String(title).toLowerCase())) {
      return title;
    }
  }
  return null;
};

export default function AgentWorkspacePage() {
  const searchParams = useSearchParams();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeSessionId, setActiveSessionId] = useState(null);
  
  // sessionState: 'idle' | 'parsing' | 'outline_review' | 'generating' | 'complete'
  const [sessionState, setSessionState] = useState('idle');
  
  // Data State
  const [messages, setMessages] = useState([]);
  const [outlineData, setOutlineData] = useState(null);
  const [qualityScore, setQualityScore] = useState(null);
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState(null);
  const [lastPrompt, setLastPrompt] = useState('');
  const [documentSections, setDocumentSections] = useState([]);
  
  // Template Selection (Mock/Alpha)
  const [selectedTemplate, setSelectedTemplate] = useState('ieee');

  const eventSourceRef = useRef(null);
  const outlineBufferRef = useRef('');
  const outlineReadyRef = useRef(false);
  const lastStageRef = useRef(null);

  const fetchSessionData = useCallback(async (sessionId) => {
    const data = await getSession(sessionId);
    const config = data?.config || {};
    setOutlineData(data?.outline || null);
    setQualityScore(config?.quality || null);
    if (config?.template) {
      setSelectedTemplate(String(config.template).toLowerCase());
    }
    if (config?.user_prompt) {
      setLastPrompt(String(config.user_prompt));
    }
    setSessionState(deriveSessionState(data));
    return data;
  }, []);

  const fetchSessionMessages = useCallback(async (sessionId) => {
    try {
      const res = await getSessionMessages(sessionId);
      const rawMessages = res?.messages || res || [];
      const filtered = rawMessages.filter(msg => msg.role !== 'system');
      const mapped = filtered.map((msg, index) => ({
        id: `${msg.created_at || Date.now()}-${index}`,
        role: msg.role,
        content: msg.content,
        timestamp: msg.created_at || Date.now()
      }));
      if (mapped.length) {
        setMessages(mapped);
        return mapped.length;
      }
    } catch (err) {
      // Non-blocking
    }
    return 0;
  }, []);

  const fetchLatestDocument = useCallback(async (sessionId) => {
    try {
      const res = await getSessionDocument(sessionId);
      const content = res?.content || res?.content_json || res;
      const sections = content?.sections || {};
      let entries = [];

      if (Array.isArray(sections)) {
        entries = sections.map((item, idx) => ({
          title: item.title || item.section || `Section ${idx + 1}`,
          content: item.content || ''
        }));
      } else if (sections && typeof sections === 'object') {
        entries = Object.entries(sections).map(([title, content]) => ({ title, content: String(content || '') }));
      }

      if (content?.references && Array.isArray(content.references) && content.references.length) {
        entries.push({ title: 'References', content: content.references.join('\n') });
      }

      const mapped = entries.map((section) => ({
        id: `section-${String(section.title).toLowerCase().replace(/[^a-z0-9]+/g, '-')}`,
        title: section.title,
        content: section.content,
        isCompleted: true,
        wordCount: section.content ? section.content.trim().split(/\s+/).length : 0
      }));

      setDocumentSections(mapped);
    } catch (err) {
      // Non-blocking
    }
  }, []);

  // Load a session
  const loadSession = useCallback(async (sessionId) => {
    try {
      setError(null);
      setIsTyping(true);
      setActiveSessionId(sessionId);
      const data = await fetchSessionData(sessionId);
      const messageCount = await fetchSessionMessages(sessionId);
      await fetchLatestDocument(sessionId);
      if (!messageCount) {
        setMessages([{
          id: Date.now(),
          role: 'assistant',
          content: 'Session loaded. You can continue with refinements or downloads.',
          timestamp: Date.now(),
          isStatus: true
        }]);
      }
      if (data?.outline) {
        outlineReadyRef.current = true;
      }
      setIsTyping(false);
    } catch (err) {
      console.error("Failed to load session:", err);
      setError("Failed to load the selected session.");
      setIsTyping(false);
    }
  }, [fetchSessionData, fetchSessionMessages, fetchLatestDocument, messages.length]);

  const handleSendMessage = async (text) => {
    setMessages(prev => [...prev, { id: Date.now(), role: 'user', content: text, timestamp: Date.now() }]);
    setIsTyping(true);
    setError(null);

    let shouldStopTyping = true;
    try {
      // If idle -> create session -> parse -> outline
      if (sessionState === 'idle' || !activeSessionId) {
        setSessionState('parsing');
        setLastPrompt(text);
        setDocumentSections([]);

        const response = await createAgentSession(text, selectedTemplate, {});
        const sessionId = response?.session_id || response?.id || response?.sessionId;
        if (!sessionId) throw new Error('No session ID returned from server.');

        setActiveSessionId(sessionId);
        setMessages(prev => [...prev, { 
          id: Date.now(), 
          role: 'assistant', 
          content: 'Parsing your request and preparing an outline...',
          timestamp: Date.now(),
          isStatus: true
        }]);
        shouldStopTyping = false;
      } else {
        const rewriteSection = detectRewriteSection(text, outlineData?.sections || []);
        if (rewriteSection) {
          setMessages(prev => [...prev, {
            id: Date.now(),
            role: 'assistant',
            content: `Rewriting ${rewriteSection}...`,
            timestamp: Date.now(),
            isStatus: true
          }]);
        }

        const res = await sendMessage(activeSessionId, text);
        if (res && res.content) {
          setMessages(prev => [...prev, { 
            id: Date.now(), 
            role: res.role || 'assistant', 
            content: res.content,
            sources: res.sources || [],
            timestamp: res.created_at || Date.now() 
          }]);
        } else {
          setMessages(prev => [...prev, { role: 'assistant', content: "I couldn't generate a response.", timestamp: Date.now() }]);
        }
        await fetchLatestDocument(activeSessionId);
      }
    } catch (err) {
      setError(err.message || "An error occurred while communicating with the agent.");
      setIsTyping(false);
    } finally {
      if (shouldStopTyping) {
        setIsTyping(false);
      }
    }
  };

  const handleApproveOutline = async (modifiedOutline) => {
    if (!activeSessionId) return;
    setOutlineData(modifiedOutline);
    setSessionState('generating');
    setDocumentSections([]);
    
    setMessages(prev => [...prev, { 
      id: Date.now(), 
      role: 'user', 
      content: 'I have approved the outline. Please proceed with writing.', 
      timestamp: Date.now() 
    }, {
      id: Date.now() + 1,
      role: 'assistant',
      content: 'Starting document generation based on the approved outline. You can watch the progress in the right panel.',
      timestamp: Date.now() + 100,
      isStatus: true
    }]);

    try {
      await approveOutline(activeSessionId, modifiedOutline);
    } catch (err) {
      setError(err.message || 'Failed to approve outline.');
    }
  };

  const handleRegenerateOutline = async () => {
    if (!lastPrompt) return;
    setOutlineData(null);
    setSessionState('parsing');
    setMessages(prev => [...prev, { id: Date.now(), role: 'user', content: 'Please generate a different outline structure.', timestamp: Date.now() }]);
    setIsTyping(true);
    
    try {
      const response = await createAgentSession(lastPrompt, selectedTemplate, { regenerate: true });
      const sessionId = response?.session_id || response?.id || response?.sessionId;
      if (!sessionId) throw new Error('No session ID returned from server.');
      setActiveSessionId(sessionId);
      setDocumentSections([]);
    } catch (err) {
      setError(err.message || 'Failed to regenerate outline.');
      setIsTyping(false);
    } finally {
      // Keep typing indicator active until outline arrives
    }
  };

  const handleDownload = (format) => {
    if (!activeSessionId) return;
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const url = `${apiUrl}/api/v1/generator/sessions/${activeSessionId}/download?format=${format}`;
    const a = document.createElement('a');
    a.href = url;
    a.download = `generated_document.${format}`;
    document.body.appendChild(a);
    a.click();
    a.remove();
  };

  const handleOutlineEdit = (updatedOutline) => {
    setOutlineData(updatedOutline);
  };

  // Load session from query param or local storage
  useEffect(() => {
    const sessionFromQuery = searchParams.get('session');
    if (sessionFromQuery) {
      loadSession(sessionFromQuery);
      return;
    }
    if (typeof window !== 'undefined' && !activeSessionId) {
      const stored = window.localStorage.getItem('agent_session_id');
      if (stored) {
        loadSession(stored);
      }
    }
  }, [searchParams, activeSessionId, loadSession]);

  // Persist active session for refresh
  useEffect(() => {
    if (typeof window === 'undefined') return;
    if (activeSessionId) {
      window.localStorage.setItem('agent_session_id', activeSessionId);
    }
  }, [activeSessionId]);

  // SSE listener for outline + status updates
  useEffect(() => {
    if (!activeSessionId) return;

    outlineReadyRef.current = false;
    outlineBufferRef.current = '';
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const eventSource = new EventSource(`${apiUrl}/api/v1/generator/sessions/${activeSessionId}/events`, { withCredentials: true });
    eventSourceRef.current = eventSource;

    const handleOutlineChunk = (event) => {
      if (outlineReadyRef.current) return;
      try {
        const data = JSON.parse(event.data);
        const payload = data.payload || {};
        const chunk = payload.content || '';
        if (!chunk) return;
        outlineBufferRef.current += chunk;
        try {
          const parsed = JSON.parse(outlineBufferRef.current);
          if (parsed && parsed.sections) {
            outlineReadyRef.current = true;
            setOutlineData(parsed);
            setSessionState('outline_review');
            setIsTyping(false);
            const topic = parsed.title || lastPrompt || 'your topic';
            const sectionTitles = parsed.sections.map((s) => s.title || s.section || '').filter(Boolean).join(', ');
            const sectionsLine = sectionTitles ? `with sections: ${sectionTitles}` : 'with the recommended structure';
            setMessages(prev => [...prev, {
              id: Date.now(),
              role: 'assistant',
              content: `I'll draft a ${selectedTemplate.toUpperCase()} paper about ${topic} ${sectionsLine}. Review the outline above.`,
              timestamp: Date.now()
            }]);
          }
        } catch (err) {
          // Wait for more chunks
        }
      } catch (error) {
        console.error("Error parsing outline_chunk SSE data:", error);
      }
    };

    const handleStageUpdate = async (event) => {
      try {
        const data = JSON.parse(event.data);
        const payload = data.payload || {};
        const stage = data.stage || payload.stage;
        const status = payload.status || data.status;

        if (stage && lastStageRef.current !== stage) {
          lastStageRef.current = stage;
        }

        if (stage === 'outline' || stage === 'awaiting_approval') {
          setSessionState('outline_review');
          if (!outlineReadyRef.current) {
            try {
              const data = await fetchSessionData(activeSessionId);
              if (data?.outline) {
                outlineReadyRef.current = true;
                setIsTyping(false);
              }
            } catch (err) {
              // no-op
            }
          }
        }

        if (stage === 'writing' || stage === 'citations' || stage === 'rendering' || stage === 'scoring' || stage === 'rewriting' || stage === 'quality_boost') {
          setSessionState('generating');
        }

        if (stage === 'done' || status === 'completed') {
          setSessionState('complete');
          setIsTyping(false);
          await fetchSessionData(activeSessionId);
          await fetchLatestDocument(activeSessionId);
          setMessages(prev => [...prev, {
            id: Date.now(),
            role: 'assistant',
            content: 'Draft complete. Quality checks finished and the document is ready for download.',
            timestamp: Date.now()
          }]);
        }
      } catch (error) {
        console.error("Error parsing stage_update SSE data:", error);
      }
    };

    eventSource.addEventListener('outline_chunk', handleOutlineChunk);
    eventSource.addEventListener('stage_update', handleStageUpdate);

    eventSource.onerror = (err) => {
      console.error('SSE Error:', err);
    };

    return () => {
      eventSource.close();
    };
  }, [activeSessionId, selectedTemplate, lastPrompt, fetchSessionData, fetchLatestDocument]);

  return (
    <div className="flex flex-col h-[100dvh] bg-zinc-100 dark:bg-zinc-900 overflow-hidden">
      
      {/* Top Header Layer */}
      <header className="flex-shrink-0 h-14 border-b border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 px-4 flex items-center justify-between z-20">
        <div className="flex items-center gap-3">
          <button 
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 -ml-2 rounded-lg text-zinc-500 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
          >
            {sidebarOpen ? <PanelLeftClose className="w-5 h-5" /> : <PanelLeft className="w-5 h-5" />}
          </button>
          
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded bg-indigo-600 flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <h1 className="font-semibold text-zinc-900 dark:text-zinc-100 hidden sm:block">Agent Workspace</h1>
          </div>
        </div>

        <div className="flex items-center gap-4 text-sm">
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-50 dark:bg-indigo-500/10 text-indigo-700 dark:text-indigo-300 text-xs font-semibold border border-indigo-100 dark:border-indigo-500/20">
            Agent Session
          </div>
          <div className="flex items-center gap-2 border border-zinc-200 dark:border-zinc-800 rounded-lg px-3 py-1.5 bg-zinc-50 dark:bg-zinc-900">
            <LayoutTemplate className="w-4 h-4 text-zinc-500" />
            <select 
              value={selectedTemplate}
              onChange={(e) => setSelectedTemplate(e.target.value)}
              className="bg-transparent border-none appearance-none focus:ring-0 text-zinc-700 dark:text-zinc-300 font-medium py-0 pr-6"
            >
              <option value="ieee">IEEE Paper format</option>
              <option value="nature">Nature Journal</option>
              <option value="apa">APA 7th Edition</option>
            </select>
          </div>
        </div>
      </header>

      {/* Main Workspace Area with Resizable Panels */}
      <div className="flex-1 overflow-hidden h-full">
        <PanelGroup direction="horizontal">
          
          {/* Left Sidebar - Session History */}
          {sidebarOpen && (
            <>
              <Panel 
                defaultSize={20} 
                minSize={15} 
                maxSize={30}
                className="bg-zinc-50 dark:bg-zinc-900 shadow-xl z-10"
              >
                <SessionHistory 
                  activeSessionId={activeSessionId}
                  onSelectSession={loadSession}
                />
              </Panel>
              <PanelResizeHandle className="w-1 bg-zinc-200 dark:bg-zinc-800 hover:bg-indigo-500 dark:hover:bg-indigo-500 transition-colors" />
            </>
          )}

          {/* Middle Panel - Chat Interface & Interactions */}
          <Panel defaultSize={35} minSize={25} className="flex flex-col min-w-0">
            <div className="flex flex-col h-full bg-zinc-100/50 dark:bg-zinc-950/50 p-4 gap-4 overflow-hidden">
              
              {/* Dynamic Top Area (Outline Approval takes this space when active) */}
              {sessionState === 'outline_review' && outlineData && (
                <div className="flex-shrink-0 h-[50%] min-h-[300px]">
                  <OutlineApproval 
                    outline={outlineData}
                    onApprove={handleApproveOutline}
                    onEdit={handleOutlineEdit}
                    onRegenerate={handleRegenerateOutline}
                  />
                </div>
              )}
              
              {/* Chat Area (Grows when Outline isn't showing) */}
              <div className="flex-1 min-h-0 min-w-0">
                <AgentChatPane 
                  sessionId={activeSessionId}
                  messages={messages}
                  onSendMessage={handleSendMessage}
                  isTyping={isTyping}
                  error={error}
                />
              </div>

            </div>
          </Panel>

          <PanelResizeHandle className="w-1 bg-zinc-200 dark:bg-zinc-800 hover:bg-indigo-500 dark:hover:bg-indigo-500 transition-colors" />

          {/* Right Panel - Live Document Viewer */}
          <Panel defaultSize={45} minSize={30} className="bg-white dark:bg-zinc-950 relative min-w-0 shadow-[-4px_0_24px_-12px_rgba(0,0,0,0.1)] z-10">
            <DocumentBuildPane 
              sessionId={activeSessionId}
              stage={['generating', 'complete'].includes(sessionState) ? sessionState : 'idle'}
              qualityScore={qualityScore}
              initialSections={documentSections}
              onDownload={handleDownload}
            />
          </Panel>

        </PanelGroup>
      </div>

    </div>
  );
}
