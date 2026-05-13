import { Code } from "@/types/codebook";
import { FeatureEditor } from "./FeatureEditor";

export function CodeEditor({ code }: { code: Code }) {
  const sections: [string, string[] | undefined][] = [
    ["Indicators", code.indicators],
    ["Inclusion criteria", code.inclusion_criteria],
    ["Exclusion criteria", code.exclusion_criteria],
    ["Examples", code.examples],
    ["Counterexamples", code.counterexamples],
  ];
  return (
    <div className="rounded-md border border-border bg-background p-3">
      <p className="text-sm font-medium">{code.name}</p>
      {code.description && <p className="text-xs text-muted-foreground mt-0.5">{code.description}</p>}
      <div className="mt-2 grid gap-2 sm:grid-cols-2">
        {sections.map(([label, items]) => (
          <div key={label}>
            <p className="text-[10px] uppercase tracking-wide text-muted-foreground">{label}</p>
            {items?.length ? (
              <ul className="mt-0.5 list-disc pl-4 text-xs">
                {items.map((x, i) => <li key={i}>{x}</li>)}
              </ul>
            ) : (
              <p className="text-xs text-muted-foreground">—</p>
            )}
          </div>
        ))}
      </div>
      {!!code.features?.length && <FeatureEditor features={code.features} />}
      {!!code.subcodes?.length && (
        <div className="mt-2 space-y-2 border-l border-border pl-3">
          {code.subcodes.map((s) => <CodeEditor key={s.id} code={s} />)}
        </div>
      )}
    </div>
  );
}
