const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function apiFetch<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail ?? "API error");
  }
  return res.json() as Promise<T>;
}

// ─── Types ──────────────────────────────────────────────────

export interface UploadResponse {
  document_id: string;
  filename: string;
  page_count: number;
  word_count: number;
  chunk_count: number;
  status: string;
}

export interface AnalysisResult {
  document_id: string;
  research_quality_score: number;
  methodology_score: number;
  citation_integrity: number;
  logical_consistency: number;
  literature_review_score: number;
  data_transparency_score: number;
  strengths: string[];
  weaknesses: string[];
  potential_biases: string[];
  improvement_suggestions: string[];
  missing_citation_areas: string[];
}

export type ReferenceStatus =
  | "VALID"
  | "PARTIALLY_MATCHED"
  | "LIKELY_FAKE"
  | "UNVERIFIED";

export interface ValidatedReference {
  index: number;
  raw_text: string;
  title?: string;
  authors: string[];
  year?: number;
  journal?: string;
  doi?: string;
  status: ReferenceStatus;
  confidence_score: number;
  source?: string;
}

export interface ValidationReport {
  document_id: string;
  total_references: number;
  valid_count: number;
  partially_matched_count: number;
  likely_fake_count: number;
  unverified_count: number;
  references: ValidatedReference[];
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatResponse {
  answer: string;
  sources: string[];
}

// ─── API Functions ───────────────────────────────────────────

export async function uploadDocument(
  file?: File,
  text?: string
): Promise<UploadResponse> {
  const formData = new FormData();
  if (file) formData.append("file", file);
  if (text) formData.append("text", text);

  const res = await fetch(`${BASE}/upload-document`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail ?? "Upload failed");
  }
  return res.json();
}

export async function analyzePaper(documentId: string): Promise<AnalysisResult> {
  return apiFetch<AnalysisResult>(`/analyze-paper/${documentId}`, {
    method: "POST",
  });
}

export async function validateReferences(
  documentId: string,
  rawText?: string
): Promise<ValidationReport> {
  return apiFetch<ValidationReport>("/validate-references", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ document_id: documentId, raw_text: rawText }),
  });
}

export async function sendChat(
  documentId: string,
  message: string,
  history: ChatMessage[]
): Promise<ChatResponse> {
  return apiFetch<ChatResponse>("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ document_id: documentId, message, history }),
  });
}
