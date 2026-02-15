import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

interface PressureChartProps {
    data: { date: string; systolic: number; diastolic: number }[];
}

const PressureChart: React.FC<PressureChartProps> = ({ data }) => {
    return (
        <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm h-80">
            <h3 className="text-lg font-bold text-slate-900 mb-4">Presión Arterial</h3>
            <ResponsiveContainer width="100%" height="85%">
                <AreaChart data={data}>
                    <defs>
                        <linearGradient id="colorSistolica" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#ef4444" stopOpacity={0.1} />
                            <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                        </linearGradient>
                        <linearGradient id="colorDiastolica" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.1} />
                            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                    <XAxis
                        dataKey="date"
                        axisLine={false}
                        tickLine={false}
                        tick={{ fill: '#94a3b8', fontSize: 12 }}
                        dy={10}
                    />
                    <YAxis
                        axisLine={false}
                        tickLine={false}
                        tick={{ fill: '#94a3b8', fontSize: 12 }}
                    />
                    <Tooltip
                        contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                    />
                    <Legend verticalAlign="top" align="right" iconType="circle" />
                    <Area
                        name="Sistólica"
                        type="monotone"
                        dataKey="systolic"
                        stroke="#ef4444"
                        fillOpacity={1}
                        fill="url(#colorSistolica)"
                        strokeWidth={2}
                    />
                    <Area
                        name="Diastólica"
                        type="monotone"
                        dataKey="diastolic"
                        stroke="#3b82f6"
                        fillOpacity={1}
                        fill="url(#colorDiastolica)"
                        strokeWidth={2}
                    />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
};

export default PressureChart;
