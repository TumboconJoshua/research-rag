import { ChatMessage } from "@/lib/api";
import { Bot, User, TextQuote } from "lucide-react";

export function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex gap-4 w-full ${isUser ? "flex-row-reverse" : ""}`}>
      {/* Avatar */}
      <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center
        bg-gray-800 border border-gray-700 mt-1 shadow-sm">
        {isUser ? (
          <User size={16} className="text-gray-300" />
        ) : (
          <Bot size={16} className="text-indigo-400" />
        )}
      </div>

      {/* Bubble */}
      <div className={`flex flex-col max-w-[85%] ${isUser ? "items-end" : "items-start"}`}>
        <div
          className={`px-5 py-3.5 text-[0.95rem] leading-[1.6] shadow-sm whitespace-pre-wrap
          ${isUser
              ? "bg-gradient-to-br from-indigo-600 to-indigo-500 text-white rounded-[20px] rounded-tr-md"
              : "bg-[#161b2e] border border-indigo-500/10 text-gray-200 rounded-[20px] rounded-tl-md"
            }`}
        >
          {message.content}
        </div>

        {/* Source citation handling if assistant */}
        {!isUser && message.content.includes("[Excerpt") && (
          <div className="mt-2 text-xs text-gray-500 flex items-center gap-1.5 px-2">
            <TextQuote size={12} />
            <span>Sourced from document context</span>
          </div>
        )}
      </div>
    </div>
  );
}
