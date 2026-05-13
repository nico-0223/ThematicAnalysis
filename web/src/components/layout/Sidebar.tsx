import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  BookOpen,
  Upload,
  MessageSquare,
  Filter,
  PlayCircle,
  ListChecks,
  Tag,
  Layers,
  NotebookPen,
  History,
  Scale,
  Download,
  Settings,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { env } from "@/lib/env";

const items = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/codebooks", label: "Codebooks", icon: BookOpen },
  { to: "/import", label: "Import Conversations", icon: Upload },
  { to: "/conversations", label: "Conversations", icon: MessageSquare },
  { to: "/preprocessing", label: "Preprocessing", icon: Filter },
  { to: "/runs", label: "Analysis Runs", icon: PlayCircle },
  { to: "/workflow", label: "Braun & Clarke Workflow", icon: ListChecks },
  { to: "/annotation", label: "Annotation Workspace", icon: Tag },
  { to: "/themes", label: "Theme Review", icon: Layers },
  { to: "/memos", label: "Memos & Reflexive Journal", icon: NotebookPen },
  { to: "/audit", label: "Audit Trail", icon: History },
  { to: "/reliability", label: "Reliability & Adjudication", icon: Scale },
  { to: "/exports", label: "Exports", icon: Download },
  { to: "/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  return (
    <aside className="w-64 shrink-0 border-r border-border bg-card flex flex-col">
      <div className="p-4 border-b border-border">
        <p className="text-sm font-semibold leading-tight">{env.appName}</p>
        <p className="text-xs text-muted-foreground mt-0.5">Research workflow interface</p>
      </div>
      <nav className="flex-1 overflow-y-auto p-2">
        {items.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-2 rounded-md px-2.5 py-2 text-xs font-medium transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-foreground",
              )
            }
          >
            <Icon className="h-3.5 w-3.5 shrink-0" />
            <span className="truncate">{label}</span>
          </NavLink>
        ))}
      </nav>
      <div className="p-3 border-t border-border text-[10px] text-muted-foreground">
        Software supports Braun &amp; Clarke workflow.
        <br />
        Researcher provides interpretation.
      </div>
    </aside>
  );
}
