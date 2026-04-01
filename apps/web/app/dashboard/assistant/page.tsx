import { AssistantConfigForm } from "@/components/forms/assistant-config-form";

export default function AssistantPage() {
  return (
    <div className="space-y-6">
      <div>
        <div className="text-sm uppercase tracking-[0.2em] text-slate-400">Assistant config</div>
        <h1 className="mt-2 text-3xl font-semibold text-white">Tune the merchant assistant</h1>
        <p className="mt-2 max-w-3xl text-sm leading-7 text-slate-300">
          Configure the per-store assistant name, prompt, welcome message, voice mode, and the balance between conversion help and support clarity.
        </p>
      </div>
      <AssistantConfigForm />
    </div>
  );
}
