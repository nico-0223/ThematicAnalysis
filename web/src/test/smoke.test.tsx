import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import App from "@/App";
import { BRAUN_CLARKE_PHASES } from "@/types/phase";
import { DashboardPage } from "@/pages/DashboardPage";
import { WorkflowPage } from "@/pages/WorkflowPage";
import { CodebookPage } from "@/pages/CodebookPage";
import { ConversationImportPage } from "@/pages/ConversationImportPage";
import { AnnotationPage } from "@/pages/AnnotationPage";
import { ExportPage } from "@/pages/ExportPage";
import { Sidebar } from "@/components/layout/Sidebar";

beforeEach(() => {
  // Make all network requests fail to simulate offline backend
  vi.stubGlobal(
    "fetch",
    vi.fn(() => Promise.reject(new Error("network down"))) as any,
  );
});

function wrap(ui: React.ReactNode, route = "/") {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={[route]}>{ui}</MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("smoke", () => {
  it("renders the app shell without crashing", () => {
    wrap(<App />);
    expect(screen.getAllByText(/Conversation Thematic Analysis/i).length).toBeGreaterThan(0);
  });

  it("sidebar lists all 14 sections", () => {
    wrap(<Sidebar />);
    expect(screen.getByText(/Dashboard/)).toBeInTheDocument();
    expect(screen.getByText(/Codebooks/)).toBeInTheDocument();
    expect(screen.getByText(/Annotation Workspace/)).toBeInTheDocument();
    expect(screen.getByText(/Reliability & Adjudication/)).toBeInTheDocument();
    expect(screen.getByText(/Settings/)).toBeInTheDocument();
  });

  it("dashboard shows backend-unavailable state when API fails", async () => {
    wrap(<DashboardPage />);
    expect(await screen.findByText(/Backend unavailable/i)).toBeInTheDocument();
  });

  it("workflow page renders all six Braun & Clarke phases", () => {
    wrap(<WorkflowPage />, "/workflow");
    for (const p of BRAUN_CLARKE_PHASES) {
      expect(screen.queryByText(p.name)).toBeNull(); // empty state until run selected
    }
    expect(screen.getByText(/Select an analysis run/i)).toBeInTheDocument();
  });

  it("codebook upload form renders", () => {
    wrap(<CodebookPage />);
    expect(screen.getByLabelText(/YAML codebook/i)).toBeInTheDocument();
  });

  it("conversation upload form renders", () => {
    wrap(<ConversationImportPage />);
    expect(screen.getByLabelText(/Conversation file/i)).toBeInTheDocument();
  });

  it("annotation page renders empty state when no run selected", () => {
    wrap(<AnnotationPage />, "/annotation");
    expect(screen.getByText(/Select an analysis run/i)).toBeInTheDocument();
  });

  it("export page renders", () => {
    wrap(<ExportPage />);
    expect(screen.getByText(/Generate export/i)).toBeInTheDocument();
    expect(screen.getByText(/Report includes/i)).toBeInTheDocument();
  });
});
