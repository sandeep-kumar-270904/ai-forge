import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('token')?.value;

  if (!token && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  if (!token && request.nextUrl.pathname.startsWith('/agents')) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  if (!token && request.nextUrl.pathname.startsWith('/knowledge')) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  if (!token && request.nextUrl.pathname.startsWith('/workflows')) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  if (token && request.nextUrl.pathname === '/login') {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/agents/:path*', '/knowledge/:path*', '/workflows/:path*', '/login'],
};
