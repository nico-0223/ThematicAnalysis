import { PageHeader } from "@/components/common/PageHeader";
import { ExportPanel } from "@/components/exports/ExportPanel";

export function ExportPage() {
  return (
    <>
      <PageHeader
        title="Exports"
        description="Generate methodologically transparent reports for an analysis run."
      />
      <ExportPanel />
    </>
  );
}
