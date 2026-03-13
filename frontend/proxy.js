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

        // SECURITY HEADERS from Phase B4 (production only)
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
                        // Enforce secure cookie options for tokens
                        const secureOptions = {
                            ...options,
                            httpOnly: true,
                            sameSite: 'lax',
                            secure: process.env.NODE_ENV === 'production'
                        };
                        request.cookies.set(name, value);
                        supabaseResponse.cookies.set(name, value, secureOptions);
                    });
                },
            },
        }
    );

    const {
        data: { session },
    } = await supabase.auth.getSession();

    let user = session?.user || null;
    if (!user) {
        try {
            const { data, error } = await supabase.auth.getUser();
            if (!error && data?.user) {
                user = data.user;
            }
        } catch (err) {
            console.warn('[Auth] Failed to fetch user for SSR guard:', err);
        }
    }

    const url = request.nextUrl.clone();
    const pathname = url.pathname;

    const hasAuthCookie = request.cookies
        .getAll()
        .some(({ name }) => name.startsWith('sb-') && name.includes('auth-token'));

    const isAuthenticated = Boolean(user) || hasAuthCookie;

    const protectedRoutes = [
        '/dashboard', '/profile', '/feedback', '/notifications', '/settings',
        '/history', '/template-editor', '/batch-upload', '/generate'
    ];

    const isProtected = protectedRoutes.some(route => pathname.startsWith(route));
    const isAdminRoute = pathname.startsWith('/admin-dashboard');

    if (!isAuthenticated) {
        // Not logged in
        if (isProtected || isAdminRoute) {
            if (process.env.NODE_ENV !== 'production') {
                return supabaseResponse;
            }
            const loginUrl = new URL('/login', request.url);
            loginUrl.searchParams.set('next', `${pathname}${url.search || ''}`);
            return NextResponse.redirect(loginUrl, 307);
        }
    } else {
        // Logged in
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
