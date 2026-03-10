'use client';
import { useEffect, useRef, useState } from 'react';

export default function Minimap({ content, editorRef }) {
    const minimapRef = useRef(null);
    const scrollBoxRef = useRef(null);
    const [scrollRatio, setScrollRatio] = useState(0);
    const [viewportRatio, setViewportRatio] = useState(1);

    // Sync scroll from editor to minimap
    useEffect(() => {
        const editor = editorRef?.current;
        if (!editor) return;

        const handleScroll = () => {
            const { scrollTop, scrollHeight, clientHeight } = editor;
            const maxScroll = scrollHeight - clientHeight;
            if (maxScroll <= 0) {
                setScrollRatio(0);
                setViewportRatio(1);
                return;
            }
            // Ratio of visible area to total area
            setViewportRatio(Math.min(1, clientHeight / scrollHeight));
            // Current scroll percentage
            setScrollRatio(scrollTop / maxScroll);
        };

        editor.addEventListener('scroll', handleScroll, { passive: true });
        window.addEventListener('resize', handleScroll);

        // Initial setup via setTimeout to ensure DOM is ready
        setTimeout(handleScroll, 100);

        return () => {
            editor.removeEventListener('scroll', handleScroll);
            window.removeEventListener('resize', handleScroll);
        };
    }, [editorRef, content]);

    // Fast navigation by clicking minimap
    const handleMinimapClick = (e) => {
        const editor = editorRef?.current;
        const minimap = minimapRef?.current;
        if (!editor || !minimap) return;

        const rect = minimap.getBoundingClientRect();
        const clickY = e.clientY - rect.top;
        const clickRatio = Math.max(0, Math.min(1, clickY / rect.height));

        const maxScroll = editor.scrollHeight - editor.clientHeight;
        editor.scrollTop = clickRatio * maxScroll;
    };

    return (
        <div
            className="hidden 2xl:block w-32 shrink-0 bg-slate-50 dark:bg-slate-900 border-l border-slate-200 dark:border-slate-800 relative z-10 overflow-hidden cursor-pointer select-none"
            onClick={handleMinimapClick}
            ref={minimapRef}
        >
            {/* The scaled down content */}
            <div className="absolute top-0 left-0 w-[320px] origin-top-left scale-[0.1] text-slate-400/50 dark:text-slate-500/50 font-serif leading-relaxed whitespace-pre-wrap break-words px-4 pointer-events-none">
                {content}
            </div>

            {/* The highlight showing current scroll position */}
            {viewportRatio < 1 && (
                <div
                    ref={scrollBoxRef}
                    className="absolute left-0 w-full bg-primary/10 border-y border-primary/20 transition-all duration-75 pointer-events-none"
                    style={{
                        height: `${viewportRatio * 100}%`,
                        top: `${scrollRatio * (1 - viewportRatio) * 100}%`
                    }}
                />
            )}
        </div>
    );
}
