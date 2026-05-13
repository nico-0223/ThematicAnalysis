import { Memo } from "@/types/memo";
import { Input, Label, Select, Textarea } from "@/components/ui/Form";
import { Button } from "@/components/ui/Button";

interface Props {
  memo: Partial<Memo>;
  onChange: (m: Partial<Memo>) => void;
  onSave: () => void;
  onCancel: () => void;
  saving?: boolean;
}

export function MemoEditor({ memo, onChange, onSave, onCancel, saving }: Props) {
  return (
    <div className="rounded-lg border border-border bg-card p-3 space-y-2">
      <div>
        <Label>Title</Label>
        <Input value={memo.title ?? ""} onChange={(e) => onChange({ ...memo, title: e.target.value })} />
      </div>
      <div>
        <Label>Type</Label>
        <Select value={memo.type ?? "analytic"} onChange={(e) => onChange({ ...memo, type: e.target.value as Memo["type"] })}>
          <option value="analytic">Analytic</option>
          <option value="reflexive">Reflexive</option>
          <option value="method">Method</option>
          <option value="phase">Phase</option>
          <option value="general">General</option>
        </Select>
      </div>
      <div>
        <Label>Phase (optional)</Label>
        <Select
          value={memo.phase_number?.toString() ?? ""}
          onChange={(e) => onChange({ ...memo, phase_number: e.target.value ? Number(e.target.value) : undefined })}
        >
          <option value="">—</option>
          {[1,2,3,4,5,6].map((n) => <option key={n} value={n}>Phase {n}</option>)}
        </Select>
      </div>
      <div>
        <Label>Body</Label>
        <Textarea rows={6} value={memo.body ?? ""} onChange={(e) => onChange({ ...memo, body: e.target.value })} />
      </div>
      <div className="flex gap-2">
        <Button size="sm" onClick={onSave} disabled={saving}>{saving ? "Saving…" : "Save"}</Button>
        <Button size="sm" variant="ghost" onClick={onCancel}>Cancel</Button>
      </div>
    </div>
  );
}
