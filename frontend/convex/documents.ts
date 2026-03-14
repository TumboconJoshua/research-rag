import { v } from "convex/values";
import { mutation, query } from "./_generated/server";

export const createDocument = mutation({
  args: {
    filename: v.string(),
    fileType: v.string(),
    wordCount: v.number(),
  },
  handler: async (ctx, args) => {
    const docId = await ctx.db.insert("documents", {
      ...args,
      status: "processing",
    });
    return docId;
  },
});

export const updateDocumentStatus = mutation({
  args: {
    id: v.id("documents"),
    status: v.string(),
  },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, { status: args.status });
  },
});

export const getDocument = query({
  args: { id: v.id("documents") },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.id);
  },
});

export const listDocuments = query({
  handler: async (ctx) => {
    return await ctx.db.query("documents").order("desc").collect();
  },
});

export const saveAnalysis = mutation({
  args: {
    documentId: v.string(),
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
  },
  handler: async (ctx, args) => {
    const existing = await ctx.db
      .query("analyses")
      .withIndex("by_document_id", (q) => q.eq("documentId", args.documentId))
      .unique();
    
    if (existing) {
      await ctx.db.replace(existing._id, args);
      return existing._id;
    }
    return await ctx.db.insert("analyses", args);
  },
});

export const getAnalysis = query({
  args: { documentId: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("analyses")
      .withIndex("by_document_id", (q) => q.eq("documentId", args.documentId))
      .unique();
  },
});

export const saveReference = mutation({
  args: {
    documentId: v.string(),
    index: v.number(),
    rawText: v.string(),
    title: v.union(v.string(), v.null()),
    authors: v.array(v.string()),
    year: v.union(v.string(), v.null()),
    journal: v.union(v.string(), v.null()),
    doi: v.union(v.string(), v.null()),
    status: v.string(),
    confidenceScore: v.number(),
    sourceProvider: v.union(v.string(), v.null()),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("references", args);
  },
});
