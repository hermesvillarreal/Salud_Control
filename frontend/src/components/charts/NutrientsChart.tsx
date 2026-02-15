import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

interface NutrientsChartProps {
    data: { name: string; value: number; color: string }[];
    totalCalories: number;
}

const NutrientsChart: React.FC<NutrientsChartProps> = ({ data, totalCalories }) => {
    return (
        <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm h-80">
            <h3 className="text-lg font-bold text-slate-900 mb-4">Macronutrientes Hoy</h3>
            <div className="relative h-64">
                <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                        <Pie
                            data={data}
                            cx="50%"
                            cy="50%"
                            innerRadius={65}
                            outerRadius={85}
                            paddingAngle={5}
                            dataKey="value"
                            stroke="none"
                        >
                            {data.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                        </Pie>
                        <Tooltip
                            contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                        />
                    </PieChart>
                </ResponsiveContainer>
                <div className="absolute inset-x-0 bottom-24 flex flex-col items-center justify-center pointer-events-none">
                    <span className="text-3xl font-bold text-slate-900">{totalCalories}</span>
                    <span className="text-sm font-medium text-slate-500 uppercase tracking-wider">Kcal</span>
                </div>
            </div>
            <div className="flex justify-center mt-2 gap-4">
                {data.map((entry, index) => (
                    <div key={index} className="flex items-center gap-1.5">
                        <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: entry.color }} />
                        <span className="text-xs font-medium text-slate-600">{entry.name}</span>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default NutrientsChart;
