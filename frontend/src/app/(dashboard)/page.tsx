export default function DashboardPage() {
  return (
    <div>
      <h1 className="text-3xl font-bold tracking-tight mb-8">Dashboard</h1>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl">
          <h3 className="font-medium text-zinc-400">Total Agents</h3>
          <p className="text-3xl font-bold mt-2">0</p>
        </div>
        <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl">
          <h3 className="font-medium text-zinc-400">Knowledge Bases</h3>
          <p className="text-3xl font-bold mt-2">0</p>
        </div>
        <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl">
          <h3 className="font-medium text-zinc-400">Active Workflows</h3>
          <p className="text-3xl font-bold mt-2">0</p>
        </div>
        <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl">
          <h3 className="font-medium text-zinc-400">API Calls</h3>
          <p className="text-3xl font-bold mt-2">0</p>
        </div>
      </div>
    </div>
  );
}
