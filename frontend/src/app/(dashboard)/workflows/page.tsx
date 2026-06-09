'use client';

import React, { useCallback } from 'react';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Edge
} from 'reactflow';
import 'reactflow/dist/style.css';

const initialNodes = [
  { id: '1', position: { x: 250, y: 5 }, data: { label: 'Trigger Node' }, type: 'input' },
  { id: '2', position: { x: 100, y: 100 }, data: { label: 'LLM Processor' } },
  { id: '3', position: { x: 400, y: 100 }, data: { label: 'API Fetcher' } },
  { id: '4', position: { x: 250, y: 200 }, data: { label: 'Output Format' }, type: 'output' },
];

const initialEdges = [
  { id: 'e1-2', source: '1', target: '2' },
  { id: 'e1-3', source: '1', target: '3' },
  { id: 'e2-4', source: '2', target: '4' },
  { id: 'e3-4', source: '3', target: '4' },
];

export default function WorkflowsPage() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback((params: Edge | Connection) => setEdges((eds) => addEdge(params, eds)), [setEdges]);

  return (
    <div className="h-[calc(100vh-6rem)] flex flex-col">
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">Workflow Builder</h1>
        <button className="bg-zinc-100 text-zinc-950 px-4 py-2 rounded-md hover:bg-zinc-300 font-medium">
          Deploy Workflow
        </button>
      </div>
      <div className="flex-1 bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          fitView
          className="bg-zinc-950"
        >
          <Controls className="bg-zinc-800 text-zinc-100 border-zinc-700 fill-zinc-100" />
          <MiniMap nodeColor="#3f3f46" maskColor="rgba(0,0,0,0.5)" style={{ backgroundColor: '#18181b' }} />
          <Background color="#3f3f46" gap={16} />
        </ReactFlow>
      </div>
    </div>
  );
}
