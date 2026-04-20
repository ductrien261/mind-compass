"use client";

import { useState, useEffect, useCallback } from "react";
import { ArrowLeft, X, ShieldCheck, Keyboard } from "lucide-react";
import {
    DASS_QUESTIONS,
    SCREENING_Q_IDS,
    getScreeningQuestions,
    getQuestionsByIds,
    ANSWER_OPTIONS,
    YESNO_OPTIONS,
} from "@/app/lib/questions";
import {
    apiScreening,
    apiFuzzyAnalysis,
    apiBackwardChaining,
    ScreeningResponse,
    FuzzyResponse,
    FinalResult,
} from "@/app/lib/api";
import AnalysisScreen from "./AnalysisScreen";

type Phase =
    | "screening"       // 6 câu sàng lọc
    | "analyzing_1"     // loading sau screening
    | "full_questions"  // các câu còn lại (nếu ask_more)
    | "analyzing_2"     // loading sau full questions
    | "backward"        // backward chaining (yes/no)
    | "analyzing_3"     // loading sau backward
    | "done";           // chuyển sang result

interface Props {
    onComplete: (result: FinalResult) => void;
}

export default function AssessmentFlow({ onComplete }: Props) {
    // State 
    const [phase, setPhase] = useState<Phase>("screening");
    const [answers, setAnswers] = useState<Record<number, number>>({});
    const [backwardAns, setBackwardAns] = useState<Record<string, string>>({});
    const [currentIdx, setCurrentIdx] = useState(0);
    const [screeningRes, setScreeningRes] = useState<ScreeningResponse | null>(null);
    const [fuzzyRes, setFuzzyRes] = useState<FuzzyResponse | null>(null);
    const [error, setError] = useState<string>("");

    // Câu hỏi hiện tại theo phase
    const screeningQs = getScreeningQuestions();
    const fullQIds = screeningRes?.questions_needed ?? [];
    const fullQs = getQuestionsByIds(fullQIds);
    const backwardQs = fuzzyRes?.backward_questions ?? [];

    const currentQuestions =
        phase === "screening" ? screeningQs :
            phase === "full_questions" ? fullQs :
                phase === "backward" ? backwardQs.map(q => ({ id: 0, text: q.text, key: q.key })) :
                    [];

    const totalQs = currentQuestions.length;
    const progress = totalQs > 0 ? (currentIdx / totalQs) * 100 : 0;

    const currentQ = currentQuestions[currentIdx];
    const isBackwardPhase = phase === "backward";
    const currentOptions = isBackwardPhase ? YESNO_OPTIONS : ANSWER_OPTIONS;

    // Handlers 

    const handleSelect = useCallback(async (value: number | string) => {
        if (!currentQ) return;

        if (isBackwardPhase) {
            // Backward: key-based
            const q = backwardQs[currentIdx];
            const updated = { ...backwardAns, [q.key]: value as string };
            setBackwardAns(updated);

            if (currentIdx < totalQs - 1) {
                setCurrentIdx(i => i + 1);
            } else {
                // Gửi backward
                setPhase("analyzing_3");
            }
        } else {
            // DASS: id-based
            const updated = { ...answers, [(currentQ as any).id]: value as number };
            setAnswers(updated);

            if (currentIdx < totalQs - 1) {
                setCurrentIdx(i => i + 1);
            } else {
                // Hết câu hiện phase
                if (phase === "screening") {
                    setPhase("analyzing_1");
                } else if (phase === "full_questions") {
                    setPhase("analyzing_2");
                }
            }
        }
    }, [currentQ, currentIdx, totalQs, phase, isBackwardPhase, answers, backwardAns, backwardQs]);

    // Keyboard shortcut
    useEffect(() => {
        if (phase === "analyzing_1" || phase === "analyzing_2" || phase === "analyzing_3" || phase === "done") return;
        const handler = (e: KeyboardEvent) => {
            const opt = currentOptions.find(o => o.key === e.key);
            if (opt) handleSelect(opt.value);
        };
        window.addEventListener("keydown", handler);
        return () => window.removeEventListener("keydown", handler);
    }, [phase, currentOptions, handleSelect]);

    // Analysis callbacks

    const handleAnalysis1Done = async () => {
        try {
            const res = await apiScreening(answers);
            setScreeningRes(res);

            if (res.questions_needed.length > 0) {
                setPhase("full_questions");
                setCurrentIdx(0);
            } else {
                setPhase("analyzing_2");
            }
        } catch (e: any) {
            setError(e.message);
        }
    };

    const handleAnalysis2Done = async () => {
        if (!screeningRes) return;
        try {
            const res = await apiFuzzyAnalysis(answers, screeningRes);
            setFuzzyRes(res);

            if (res.needs_backward && res.backward_questions.length > 0) {
                setPhase("backward");
                setCurrentIdx(0);
            } else {
                setPhase("analyzing_3");
            }
        } catch (e: any) {
            setError(e.message);
        }
    };

    const handleAnalysis3Done = async () => {
        if (!fuzzyRes) return;
        try {
            const res = await apiBackwardChaining(fuzzyRes.profile, backwardAns, fuzzyRes);
            onComplete(res);
        } catch (e: any) {
            setError(e.message);
        }
    };

    // Render

    if (phase === "analyzing_1") return <AnalysisScreen phase={1} onDone={handleAnalysis1Done} />;
    if (phase === "analyzing_2") return <AnalysisScreen phase={2} onDone={handleAnalysis2Done} />;
    if (phase === "analyzing_3") return <AnalysisScreen phase={3} onDone={handleAnalysis3Done} />;

    const phaseLabel =
        phase === "screening" ? "Sàng lọc ban đầu" :
            phase === "full_questions" ? "Đánh giá chuyên sâu" :
                "Xác nhận triệu chứng";

    if (error) {
        return (
            <div className="min-h-screen bg-[#FAFAFA] flex items-center justify-center">
                <div className="text-center p-8">
                    <p className="text-red-500 font-bold mb-4">Có lỗi xảy ra: {error}</p>
                    <button onClick={() => { setError(""); setPhase("screening"); setCurrentIdx(0); }}
                        className="text-blue-600 underline">Thử lại</button>
                </div>
            </div>
        );
    }

    return (
        <div className="flex flex-col min-h-screen bg-[#FAFAFA] text-slate-900">

            {/* TOP BAR */}
            <header className="px-6 py-6 md:px-12 max-w-5xl mx-auto w-full flex items-center justify-between">
                <div className="flex items-center gap-4 w-1/3">
                    <button
                        onClick={() => currentIdx > 0 && setCurrentIdx(i => i - 1)}
                        className={`p-2 rounded-full transition-all ${currentIdx === 0 ? "opacity-0 pointer-events-none" : "hover:bg-slate-200 text-slate-500"}`}
                    >
                        <ArrowLeft size={24} />
                    </button>
                </div>

                <div className="w-1/3 flex flex-col items-center">
                    <span className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">{phaseLabel}</span>
                    <div className="w-full max-w-50 h-1.5 bg-slate-200 rounded-full overflow-hidden">
                        <div className="h-full bg-blue-600 rounded-full transition-all duration-500" style={{ width: `${progress}%` }} />
                    </div>
                    <span className="text-xs text-slate-400 mt-1">{currentIdx + 1} / {totalQs}</span>
                </div>

                <div className="w-1/3 flex justify-end">
                    <button className="p-2 rounded-full hover:bg-slate-200 text-slate-400 transition-colors">
                        <X size={24} />
                    </button>
                </div>
            </header>

            {/* QUESTION AREA */}
            <main className="flex-1 flex flex-col justify-center px-6 md:px-12 max-w-3xl mx-auto w-full py-12">
                {currentQ && (
                    <div key={`${phase}-${currentIdx}`} className="w-full animate-[fadeSlide_0.35s_ease]">
                        <h1 className="text-2xl md:text-4xl font-extrabold text-slate-900 mb-12 leading-[1.3]">
                            {currentQ.text}
                        </h1>

                        <div className="flex flex-col gap-4">
                            {currentOptions.map(opt => (
                                <button
                                    key={opt.key}
                                    onClick={() => handleSelect(opt.value)}
                                    className="group relative w-full flex items-center p-5 md:p-6 bg-white border-2 border-slate-100 hover:border-blue-500 rounded-2xl transition-all shadow-sm hover:shadow-md hover:shadow-blue-500/10 text-left focus:outline-none focus:border-blue-500"
                                >
                                    <div className="absolute left-6 w-8 h-8 rounded-lg bg-slate-100 text-slate-500 font-bold flex items-center justify-center text-sm group-hover:bg-blue-100 group-hover:text-blue-600 transition-colors">
                                        {opt.key}
                                    </div>
                                    <div className="ml-14">
                                        <div className="text-lg font-bold text-slate-800 group-hover:text-blue-700 transition-colors">{opt.label}</div>
                                        <div className="text-sm text-slate-500 mt-1 font-medium">{opt.desc}</div>
                                    </div>
                                </button>
                            ))}
                        </div>
                    </div>
                )}
            </main>

            {/* BOTTOM BAR */}
            <footer className="px-6 py-8 flex flex-col md:flex-row items-center justify-between max-w-5xl mx-auto w-full text-slate-400">
                <div className="flex items-center gap-2 text-sm font-medium">
                    <ShieldCheck size={18} /> Mọi lựa chọn đều được ẩn danh
                </div>
                <div className="hidden md:flex items-center gap-2 text-sm font-medium mt-4 md:mt-0">
                    <Keyboard size={18} /> Sử dụng phím số để chọn nhanh
                </div>
            </footer>
        </div>
    );
}