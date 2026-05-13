import { Feature } from "@/types/codebook";

export function FeatureEditor({ features }: { features: Feature[] }) {
  return (
    <div className="mt-2">
      <p className="text-[10px] uppercase tracking-wide text-muted-foreground">Coding features</p>
      <ul className="mt-0.5 space-y-1 text-xs">
        {features.map((f, i) => (
          <li key={f.id ?? i} className="flex gap-2">
            <span className="font-medium">{f.name}</span>
            {f.type && <span className="text-muted-foreground">({f.type})</span>}
            {f.pattern && <code className="rounded bg-muted px-1">{f.pattern}</code>}
          </li>
        ))}
      </ul>
    </div>
  );
}
