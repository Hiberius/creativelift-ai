import { BarChart3 } from "lucide-react";

export function Logo() {
  return (
    <div className="flex items-center gap-3">
      <div className="grid h-9 w-9 place-items-center rounded-md border border-cyan/40 bg-cyan/10 text-cyan shadow-glow">
        <BarChart3 className="h-5 w-5" />
      </div>
      <span className="text-xl font-semibold tracking-normal text-white">CreativeLift AI</span>
    </div>
  );
}
