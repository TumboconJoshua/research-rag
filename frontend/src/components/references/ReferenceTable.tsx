import { useState } from "react";
import { ValidationReport, ValidatedReference } from "@/lib/api";
import { StatusBadge } from "./StatusBadge";
import { Search, ChevronDown, ChevronUp, ExternalLink, ShieldAlert } from "lucide-react";
import { cn } from "@/lib/utils";

export function ReferenceTable({ report }: { report: ValidationReport }) {
  const [searchTerm, setSearchTerm] = useState("");
  const [expandedRow, setExpandedRow] = useState<number | null>(null);
  const [filter, setFilter] = useState<string>("ALL");

  const filteredRefs = report.references.filter((ref) => {
    const matchesSearch =
      ref.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ref.authors.some((a) => a.toLowerCase().includes(searchTerm.toLowerCase())) ||
      ref.raw_text.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesFilter = filter === "ALL" || ref.status === filter;

    return matchesSearch && matchesFilter;
  });

  return (
    <div className="space-y-6 animate-fade-in">
      {/* ── Summary Cards ── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: "Total Citations", value: report.total_references, color: "text-blue-500" },
          { label: "Valid", value: report.valid_count, color: "text-emerald-500" },
          { label: "Partial Match", value: report.partially_matched_count, color: "text-amber-500" },
          { label: "Likely Fake / Unverified", value: report.likely_fake_count + report.unverified_count, color: "text-rose-500" },
        ].map((stat, i) => (
          <div key={i} className="glass-card p-5 border border-[var(--border)] bg-[var(--bg-elevated)]">
            <h4 className="text-[var(--text-muted)] text-sm font-medium mb-1">{stat.label}</h4>
            <div className={cn("text-3xl font-bold font-mono", stat.color)}>{stat.value}</div>
          </div>
        ))}
      </div>

      {/* ── Controls ── */}
      <div className="flex flex-col sm:flex-row gap-4 justify-between items-center glass-card p-4 bg-[var(--bg-surface)]">
        <div className="relative w-full sm:w-[320px]">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-muted)]" />
          <input
            type="text"
            placeholder="Search references..."
            className="pl-9 bg-transparent"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="flex bg-[var(--bg-elevated)] rounded-lg p-1 border border-[var(--border)] w-full sm:w-auto overflow-x-auto gap-1">
          {["ALL", "VALID", "PARTIALLY_MATCHED", "LIKELY_FAKE", "UNVERIFIED"].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={cn(
                "px-3 py-1.5 rounded-md text-xs font-semibold uppercase tracking-wider transition-colors min-w-max",
                filter === f
                  ? "bg-indigo-500/20 text-indigo-500"
                  : "text-[var(--text-muted)] hover:text-[var(--text-primary)]"
              )}
            >
              {f.replace("_", " ")}
            </button>
          ))}
        </div>
      </div>

      {/* ── Table ── */}
      <div className="glass-card overflow-hidden border border-[var(--border)] bg-[var(--bg-surface)]">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-[var(--bg-elevated)] border-b border-[var(--border)] text-xs text-[var(--text-muted)] uppercase tracking-wider">
                <th className="px-5 py-4 w-12 text-center">#</th>
                <th className="px-5 py-4">Title / Source</th>
                <th className="px-5 py-4 w-40 text-center">Status</th>
                <th className="px-5 py-4 w-28 text-center text-nowrap">Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--border)] text-sm">
              {filteredRefs.length > 0 ? (
                filteredRefs.map((ref) => (
                  <React.Fragment key={ref.index}>
                    <tr
                      className="hover:bg-[var(--bg-elevated)] transition-colors cursor-pointer"
                      onClick={() => setExpandedRow(expandedRow === ref.index ? null : ref.index)}
                    >
                      <td className="px-5 py-4 text-center font-mono text-[var(--text-muted)]">
                        {ref.index + 1}
                      </td>
                      <td className="px-5 py-4">
                        <div className="font-medium text-[var(--text-primary)] line-clamp-1 mb-1">
                          {ref.title || <span className="text-[var(--text-muted)] italic">No exact title matched</span>}
                        </div>
                        <div className="text-xs text-[var(--text-secondary)] line-clamp-1">
                          {ref.authors.slice(0, 2).join(", ")}
                          {ref.authors.length > 2 && " et al."}
                          {ref.year && ` (${ref.year})`}
                          {ref.journal && ` - ${ref.journal}`}
                        </div>
                      </td>
                      <td className="px-5 py-4 text-center">
                        <StatusBadge status={ref.status} />
                      </td>
                      <td className="px-5 py-4 text-center">
                        <div className="flex items-center justify-between gap-2">
                          <span className={cn(
                            "font-mono font-bold",
                            ref.confidence_score >= 0.8 ? "text-emerald-400" :
                            ref.confidence_score >= 0.5 ? "text-amber-400" : "text-rose-400"
                          )}>
                            {Math.round(ref.confidence_score * 100)}%
                          </span>
                          {expandedRow === ref.index ? (
                            <ChevronUp size={16} className="text-gray-500" />
                          ) : (
                            <ChevronDown size={16} className="text-gray-500" />
                          )}
                        </div>
                      </td>
                    </tr>

                    {/* Expandable Details */}
                    {expandedRow === ref.index && (
                      <tr className="bg-[var(--bg-surface)]">
                        <td colSpan={4} className="px-5 py-4">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-4 rounded-xl border border-[var(--border)] bg-[var(--bg-elevated)]">
                            {/* Raw Excerpt */}
                            <div>
                              <div className="text-xs font-bold text-[var(--text-muted)] uppercase tracking-widest mb-2 flex items-center gap-2">
                                <ShieldAlert size={14} className="text-indigo-500" /> 
                                Extracted String
                              </div>
                              <p className="text-[var(--text-secondary)] font-mono text-xs leading-relaxed bg-[var(--bg-surface)] p-3 rounded-lg border border-[var(--border)] break-words whitespace-pre-wrap">
                                {ref.raw_text}
                              </p>
                            </div>

                            {/* Verification Data */}
                            <div>
                              <div className="text-xs font-bold text-[var(--text-muted)] uppercase tracking-widest mb-2">Verified Metadata</div>
                              <ul className="space-y-2 text-sm">
                                <li className="flex gap-2">
                                  <span className="text-[var(--text-muted)] w-20">Source:</span>
                                  <span className="text-[var(--text-primary)] uppercase">{ref.source || "None"}</span>
                                </li>
                                <li className="flex items-start gap-2">
                                  <span className="text-[var(--text-muted)] w-20">Authors:</span>
                                  <span className="text-[var(--text-primary)] line-clamp-2">{ref.authors.join(", ") || "Unknown"}</span>
                                </li>
                                <li className="flex gap-2">
                                  <span className="text-[var(--text-muted)] w-20">Venue:</span>
                                  <span className="text-[var(--text-primary)]">{ref.journal || "Unknown"}</span>
                                </li>
                                {ref.doi && (
                                  <li className="flex gap-2 mt-2">
                                    <span className="text-[var(--text-muted)] w-20">DOI:</span>
                                    <a href={`https://doi.org/${ref.doi}`} target="_blank" rel="noreferrer" className="text-indigo-500 hover:underline flex items-center gap-1 font-medium">
                                      {ref.doi} <ExternalLink size={12} />
                                    </a>
                                  </li>
                                )}
                              </ul>
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))
              ) : (
                <tr>
                  <td colSpan={4} className="px-5 py-12 text-center text-gray-500">
                    No references found matching your search.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

import React from "react";
