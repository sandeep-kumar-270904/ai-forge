'use client';

import { useState, useRef, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function AgentsChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const ws = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const workspaceId = 'default_workspace';

  useEffect(() => {
    const token = document.cookie.split('; ').find(row => row.startsWith('token='))?.split('=')[1] || localStorage.getItem('token');
    
    if (!token) {
        console.error("No authentication token found");
        return;
    }

    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.host}/api/chat/ws/${workspaceId}?token=${token}`;
    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => setIsConnected(true);
    ws.current.onclose = () => setIsConnected(false);

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'stream') {
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          if (last && last.role === 'assistant') {
            return [...prev.slice(0, -1), { ...last, content: last.content + data.content }];
          } else {
            return [...prev, { role: 'assistant', content: data.content }];
          }
        });
      }
    };

    return () => {
      ws.current?.close();
    };
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !ws.current || ws.current.readyState !== WebSocket.OPEN) return;

    setMessages((prev) => [...prev, { role: 'user', content: input }]);
    ws.current.send(JSON.stringify({ message: input }));
    setInput('');
  };

  return (
    <div className="h-[calc(100vh-6rem)] flex flex-col">
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight">Agent Chat</h1>
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
          <span className="text-sm text-zinc-400">{isConnected ? 'Connected' : 'Disconnected'}</span>
        </div>
      </div>

      <Card className="flex-1 flex flex-col bg-zinc-900 border-zinc-800 text-zinc-100 overflow-hidden">
        <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="h-full flex items-center justify-center text-zinc-500">
              Send a message to start chatting with the agent...
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] rounded-xl p-3 ${
                  msg.role === 'user' ? 'bg-zinc-100 text-zinc-950' : 'bg-zinc-800 text-zinc-100'
                }`}>
                  <p className="whitespace-pre-wrap text-sm">{msg.content}</p>
                </div>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </CardContent>

        <div className="p-4 border-t border-zinc-800 bg-zinc-950">
          <form onSubmit={sendMessage} className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              className="bg-zinc-900 border-zinc-800 focus-visible:ring-zinc-700 text-zinc-100"
              disabled={!isConnected}
            />
            <Button type="submit" disabled={!isConnected || !input.trim()} className="bg-zinc-100 text-zinc-950 hover:bg-zinc-300">
              Send
            </Button>
          </form>
        </div>
      </Card>
    </div>
  );
}
