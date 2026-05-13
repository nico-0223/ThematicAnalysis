import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { codebooksApi } from "@/api/codebooks";
import { PageHeader } from "@/components/common/PageHeader";
import { CodebookUpload } from "@/components/codebook/CodebookUpload";
import { CodebookSummary } from "@/components/codebook/CodebookSummary";
import { ThemeEditor } from "@/components/codebook/ThemeEditor";
import { LoadingState } from "@/components/common/LoadingState";
import { ErrorState } from "@/components/common/ErrorState";
import { EmptyState } from "@/components/common/EmptyState";

export function CodebookPage() {
  const { id } = useParams();
  const list = useQuery({ queryKey: ["codebooks"], queryFn: () => codebooksApi.list() });
  const activeId = id ?? list.data?.[0]?.id;
  const detail = useQuery({
    queryKey: ["codebook", activeId],
    queryFn: () => codebooksApi.get(activeId!),
    enabled: !!activeId,
  });

  return (
    <>
      <PageHeader
        title="Codebooks"
        description="Upload, validate, and edit YAML codebooks. All edits are saved through backend API calls."
      />
      <div className="grid gap-4 lg:grid-cols-3">
        <div className="space-y-3">
          <CodebookUpload />
          <div className="rounded-lg border border-border bg-card p-3">
            <p className="text-xs font-medium mb-2">Available codebooks</p>
            {list.isLoading && <LoadingState />}
            {list.isError && <ErrorState message={(list.error as Error).message} onRetry={() => list.refetch()} />}
            {list.data && list.data.length === 0 && <EmptyState title="None uploaded yet" />}
            <ul className="space-y-1 text-xs">
              {list.data?.map((c) => (
                <li key={c.id}>
                  <a href={`/codebooks/${c.id}`} className="hover:underline">{c.name} v{c.version}</a>
                </li>
              ))}
            </ul>
          </div>
        </div>
        <div className="lg:col-span-2 space-y-3">
          {detail.isLoading && <LoadingState />}
          {detail.isError && <ErrorState message={(detail.error as Error).message} onRetry={() => detail.refetch()} />}
          {detail.data && (
            <>
              <CodebookSummary codebook={detail.data} />
              <ThemeEditor themes={detail.data.themes ?? []} />
              {!!detail.data.memo_prompts?.length && (
                <div className="rounded-lg border border-border bg-card p-4">
                  <p className="text-sm font-semibold mb-2">Memo prompts</p>
                  <ul className="list-disc pl-5 text-xs">
                    {detail.data.memo_prompts.map((p, i) => <li key={i}>{p}</li>)}
                  </ul>
                </div>
              )}
            </>
          )}
          {!detail.data && !detail.isLoading && (
            <EmptyState title="Select a codebook to view details" />
          )}
        </div>
      </div>
    </>
  );
}
