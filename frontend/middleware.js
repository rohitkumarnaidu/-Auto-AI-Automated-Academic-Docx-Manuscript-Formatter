import { NextResponse } from 'next/server';
import { createServerClient } from '@supabase/ssr';

export async function middleware(request) {
    let supabaseResponse = NextResponse.next({
        request: {
            headers: request.headers,
        },
    });

    // SECURITY HEADERS from Phase B4
    supabaseResponse.headers.set('Content-Security-Policy', [
        "default-src 'self'",
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
        "font-src 'self' https://fonts.gstatic.com",
        "img-src 'self' data: blob: https://*.supabase.co",
        "connect-src 'self' https://*.supabase.co wss://*.supabase.co " + (process.env.NEXT_PUBLIC_API_BASE_URL || ''),
    ].join('; '));

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
                        request.cookies.set(name, value);
                        supabaseResponse.cookies.set(name, value, options);
                    });
                },
            },
        }
    );

    const {
        data: { user },
    } = await supabase.auth.getUser();

    const url = request.nextUrl.clone();
    const pathname = url.pathname;

    const protectedRoutes = [
        '/dashboard', '/profile', '/feedback', '/notifications', '/settings',
        '/history', '/template-editor', '/batch-upload', '/generate'
    ];

    const isProtected = protectedRoutes.some(route => pathname.startsWith(route));
    const isAdminRoute = pathname.startsWith('/admin-dashboard');

    if (!user) {
        // Not logged in
        if (isProtected || isAdminRoute) {
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
