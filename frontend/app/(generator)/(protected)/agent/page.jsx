"use client";

import React, { useState, useEffect, Suspense } from 'react';
import dynamic from 'next/dynamic';
import { useSearchParams } from 'next/navigation';
import { 
  BrainCircuit, 
  PanelLeftClose, 
  PanelLeftOpen, 
  Plus, 
  Settings2
} from 'lucide-react';

// Dynamic imports for heavy panels
const ResizablePanelGroup = dynamic(() => import('react-resizable-panels').then(mod => mod.PanelGroup), { ssr: false });
const ResizablePanel = dynamic(() => import('react-resizable-panels').then(mod => mod.Panel), { ssr: false });
const ResizableHandle = dynamic(() => import('react-resizable-panels').then(mod => mod.PanelResizeHandle), { ssr: false });

import AgentChatPane from '@/src/components/generator/AgentChatPane';
import DocumentBuildPane from '@/src/components/generator/DocumentBuildPane';
import SessionHistory from '@/src/components/generator/SessionHistory';
import OutlineApproval from '@/src/components/generator/OutlineApproval';
import UpgradeModal from '@/src/components/UpgradeModal';

import { useAgent } from '@/src/hooks/useAgent';
import { useAgentEvents } from '@/src/hooks/useAgentEvents';
import { useAuth } from '@/src/context/AuthContext';
import { canAccess } from '@/src/lib/planTier';

/**
 * AgentWorkspaceContent
 * 
 * Performance-optimized main container for the AI Agent authoring experience.
 * Uses custom hooks for state management and SSE event handling.
 */
function AgentWorkspaceContent() {
  const searchParams = useSearchParams();
  const { user } = useAuth();
  
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  
  // Use our optimized hooks
  const {
    activeSessionId,
    messages,
    isTyping,
    sessionState,
    outlineData,
    qualityScore,
    documentSections,
    setActiveSessionId,
    handleSendMessage,
    handleStop,
    handleApprove,
    loadSession
  } = useAgent();

  // Handle SSE events
  useAgentEvents(activeSessionId, sessionState);

  // Initial load from search params
  useEffect(() => {
    const sessionFromQuery = searchParams.get('session');
    if (sessionFromQuery && sessionFromQuery !== activeSessionId) {
      loadSession(sessionFromQuery);
    }
  }, [searchParams, loadSession, activeSessionId]);

  // Auth check
  useEffect(() => {
    if (user && !canAccess(user, 'generator_agent')) {
      setShowUpgradeModal(true);
    }
  }, [user]);

  // Layout Handlers
  const toggleSidebar = () => setIsSidebarOpen(!isSidebarOpen);

  const handleSelectSession = (id) => {
    loadSession(id);
  };

  const handleNewSession = () => {
    setActiveSessionId(null);
  };

  if (user && !canAccess(user, 'generator_agent')) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-8 text-center bg-white dark:bg-zinc-950">
        <UpgradeModal 
          isOpen={showUpgradeModal} 
          onClose={() => setShowUpgradeModal(false)} 
          title="Upgrade to Pro for AI Agent" 
        />
        <div className="w-16 h-16 rounded-2xl bg-indigo-100 dark:bg-indigo-500/10 flex items-center justify-center mb-6">
          <BrainCircuit className="w-8 h-8 text-indigo-600 dark:text-indigo-400" />
        </div>
        <h2 className="text-2xl font-bold text-zinc-900 dark:text-zinc-100 mb-4">AI Agent is a Pro Feature</h2>
        <p className="text-zinc-600 dark:text-zinc-400 mb-8 max-w-md">
          Upgrade to our Pro plan to interact with the AI Agent for intelligent document synthesis and drafting.
        </p>
        <button 
          onClick={() => setShowUpgradeModal(true)} 
          className="px-8 py-3 bg-indigo-600 text-white font-semibold rounded-xl hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-600/20"
        >
          View Plans
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-[calc(100vh-64px)] overflow-hidden bg-white dark:bg-zinc-950">
      <UpgradeModal 
        isOpen={showUpgradeModal} 
        onClose={() => setShowUpgradeModal(false)} 
        title="Upgrade to Pro for AI Agent" 
      />
      
      {/* Top Toolbar */}
      <div className="h-12 border-b border-zinc-200 dark:border-zinc-800 flex items-center justify-between px-4 bg-zinc-50/50 dark:bg-zinc-900/50">
        <div className="flex items-center gap-3">
          <button 
            onClick={toggleSidebar}
            className="p-1.5 hover:bg-zinc-200 dark:hover:bg-zinc-800 rounded-md transition-colors text-zinc-500"
            title={isSidebarOpen ? "Hide History" : "Show History"}
          >
            {isSidebarOpen ? <PanelLeftClose className="w-4 h-4" /> : <PanelLeftOpen className="w-4 h-4" />}
          </button>
          
          <div className="h-4 w-px bg-zinc-300 dark:bg-zinc-700 mx-1" />
          
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-lg bg-indigo-600 flex items-center justify-center">
              <BrainCircuit className="w-3.5 h-3.5 text-white" />
            </div>
            <h1 className="text-sm font-semibold text-zinc-900 dark:text-zinc-100 italic">
              ECLearnIX <span className="text-zinc-400 font-normal">Agent Workspace</span>
            </h1>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button 
            onClick={handleNewSession}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-white dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 rounded-lg text-xs font-medium text-zinc-700 dark:text-zinc-300 hover:bg-zinc-50 dark:hover:bg-zinc-700/50 transition-colors shadow-sm"
          >
            <Plus className="w-3.5 h-3.5" />
            New Project
          </button>
          <button className="p-1.5 hover:bg-zinc-200 dark:hover:bg-zinc-800 rounded-md transition-colors text-zinc-500">
            <Settings2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Main Resizable Layout */}
      <ResizablePanelGroup direction="horizontal" className="flex-1">
        
        {/* Sidebar: History */}
        {isSidebarOpen && (
          <>
            <ResizablePanel defaultSize={20} minSize={15} maxSize={30}>
              <SessionHistory 
                activeSessionId={activeSessionId} 
                onSelectSession={handleSelectSession} 
              />
            </ResizablePanel>
            <ResizableHandle withHandle className="bg-zinc-200 dark:bg-zinc-800" />
          </>
        )}

        {/* Center: Chat & Actions */}
        <ResizablePanel defaultSize={40} minSize={30}>
          <div className="h-full flex flex-col relative">
            
            {/* Outline Approval Overlay - Dynamic based on sessionState */}
            {sessionState === 'outline_review' && outlineData && (
              <div className="absolute inset-x-4 top-4 bottom-24 z-30 transition-all">
                <OutlineApproval 
                  outline={outlineData}
                  onApprove={handleApprove}
                  onRegenerate={() => handleSendMessage("Regenerate the outline with more focus on methodology.")}
                />
              </div>
            )}

            <AgentChatPane 
              messages={messages}
              onSendMessage={handleSendMessage}
              onStopSession={handleStop}
              isProcessing={isTyping}
              stage={sessionState}
            />
          </div>
        </ResizablePanel>

        <ResizableHandle withHandle className="bg-zinc-200 dark:bg-zinc-800" />

        {/* Right: Live Preview */}
        <ResizablePanel defaultSize={40} minSize={30}>
          <DocumentBuildPane 
            sessionId={activeSessionId}
            stage={sessionState}
            qualityScore={qualityScore}
            initialSections={documentSections}
            onDownload={(format) => window.open(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/generator/sessions/${activeSessionId}/export?format=${format}`)}
          />
        </ResizablePanel>

      </ResizablePanelGroup>
    </div>
  );
}

export default function AgentPage() {
  return (
    <Suspense fallback={<div className="h-screen flex items-center justify-center bg-white dark:bg-zinc-950"><div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div></div>}>
      <AgentWorkspaceContent />
    </Suspense>
  );
}
