"use client";

import { useState, useEffect, useCallback } from "react";
import { ArrowLeft, X, ShieldCheck, Keyboard, CheckSquare } from "lucide-react";
import {
    DASS_QUESTIONS,
    SCREENING_Q_IDS,
    getScreeningQuestions,
    getQuestionsByIds,
    ANSWER_OPTIONS,
    YESNO_OPTIONS,
    BackwardQuestion,
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
    | "backward"        // backward chaining (yesno + multiselect)
    | "analyzing_3"     // loading sau backward
    | "done";

interface Props {
    onComplete: (result: FinalResult) => void;
}

export default function AssessmentFlow({ onComplete }: Props) {
    // State
    const [phase, setPhase] = useState<Phase>("screening");
    const [answers, setAnswers] = useState<Record<number, number>>({});

    const [backwardAns, setBackwardAns] = useState<Record<string, string | string[]>>({});
    const [selectedOptions, setSelectedOptions] = useState<string[]>([]);

    const [currentIdx, setCurrentIdx] = useState(0);
    const [screeningRes, setScreeningRes] = useState<ScreeningResponse | null>(null);
    const [fuzzyRes, setFuzzyRes] = useState<FuzzyResponse | null>(null);
    const [error, setError] = useState<string>("");

    //  Derived 
    const screeningQs = getScreeningQuestions();
    const fullQIds = screeningRes?.questions_needed ?? [];
    const fullQs = getQuestionsByIds(fullQIds);
    const backwardQs: BackwardQuestion[] = fuzzyRes?.backward_questions ?? [];

    const currentQuestions =
        phase === "screening" ? screeningQs :
        phase === "full_questions" ? fullQs :
        phase === "backward" ? backwardQs :
        [];

    const totalQs = currentQuestions.length;
    const progress = totalQs > 0 ? ((currentIdx + 1) / totalQs) * 100 : 0;

    const currentQ = currentQuestions[currentIdx];
    const isBackwardPhase = phase === "backward";
    const currentBwQ = isBackwardPhase ? (currentQ as BackwardQuestion) : null;
    const isMultiselect = currentBwQ?.type === "multiselect";

    // Reset selectedOptions khi chuyển câu
    useEffect(() => {
        setSelectedOptions([]);
    }, [currentIdx, phase]);

    // Helpers

    const goNext = useCallback(() => {
        if (currentIdx < totalQs - 1) {
            setCurrentIdx(i => i + 1);
        } else {
            if (phase === "screening") setPhase("analyzing_1");
            else if (phase === "full_questions") setPhase("analyzing_2");
            else if (phase === "backward") setPhase("analyzing_3");
        }
    }, [currentIdx, totalQs, phase]);

    // Handler: DASS yes/no/scale
    const handleDassSelect = useCallback((value: number) => {
        if (!currentQ) return;
        const updated = { ...answers, [(currentQ as any).id]: value };
        setAnswers(updated);
        goNext();
    }, [currentQ, answers, goNext]);

    // Handler: Backward yes/no
    const handleYesNo = useCallback((value: string) => {
        if (!currentBwQ) return;

        const updated = { ...backwardAns, [currentBwQ.key]: value };
        setBackwardAns(updated);

        // stop_if: nếu câu này trả lời = stop_if → kết thúc backward sớm
        if (currentBwQ.stop_if && value === currentBwQ.stop_if) {
            setPhase("analyzing_3");
            return;
        }

        goNext();
    }, [currentBwQ, backwardAns, goNext]);

    // Handler: Multiselect toggle
    const handleToggleOption = useCallback((optValue: string) => {
        setSelectedOptions(prev =>
            prev.includes(optValue)
                ? prev.filter(v => v !== optValue)
                : [...prev, optValue]
        );
    }, []);

    // Handler: Multiselect confirm
    const handleMultiselectConfirm = useCallback(() => {
        if (!currentBwQ) return;
        const updated = { ...backwardAns, [currentBwQ.key]: selectedOptions };
        setBackwardAns(updated);
        goNext();
    }, [currentBwQ, backwardAns, selectedOptions, goNext]);

    // Keyboard shortcuts
    useEffect(() => {
        if (["analyzing_1", "analyzing_2", "analyzing_3", "done"].includes(phase)) return;
        if (isMultiselect) return; // multiselect dùng mouse/touch

        const handler = (e: KeyboardEvent) => {
            if (isBackwardPhase) {
                if (e.key === "1") handleYesNo("yes");
                if (e.key === "2") handleYesNo("no");
            } else {
                const opt = ANSWER_OPTIONS.find(o => o.key === e.key);
                if (opt) handleDassSelect(opt.value);
            }
        };
        window.addEventListener("keydown", handler);
        return () => window.removeEventListener("keydown", handler);
    }, [phase, isBackwardPhase, isMultiselect, handleYesNo, handleDassSelect]);

    // Analysis callbacks
    const handleAnalysis1Done = async () => {
        try {
            console.log("answers before screening:", answers)
            const res = await apiScreening(answers);
            setScreeningRes(res);
            if (res.questions_needed.length > 0) {
                setPhase("full_questions");
                setCurrentIdx(0);
            } else {
                setPhase("analyzing_2");
            }
        } catch (e: any) { setError(e.message); }
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
        } catch (e: any) { setError(e.message); }
    };

    const handleAnalysis3Done = async () => {
        if (!fuzzyRes) return;
        try {
            const res = await apiBackwardChaining(fuzzyRes.profile, backwardAns, fuzzyRes);
            onComplete(res);
        } catch (e: any) { setError(e.message); }
    };

    if (phase === "analyzing_1") return <AnalysisScreen phase={1} onDone={handleAnalysis1Done} />;
    if (phase === "analyzing_2") return <AnalysisScreen phase={2} onDone={handleAnalysis2Done} />;
    if (phase === "analyzing_3") return <AnalysisScreen phase={3} onDone={handleAnalysis3Done} />;

    const phaseLabel =
        phase === "screening" ? "Sàng lọc ban đầu" :
        phase === "full_questions" ? "Đánh giá chuyên sâu" :
        "Xác nhận triệu chứng";

    // ─── Render: error ────────────────────────────────────────────────────────
    if (error) {
        return (
            <div className="min-h-screen bg-[#FAFAFA] flex items-center justify-center">
                <div className="text-center p-8">
                    <p className="text-red-500 font-bold mb-4">Có lỗi xảy ra: {error}</p>
                    <button
                        onClick={() => { setError(""); setPhase("screening"); setCurrentIdx(0); }}
                        className="text-blue-600 underline"
                    >
                        Thử lại
                    </button>
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
                        className={`p-2 rounded-full transition-all ${
                            currentIdx === 0
                                ? "opacity-0 pointer-events-none"
                                : "hover:bg-slate-200 text-slate-500"
                        }`}
                    >
                        <ArrowLeft size={24} />
                    </button>
                </div>

                <div className="w-1/3 flex flex-col items-center">
                    <span className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">
                        {phaseLabel}
                    </span>
                    <div className="w-full max-w-50 h-1.5 bg-slate-200 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-blue-600 rounded-full transition-all duration-500"
                            style={{ width: `${progress}%` }}
                        />
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
                        <h1 className="text-2xl md:text-4xl font-extrabold text-slate-900 mb-4 leading-[1.3]">
                            {currentQ.text}
                        </h1>

                        {/* ── MULTISELECT ── */}
                        {isMultiselect && currentBwQ?.options ? (
                            <>
                                {/* Hướng dẫn + counter */}
                                <div className="flex items-center justify-between mb-6">
                                    <p className="text-sm text-slate-500 flex items-center gap-1.5">
                                        <CheckSquare size={15} />
                                        Chọn tất cả triệu chứng bạn gặp phải
                                    </p>
                                    <span className="text-sm font-bold text-blue-600">
                                        {selectedOptions.length} / {currentBwQ.options.length} đã chọn
                                        {currentBwQ.min_count && (
                                            <span className="text-slate-400 font-normal ml-1">
                                                (cần ≥ {currentBwQ.min_count})
                                            </span>
                                        )}
                                    </span>
                                </div>

                                {/* Checkbox list */}
                                <div className="flex flex-col gap-3 mb-8">
                                    {currentBwQ.options.map(opt => {
                                        const checked = selectedOptions.includes(opt.value);
                                        return (
                                            <button
                                                key={opt.value}
                                                onClick={() => handleToggleOption(opt.value)}
                                                className={`group relative w-full flex items-start gap-4 p-4 md:p-5 border-2 rounded-2xl transition-all shadow-sm text-left focus:outline-none ${
                                                    checked
                                                        ? "bg-blue-50 border-blue-500 shadow-blue-500/10"
                                                        : "bg-white border-slate-100 hover:border-blue-300 hover:shadow-md"
                                                }`}
                                            >
                                                {/* Checkbox visual */}
                                                <div className={`shrink-0 mt-0.5 w-5 h-5 rounded-md border-2 flex items-center justify-center transition-all ${
                                                    checked
                                                        ? "bg-blue-600 border-blue-600"
                                                        : "border-slate-300 group-hover:border-blue-400"
                                                }`}>
                                                    {checked && (
                                                        <svg width="10" height="8" viewBox="0 0 10 8" fill="none">
                                                            <path d="M1 4L3.5 6.5L9 1" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                                                        </svg>
                                                    )}
                                                </div>
                                                <span className={`text-base font-medium leading-snug transition-colors ${
                                                    checked ? "text-blue-800" : "text-slate-700 group-hover:text-slate-900"
                                                }`}>
                                                    {opt.label}
                                                </span>
                                            </button>
                                        );
                                    })}
                                </div>

                                {/* Confirm button */}
                                <button
                                    onClick={handleMultiselectConfirm}
                                    className="w-full py-4 bg-blue-600 hover:bg-blue-700 text-white font-bold text-lg rounded-2xl transition-all shadow-md hover:shadow-blue-500/30 active:scale-[0.98]"
                                >
                                    Xác nhận ({selectedOptions.length} triệu chứng)
                                </button>
                            </>
                        ) : (
                            /* ── YES/NO hoặc DASS scale ── */
                            <>
                                <div className="mb-12" />
                                <div className="flex flex-col gap-4">
                                    {(isBackwardPhase ? YESNO_OPTIONS : ANSWER_OPTIONS).map(opt => (
                                        <button
                                            key={opt.key}
                                            onClick={() =>
                                                isBackwardPhase
                                                    ? handleYesNo(opt.value as string)
                                                    : handleDassSelect(opt.value as number)
                                            }
                                            className="group relative w-full flex items-center p-5 md:p-6 bg-white border-2 border-slate-100 hover:border-blue-500 rounded-2xl transition-all shadow-sm hover:shadow-md hover:shadow-blue-500/10 text-left focus:outline-none focus:border-blue-500"
                                        >
                                            <div className="absolute left-6 w-8 h-8 rounded-lg bg-slate-100 text-slate-500 font-bold flex items-center justify-center text-sm group-hover:bg-blue-100 group-hover:text-blue-600 transition-colors">
                                                {opt.key}
                                            </div>
                                            <div className="ml-14">
                                                <div className="text-lg font-bold text-slate-800 group-hover:text-blue-700 transition-colors">
                                                    {opt.label}
                                                </div>
                                                <div className="text-sm text-slate-500 mt-1 font-medium">
                                                    {opt.desc}
                                                </div>
                                            </div>
                                        </button>
                                    ))}
                                </div>
                            </>
                        )}
                    </div>
                )}
            </main>

            {/* BOTTOM BAR */}
            <footer className="px-6 py-8 flex flex-col md:flex-row items-center justify-between max-w-5xl mx-auto w-full text-slate-400">
                <div className="flex items-center gap-2 text-sm font-medium">
                    <ShieldCheck size={18} /> Mọi lựa chọn đều được ẩn danh
                </div>
                {!isMultiselect && (
                    <div className="hidden md:flex items-center gap-2 text-sm font-medium mt-4 md:mt-0">
                        <Keyboard size={18} /> Sử dụng phím số để chọn nhanh
                    </div>
                )}
            </footer>
        </div>
    );
}