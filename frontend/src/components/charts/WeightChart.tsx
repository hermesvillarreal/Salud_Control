import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface WeightChartProps {
    data: { date: string; weight: number }[];
}

const WeightChart: React.FC<WeightChartProps> = ({ data }) => {
    return (
        <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm h-80">
            <h3 className="text-lg font-bold text-slate-900 mb-4">Evolución de Peso</h3>
            <ResponsiveContainer width="100%" height="85%">
                <LineChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                    <XAxis
                        dataKey="date"
                        axisLine={false}
                        tickLine={false}
                        tick={{ fill: '#94a3b8', fontSize: 12 }}
                        dy={10}
                    />
                    <YAxis
                        hide
                        domain={['dataMin - 2', 'dataMax + 2']}
                    />
                    <Tooltip
                        contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                        labelStyle={{ fontWeight: 'bold' }}
                    />
                    <Line
                        type="monotone"
                        dataKey="weight"
                        stroke="#2563eb"
                        strokeWidth={3}
                        dot={{ r: 4, fill: '#2563eb', strokeWidth: 2, stroke: '#fff' }}
                        activeDot={{ r: 6, strokeWidth: 0 }}
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};

export default WeightChart;
