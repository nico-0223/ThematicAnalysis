import * as React from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { codebooksApi } from "@/api/codebooks";
import { Button } from "@/components/ui/Button";
import { Label } from "@/components/ui/Form";

export function CodebookUpload() {
  const [file, setFile] = React.useState<File | null>(null);
  const [validation, setValidation] = React.useState<string | null>(null);
  const qc = useQueryClient();

  const validate = useMutation({
    mutationFn: (f: File) => codebooksApi.validate(f),
    onSuccess: (r) => setValidation(r.valid ? "Valid YAML codebook" : `Invalid: ${(r.errors || []).join(", ")}`),
    onError: (e: Error) => setValidation(e.message),
  });
  const upload = useMutation({
    mutationFn: (f: File) => codebooksApi.upload(f),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["codebooks"] }),
  });

  return (
    <div className="rounded-lg border border-border bg-card p-4 space-y-3">
      <div>
        <Label htmlFor="codebook-file">YAML codebook</Label>
        <input
          id="codebook-file"
          type="file"
          accept=".yaml,.yml,application/x-yaml,text/yaml"
          onChange={(e) => {
            setFile(e.target.files?.[0] ?? null);
            setValidation(null);
          }}
          className="mt-1 block w-full text-xs"
        />
      </div>
      <div className="flex gap-2">
        <Button size="sm" variant="outline" disabled={!file || validate.isPending} onClick={() => file && validate.mutate(file)}>
          Validate
        </Button>
        <Button size="sm" disabled={!file || upload.isPending} onClick={() => file && upload.mutate(file)}>
          {upload.isPending ? "Uploading…" : "Upload"}
        </Button>
      </div>
      {validation && <p className="text-xs text-muted-foreground">{validation}</p>}
      {upload.isError && <p className="text-xs text-destructive">{(upload.error as Error).message}</p>}
      {upload.isSuccess && <p className="text-xs text-emerald-700">Uploaded codebook {upload.data.name} v{upload.data.version}.</p>}
    </div>
  );
}
