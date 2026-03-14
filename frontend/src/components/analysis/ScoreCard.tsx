import { cn, formatScore, scoreClass } from "@/lib/utils";
import { type LucideIcon } from "lucide-react";

interface ScoreCardProps {
  title: string;
  score: number;
  icon: LucideIcon;
  description: string;
}

export function ScoreCard({ title, score, icon: Icon, description }: ScoreCardProps) {
  const percentage = (score / 10) * 100;
  const colorClass = scoreClass(score);

  return (
    <div className="glass-card p-5 relative overflow-hidden group">
      {/* Background glow based on score */}
      <div
        className={cn(
          "absolute -top-12 -right-12 w-32 h-32 rounded-full blur-[50px] opacity-10 transition-opacity group-hover:opacity-20",
          colorClass === "score-high" ? "bg-emerald-500" :
          colorClass === "score-mid" ? "bg-amber-500" : "bg-rose-500"
        )}
      />

      <div className="flex items-start justify-between mb-4 relative z-10">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg" style={{ background: "var(--bg-elevated)", border: "1px solid var(--border)" }}>
            <Icon size={18} style={{ color: "var(--text-secondary)" }} />
          </div>
          <h3 className="font-medium text-sm text-gray-200">{title}</h3>
        </div>
        <div className={cn("text-2xl font-bold tracking-tight", colorClass)}>
          {formatScore(score)}<span className="text-sm font-medium text-gray-500">/10</span>
        </div>
      </div>

      <div className="relative z-10">
        <div className="progress-bar-track mb-3">
          <div
            className={cn(
              "progress-bar-fill",
              colorClass === "score-high" ? "bg-gradient-to-r from-emerald-500 to-emerald-400" :
              colorClass === "score-mid" ? "bg-gradient-to-r from-amber-500 to-amber-400" :
              "bg-gradient-to-r from-rose-500 to-rose-400"
            )}
            style={{ width: `${percentage}%` }}
          />
        </div>
        <p className="text-xs text-gray-400 leading-relaxed">{description}</p>
      </div>
    </div>
  );
}
