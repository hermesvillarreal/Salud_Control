import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

interface NutrientsChartProps {
    data: { name: string; value: number; color: string }[];
}

const NutrientsChart: React.FC<NutrientsChartProps> = ({ data }) => {
    return (
        <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm h-80">
            <h3 className="text-lg font-bold text-slate-900 mb-4">Macronutrientes Hoy</h3>
            <ResponsiveContainer width="100%" height="85%">
                <PieChart>
                    <Pie
                        data={data}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={80}
                        paddingAngle={5}
                        dataKey="value"
                    >
                        {data.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                    </Pie>
                    <Tooltip
                        contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                    />
                    <Legend verticalAlign="bottom" align="center" iconType="circle" />
                </PieChart>
            </ResponsiveContainer>
        </div>
    );
};

export default NutrientsChart;
