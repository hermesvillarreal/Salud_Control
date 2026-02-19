import React from 'react';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
    ResponsiveContainer, Legend, ReferenceLine
} from 'recharts';

interface DayBalance {
    date: string;
    consumed: number;
    burned: number;
    net: number;
    goal: number | null;
}

interface CalorieBalanceChartProps {
    data: DayBalance[];
}

const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
        const consumed = payload.find((p: any) => p.dataKey === 'consumed')?.value ?? 0;
        const burned = payload.find((p: any) => p.dataKey === 'burned')?.value ?? 0;
        const goal = payload[0]?.payload?.goal;
        return (
            <div style={{
                background: 'white',
                borderRadius: '12px',
                boxShadow: '0 4px 16px rgba(0,0,0,0.1)',
                padding: '12px 16px',
                border: 'none',
                minWidth: 160
            }}>
                <p style={{ fontWeight: 700, color: '#1e293b', marginBottom: 6 }}>{label}</p>
                <p style={{ color: '#f97316', margin: '2px 0', fontSize: 13 }}>
                    🍽 Consumidas: <strong>{consumed} kcal</strong>
                </p>
                <p style={{ color: '#22c55e', margin: '2px 0', fontSize: 13 }}>
                    🏃 Quemadas: <strong>{burned} kcal</strong>
                </p>
                <p style={{ color: '#6366f1', margin: '2px 0', fontSize: 13 }}>
                    ⚡ Neto: <strong>{consumed - burned} kcal</strong>
                </p>
                {goal && (
                    <p style={{ color: '#94a3b8', margin: '4px 0 0', fontSize: 12, borderTop: '1px solid #f1f5f9', paddingTop: 4 }}>
                        🎯 Meta: {goal} kcal
                    </p>
                )}
            </div>
        );
    }
    return null;
};

const CalorieBalanceChart: React.FC<CalorieBalanceChartProps> = ({ data }) => {
    // Reference line value (use first non-null goal)
    const goalValue = data.find(d => d.goal !== null)?.goal ?? undefined;

    return (
        <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm h-72">
            <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-4">
                Últimos 7 días
            </h3>
            <ResponsiveContainer width="100%" height="85%">
                <BarChart data={data} barGap={4} barCategoryGap="30%">
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                    <XAxis
                        dataKey="date"
                        axisLine={false}
                        tickLine={false}
                        tick={{ fill: '#94a3b8', fontSize: 11 }}
                        dy={8}
                    />
                    <YAxis hide domain={[0, goalValue ? goalValue * 1.3 : 'auto']} />
                    <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(241,245,249,0.6)' }} />
                    <Legend
                        verticalAlign="top"
                        height={28}
                        formatter={(value) =>
                            value === 'consumed' ? 'Consumidas' : 'Quemadas'
                        }
                        wrapperStyle={{ fontSize: 12, color: '#64748b' }}
                    />
                    {goalValue !== undefined && (
                        <ReferenceLine
                            y={goalValue}
                            stroke="#94a3b8"
                            strokeDasharray="6 3"
                            strokeWidth={1.5}
                            label={{
                                value: `Meta ${goalValue}`,
                                position: 'insideTopRight',
                                fill: '#94a3b8',
                                fontSize: 10
                            }}
                        />
                    )}
                    <Bar
                        dataKey="consumed"
                        name="consumed"
                        fill="#f97316"
                        radius={[4, 4, 0, 0]}
                        maxBarSize={32}
                    />
                    <Bar
                        dataKey="burned"
                        name="burned"
                        fill="#22c55e"
                        radius={[4, 4, 0, 0]}
                        maxBarSize={32}
                    />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
};

export default CalorieBalanceChart;
