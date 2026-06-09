import React from 'react';

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-zinc-950 text-zinc-50">
      <div className="w-full max-w-md p-8">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold tracking-tighter">AIForge</h1>
          <p className="text-zinc-400 mt-2">Sign in to your account</p>
        </div>
        {children}
      </div>
    </div>
  );
}
