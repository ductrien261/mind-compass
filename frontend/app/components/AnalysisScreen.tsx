"use client";

import { useEffect, useState } from "react";
import { BrainCircuit } from "lucide-react";

interface Props {
    phase: 1 | 2 | 3;  // 1=screening, 2=fuzzy, 3=backward
    onDone: () => void;
}

const MESSAGES: Record<number, string[]> = {
    1: [
        "Đang thu thập và mã hóa câu trả lời...",
        "Áp dụng Prolog Screening đánh giá ngưỡng...",
        "Hệ chuyên gia đang quyết định bước tiếp theo...",
    ],
    2: [
        "Đang mờ hóa điểm số (Fuzzification)...",
        "Chạy luật Gaussian & giải mờ (Centroid)...",
        "Forward Chaining nhận diện hồ sơ tâm lý...",
    ],
    3: [
        "Đang phân tích các dấu hiệu chuyên sâu...",
        "Tổng hợp báo cáo và đúc kết lời khuyên...",
    ],
};

export default function AnalysisScreen({ phase, onDone }: Props) {
    const messages = MESSAGES[phase];
    const [step, setStep] = useState(0);
    const [width, setWidth] = useState(0);

    useEffect(() => {
        setStep(0);
        setWidth(0);

        const totalTime = messages.length * 1600;
        const stepInterval = 1600;

        const stepTimer = setInterval(() => {
            setStep(prev => {
                if (prev + 1 >= messages.length) {
                    clearInterval(stepTimer);
                    return prev;
                }
                return prev + 1;
            });
        }, stepInterval);

        // Fake progress bar
        const progressTimer = setInterval(() => {
            setWidth(prev => Math.min(prev + 2, 98));
        }, totalTime / 50);

        const doneTimer = setTimeout(() => {
            clearInterval(progressTimer);
            setWidth(100);
            setTimeout(onDone, 300);
        }, totalTime);

        return () => {
            clearInterval(stepTimer);
            clearInterval(progressTimer);
            clearTimeout(doneTimer);
        };
    }, [phase]);

    return (
        <div className="flex flex-col min-h-screen bg-slate-900 text-white items-center justify-center p-6">
            <div className="max-w-md w-full flex flex-col items-center text-center">

                {/* Animated icon */}
                <div className="relative w-32 h-32 mb-12">
                    <div className="absolute inset-0 bg-blue-500/20 rounded-full blur-2xl animate-pulse" />
                    <div className="absolute inset-4 border-2 border-blue-500/30 rounded-full"
                        style={{ animation: "spin 4s linear infinite" }} />
                    <div className="absolute inset-4 border-2 border-dashed border-teal-400/40 rounded-full"
                        style={{ animation: "spin 6s linear infinite reverse" }} />
                    <div className="absolute inset-0 flex items-center justify-center z-10">
                        <BrainCircuit size={48} className="text-blue-400" />
                    </div>
                </div>

                {/* Status text */}
                <div className="h-16 flex items-center justify-center">
                    <h2
                        key={step}
                        className="text-xl md:text-2xl font-bold text-slate-100 transition-all duration-300"
                    >
                        {messages[step]}
                    </h2>
                </div>

                {/* Progress bar */}
                <div className="w-full h-1 bg-slate-800 rounded-full mt-8 overflow-hidden">
                    <div
                        className="h-full bg-linear-to-r from-blue-500 to-teal-400 rounded-full transition-all duration-300"
                        style={{ width: `${width}%` }}
                    />
                </div>

                <p className="text-slate-500 mt-8 text-sm">
                    Bạn đang làm rất tốt. Hãy hít một hơi thật sâu...
                </p>
            </div>
        </div>
    );
}