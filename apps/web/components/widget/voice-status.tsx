import { Mic, PhoneCall, Radio } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export function VoiceStatus({
  enabled,
  connected,
  onToggle,
}: {
  enabled: boolean;
  connected: boolean;
  onToggle: () => void;
}) {
  return (
    <Card className="space-y-4 p-4">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-accent/20 text-accent2">
            <Mic className="h-5 w-5" />
          </div>
          <div>
            <div className="text-sm font-medium text-white">OmniNew voice</div>
            <div className="text-xs text-slate-400">Website voice + AI telephony ready</div>
          </div>
        </div>
        <Badge className={connected ? "bg-green-500/15 text-green-200" : "bg-white/10 text-slate-200"}>
          <Radio className="mr-1 h-3.5 w-3.5" />
          {connected ? "connected" : enabled ? "ready" : "disabled"}
        </Badge>
      </div>
      <div className="flex flex-wrap gap-3">
        <Button variant={enabled ? "primary" : "outline"} onClick={onToggle}>
          {enabled ? "Disable voice" : "Enable voice"}
        </Button>
        <Button variant="secondary">
          <PhoneCall className="mr-2 h-4 w-4" />
          AI telephony later
        </Button>
      </div>
    </Card>
  );
}
