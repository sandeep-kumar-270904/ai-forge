"use client";

import { Handle, Position, NodeProps } from "reactflow";
import { MessageSquare } from "lucide-react";

export function LLMNode({ data, isConnectable }: NodeProps) {
  return (
    <div className="bg-slate-900 border border-slate-700 rounded-lg p-4 shadow-xl min-w-[250px]">
      <Handle
        type="target"
        position={Position.Top}
        isConnectable={isConnectable}
        className="w-3 h-3 bg-blue-500"
      />
      
      <div className="flex items-center gap-2 mb-3 border-b border-slate-700 pb-2">
        <MessageSquare className="w-5 h-5 text-blue-400" />
        <span className="font-semibold text-slate-200">LLM Generation</span>
      </div>

      <div className="flex flex-col gap-2">
        <label className="text-xs text-slate-400 font-medium">System Prompt</label>
        <textarea 
          className="bg-slate-800 text-sm text-slate-200 p-2 rounded border border-slate-700 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none resize-none"
          rows={3}
          defaultValue={data.prompt || "You are a helpful assistant..."}
          onChange={(e) => {
            if(data.onChange) data.onChange(e.target.value);
          }}
        />
      </div>

      <Handle
        type="source"
        position={Position.Bottom}
        isConnectable={isConnectable}
        className="w-3 h-3 bg-blue-500"
      />
    </div>
  );
}
