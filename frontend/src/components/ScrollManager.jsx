import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

/**
 * Keeps route navigation consistent by resetting scroll position on page changes.
 * Supports hash anchors on the landing page.
 */
export default function ScrollManager() {
    const { pathname, search, hash } = useLocation();

    useEffect(() => {
        if (typeof window === 'undefined' || !window.history) {
            return undefined;
        }
        const previousMode = window.history.scrollRestoration;
        window.history.scrollRestoration = 'manual';
        return () => {
            window.history.scrollRestoration = previousMode;
        };
    }, []);

    useEffect(() => {
        if (typeof window === 'undefined') {
            return;
        }

        if (hash) {
            const id = decodeURIComponent(hash.slice(1));
            const target = document.getElementById(id);
            if (target) {
                const prefersReducedMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches;
                const behavior = prefersReducedMotion ? 'auto' : 'smooth';
                const scrollToAnchor = () => target.scrollIntoView({ behavior, block: 'start' });
                if (typeof window.requestAnimationFrame === 'function') {
                    window.requestAnimationFrame(scrollToAnchor);
                } else {
                    setTimeout(scrollToAnchor, 0);
                }
                return;
            }
        }

        if (typeof window.scrollTo === 'function') {
            window.scrollTo({ top: 0, left: 0, behavior: 'auto' });
        }
    }, [pathname, search, hash]);

    return null;
}
