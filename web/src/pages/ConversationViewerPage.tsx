import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { conversationsApi } from "@/api/conversations";
import { PageHeader } from "@/components/common/PageHeader";
import { ConversationTable } from "@/components/conversations/ConversationTable";
import { ConversationViewer } from "@/components/conversations/ConversationViewer";
import { LoadingState } from "@/components/common/LoadingState";
import { ErrorState } from "@/components/common/ErrorState";

export function ConversationViewerPage() {
  const { id } = useParams();
  const list = useQuery({ queryKey: ["conversations"], queryFn: () => conversationsApi.list(), enabled: !id });

  if (id) {
    return (
      <>
        <PageHeader title={`Conversation ${id}`} description="Original turns alongside segmented text." />
        <ConversationViewer conversationId={id} />
      </>
    );
  }

  return (
    <>
      <PageHeader title="Conversations" description="Browse imported conversations." />
      {list.isLoading && <LoadingState />}
      {list.isError && <ErrorState message={(list.error as Error).message} onRetry={() => list.refetch()} />}
      {list.data && <ConversationTable rows={list.data} />}
    </>
  );
}
