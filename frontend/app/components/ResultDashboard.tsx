"use client";

import { FinalResult, DimensionResult } from "@/app/lib/api";
import RadarChart from "./RadarChart";
import {
    Brain, Wind, Headphones, CalendarPlus, Download,
    Sparkles, Activity, HeartPulse, ShieldCheck,
    CheckCircle2, Target, GitMerge, ChevronRight,
} from "lucide-react";

const DIM_CONFIG = {
    depression: {
        label: "Trầm cảm (Depression)", icon: <Activity size={20} />,
        colorClass: "bg-blue-500", colorHex: "#3b82f6", bgSoft: "bg-blue-50", text: "text-blue-600",
        radarLabel: "Trầm cảm",
    },
    anxiety: {
        label: "Lo âu (Anxiety)", icon: <HeartPulse size={20} />,
        colorClass: "bg-orange-500", colorHex: "#f97316", bgSoft: "bg-orange-50", text: "text-orange-600",
        radarLabel: "Lo âu",
    },
    stress: {
        label: "Căng thẳng (Stress)", icon: <Wind size={20} />,
        colorClass: "bg-emerald-500", colorHex: "#10b981", bgSoft: "bg-emerald-50", text: "text-emerald-600",
        radarLabel: "Căng thẳng",
    },
};

const LEVEL_VI: Record<string, string> = {
    "Normal": "Bình thường",
    "Mild": "Mức độ Nhẹ",
    "Moderate": "Mức độ Vừa",
    "Severe": "Mức độ Nặng",
    "Extremely Severe": "Cực kỳ Nặng",
};

const PROFILE_VI: Record<string, string> = {
    "low_risk": "Ổn định — Không có dấu hiệu đáng lo ngại",
    "pure_depression": "Nghi ngờ Trầm cảm (MDD)",
    "gad_stress_dominant": "Nghi ngờ Rối loạn Lo âu lan tỏa (GAD)",
    "panic_disorder": "Nghi ngờ Rối loạn Hoảng sợ (Panic Disorder)",
    "social_anxiety": "Nghi ngờ Lo âu xã hội (Social Anxiety)",
    "mdd_anxious_distress": "Nghi ngờ Trầm cảm kèm Lo âu",
    "maladaptive_crisis": "Khủng hoảng toàn diện — Cần hỗ trợ khẩn cấp",
};

interface Props { result: FinalResult }

export default function ResultDashboard({ result }: Props) {
    const dims = result.dimensions;

    const radarScores = (["depression", "anxiety", "stress"] as const).map(dim => ({
        label: DIM_CONFIG[dim].radarLabel,
        value: Math.round((dims[dim]?.fuzzy_value ?? 0) / 4 * 100),
        colorHex: DIM_CONFIG[dim].colorHex,
    }));

    const profileLabel = PROFILE_VI[result.profile] ?? result.profile;

    // Lời khuyên chuyên gia (từ backward chaining details)
    const evidence = result.confirm_detail
        .filter(d => d.answer === "yes")
        .map(d => d.text)
        .slice(0, 3);

    return (
        <div className="min-h-screen bg-[#FAFAFA] font-sans text-slate-900 p-4 md:p-8 pb-24">

            {/* HEADER */}
            <header className="max-w-7xl mx-auto mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4">
                <div>
                    <div className="flex items-center gap-2 text-blue-600 font-extrabold text-xl tracking-tighter mb-4">
                        MindCompass<span className="text-orange-500">.</span>
                    </div>
                    <h1 className="text-3xl md:text-5xl font-extrabold text-slate-900 mb-3 tracking-tight">
                        Bản đồ Tâm trí của bạn
                    </h1>
                    <p className="text-slate-500 font-medium flex items-center gap-2">
                        <ShieldCheck size={18} className="text-teal-500" />
                        Phân tích hoàn tất • Bảo mật ẩn danh
                    </p>
                </div>
                <button className="flex items-center justify-center gap-2 bg-slate-900 text-white px-6 py-3 rounded-full font-bold text-sm hover:bg-slate-800 transition-all">
                    <Download size={18} /> Lưu báo cáo PDF
                </button>
            </header>

            <div className="max-w-7xl mx-auto grid grid-cols-1 xl:grid-cols-12 gap-6">

                {/* AI INSIGHT HERO */}
                <div className="col-span-1 xl:col-span-12">
                    <div className="bg-linear-to-br from-slate-900 to-slate-800 rounded-[2.5rem] p-8 md:p-12 relative overflow-hidden shadow-2xl shadow-slate-900/10">
                        <div className="absolute top-0 right-0 w-96 h-96 bg-blue-500/20 rounded-full blur-[80px] -translate-y-1/2 translate-x-1/3" />
                        <div className="absolute bottom-0 left-0 w-64 h-64 bg-orange-500/20 rounded-full blur-[60px] translate-y-1/2 -translate-x-1/4" />
                        <div className="relative z-10">
                            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/10 border border-white/10 text-blue-300 text-xs font-bold mb-6 uppercase tracking-wider">
                                <Sparkles size={16} className="animate-pulse" /> Đúc kết từ AI Hệ chuyên gia
                            </div>
                            <h2 className="text-2xl md:text-3xl font-medium text-white mb-4 leading-relaxed">
                                "{profileLabel}"
                            </h2>
                            <p className="text-slate-400 text-lg leading-relaxed max-w-4xl">
                                {result.profile_advice}
                            </p>
                        </div>
                    </div>
                </div>

                {/* RADAR CHART */}
                <div className="col-span-1 xl:col-span-4">
                    <div className="bg-white rounded-[2.5rem] p-8 border border-slate-200 h-full shadow-sm flex flex-col items-center">
                        <div className="w-full mb-4">
                            <h3 className="text-xl font-bold text-slate-900">Mạng lưới Cảm xúc</h3>
                            <p className="text-sm text-slate-500 mt-1">Phân bố 3 chiều tâm lý</p>
                        </div>
                        <div className="flex-1 flex items-center justify-center w-full">
                            <RadarChart scores={radarScores} />
                        </div>
                    </div>
                </div>

                {/* DASS DETAIL */}
                <div className="col-span-1 xl:col-span-8">
                    <div className="bg-white rounded-[2.5rem] p-8 md:p-10 border border-slate-200 h-full shadow-sm">
                        <div className="flex items-center justify-between mb-8">
                            <div>
                                <h3 className="text-2xl font-bold text-slate-900">Chi tiết Chỉ số DASS-42</h3>
                                <p className="text-slate-500 font-medium mt-1">Định lượng qua thuật toán Logic Mờ</p>
                            </div>
                            <div className="w-12 h-12 bg-blue-50 rounded-2xl flex items-center justify-center text-blue-500">
                                <Brain size={24} />
                            </div>
                        </div>

                        <div className="space-y-8">
                            {(["depression", "anxiety", "stress"] as const).map((dim, idx) => {
                                const cfg = DIM_CONFIG[dim];
                                const r = dims[dim] as DimensionResult;
                                if (!r) return null;
                                const pct = Math.round(r.fuzzy_value / 4 * 100);

                                return (
                                    <div key={dim}>
                                        <div className="flex justify-between items-end mb-3">
                                            <div className="flex items-center gap-3">
                                                <div className={`w-12 h-12 rounded-2xl flex items-center justify-center ${cfg.bgSoft} ${cfg.text}`}>
                                                    {cfg.icon}
                                                </div>
                                                <div>
                                                    <span className="font-bold text-slate-800 text-lg block">{cfg.label}</span>
                                                    <span className="text-sm text-slate-500">{r.total_score}/42 điểm • Fuzzy: {r.fuzzy_value.toFixed(3)}</span>
                                                </div>
                                            </div>
                                            <span className={`px-4 py-1.5 rounded-full font-bold text-xs ${cfg.bgSoft} ${cfg.text}`}>
                                                {LEVEL_VI[r.label] ?? r.label}
                                            </span>
                                        </div>

                                        <div className="relative pt-2 pb-6">
                                            <div className="h-3 w-full bg-slate-100 rounded-full overflow-hidden">
                                                <div
                                                    className={`h-full ${cfg.colorClass} rounded-full transition-all duration-1000`}
                                                    style={{ width: `${pct}%` }}
                                                />
                                            </div>
                                            <div className="absolute top-6 left-0 w-full flex justify-between text-[10px] font-bold text-slate-400">
                                                <span className="w-1/4 text-left">Bình thường</span>
                                                <span className="w-1/4 text-center border-l border-slate-200 pl-1">Nhẹ</span>
                                                <span className="w-1/4 text-center border-l border-slate-200 pl-1">Vừa</span>
                                                <span className="w-1/4 text-right border-l border-slate-200">Nặng</span>
                                            </div>
                                        </div>

                                        <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                                            <p className="text-sm text-slate-600 leading-relaxed">
                                                <strong className="text-slate-800">Lời khuyên:</strong> {r.advice}
                                            </p>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                </div>

                {/* EXPERT EVIDENCE */}
                <div className="col-span-1 xl:col-span-7">
                    <div className="bg-orange-50 rounded-[2.5rem] p-8 md:p-10 border border-orange-100 h-full flex flex-col md:flex-row gap-8 relative overflow-hidden">
                        <div className="absolute top-0 right-0 w-64 h-64 bg-orange-200/40 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3" />

                        <div className="relative z-10 flex-1">
                            <div className="w-14 h-14 bg-white text-orange-500 rounded-2xl flex items-center justify-center mb-6 shadow-sm border border-orange-100">
                                <GitMerge size={28} />
                            </div>
                            <h4 className="text-xs font-extrabold text-orange-800/60 uppercase tracking-widest mb-2">
                                Kết quả Chẩn đoán
                            </h4>
                            <h3 className="text-2xl md:text-3xl font-black text-orange-900 mb-4 leading-tight">
                                {profileLabel}
                            </h3>
                            <p className="text-orange-800/80 font-medium leading-relaxed">
                                {result.profile_verified
                                    ? `Đã xác nhận với ${result.confirm_score}/${result.confirm_total} triệu chứng đặc trưng.`
                                    : "Không đủ tiêu chí chẩn đoán. Đây là đánh giá sơ bộ, không thay thế tư vấn chuyên gia."}
                            </p>
                        </div>

                        {evidence.length > 0 && (
                            <div className="relative z-10 flex-1 bg-white/60 backdrop-blur-sm rounded-3xl p-6 border border-white">
                                <h4 className="font-bold text-orange-900 mb-4 flex items-center gap-2">
                                    <Target size={18} className="text-orange-500" /> Cơ sở phân tích
                                </h4>
                                <ul className="space-y-3">
                                    {evidence.map((ev, i) => (
                                        <li key={i} className="flex items-start gap-3">
                                            <div className="mt-0.5 bg-orange-100 text-orange-600 rounded-full p-1 shrink-0">
                                                <CheckCircle2 size={14} strokeWidth={3} />
                                            </div>
                                            <span className="text-sm font-medium text-orange-900/80 leading-snug">{ev}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </div>
                </div>

                {/* ACTION PLAN */}
                <div className="col-span-1 xl:col-span-5">
                    <div className="bg-white rounded-[2.5rem] p-8 md:p-10 border border-slate-200 h-full shadow-sm">
                        <h3 className="text-2xl font-bold text-slate-900 mb-2">Kế hoạch phục hồi</h3>
                        <p className="text-slate-500 font-medium mb-8">3 bước để lấy lại sự cân bằng</p>

                        <div className="space-y-4">
                            {[
                                { icon: <Wind size={20} />, color: "bg-blue-100 text-blue-600", title: "Cắt cơn lo âu ngay hôm nay", desc: "Học bài tập hít thở 4-7-8 khi cảm thấy căng thẳng.", border: "border-blue-100" },
                                { icon: <Headphones size={20} />, color: "bg-emerald-100 text-emerald-600", title: "Chữa lành thụ động", desc: "Nghe Playlist tần số Alpha khi ngủ để thư giãn.", border: "border-emerald-100" },
                                { icon: <CalendarPlus size={20} />, color: "bg-orange-100 text-orange-600", title: "Gặp chuyên gia", desc: "Nên đặt lịch tham vấn trong tuần tới.", border: "border-orange-200 bg-orange-50" },
                            ].map((step, i) => (
                                <div key={i} className={`flex items-center gap-4 p-4 rounded-2xl border ${step.border} transition-colors cursor-pointer hover:shadow-sm`}>
                                    <div className={`w-12 h-12 rounded-2xl flex items-center justify-center shrink-0 ${step.color}`}>
                                        {step.icon}
                                    </div>
                                    <div>
                                        <h4 className="font-bold text-slate-800 text-sm">{step.title}</h4>
                                        <p className="text-xs text-slate-500 mt-0.5">{step.desc}</p>
                                    </div>
                                    <ChevronRight size={16} className="ml-auto text-slate-400" />
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

            </div>
        </div>
    );
}