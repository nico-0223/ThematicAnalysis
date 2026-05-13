import { Routes, Route } from "react-router-dom";
import { AppShell } from "@/components/layout/AppShell";
import { DashboardPage } from "@/pages/DashboardPage";
import { CodebookPage } from "@/pages/CodebookPage";
import { ConversationImportPage } from "@/pages/ConversationImportPage";
import { ConversationViewerPage } from "@/pages/ConversationViewerPage";
import { PreprocessingPage } from "@/pages/PreprocessingPage";
import { AnalysisRunsPage } from "@/pages/AnalysisRunsPage";
import { RunDetailPage } from "@/pages/RunDetailPage";
import { WorkflowPage } from "@/pages/WorkflowPage";
import { AnnotationPage } from "@/pages/AnnotationPage";
import { ThemeReviewPage } from "@/pages/ThemeReviewPage";
import { MemosPage } from "@/pages/MemosPage";
import { AuditTrailPage } from "@/pages/AuditTrailPage";
import { ReliabilityPage } from "@/pages/ReliabilityPage";
import { ExportPage } from "@/pages/ExportPage";
import { SettingsPage } from "@/pages/SettingsPage";
import { NotFoundPage } from "@/pages/NotFoundPage";

export default function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/codebooks" element={<CodebookPage />} />
        <Route path="/codebooks/:id" element={<CodebookPage />} />
        <Route path="/import" element={<ConversationImportPage />} />
        <Route path="/conversations" element={<ConversationViewerPage />} />
        <Route path="/conversations/:id" element={<ConversationViewerPage />} />
        <Route path="/preprocessing" element={<PreprocessingPage />} />
        <Route path="/runs" element={<AnalysisRunsPage />} />
        <Route path="/runs/:id" element={<RunDetailPage />} />
        <Route path="/workflow" element={<WorkflowPage />} />
        <Route path="/workflow/:runId" element={<WorkflowPage />} />
        <Route path="/annotation" element={<AnnotationPage />} />
        <Route path="/annotation/:runId" element={<AnnotationPage />} />
        <Route path="/themes" element={<ThemeReviewPage />} />
        <Route path="/themes/:runId" element={<ThemeReviewPage />} />
        <Route path="/memos" element={<MemosPage />} />
        <Route path="/audit" element={<AuditTrailPage />} />
        <Route path="/reliability" element={<ReliabilityPage />} />
        <Route path="/reliability/:runId" element={<ReliabilityPage />} />
        <Route path="/exports" element={<ExportPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </AppShell>
  );
}
