import { BackwardQuestion } from "./questions";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export interface ScreeningResponse {
    phase: "screening_done";
    screening: Record<string, {
        screening: { action: string; q1: number; q2: number; v1: number; v2: number; threshold: number; reason: string };
        needs_full_questions: boolean;
    }>;
    questions_needed: number[];
}

export interface DimensionResult {
    screening_action: string;
    total_score: number;
    fuzzy_value: number;
    label_idx: number;
    label: string;
    advice: string;
    memberships: { label: string; mu: number }[];
}

export interface FuzzyResponse {
    phase: "fuzzy_done";
    dimensions: Record<string, DimensionResult>;
    profile: string;
    backward_questions: BackwardQuestion[];
    needs_backward: boolean;
}

export interface FinalResult {
    phase: "complete";
    profile: string;
    profile_verified: boolean;
    confirm_score: number;
    confirm_total: number;
    profile_advice: string;
    confirm_detail: { key: string; text: string; answer: string }[];
    dimensions: Record<string, DimensionResult>;
}

async function post<T>(endpoint: string, body: object): Promise<T> {
    const res = await fetch(`${API_BASE}/${endpoint}/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({ message: "Unknown error" }));
        throw new Error(err.message || `HTTP ${res.status}`);
    }
    const json = await res.json();
    if (json.status === "error") throw new Error(json.message);
    return json.data as T;
}

export const apiScreening = (answers: Record<number, number>) =>
    post<ScreeningResponse>("screening", { answers });

export const apiFuzzyAnalysis = (answers: Record<number, number>, screening: ScreeningResponse) =>
    post<FuzzyResponse>("fuzzy-analysis", { answers, screening });

export const apiBackwardChaining = (
    profile: string,
    known_answers: Record<string, string | string[]>,
    fuzzy_result: FuzzyResponse
) => post<FinalResult>("backward-chaining", { profile, known_answers, fuzzy_result });