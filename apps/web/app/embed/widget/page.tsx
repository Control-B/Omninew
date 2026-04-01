import { ChatWidget } from "@/components/widget/chat-widget";

export const dynamic = "force-static";

export default function EmbedWidgetPage() {
  return (
    <main className="min-h-screen bg-transparent">
      <ChatWidget />
    </main>
  );
}
