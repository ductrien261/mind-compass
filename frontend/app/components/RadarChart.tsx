"use client";

interface RadarScore {
    label: string;
    value: number;   // 0-100
    colorHex: string;
}

export default function RadarChart({ scores }: { scores: RadarScore[] }) {
    const size = 240;
    const center = size / 2;
    const radius = size / 2 - 35;

    const getCoords = (value: number, angleIndex: number) => {
        const angle = Math.PI / 2 - angleIndex * ((2 * Math.PI) / 3);
        const distance = (value / 100) * radius;
        return { x: center + distance * Math.cos(angle), y: center - distance * Math.sin(angle) };
    };

    const points = scores.map((s, i) => getCoords(s.value, i));
    const maxPoints = scores.map((_, i) => getCoords(100, i));
    const midPoints = scores.map((_, i) => getCoords(50, i));

    const toPath = (pts: { x: number; y: number }[]) => pts.map(p => `${p.x},${p.y}`).join(" ");

    return (
        <div className="flex items-center justify-center w-full h-full min-h-62.5">
            <svg width={size} height={size} className="overflow-visible">
                {/* Grid */}
                <polygon points={toPath(maxPoints)} fill="none" stroke="#e2e8f0" strokeWidth="1" strokeDasharray="4 4" />
                <polygon points={toPath(midPoints)} fill="none" stroke="#e2e8f0" strokeWidth="1" strokeDasharray="4 4" />
                {maxPoints.map((p, i) => (
                    <line key={i} x1={center} y1={center} x2={p.x} y2={p.y} stroke="#e2e8f0" strokeWidth="1" />
                ))}

                {/* Data polygon */}
                <polygon
                    points={toPath(points)}
                    fill="rgba(59,130,246,0.2)"
                    stroke="#3b82f6"
                    strokeWidth="2.5"
                    style={{ transition: "all 0.6s ease" }}
                />

                {/* Dots */}
                {points.map((p, i) => (
                    <circle key={i} cx={p.x} cy={p.y} r="5" fill={scores[i].colorHex} />
                ))}

                {/* Labels */}
                {maxPoints.map((p, i) => {
                    const offsets = [
                        { dx: 0, dy: -15 },
                        { dx: 40, dy: 5 },
                        { dx: -40, dy: 5 },
                    ];
                    return (
                        <text
                            key={`label-${i}`}
                            x={p.x + offsets[i].dx}
                            y={p.y + offsets[i].dy}
                            textAnchor="middle"
                            fontSize="11"
                            fontWeight="600"
                            fill="#64748b"
                        >
                            {scores[i].label}
                        </text>
                    );
                })}
            </svg>
        </div>
    );
}