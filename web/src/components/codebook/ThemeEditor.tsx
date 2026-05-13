import { Theme } from "@/types/codebook";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { CodeEditor } from "./CodeEditor";

interface Props {
  themes: Theme[];
  onChange?: (themes: Theme[]) => void;
}

export function ThemeEditor({ themes, onChange: _onChange }: Props) {
  if (!themes.length) return <p className="text-xs text-muted-foreground">No themes defined in this codebook.</p>;
  return (
    <div className="space-y-3">
      {themes.map((t) => (
        <Card key={t.id}>
          <CardHeader>
            <CardTitle>{t.name}</CardTitle>
            {t.description && <p className="text-xs text-muted-foreground">{t.description}</p>}
          </CardHeader>
          <CardContent className="space-y-2">
            {(t.codes ?? []).map((c) => (
              <CodeEditor key={c.id} code={c} />
            ))}
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
