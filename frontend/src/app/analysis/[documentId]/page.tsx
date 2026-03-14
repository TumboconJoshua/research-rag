"use client";
import { useState } from "react";
import { useParams, useSearchParams } from "next/navigation";
import { useQuery, useMutation } from "@tanstack/react-query";
import {
  analyzePaper,
  validateReferences,
  sendChat,
  AnalysisResult,
  ValidationReport,
  ChatMessage,
} from "@/lib/api";
import { ScoreCard } from "@/components/analysis/ScoreCard";
import { QualityReport } from "@/components/analysis/QualityReport";
import { ReferenceTable } from "@/components/references/ReferenceTable";
import { ChatPanel } from "@/components/chat/ChatPanel";
import {
  BarChart3,
  BookOpen,
  ShieldCheck,
  MessageSquare,
  FileText,
  Loader2,
  Sparkles,
  ArrowLeft,
} from "lucide-react";
import Link from "next/link";

type Tab = "analysis" | "references" | "chat";

export default function AnalysisPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const documentId = params.documentId as string;
  const filename = searchParams.get("filename") ?? "Document";
  const wordCount = searchParams.get("words") ?? "—";
  const pageCount = searchParams.get("pages") ?? "—";

  const [activeTab, setActiveTab] = useState<Tab>("analysis");
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState("");

  // Analysis query (manual trigger)
  const analysisQuery = useQuery<AnalysisResult>({
    queryKey: ["analysis", documentId],
    queryFn: () => analyzePaper(documentId),
    enabled: false,
    staleTime: Infinity,
    retry: 1,
  });

  const refQuery = useQuery<ValidationReport>({
    queryKey: ["references", documentId],
    queryFn: () => validateReferences(documentId),
    enabled: false,
    staleTime: Infinity,
    retry: 1,
  });

  const chatMutation = useMutation({
    mutationFn: ({ msg, hist }: { msg: string; hist: ChatMessage[] }) =>
      sendChat(documentId, msg, hist),
    onSuccess: (data) => {
      setChatHistory((prev) => [
        ...prev,
        { role: "assistant", content: data.answer },
      ]);
    },
    onError: (err: Error) => {
      setChatHistory((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `⚠️ Error: ${err.message}`,
        },
      ]);
    },
  });

  const handleSendChat = () => {
    if (!chatInput.trim()) return;
    const newHistory: ChatMessage[] = [
      ...chatHistory,
      { role: "user", content: chatInput },
    ];
    setChatHistory(newHistory);
    setChatInput("");
    chatMutation.mutate({ msg: chatInput, hist: chatHistory });
  };

  const tabs = [
    {
      id: "analysis" as Tab,
      label: "Quality Analysis",
      icon: BarChart3,
      action: () => {
        setActiveTab("analysis");
        if (!analysisQuery.data) analysisQuery.refetch();
      },
    },
    {
      id: "references" as Tab,
      label: "References",
      icon: ShieldCheck,
      action: () => {
        setActiveTab("references");
        if (!refQuery.data) refQuery.refetch();
      },
    },
    {
      id: "chat" as Tab,
      label: "Chat",
      icon: MessageSquare,
      action: () => setActiveTab("chat"),
    },
  ];

  return (
    <main
      className="min-h-screen bg-grid"
      style={{ background: "var(--bg-base)" }}
    >
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Back + Header */}
        <div className="mb-8 animate-fade-in">
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-sm mb-6 transition-colors"
            style={{ color: "var(--text-muted)" }}
          >
            <ArrowLeft size={14} />
            Back to Upload
          </Link>

          <div className="flex items-start justify-between flex-wrap gap-4">
            <div>
              <h1 className="text-2xl font-bold mb-1">
                <span className="gradient-text">Analysis Dashboard</span>
              </h1>
              <div
                className="flex items-center gap-3 text-sm"
                style={{ color: "var(--text-secondary)" }}
              >
                <span className="flex items-center gap-1.5">
                  <FileText size={13} /> {filename}
                </span>
                <span
                  className="w-1 h-1 rounded-full"
                  style={{ background: "var(--text-muted)" }}
                />
                <span>{wordCount} words</span>
                <span
                  className="w-1 h-1 rounded-full"
                  style={{ background: "var(--text-muted)" }}
                />
                <span>{pageCount} pages</span>
              </div>
            </div>

            {/* Document ID Badge */}
            <div
              className="px-3 py-1.5 rounded-lg text-xs"
              style={{
                background: "var(--bg-elevated)",
                border: "1px solid var(--border)",
                color: "var(--text-muted)",
                fontFamily: "var(--font-mono)",
              }}
            >
              ID: {documentId.slice(0, 8)}…
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div
          className="flex gap-1 p-1 rounded-xl mb-8"
          style={{ background: "var(--bg-elevated)", width: "fit-content" }}
        >
          {tabs.map((tab) => (
            <button
              key={tab.id}
              id={`tab-${tab.id}`}
              onClick={tab.action}
              className="flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium transition-all duration-200"
              style={
                activeTab === tab.id
                  ? {
                      background: "linear-gradient(135deg, var(--accent-primary), #818cf8)",
                      color: "white",
                      boxShadow: "0 4px 16px var(--accent-glow)",
                    }
                  : {
                      background: "transparent",
                      color: "var(--text-secondary)",
                    }
              }
            >
              <tab.icon size={15} />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="animate-fade-in" key={activeTab}>
          {/* ── ANALYSIS TAB ── */}
          {activeTab === "analysis" && (
            <div>
              {!analysisQuery.data && !analysisQuery.isFetching && (
                <div className="glass-card p-16 flex flex-col items-center gap-5 text-center">
                  <div
                    className="w-20 h-20 rounded-2xl flex items-center justify-center"
                    style={{
                      background: "rgba(99,102,241,0.12)",
                      border: "1px solid rgba(99,102,241,0.2)",
                    }}
                  >
                    <Sparkles size={36} style={{ color: "var(--accent-primary)" }} />
                  </div>
                  <div>
                    <h2 className="text-xl font-semibold mb-2">
                      Run AI Quality Analysis
                    </h2>
                    <p
                      className="text-sm max-w-md"
                      style={{ color: "var(--text-secondary)" }}
                    >
                      The AI will evaluate methodology, citations, logical consistency,
                      and more. This takes ~15 seconds.
                    </p>
                  </div>
                  <button
                    id="run-analysis-btn"
                    className="btn-primary"
                    onClick={() => analysisQuery.refetch()}
                  >
                    <Sparkles size={16} /> Analyze Paper
                  </button>
                </div>
              )}

              {analysisQuery.isFetching && (
                <div className="glass-card p-16 flex flex-col items-center gap-4 text-center">
                  <Loader2
                    size={48}
                    className="animate-spin-slow"
                    style={{ color: "var(--accent-primary)" }}
                  />
                  <p className="font-medium">Analyzing research paper…</p>
                  <p
                    className="text-sm"
                    style={{ color: "var(--text-secondary)" }}
                  >
                    Gemini is evaluating methodology, citations, and logical flow
                  </p>
                </div>
              )}

              {analysisQuery.error && (
                <div
                  className="glass-card p-8 text-center"
                  style={{ borderColor: "rgba(244,63,94,0.3)" }}
                >
                  <p style={{ color: "var(--danger)" }}>
                    Analysis failed: {(analysisQuery.error as Error).message}
                  </p>
                  <button
                    className="btn-secondary mt-4"
                    onClick={() => analysisQuery.refetch()}
                  >
                    Retry
                  </button>
                </div>
              )}

              {analysisQuery.data && (
                <QualityReport data={analysisQuery.data} />
              )}
            </div>
          )}

          {/* ── REFERENCES TAB ── */}
          {activeTab === "references" && (
            <div>
              {!refQuery.data && !refQuery.isFetching && (
                <div className="glass-card p-16 flex flex-col items-center gap-5 text-center">
                  <div
                    className="w-20 h-20 rounded-2xl flex items-center justify-center"
                    style={{
                      background: "rgba(34,211,165,0.08)",
                      border: "1px solid rgba(34,211,165,0.2)",
                    }}
                  >
                    <ShieldCheck size={36} style={{ color: "var(--success)" }} />
                  </div>
                  <div>
                    <h2 className="text-xl font-semibold mb-2">
                      Validate References
                    </h2>
                    <p
                      className="text-sm max-w-md"
                      style={{ color: "var(--text-secondary)" }}
                    >
                      Checks every citation against Crossref, Semantic Scholar, and OpenAlex.
                      Classifies each as VALID, PARTIALLY MATCHED, LIKELY FAKE, or UNVERIFIED.
                    </p>
                  </div>
                  <button
                    id="run-validation-btn"
                    className="btn-primary"
                    onClick={() => refQuery.refetch()}
                    style={{
                      background: "linear-gradient(135deg, #22d3a5, #059669)",
                    }}
                  >
                    <ShieldCheck size={16} /> Validate References
                  </button>
                </div>
              )}

              {refQuery.isFetching && (
                <div className="glass-card p-16 flex flex-col items-center gap-4 text-center">
                  <Loader2
                    size={48}
                    className="animate-spin-slow"
                    style={{ color: "var(--success)" }}
                  />
                  <p className="font-medium">Validating references…</p>
                  <p
                    className="text-sm"
                    style={{ color: "var(--text-secondary)" }}
                  >
                    Querying Crossref, Semantic Scholar & OpenAlex in parallel
                  </p>
                </div>
              )}

              {refQuery.error && (
                <div
                  className="glass-card p-8 text-center"
                  style={{ borderColor: "rgba(244,63,94,0.3)" }}
                >
                  <p style={{ color: "var(--danger)" }}>
                    Validation failed: {(refQuery.error as Error).message}
                  </p>
                  <button
                    className="btn-secondary mt-4"
                    onClick={() => refQuery.refetch()}
                  >
                    Retry
                  </button>
                </div>
              )}

              {refQuery.data && <ReferenceTable report={refQuery.data} />}
            </div>
          )}

          {/* ── CHAT TAB ── */}
          {activeTab === "chat" && (
            <ChatPanel
              documentId={documentId}
              history={chatHistory}
              input={chatInput}
              isLoading={chatMutation.isPending}
              onInputChange={setChatInput}
              onSend={handleSendChat}
            />
          )}
        </div>
      </div>
    </main>
  );
}
