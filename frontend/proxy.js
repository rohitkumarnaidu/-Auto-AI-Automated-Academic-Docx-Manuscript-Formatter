import { NextResponse } from 'next/server';
import { createServerClient } from '@supabase/ssr';

export async function proxy(request) {
    let supabaseResponse = NextResponse.next({
        request: {
            headers: request.headers,
        },
    });

    if (process.env.NODE_ENV === 'production') {
        const connectSrcAllowlist = [
            "https://*.supabase.co",
            "wss://*.supabase.co",
        ];

        const apiUrl = process.env.NEXT_PUBLIC_API_URL;
        const legacyApiUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
        if (apiUrl) {
            connectSrcAllowlist.push(apiUrl);
        }
        if (legacyApiUrl && legacyApiUrl !== apiUrl) {
            connectSrcAllowlist.push(legacyApiUrl);
        }

        // SECURITY HEADERS (production only)
        supabaseResponse.headers.set('Content-Security-Policy', [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
            "font-src 'self' https://fonts.gstatic.com",
            "img-src 'self' data: blob: https://*.supabase.co",
            `connect-src 'self' ${connectSrcAllowlist.join(' ')}`,
        ].join('; '));
    }

    supabaseResponse.headers.set('X-Frame-Options', 'DENY');
    supabaseResponse.headers.set('X-Content-Type-Options', 'nosniff');
    supabaseResponse.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
    supabaseResponse.headers.set('Permissions-Policy', 'camera=(), microphone=(), geolocation=()');

    const url = request.nextUrl.clone();
    const pathname = url.pathname;

    const protectedRoutes = [
        '/dashboard', '/profile', '/feedback', '/notifications', '/settings',
        '/history', '/template-editor', '/batch-upload', '/generate',
    ];
    const isProtected = protectedRoutes.some(route => pathname.startsWith(route));
    const isAdminRoute = pathname.startsWith('/admin-dashboard');

    // ── Fast path: skip ALL Supabase network calls for non-protected routes ────
    // This eliminates the 2-3s latency on every public page load.
    if (!isProtected && !isAdminRoute) {
        return supabaseResponse;
    }

    // ── Auth check: only reaches here for protected / admin routes ─────────────
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

    if (!supabaseUrl || !supabaseAnonKey) {
        return supabaseResponse;
    }

    const supabase = createServerClient(
        supabaseUrl,
        supabaseAnonKey,
        {
            cookies: {
                getAll() {
                    return request.cookies.getAll();
                },
                setAll(cookiesToSet) {
                    cookiesToSet.forEach(({ name, value, options }) => {
                        const secureOptions = {
                            ...options,
                            httpOnly: true,
                            sameSite: 'lax',
                            secure: process.env.NODE_ENV === 'production',
                        };
                        request.cookies.set(name, value);
                        supabaseResponse.cookies.set(name, value, secureOptions);
                    });
                },
            },
        }
    );

    // Single getSession() — removed the redundant getUser() fallback that was
    // doubling latency by making two sequential network calls on every request.
    const {
        data: { session },
    } = await supabase.auth.getSession();

    const user = session?.user || null;

    const hasAuthCookie = request.cookies
        .getAll()
        .some(({ name }) => name.startsWith('sb-') && name.includes('auth-token'));

    const isAuthenticated = Boolean(user) || hasAuthCookie;

    if (!isAuthenticated) {
        if (isProtected || isAdminRoute) {
            if (process.env.NODE_ENV !== 'production') {
                return supabaseResponse;
            }
            const loginUrl = new URL('/login', request.url);
            loginUrl.searchParams.set('next', `${pathname}${url.search || ''}`);
            return NextResponse.redirect(loginUrl, 307);
        }
    } else {
        if (isAdminRoute) {
            const role = user?.user_metadata?.role;
            if (role !== 'admin') {
                return NextResponse.redirect(new URL('/dashboard', request.url), 307);
            }
        }
    }

    return supabaseResponse;
}

export const config = {
    matcher: [
        '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
    ],
};
