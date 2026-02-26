import { useEffect, useRef } from 'react';

/**
 * Lightweight scroll-reveal hook using IntersectionObserver.
 * Adds 'revealed' class when element enters viewport, then disconnects.
 * Respects prefers-reduced-motion by revealing immediately.
 */
export default function useScrollReveal(options = {}) {
    const ref = useRef(null);

    useEffect(() => {
        const el = ref.current;
        if (!el) return;

        // Respect reduced-motion preference
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            el.classList.add('revealed');
            return;
        }

        const observer = new IntersectionObserver(
            ([entry]) => {
                if (entry.isIntersecting) {
                    el.classList.add('revealed');
                    observer.disconnect();
                }
            },
            { threshold: 0.15, ...options }
        );

        observer.observe(el);
        return () => observer.disconnect();
    }, []);

    return ref;
}
