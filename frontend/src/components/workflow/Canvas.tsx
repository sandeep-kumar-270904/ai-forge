"use client";

import { useState, useCallback, useMemo } from 'react';
import ReactFlow, { 
  Background, 
  Controls, 
  MiniMap,
  applyNodeChanges,
  applyEdgeChanges,
  addEdge,
  Node,
  Edge,
  NodeChange,
  EdgeChange,
  Connection,
  Panel
} from 'reactflow';
import 'reactflow/dist/style.css';
import { LLMNode } from './nodes/LLMNode';
import { ToolNode } from './nodes/ToolNode';
import { Save, Play } from 'lucide-react';

const initialNodes: Node[] = [
  {
    id: '__start__',
    type: 'input',
    position: { x: 250, y: 50 },
    data: { label: 'Start (User Input)' },
    className: 'bg-green-900 border-green-500 text-white font-bold',
  },
  {
    id: 'node_1',
    type: 'llm',
    position: { x: 250, y: 150 },
    data: { prompt: 'You are a helpful assistant.' },
  },
  {
    id: '__end__',
    type: 'output',
    position: { x: 250, y: 350 },
    data: { label: 'End (Output)' },
    className: 'bg-red-900 border-red-500 text-white font-bold',
  }
];

const initialEdges: Edge[] = [
  { id: 'e1', source: '__start__', target: 'node_1', animated: true },
  { id: 'e2', source: 'node_1', target: '__end__', animated: true }
];

export function WorkflowCanvas() {
  const [nodes, setNodes] = useState<Node[]>(initialNodes);
  const [edges, setEdges] = useState<Edge[]>(initialEdges);
  const [isSaving, setIsSaving] = useState(false);

  const nodeTypes = useMemo(() => ({ llm: LLMNode, tool: ToolNode }), []);

  const onNodesChange = useCallback(
    (changes: NodeChange[]) => setNodes((nds) => applyNodeChanges(changes, nds)),
    []
  );

  const onEdgesChange = useCallback(
    (changes: EdgeChange[]) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    []
  );

  const onConnect = useCallback(
    (connection: Connection) => setEdges((eds) => addEdge({ ...connection, animated: true }, eds)),
    []
  );

  const addLLMNode = () => {
    const newNode: Node = {
      id: `llm_${Math.random().toString(36).substr(2, 9)}`,
      type: 'llm',
      position: { x: 100, y: 100 },
      data: { prompt: 'New LLM Prompt' }
    };
    setNodes((nds) => [...nds, newNode]);
  };

  const addToolNode = () => {
    const newNode: Node = {
      id: `tool_${Math.random().toString(36).substr(2, 9)}`,
      type: 'tool',
      position: { x: 300, y: 100 },
      data: { toolName: 'search_web' }
    };
    setNodes((nds) => [...nds, newNode]);
  };

  const handleSave = async () => {
    setIsSaving(true);
    // Transform React Flow state to our Backend JSON Schema
    const payload = {
      name: "Visual Workflow " + new Date().toLocaleTimeString(),
      description: "Generated from React Flow",
      nodes: nodes.filter(n => n.id !== '__start__' && n.id !== '__end__').map(n => ({
        id: n.id,
        node_type: n.type,
        config: n.data
      })),
      edges: edges.map(e => ({
        id: e.id,
        source_node_id: e.source,
        target_node_id: e.target,
        condition_type: "always"
      }))
    };

    try {
      const res = await fetch('http://localhost:8000/api/v1/workflows/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer placeholder_token' // Would use actual auth here
        },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        alert("Workflow Saved to PostgreSQL!");
      } else {
        alert("Failed to save workflow");
      }
    } catch (err) {
      console.error(err);
      alert("Error saving workflow. Is the backend running?");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="w-full h-full min-h-[700px] border border-slate-800 rounded-xl overflow-hidden bg-slate-950">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        fitView
        className="dark"
      >
        <Background color="#334155" gap={16} />
        <Controls className="bg-slate-800 border-slate-700 fill-slate-300" />
        <MiniMap 
          nodeColor={(node) => {
            if (node.type === 'llm') return '#3b82f6';
            if (node.type === 'tool') return '#f97316';
            return '#1e293b';
          }}
          className="bg-slate-900 border-slate-700"
        />
        
        <Panel position="top-left" className="flex gap-2 bg-slate-900/80 p-2 rounded-lg backdrop-blur-sm border border-slate-800">
          <button 
            onClick={addLLMNode}
            className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded transition-colors"
          >
            + Add LLM
          </button>
          <button 
            onClick={addToolNode}
            className="px-3 py-1.5 bg-orange-600 hover:bg-orange-700 text-white text-sm font-medium rounded transition-colors"
          >
            + Add Tool
          </button>
        </Panel>

        <Panel position="top-right" className="flex gap-2">
          <button 
            onClick={handleSave}
            disabled={isSaving}
            className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white text-sm font-medium rounded-lg shadow-lg transition-colors"
          >
            <Save className="w-4 h-4" />
            {isSaving ? 'Saving...' : 'Deploy to Engine'}
          </button>
          <button 
            className="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white text-sm font-medium rounded-lg shadow-lg transition-colors"
          >
            <Play className="w-4 h-4" />
            Test Run
          </button>
        </Panel>
      </ReactFlow>
    </div>
  );
}
