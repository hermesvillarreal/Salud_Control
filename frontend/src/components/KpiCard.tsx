import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

interface KpiCardProps {
    title: string;
    value: string | number;
    unit?: string;
    trend?: 'up' | 'down' | 'stable';
    trendValue?: string;
    icon: React.ReactNode;
    color: 'blue' | 'green' | 'red' | 'orange' | 'purple';
}

const colorMap = {
    blue: 'bg-blue-50 text-blue-600 border-blue-100',
    green: 'bg-green-50 text-green-600 border-green-100',
    red: 'bg-red-50 text-red-600 border-red-100',
    orange: 'bg-orange-50 text-orange-600 border-orange-100',
    purple: 'bg-purple-50 text-purple-600 border-purple-100',
};

const KpiCard: React.FC<KpiCardProps> = ({
    title,
    value,
    unit,
    trend,
    trendValue,
    icon,
    color
}) => {
    return (
        <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start mb-4">
                <div className={cn("p-3 rounded-xl border", colorMap[color])}>
                    {icon}
                </div>
                {trend && (
                    <div className={cn(
                        "flex items-center gap-1 text-xs font-bold px-2 py-1 rounded-full",
                        trend === 'up' ? "bg-red-50 text-red-600" :
                            trend === 'down' ? "bg-green-50 text-green-600" :
                                "bg-slate-50 text-slate-600"
                    )}>
                        {trend === 'up' && <TrendingUp className="w-3 h-3" />}
                        {trend === 'down' && <TrendingDown className="w-3 h-3" />}
                        {trend === 'stable' && <Minus className="w-3 h-3" />}
                        {trendValue}
                    </div>
                )}
            </div>
            <div>
                <p className="text-sm font-medium text-slate-500 mb-1">{title}</p>
                <div className="flex items-baseline gap-1">
                    <h3 className="text-2xl font-bold text-slate-900">{value}</h3>
                    {unit && <span className="text-sm font-medium text-slate-400">{unit}</span>}
                </div>
            </div>
        </div>
    );
};

export default KpiCard;
