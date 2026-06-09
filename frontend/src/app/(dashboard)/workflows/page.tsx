export default function WorkflowsPage() {
  return (
    <div className="h-[calc(100vh-6rem)] flex flex-col">
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">Workflow Builder</h1>
        <button className="bg-zinc-100 text-zinc-950 px-4 py-2 rounded-md hover:bg-zinc-300 font-medium">
          New Workflow
        </button>
      </div>
      <div className="flex-1 bg-zinc-900 border border-zinc-800 rounded-xl flex items-center justify-center text-zinc-500">
        <div className="text-center">
          <p className="text-lg mb-2 text-zinc-300 font-medium">Visual Workflow Canvas</p>
          <p className="text-sm">Drag and drop nodes to build AI agents and data pipelines.</p>
          <p className="text-xs mt-4 opacity-50">(React Flow integration pending)</p>
        </div>
      </div>
    </div>
  );
}
