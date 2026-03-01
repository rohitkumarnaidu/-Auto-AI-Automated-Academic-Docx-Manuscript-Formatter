import { NextResponse } from 'next/server';
import { createServerClient } from '@supabase/ssr';

const isSafeInternalPath = (value) => typeof value === 'string' && value.startsWith('/') && !value.startsWith('//');

export async function proxy(request) {
    let supabaseResponse = NextResponse.next({
        request: {
            headers: request.headers,
        },
    });

    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

    // Gracefully handle missing envs (allow pass-through so local UI testing doesn't break)
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
        if (pathname === '/login' || pathname === '/signup') {
            const requestedNext = url.searchParams.get('next');
            const nextPath = isSafeInternalPath(requestedNext) ? requestedNext : '/dashboard';
            return NextResponse.redirect(new URL(nextPath, request.url), 307);
        }

        if (isAdminRoute) {
            // Verify admin role via user_metadata or custom claim
            // Based on previous implementation, let's assume user.user_metadata.role === 'admin'
            // or we just check if it's admin (we fall back to standard if not explicitly 'admin')
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
