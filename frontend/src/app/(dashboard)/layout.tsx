import React from 'react';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex bg-zinc-950 text-zinc-50">
      <aside className="w-64 border-r border-zinc-800 p-6 hidden md:block">
        <h2 className="text-xl font-bold mb-6 tracking-tight">AIForge</h2>
        <nav className="space-y-2">
          <a href="/dashboard" className="block p-2 bg-zinc-900 rounded-md text-sm font-medium">Dashboard</a>
          <a href="/agents" className="block p-2 text-zinc-400 hover:text-zinc-50 text-sm font-medium">Agents</a>
          <a href="/knowledge" className="block p-2 text-zinc-400 hover:text-zinc-50 text-sm font-medium">Knowledge Base</a>
          <a href="/workflows" className="block p-2 text-zinc-400 hover:text-zinc-50 text-sm font-medium">Workflows</a>
        </nav>
      </aside>
      <main className="flex-1 p-8">
        {children}
      </main>
    </div>
  );
}
