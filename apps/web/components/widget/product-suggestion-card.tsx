import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import type { ProductSuggestion } from "@/lib/types";

export function ProductSuggestionCard({ suggestion }: { suggestion: ProductSuggestion }) {
  return (
    <Card className="space-y-3 p-4">
      <div className="flex items-center justify-between gap-3">
        <div className="text-sm font-medium text-white">{suggestion.title}</div>
        {suggestion.price ? <Badge>{suggestion.price}</Badge> : null}
      </div>
      {suggestion.reason ? <p className="text-xs leading-5 text-slate-300">{suggestion.reason}</p> : null}
      {suggestion.handle ? <div className="text-xs text-slate-500">/{suggestion.handle}</div> : null}
    </Card>
  );
}
