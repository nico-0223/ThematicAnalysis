import { Link } from "react-router-dom";
import { Conversation } from "@/types/conversation";
import { DataTable } from "@/components/common/DataTable";
import { EmptyState } from "@/components/common/EmptyState";

export function ConversationTable({ rows }: { rows: Conversation[] }) {
  return (
    <DataTable
      rows={rows}
      rowKey={(r) => r.id}
      empty={<EmptyState title="No conversations imported yet" description="Use Import Conversations to upload data." />}
      columns={[
        {
          key: "title",
          header: "Title",
          cell: (r) => (
            <Link to={`/conversations/${r.id}`} className="font-medium hover:underline">
              {r.title || r.id}
            </Link>
          ),
        },
        { key: "speakers", header: "Speakers", cell: (r) => r.speakers?.join(", ") || "—" },
        { key: "turns", header: "Turns", cell: (r) => r.turns_count ?? "—" },
        { key: "segments", header: "Segments", cell: (r) => r.segments_count ?? "—" },
        { key: "imported", header: "Imported", cell: (r) => r.imported_at ?? "—" },
      ]}
    />
  );
}
