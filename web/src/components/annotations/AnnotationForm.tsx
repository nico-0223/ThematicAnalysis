import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Annotation } from "@/types/annotation";
import { CodebookSummary } from "@/types/codebook";
import { Button } from "@/components/ui/Button";
import { Input, Label, Textarea } from "@/components/ui/Form";
import { CodeSelector } from "./CodeSelector";

const schema = z.object({
  segment_id: z.string().min(1, "segment id required"),
  code_id: z.string().min(1, "code required"),
  confidence: z.coerce.number().min(0).max(1).optional(),
  rationale: z.string().optional(),
  evidence: z.string().optional(),
  decision_note: z.string().optional(),
});
type FormValues = z.infer<typeof schema>;

interface Props {
  codebooks: CodebookSummary[];
  onSubmit: (body: Partial<Annotation>) => void;
  submitting?: boolean;
}

export function AnnotationForm({ codebooks: _codebooks, onSubmit, submitting }: Props) {
  const { register, handleSubmit, setValue, watch, formState: { errors } } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { segment_id: "", code_id: "" },
  });

  const submit = handleSubmit((v) =>
    onSubmit({ ...v, source: "human" as const }),
  );

  return (
    <form onSubmit={submit} className="grid gap-3 md:grid-cols-2">
      <div>
        <Label>Segment ID</Label>
        <Input {...register("segment_id")} />
        {errors.segment_id && <p className="text-xs text-destructive mt-1">{errors.segment_id.message}</p>}
      </div>
      <div>
        <Label>Code</Label>
        <CodeSelector value={watch("code_id")} onChange={(v) => setValue("code_id", v, { shouldValidate: true })} />
        {errors.code_id && <p className="text-xs text-destructive mt-1">{errors.code_id.message}</p>}
      </div>
      <div>
        <Label>Confidence (0–1)</Label>
        <Input type="number" step="0.01" min={0} max={1} {...register("confidence")} />
      </div>
      <div className="md:col-span-2">
        <Label>Evidence</Label>
        <Textarea rows={2} {...register("evidence")} />
      </div>
      <div className="md:col-span-2">
        <Label>Rationale</Label>
        <Textarea rows={2} {...register("rationale")} />
      </div>
      <div className="md:col-span-2">
        <Label>Coding-decision note</Label>
        <Textarea rows={2} {...register("decision_note")} />
      </div>
      <div className="md:col-span-2">
        <Button type="submit" size="sm" disabled={submitting}>
          {submitting ? "Saving…" : "Save annotation"}
        </Button>
      </div>
    </form>
  );
}
