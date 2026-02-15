import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceArea } from 'recharts';

interface GlucoseChartProps {
    data: { date: string; glucose: number }[];
}

const GlucoseChart: React.FC<GlucoseChartProps> = ({ data }) => {
    return (
        <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm h-80">
            <h3 className="text-lg font-bold text-slate-900 mb-4">Glucosa en Sangre</h3>
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
                        axisLine={false}
                        tickLine={false}
                        tick={{ fill: '#94a3b8', fontSize: 12 }}
                    />
                    <Tooltip
                        contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                    />
                    {/* Rango normal: 70-130 mg/dL */}
                    <ReferenceArea y1={70} y2={130} fill="#22c55e" fillOpacity={0.05} />
                    <Line
                        type="monotone"
                        dataKey="glucose"
                        stroke="#8b5cf6"
                        strokeWidth={3}
                        dot={{ r: 4, fill: '#8b5cf6', strokeWidth: 2, stroke: '#fff' }}
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};

export default GlucoseChart;
