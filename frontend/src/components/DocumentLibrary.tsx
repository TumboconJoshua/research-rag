"use client";
import { useQuery } from "convex/react";
import { api } from "../../convex/_generated/api";
import { FileText, Clock, ChevronRight, FileSearch } from "lucide-react";
import Link from "next/link";

export function DocumentLibrary() {
  const documents = useQuery(api.documents.listDocuments);

  if (!documents) return null;

  return (
    <div className="mt-12 w-full max-w-4xl animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <FileSearch size={20} className="text-indigo-400" />
          Recent Analysis
        </h2>
      </div>

      <div className="grid gap-4">
        {documents.length === 0 ? (
          <div className="glass-card p-8 text-center text-[var(--text-muted)] border-dashed border-2">
            No research papers analyzed yet. Upload your first paper above.
          </div>
        ) : (
          documents.map((doc) => (
            <Link
              key={doc._id}
              href={`/analysis/${doc._id}?filename=${encodeURIComponent(doc.filename)}`}
              className="glass-card p-4 flex items-center justify-between hover:border-indigo-500/50 hover:bg-indigo-500/5 transition-all group"
            >
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-lg bg-[var(--bg-elevated)] flex items-center justify-center text-indigo-400 group-hover:bg-indigo-500/10 transition-colors">
                  <FileText size={20} />
                </div>
                <div>
                  <h3 className="font-medium text-[var(--text-primary)] transition-colors">
                    {doc.filename}
                  </h3>
                  <div className="flex items-center gap-3 text-xs text-[var(--text-secondary)] mt-1">
                    <span className="flex items-center gap-1">
                      <Clock size={12} />
                      {new Date(doc._creationTime).toLocaleDateString()}
                    </span>
                    <span>•</span>
                    <span>{doc.wordCount} words</span>
                    <span>•</span>
                    <span className={`uppercase font-bold ${doc.status === 'ready' ? 'text-emerald-500' : 'text-amber-500'}`}>
                      {doc.status}
                    </span>
                  </div>
                </div>
              </div>
              <ChevronRight size={18} className="text-[var(--text-muted)] group-hover:text-indigo-400 translate-x-0 group-hover:translate-x-1 transition-all" />
            </Link>
          ))
        )}
      </div>
    </div>
  );
}
