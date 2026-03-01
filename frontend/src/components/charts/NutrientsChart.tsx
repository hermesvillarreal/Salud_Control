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

            <div className="flex justify-around mt-4">
                <div className="flex flex-col items-center">
                    <span className="text-xs font-medium text-slate-500 mb-2">Proteína</span>
                    <CircularProgress
                        value={getValue('ote')}
                        max={goals?.protein}
                        color="#22c55e"
                    >
                        <div className="flex flex-col items-center">
                            <div className="font-bold text-slate-800 text-sm">
                                {Math.round(getValue('ote'))}g{goals?.protein ? <span className="text-slate-400 font-normal text-xs">/{goals.protein}g</span> : ''}
                            </div>
                            {goals?.protein ? (
                                <span className="text-[10px] text-slate-500 font-medium leading-none mt-0.5">
                                    {((getValue('ote') / goals.protein) * 100).toFixed(1)}%
                                </span>
                            ) : null}
                        </div>
                    </CircularProgress>
                </div>
                <div className="flex flex-col items-center">
                    <span className="text-xs font-medium text-slate-500 mb-2">Carbos</span>
                    <CircularProgress
                        value={getValue('arb')}
                        max={goals?.carbs}
                        color="#ef4444"
                    >
                        <div className="flex flex-col items-center">
                            <div className="font-bold text-slate-800 text-sm">
                                {Math.round(getValue('arb'))}g{goals?.carbs ? <span className="text-slate-400 font-normal text-xs">/{goals.carbs}g</span> : ''}
                            </div>
                            {goals?.carbs ? (
                                <span className="text-[10px] text-slate-500 font-medium leading-none mt-0.5">
                                    {((getValue('arb') / goals.carbs) * 100).toFixed(1)}%
                                </span>
                            ) : null}
                        </div>
                    </CircularProgress>
                </div>
                <div className="flex flex-col items-center">
                    <span className="text-xs font-medium text-slate-500 mb-2">Grasas</span>
                    <CircularProgress
                        value={getValue('ras')}
                        max={goals?.fat}
                        color="#f59e0b"
                    >
                        <div className="flex flex-col items-center">
                            <div className="font-bold text-slate-800 text-sm">
                                {Math.round(getValue('ras'))}g{goals?.fat ? <span className="text-slate-400 font-normal text-xs">/{goals.fat}g</span> : ''}
                            </div>
                            {goals?.fat ? (
                                <span className="text-[10px] text-slate-500 font-medium leading-none mt-0.5">
                                    {((getValue('ras') / goals.fat) * 100).toFixed(1)}%
                                </span>
                            ) : null}
                        </div>
                    </CircularProgress>
                </div>
            </div>
        </div>
    );
};

// SVG Circular Progress
const CircularProgress = ({ value, max, color, children }: { value: number, max?: number, color: string, children: React.ReactNode }) => {
    const size = 80;
    const strokeWidth = 6;
    const radius = (size - strokeWidth) / 2;
    const circumference = radius * 2 * Math.PI;

    // Si no hay maximo, asume que esta al 0% para no llenar todo (o se podria omitir el anillo de progreso)
    const percentage = max ? Math.min((value / max) * 100, 100) : 0;
    const strokeDashoffset = circumference - (percentage / 100) * circumference;

    return (
        <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
            {max !== undefined ? (
                <svg width={size} height={size} className="absolute inset-0 transform -rotate-90">
                    {/* Background circle */}
                    <circle
                        cx={size / 2}
                        cy={size / 2}
                        r={radius}
                        fill="transparent"
                        stroke="#f1f5f9" // slate-100
                        strokeWidth={strokeWidth}
                    />
                    {/* Progress circle */}
                    <circle
                        cx={size / 2}
                        cy={size / 2}
                        r={radius}
                        fill="transparent"
                        stroke={color}
                        strokeWidth={strokeWidth}
                        strokeDasharray={circumference}
                        strokeDashoffset={strokeDashoffset}
                        strokeLinecap="round"
                        className="transition-all duration-1000 ease-out"
                    />
                </svg>
            ) : null}
            <div className="relative z-10 flex items-center justify-center w-full h-full">
                {children}
            </div>
        </div>
    );
};

export default NutrientsChart;
