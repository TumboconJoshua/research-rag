import { AnalysisResult } from "@/lib/api";
import { ScoreCard } from "./ScoreCard";
import {
  FileCheck2,
  ListTodo,
  TrendingDown,
  TrendingUp,
  BrainCircuit,
  Settings,
  ShieldAlert,
  SearchCheck,
  ClipboardList
} from "lucide-react";
import { cn } from "@/lib/utils";

export function QualityReport({ data }: { data: AnalysisResult }) {
  const scores = [
    {
      title: "Methodology",
      score: data.methodology_score,
      icon: Settings,
      description: "Rigor and appropriateness of the study design."
    },
    {
      title: "Citation Integrity",
      score: data.citation_integrity,
      icon: FileCheck2,
      description: "Coverage and quality of referenced literature."
    },
    {
      title: "Logical Consistency",
      score: data.logical_consistency,
      icon: BrainCircuit,
      description: "Internal flow and soundness of conclusions."
    },
    {
      title: "Literature Review",
      score: data.literature_review_score,
      icon: SearchCheck,
      description: "Thoroughness of prior work discussion."
    },
    {
      title: "Data Transparency",
      score: data.data_transparency_score,
      icon: ClipboardList,
      description: "Clarity of data handling and reproducibility."
    }
  ];

  const overallClass = 
    data.research_quality_score >= 8 ? "text-emerald-400" :
    data.research_quality_score >= 6 ? "text-amber-400" : "text-rose-400";

  return (
    <div className="space-y-8 animate-fade-in text-gray-200">
      {/* Overall Score Header */}
      <div className="glass-card p-8 flex flex-col md:flex-row items-center gap-8 bg-gradient-to-br from-[#1a2035] to-[#0e1120]">
        <div className="flex-shrink-0 relative">
          <svg className="w-40 h-40 transform -rotate-90">
            <circle cx="80" cy="80" r="70" stroke="currentColor" strokeWidth="12" fill="transparent" className="text-gray-800" />
            <circle
              cx="80" cy="80" r="70" stroke="currentColor" strokeWidth="12" fill="transparent"
              strokeDasharray={440}
              strokeDashoffset={440 - (440 * data.research_quality_score) / 10}
              className={cn("transition-all duration-1000 ease-out", overallClass)}
              strokeLinecap="round"
            />
          </svg>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center">
            <span className={cn("text-4xl font-bold block", overallClass)}>{data.research_quality_score.toFixed(1)}</span>
            <span className="text-xs text-gray-400 uppercase tracking-widest mt-1 block">Overall</span>
          </div>
        </div>

        <div>
          <h2 className="text-2xl font-semibold mb-3">Overall Research Quality</h2>
          <p className="text-gray-400 leading-relaxed max-w-2xl">
            This paper demonstrates <strong className="text-gray-200">{data.research_quality_score >= 8 ? "strong" : data.research_quality_score >= 6 ? "moderate" : "weak"}</strong> 
            {" "}methodology and logical flow. Based on the analysis, the research provides 
            {" "}{data.strengths.length > 0 ? "valuable contributions" : "limited contributions"} 
            {" "}but has {data.weaknesses.length} key areas for improvement.
          </p>
        </div>
      </div>

      {/* Individual Scores Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {scores.map((score, idx) => (
          <ScoreCard key={idx} {...score} />
        ))}
      </div>

      {/* Feedback Panels */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Strengths & Weaknesses */}
        <div className="space-y-5">
          <InsightsPanel
            title="Key Strengths"
            icon={TrendingUp}
            items={data.strengths}
            theme="success"
          />
          <InsightsPanel
            title="Identified Weaknesses"
            icon={TrendingDown}
            items={data.weaknesses}
            theme="danger"
          />
        </div>

        {/* Improvements & Biases */}
        <div className="space-y-5">
          <InsightsPanel
            title="Improvement Suggestions"
            icon={ListTodo}
            items={data.improvement_suggestions}
            theme="info"
          />
          <InsightsPanel
            title="Potential Biases"
            icon={ShieldAlert}
            items={data.potential_biases}
            theme="warning"
          />
        </div>
      </div>

      {/* Missing Citations (Full Width) */}
      {data.missing_citation_areas.length > 0 && (
        <InsightsPanel
          title="Missing Citation Areas"
          icon={FileCheck2}
          items={data.missing_citation_areas}
          theme="warning"
        />
      )}
    </div>
  );
}

// ── Helper Component ──
function InsightsPanel({ title, items, icon: Icon, theme }: { title: string, items: string[], icon: any, theme: "success" | "danger" | "info" | "warning" }) {
  if (items.length === 0) return null;

  const bgClasses = {
    success: "bg-[rgba(34,211,165,0.05)] border-[rgba(34,211,165,0.15)]",
    danger: "bg-[rgba(244,63,94,0.05)] border-[rgba(244,63,94,0.15)]",
    info: "bg-[rgba(99,102,241,0.05)] border-[rgba(99,102,241,0.15)]",
    warning: "bg-[rgba(245,158,11,0.05)] border-[rgba(245,158,11,0.15)]"
  };

  const iconColors = {
    success: "text-[#22d3a5]",
    danger: "text-[#f43f5e]",
    info: "text-[#818cf8]",
    warning: "text-[#f59e0b]"
  };

  return (
    <div className={cn("glass-card p-6 border", bgClasses[theme])}>
      <div className="flex items-center gap-3 mb-4">
        <Icon size={20} className={iconColors[theme]} />
        <h3 className="font-semibold text-lg">{title}</h3>
      </div>
      <ul className="space-y-3">
        {items.map((item, i) => (
          <li key={i} className="flex items-start gap-3 text-sm text-gray-300">
            <span className={cn("mt-1 flex-shrink-0 w-1.5 h-1.5 rounded-full", iconColors[theme].replace("text-", "bg-"))} />
            <span className="leading-relaxed">{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
