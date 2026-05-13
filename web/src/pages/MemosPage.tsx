import { PageHeader } from "@/components/common/PageHeader";
import { MemoPanel } from "@/components/memos/MemoPanel";

export function MemosPage() {
  return (
    <>
      <PageHeader
        title="Memos & reflexive journal"
        description="Capture analytic, methodological, and reflexive notes throughout the workflow."
      />
      <MemoPanel />
    </>
  );
}
