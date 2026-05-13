import { PageHeader } from "@/components/common/PageHeader";
import { ConversationUpload } from "@/components/conversations/ConversationUpload";

export function ConversationImportPage() {
  return (
    <>
      <PageHeader
        title="Import conversations"
        description="Upload conversation data. Parsing and validation are performed by the backend."
      />
      <div className="max-w-xl">
        <ConversationUpload />
      </div>
    </>
  );
}
