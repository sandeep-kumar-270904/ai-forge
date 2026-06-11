import { WorkflowCanvas } from '@/components/workflow/Canvas';

export default function WorkflowBuilderPage() {
  return (
    <div className="flex flex-col h-screen bg-slate-950 text-slate-200">
      <header className="flex-none px-6 py-4 border-b border-slate-800 bg-slate-950 flex justify-between items-center">
        <div>
          <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
            AIForge Workflow Builder
          </h1>
          <p className="text-sm text-slate-400">Design agentic behavior using the visual DAG canvas</p>
        </div>
      </header>
      
      <main className="flex-1 p-6">
        <WorkflowCanvas />
      </main>
    </div>
  );
}
