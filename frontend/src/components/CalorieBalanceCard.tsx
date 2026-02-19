import React from 'react';
import { Flame, Dumbbell, Target, TrendingUp } from 'lucide-react';

interface TodayBalance {
    consumed: number;
    burned: number;
    net: number;
    goal: number | null;
    goal_source: string;
    compliance_pct: number | null;
}

interface TdeeDetail {
    bmr: number;
    tdee: number;
    activity_factor: number | null;
}

interface CalorieBalanceCardProps {
    today: TodayBalance;
    tdee_detail?: TdeeDetail | null;
}

const getStatus = (pct: number | null): { label: string; color: string; bg: string; border: string } => {
    if (pct === null) return { label: 'Sin meta', color: '#94a3b8', bg: '#f8fafc', border: '#e2e8f0' };
    if (pct < 70) return { label: 'Bajo consumo', color: '#f59e0b', bg: '#fffbeb', border: '#fde68a' };
    if (pct <= 105) return { label: 'En objetivo ✓', color: '#22c55e', bg: '#f0fdf4', border: '#bbf7d0' };
    if (pct <= 120) return { label: 'Ligeramente alto', color: '#f97316', bg: '#fff7ed', border: '#fed7aa' };
    return { label: 'Exceso calórico', color: '#ef4444', bg: '#fef2f2', border: '#fecaca' };
};

const MetricBlock: React.FC<{
    icon: React.ReactNode;
    label: string;
    value: number;
    color: string;
    bg: string;
}> = ({ icon, label, value, color, bg }) => (
    <div className="flex flex-col items-center justify-center p-3 rounded-xl" style={{ background: bg }}>
        <div style={{ color }} className="mb-1">{icon}</div>
        <span className="text-xs text-slate-500 font-medium">{label}</span>
        <span className="text-lg font-bold mt-0.5" style={{ color }}>
            {value.toLocaleString()}
        </span>
        <span className="text-xs text-slate-400">kcal</span>
    </div>
);

const CalorieBalanceCard: React.FC<CalorieBalanceCardProps> = ({ today, tdee_detail }) => {
    const pct = today.compliance_pct;
    const status = getStatus(pct);
    const clampedPct = pct !== null ? Math.min(pct, 100) : 0;

    // Progress bar gradient based on status
    const progressColor =
        pct === null ? '#cbd5e1' :
            pct < 70 ? '#f59e0b' :
                pct <= 105 ? '#22c55e' :
                    pct <= 120 ? '#f97316' :
                        '#ef4444';

    return (
        <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-5">
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-orange-50 flex items-center justify-center">
                        <Flame className="w-4 h-4 text-orange-500" />
                    </div>
                    <h3 className="text-base font-bold text-slate-900">Balance Calórico del Día</h3>
                </div>
                <span
                    className="text-xs font-semibold px-3 py-1 rounded-full"
                    style={{ color: status.color, background: status.bg, border: `1px solid ${status.border}` }}
                >
                    {status.label}
                </span>
            </div>

            {/* Metric blocks */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-5">
                <MetricBlock
                    icon={<Flame className="w-4 h-4" />}
                    label="Consumidas"
                    value={today.consumed}
                    color="#f97316"
                    bg="#fff7ed"
                />
                <MetricBlock
                    icon={<Dumbbell className="w-4 h-4" />}
                    label="Quemadas"
                    value={today.burned}
                    color="#22c55e"
                    bg="#f0fdf4"
                />
                <MetricBlock
                    icon={<TrendingUp className="w-4 h-4" />}
                    label="Neto"
                    value={today.net}
                    color="#6366f1"
                    bg="#eef2ff"
                />
                <MetricBlock
                    icon={<Target className="w-4 h-4" />}
                    label="Meta"
                    value={today.goal ?? 0}
                    color="#64748b"
                    bg="#f8fafc"
                />
            </div>

            {/* Progress bar */}
            <div className="mb-2">
                <div className="flex justify-between items-center mb-1.5">
                    <span className="text-xs text-slate-500 font-medium">Cumplimiento de la meta</span>
                    <span className="text-sm font-bold" style={{ color: progressColor }}>
                        {pct !== null ? `${pct}%` : '--'}
                    </span>
                </div>
                <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden">
                    <div
                        className="h-full rounded-full transition-all duration-700"
                        style={{
                            width: `${clampedPct}%`,
                            background: progressColor,
                        }}
                    />
                </div>
            </div>

            {/* Goal source note */}
            {today.goal_source === 'tdee' && tdee_detail && (
                <div className="mt-3 pt-3 border-t border-slate-100">
                    <p className="text-xs font-semibold text-slate-500 mb-1.5 flex items-center gap-1">
                        <Target className="w-3 h-3" />
                        Meta basada en último cálculo TDEE
                    </p>
                    <div className="flex gap-4 text-xs text-slate-500">
                        <span>
                            <span className="font-medium text-slate-700">BMR</span>&nbsp;
                            {tdee_detail.bmr.toLocaleString()} kcal
                        </span>
                        <span>
                            <span className="font-medium text-slate-700">TDEE</span>&nbsp;
                            {tdee_detail.tdee.toLocaleString()} kcal
                        </span>
                        {tdee_detail.activity_factor && (
                            <span>
                                <span className="font-medium text-slate-700">Factor Act.</span>&nbsp;
                                ×{tdee_detail.activity_factor}
                            </span>
                        )}
                    </div>
                    <p className="text-xs text-slate-400 mt-1">Configura tu meta en el perfil para mayor control</p>
                </div>
            )}
            {!today.goal && (
                <p className="text-xs text-amber-500 mt-2 flex items-center gap-1">
                    <Target className="w-3 h-3" />
                    Sin meta calórica configurada · Usa la calculadora TDEE para establecer una
                </p>
            )}
        </div>
    );
};

export default CalorieBalanceCard;
