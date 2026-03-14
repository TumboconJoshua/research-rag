import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatScore(score: number): string {
  return score.toFixed(1);
}

export function scoreClass(score: number): string {
  if (score >= 7.5) return "score-high";
  if (score >= 5) return "score-mid";
  return "score-low";
}

export function confidenceToPercent(score: number): number {
  return Math.round(score * 100);
}

export function truncate(text: string, max: number): string {
  if (text.length <= max) return text;
  return text.slice(0, max) + "…";
}
