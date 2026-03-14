import { useEffect, useRef } from "react";
import { ChatMessage } from "@/lib/api";
import { MessageBubble } from "./MessageBubble";
import { Send, Loader2, Link, BotMessageSquare } from "lucide-react";

interface ChatPanelProps {
  documentId: string;
  history: ChatMessage[];
  input: string;
  isLoading: boolean;
  onInputChange: (val: string) => void;
  onSend: () => void;
}

const SUGGESTED = [
  "Summarize the main findings",
  "What is the research gap?",
  "Explain the methodology",
  "What are the limitations?",
];

export function ChatPanel({ history, input, isLoading, onInputChange, onSend }: ChatPanelProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll on new message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history, isLoading]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (input.trim() && !isLoading) onSend();
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-280px)] glass-card border border-gray-800 rounded-xl overflow-hidden animate-fade-in bg-[#0e1120]">

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-8 scroll-smooth" id="chat-messages">
        {history.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center px-4">
            <div className="w-16 h-16 rounded-full bg-indigo-500/10 flex items-center justify-center mb-4">
              <BotMessageSquare size={32} className="text-indigo-400" />
            </div>
            <h3 className="text-xl font-semibold mb-2 text-gray-200">Ask ResearchRAG</h3>
            <p className="text-gray-400 text-sm max-w-[300px] leading-relaxed mb-6">
              I can answer logic, summarize findings, and explain complex concepts 
              using only information from the uploaded document.
            </p>

            {/* Suggested */}
            <div className="mt-8 flex flex-wrap justify-center gap-2 max-w-lg">
              {SUGGESTED.map((q) => (
                <button
                  key={q}
                  className="px-4 py-2 bg-gray-900 border border-gray-800 rounded-full text-sm text-gray-300 hover:text-indigo-300 hover:border-indigo-500/30 hover:bg-indigo-500/10 transition-all font-medium flex items-center gap-2 group"
                  onClick={() => {
                    onInputChange(q);
                    setTimeout(onSend, 50);
                  }}
                >
                  <Link size={12} className="text-gray-500 group-hover:text-indigo-400" />
                  {q}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {history.map((msg, i) => (
              <MessageBubble key={i} message={msg} />
            ))}
            
            {/* Loading Indicator */}
            {isLoading && (
              <div className="flex gap-4 w-full">
                <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-gray-800 border border-gray-700 shadow-sm mt-1">
                  <BotMessageSquare size={16} className="text-indigo-400" />
                </div>
                <div className="flex flex-col items-start pt-2">
                  <div className="flex items-center gap-2 px-5 py-3.5 bg-[#161b2e] border border-indigo-500/10 text-gray-400 rounded-[20px] rounded-tl-md shadow-sm">
                    <Loader2 size={16} className="animate-spin" />
                    <span className="text-sm font-medium tracking-wide">Retrieving context...</span>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
        <div ref={bottomRef} className="h-4" />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-gray-800 bg-gray-900/50">
        <div className="relative flex items-end gap-2 bg-[#1a2035] p-2 rounded-2xl border border-gray-700/50 shadow-inner group focus-within:border-indigo-500/50 focus-within:ring-1 focus-within:ring-indigo-500/20 transition-all">
          <textarea
            className="flex-1 max-h-40 min-h-[44px] bg-transparent border-none text-gray-200 resize-none py-2.5 px-4 outline-none placeholder:text-gray-500"
            rows={1}
            value={input}
            onChange={(e) => {
              onInputChange(e.target.value);
              // Auto resize
              e.target.style.height = "auto";
              e.target.style.height = Math.min(e.target.scrollHeight, 160) + "px";
            }}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            placeholder="Ask a question about the paper..."
          />
          <button
            onClick={onSend}
            disabled={!input.trim() || isLoading}
            className="flex items-center justify-center w-11 h-11 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl disabled:opacity-50 disabled:bg-gray-700 transition-colors shadow-sm disabled:cursor-not-allowed mb-0.5"
          >
            {isLoading ? (
              <Loader2 size={18} className="animate-spin" />
            ) : (
              <Send size={18} className="-ml-0.5" />
            )}
          </button>
        </div>
        <p className="text-center text-xs text-gray-500 mt-3 flex items-center justify-center gap-1.5 font-medium">
          <BotMessageSquare size={12} className="text-gray-600" />
          ResearchRAG only answers using the provided document context.
        </p>
      </div>

    </div>
  );
}
