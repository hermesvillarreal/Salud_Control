import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

interface Goals {
    calories?: number;
    protein?: number;
    carbs?: number;
    fat?: number;
    current_goal?: string;
}

interface NutrientsChartProps {
    data: { name: string; value: number; color: string }[];
    totalCalories: number;
    goals?: Goals;
}

const NutrientsChart: React.FC<NutrientsChartProps> = ({ data, totalCalories, goals }) => {
    // Helper to find value by name (flexible matching)
    // The chart data comes from analysis or logs, typically "Proteína", "Carbohidratos", "Grasas"
    const getValue = (namePart: string) => {
        const item = data.find(d => d.name.toLowerCase().includes(namePart.toLowerCase()));
        return item ? item.value : 0;
    };

    return (
        <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm h-auto min-h-[320px]">
            <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-bold text-slate-900">Macronutrientes Hoy</h3>
                {goals?.calories && (
                    <div className="text-right">
                        <div className="text-sm text-slate-500">Objetivo</div>
                        <div className="font-bold text-slate-900">{goals.calories} kcal</div>
                        {goals.current_goal && (
                            <div className="text-xs text-indigo-600 font-medium">{goals.current_goal}</div>
                        )}
                    </div>
                )}
            </div>

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
                    <span className="text-sm font-medium text-slate-500 uppercase tracking-wider">Kcal / {goals?.calories || '--'}</span>
                </div>
            </div>

            <div className="grid grid-cols-3 gap-2 mt-2 text-center">
                <div className="flex flex-col items-center">
                    <span className="text-xs font-medium text-slate-500">Proteína</span>
                    <div className="font-bold text-slate-800 mt-0.5" style={{ color: '#22c55e' }}>
                        {Math.round(getValue('ote'))}g{goals?.protein ? <span className="text-slate-400 font-normal">/{goals.protein}g</span> : ''}
                    </div>
                    {goals?.protein ? (
                        <span className="text-xs text-slate-500 font-medium">
                            {((getValue('ote') / goals.protein) * 100).toFixed(1)}%
                        </span>
                    ) : null}
                </div>
                <div className="flex flex-col items-center">
                    <span className="text-xs font-medium text-slate-500">Carbos</span>
                    <div className="font-bold text-slate-800 mt-0.5" style={{ color: '#ef4444' }}>
                        {Math.round(getValue('arb'))}g{goals?.carbs ? <span className="text-slate-400 font-normal">/{goals.carbs}g</span> : ''}
                    </div>
                    {goals?.carbs ? (
                        <span className="text-xs text-slate-500 font-medium">
                            {((getValue('arb') / goals.carbs) * 100).toFixed(1)}%
                        </span>
                    ) : null}
                </div>
                <div className="flex flex-col items-center">
                    <span className="text-xs font-medium text-slate-500">Grasas</span>
                    <div className="font-bold text-slate-800 mt-0.5" style={{ color: '#f59e0b' }}>
                        {Math.round(getValue('ras'))}g{goals?.fat ? <span className="text-slate-400 font-normal">/{goals.fat}g</span> : ''}
                    </div>
                    {goals?.fat ? (
                        <span className="text-xs text-slate-500 font-medium">
                            {((getValue('ras') / goals.fat) * 100).toFixed(1)}%
                        </span>
                    ) : null}
                </div>
            </div>
        </div>
    );
};

export default NutrientsChart;
