import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

interface RCCChartProps {
    data: { date: string; rcc: number; waist: number }[];
}

const RCCChart: React.FC<RCCChartProps> = ({ data }) => {
    return (
        <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm h-80">
            <h3 className="text-lg font-bold text-slate-900 mb-4">Evolución de RCC y Cintura</h3>
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
                    <YAxis yAxisId="left" hide domain={['dataMin - 0.05', 'dataMax + 0.05']} />
                    <YAxis yAxisId="right" hide domain={['dataMin - 5', 'dataMax + 5']} />
                    <Tooltip
                        contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                        labelStyle={{ fontWeight: 'bold' }}
                    />
                    <Legend verticalAlign="top" height={36} />
                    <Line
                        yAxisId="left"
                        type="monotone"
                        dataKey="rcc"
                        name="RCC (Ratio)"
                        stroke="#8b5cf6"
                        strokeWidth={3}
                        dot={{ r: 4, fill: '#8b5cf6', strokeWidth: 2, stroke: '#fff' }}
                    />
                    <Line
                        yAxisId="right"
                        type="monotone"
                        dataKey="waist"
                        name="Cintura (cm)"
                        stroke="#f43f5e"
                        strokeWidth={2}
                        strokeDasharray="5 5"
                        dot={{ r: 3, fill: '#f43f5e', strokeWidth: 2, stroke: '#fff' }}
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};

export default RCCChart;
