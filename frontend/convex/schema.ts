import { v } from "convex/values";
import { defineSchema, defineTable } from "convex/server";

export default defineSchema({
  documents: defineTable({
    filename: v.string(),
    fileType: v.string(), // "pdf" or "text"
    wordCount: v.number(),
    status: v.string(), // "processing", "ready", "error"
    userId: v.optional(v.string()),
  }).index("by_status", ["status"]),

  analyses: defineTable({
    documentId: v.string(), // The ID from FastAPI/NumPy
    researchQualityScore: v.number(),
    methodologyScore: v.number(),
    citationIntegrity: v.number(),
    logicalConsistency: v.number(),
    literatureReviewScore: v.number(),
    dataTransparencyScore: v.number(),
    strengths: v.array(v.string()),
    weaknesses: v.array(v.string()),
    improvementSuggestions: v.array(v.string()),
    potentialBiases: v.array(v.string()),
    missingCitationAreas: v.array(v.string()),
  }).index("by_document_id", ["documentId"]),

  references: defineTable({
    documentId: v.string(),
    index: v.number(),
    rawText: v.string(),
    title: v.union(v.string(), v.null()),
    authors: v.array(v.string()),
    year: v.union(v.string(), v.null()),
    journal: v.union(v.string(), v.null()),
    doi: v.union(v.string(), v.null()),
    status: v.string(), // VALID, PARTIALLY_MATCHED, LIKELY_FAKE, UNVERIFIED
    confidenceScore: v.number(),
    sourceProvider: v.union(v.string(), v.null()),
  }).index("by_document_id", ["documentId"]),
});
