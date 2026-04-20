"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import ResultDashboard from "@/app/components/ResultDashboard";
import { FinalResult } from "@/app/lib/api";

export default function ResultPage() {
    const router = useRouter();
    const [result, setResult] = useState<FinalResult | null>(null);

    useEffect(() => {
        const stored = sessionStorage.getItem("mindcompass_result");
        if (!stored) {
            router.replace("/assess");
            return;
        }
        try {
            setResult(JSON.parse(stored));
        } catch {
            router.replace("/assess");
        }
    }, [router]);

    if (!result) {
        return (
            <div className="min-h-screen bg-[#FAFAFA] flex items-center justify-center">
                <div className="flex gap-2">
                    {[0, 1, 2].map(i => (
                        <span key={i} className="w-2.5 h-2.5 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: `${i * 0.15}s` }} />
                    ))}
                </div>
            </div>
        );
    }

    return <ResultDashboard result={result} />;
}