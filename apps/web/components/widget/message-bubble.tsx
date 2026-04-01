import { cn } from "@/lib/utils";

export function MessageBubble({ role, content }: { role: "user" | "assistant"; content: string }) {
  return (
    <div className={cn("flex", role === "user" ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          "max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-6",
          role === "user"
            ? "rounded-br-md bg-accent text-white"
            : "rounded-bl-md border border-white/10 bg-white/10 text-slate-100",
        )}
      >
        {content}
      </div>
    </div>
  );
}
