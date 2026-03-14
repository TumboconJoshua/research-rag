import { ReferenceStatus } from "@/lib/api";
import { CheckCircle2, AlertTriangle, XCircle, HelpCircle } from "lucide-react";
import { cn } from "@/lib/utils";

interface StatusBadgeProps {
  status: ReferenceStatus;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const badgeColors = {
    VALID: {
      bg: "bg-[rgba(34,211,165,0.15)]",
      text: "text-[#22d3a5]",
      border: "border-[rgba(34,211,165,0.3)]",
      icon: CheckCircle2,
      label: "Valid",
    },
    PARTIALLY_MATCHED: {
      bg: "bg-[rgba(245,158,11,0.15)]",
      text: "text-[#f59e0b]",
      border: "border-[rgba(245,158,11,0.3)]",
      icon: AlertTriangle,
      label: "Partial",
    },
    LIKELY_FAKE: {
      bg: "bg-[rgba(244,63,94,0.15)]",
      text: "text-[#f43f5e]",
      border: "border-[rgba(244,63,94,0.3)]",
      icon: XCircle,
      label: "Fake",
    },
    UNVERIFIED: {
      bg: "bg-[rgba(148,163,184,0.1)]",
      text: "text-gray-400",
      border: "border-gray-800",
      icon: HelpCircle,
      label: "Unverified",
    },
  };

  const config = badgeColors[status] || badgeColors.UNVERIFIED;
  const Icon = config.icon;

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold uppercase tracking-wider border",
        config.bg,
        config.text,
        config.border
      )}
    >
      <Icon size={14} className={config.text} />
      {config.label}
    </span>
  );
}
