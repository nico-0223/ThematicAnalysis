import * as React from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { conversationsApi } from "@/api/conversations";
import { Button } from "@/components/ui/Button";
import { Label } from "@/components/ui/Form";

export function ConversationUpload() {
  const [file, setFile] = React.useState<File | null>(null);
  const qc = useQueryClient();
  const upload = useMutation({
    mutationFn: (f: File) => conversationsApi.upload(f),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["conversations"] }),
  });

  return (
    <div className="rounded-lg border border-border bg-card p-4 space-y-3">
      <div>
        <Label htmlFor="conv-file">Conversation file (CSV, JSON, JSONL, or TXT)</Label>
        <input
          id="conv-file"
          type="file"
          accept=".csv,.json,.jsonl,.txt"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          className="mt-1 block w-full text-xs"
        />
      </div>
      <div className="text-xs text-muted-foreground">
        Accepted: <code>.csv</code>, <code>.json</code>, <code>.jsonl</code>, <code>.txt</code>
      </div>
      {file && (
        <div className="text-xs text-muted-foreground">
          {file.name} &middot; {(file.size / 1024).toFixed(1)} KB
        </div>
      )}
      <Button size="sm" disabled={!file || upload.isPending} onClick={() => file && upload.mutate(file)}>
        {upload.isPending ? "Uploading…" : "Upload"}
      </Button>
      {upload.isError && <p className="text-xs text-destructive">{(upload.error as Error).message}</p>}
      {upload.isSuccess && (
        <p className="text-xs text-emerald-700">Imported {upload.data.imported} conversation(s).</p>
      )}
    </div>
  );
}
