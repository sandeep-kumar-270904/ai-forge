'use client';
import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export default function KnowledgeBasePage() {
  const [file, setFile] = useState<File | null>(null);

  const handleUpload = (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    alert(`Uploading ${file.name} to vector store...`);
    // API integration logic goes here
  };

  return (
    <div>
      <h1 className="text-3xl font-bold tracking-tight mb-8">Knowledge Base</h1>
      <Card className="bg-zinc-900 border-zinc-800 text-zinc-100 max-w-xl">
        <CardHeader>
          <CardTitle>Upload Document</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleUpload} className="space-y-4">
            <div>
              <Input 
                type="file" 
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="bg-zinc-950 border-zinc-800 text-zinc-100 cursor-pointer"
              />
            </div>
            <Button type="submit" className="bg-zinc-100 text-zinc-950 hover:bg-zinc-300" disabled={!file}>
              Process & Embed
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
