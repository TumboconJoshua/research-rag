"use client";
import { useMutation } from "@tanstack/react-query";
import { uploadDocument, UploadResponse } from "@/lib/api";
import {
  UploadCloud,
  FileText,
  Sparkles,
  ShieldCheck,
  BrainCircuit,
  Search,
  ChevronRight,
  Loader2,
  AlertCircle
} from "lucide-react";
import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import ThemeToggle from "@/components/ThemeToggle";

export default function LandingPage() {
  const router = useRouter();
  const [isDragActive, setIsDragActive] = useState(false);
  const [uploadMode, setUploadMode] = useState<"file" | "text">("file");
  const [textInput, setTextInput] = useState("");
  const [error, setError] = useState<string | null>(null);

  const uploadMutation = useMutation({
    mutationFn: (data: { file?: File; text?: string }) =>
      uploadDocument(data.file, data.text),
    onSuccess: (data: UploadResponse) => {
      // Use Convex Document ID for routing
      router.push(`/analysis/${data.document_id}?filename=${encodeURIComponent(data.filename)}&words=${data.word_count}&pages=${data.page_count}`);
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || "Upload failed. Please try again.");
    },
  });

  const onDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragActive(true);
  }, []);

  const onDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragActive(false);
  }, []);

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragActive(false);
    const file = e.dataTransfer.files?.[0];
    if (file && file.type === "application/pdf") {
      uploadMutation.mutate({ file });
    } else {
      setError("Please upload a valid PDF file.");
    }
  }, [uploadMutation]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) uploadMutation.mutate({ file });
  };

  const handleTextSubmit = () => {
    if (textInput.trim().length < 50) {
      setError("Please provide at least 50 characters of research text.");
      return;
    }
    uploadMutation.mutate({ text: textInput });
  };

  return (
    <main className="min-h-screen bg-grid p-6 text-[var(--text-primary)] transition-colors duration-300">
      <div className="absolute top-6 right-6 z-50">
        <ThemeToggle />
      </div>
      <div className="max-w-5xl mx-auto flex flex-col items-center pt-20 pb-20">
        
        {/* Hero Section */}
        <div className="text-center mb-12 animate-fade-in">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold uppercase tracking-wider mb-6">
            <Sparkles size={14} />
            Powered by Gemini 2.5 Pro
          </div>
          <h1 className="text-5xl md:text-6xl font-bold tracking-tight mb-6">
            <span className="italic gradient-text p-2 md:text-7xl">VeriPy</span> <br />
            the Integrity of your <br />Research Paper.
          </h1>
          <p className="text-[var(--text-secondary)] text-sm max-w-2xl mx-auto leading-relaxed">
            Upload a PDF or paste text to perform deep analysis on methodology,
            citation legitimacy, and logical consistency using Gemini 2.5 Pro.
          </p>
        </div>

        {/* Action Area */}
        <div className="w-full max-w-3xl glass-card overflow-hidden animate-fade-in delay-100">
          {/* Mode Switcher */}
          <div className="flex border-b border-[var(--border)] bg-[var(--bg-surface)]">
            <button
              onClick={() => setUploadMode("file")}
              className={cn(
                "flex-1 py-4 text-sm font-medium transition-colors border-b-2",
                uploadMode === "file" ? "border-indigo-500 text-[var(--text-primary)] bg-indigo-500/5" : "border-transparent text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
              )}
            >
              Upload PDF
            </button>
            <button
              onClick={() => setUploadMode("text")}
              className={cn(
                "flex-1 py-4 text-sm font-medium transition-colors border-b-2",
                uploadMode === "text" ? "border-indigo-500 text-[var(--text-primary)] bg-indigo-500/5" : "border-transparent text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
              )}
            >
              Paste Text
            </button>
          </div>

          <div className="p-8">
            {error && (
              <div className="mb-6 p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm flex items-center gap-3 animate-shake">
                <AlertCircle size={18} />
                {error}
              </div>
            )}

            {uploadMode === "file" ? (
              <div
                onDragOver={onDragOver}
                onDragLeave={onDragLeave}
                onDrop={onDrop}
                className={cn(
                  "relative h-64 rounded-2xl border-2 border-dashed transition-all flex flex-col items-center justify-center p-6 text-center group",
                  isDragActive ? "border-indigo-500 bg-indigo-500/5" : "border-[var(--border)] hover:border-[var(--border-hover)] hover:bg-[var(--bg-surface)]"
                )}
              >
                <input
                  type="file"
                  id="file-upload"
                  className="hidden"
                  accept=".pdf"
                  onChange={handleFileSelect}
                />
                <label
                  htmlFor="file-upload"
                  className="absolute inset-0 cursor-pointer"
                />
                
                <div className="w-16 h-16 rounded-2xl bg-[var(--bg-elevated)] flex items-center justify-center mb-4 text-[var(--text-secondary)] group-hover:scale-110 group-hover:text-indigo-400 transition-all duration-300">
                  {uploadMutation.isPending ? (
                    <Loader2 size={32} className="animate-spin" />
                  ) : (
                    <UploadCloud size={32} />
                  )}
                </div>
                
                <h3 className="text-xl font-semibold mb-2">
                  {uploadMutation.isPending ? "Ingesting Paper..." : "Drop your PDF here"}
                </h3>
                <p className="text-sm text-[var(--text-secondary)] max-w-[240px]">
                  {uploadMutation.isPending ? "Extracting text and generating embeddings..." : "or click to browse from your computer (Max 20MB)"}
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                <textarea
                  value={textInput}
                  onChange={(e) => setTextInput(e.target.value)}
                  placeholder="Paste the abstract or full text of the research paper here..."
                  className="w-full h-64 bg-transparent border-[var(--border)] resize-none p-4 placeholder:text-[var(--text-muted)] focus:border-indigo-500/50 transition-colors"
                />
                <button
                  onClick={handleTextSubmit}
                  disabled={uploadMutation.isPending || !textInput.trim()}
                  className="btn-primary w-full h-12 flex items-center justify-center gap-2"
                >
                  {uploadMutation.isPending ? (
                    <>
                      <Loader2 size={18} className="animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <Sparkles size={18} />
                      Analyze Pasted Text
                    </>
                  )}
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-4xl mt-12">
          {[
            { icon: BrainCircuit, title: "Deep Analysis", desc: "Logical consistency and methodological rigor evaluation." },
            { icon: ShieldCheck, title: "Ref-Check", desc: "Cross-platform verification of all cited publications." },
            { icon: Search, title: "RAG Powered", desc: "Context-aware queries against the entire document." }
          ].map((f, i) => (
            <div key={i} className="glass-card p-6 border border-[var(--border)]">
              <f.icon className="text-indigo-400 mb-4" size={24} />
              <h3 className="font-semibold mb-2">{f.title}</h3>
              <p className="text-xs text-[var(--text-secondary)] leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
