import React from 'react';
import { Scale, Activity, Droplets } from 'lucide-react';
import DashboardHeader from '../components/DashboardHeader';
import KpiCard from '../components/KpiCard';
import WeightChart from '../components/charts/WeightChart';
import PressureChart from '../components/charts/PressureChart';
import GlucoseChart from '../components/charts/GlucoseChart';
import NutrientsChart from '../components/charts/NutrientsChart';

// Datos mock para demostración
const mockWeightData = [
    { date: '01 Feb', weight: 82.5 },
    { date: '04 Feb', weight: 81.8 },
    { date: '07 Feb', weight: 81.5 },
    { date: '10 Feb', weight: 80.9 },
    { date: '13 Feb', weight: 80.2 },
    { date: '15 Feb', weight: 79.8 },
];

const mockPressureData = [
    { date: '01 Feb', systolic: 120, diastolic: 80 },
    { date: '04 Feb', systolic: 122, diastolic: 82 },
    { date: '07 Feb', systolic: 118, diastolic: 78 },
    { date: '10 Feb', systolic: 125, diastolic: 85 },
    { date: '13 Feb', systolic: 121, diastolic: 81 },
    { date: '15 Feb', systolic: 119, diastolic: 79 },
];

const mockGlucoseData = [
    { date: '01 Feb', glucose: 95 },
    { date: '04 Feb', glucose: 102 },
    { date: '07 Feb', glucose: 98 },
    { date: '10 Feb', glucose: 115 },
    { date: '13 Feb', glucose: 105 },
    { date: '15 Feb', glucose: 92 },
];

const mockNutrientsData = [
    { name: 'Proteína', value: 30, color: '#3b82f6' },
    { name: 'Carbos', value: 45, color: '#22c55e' },
    { name: 'Grasas', value: 25, color: '#f59e0b' },
];

const Dashboard: React.FC = () => {
    return (
        <div className="min-h-screen bg-slate-50 p-4 md:p-8">
            <div className="max-w-7xl mx-auto">
                <DashboardHeader />

                {/* Tarjetas KPI */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <KpiCard
                        title="Peso Actual"
                        value="79.8"
                        unit="kg"
                        trend="down"
                        trendValue="1.2%"
                        icon={<Scale className="w-6 h-6" />}
                        color="blue"
                    />
                    <KpiCard
                        title="Última Presión"
                        value="119/79"
                        unit="mmHg"
                        trend="down"
                        trendValue="2%"
                        icon={<Activity className="w-6 h-6" />}
                        color="red"
                    />
                    <KpiCard
                        title="Promedio Glucosa"
                        value="98"
                        unit="mg/dL"
                        trend="stable"
                        trendValue="0.5%"
                        icon={<Droplets className="w-6 h-6" />}
                        color="purple"
                    />
                </div>

                {/* Gráficos */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <WeightChart data={mockWeightData} />
                    <PressureChart data={mockPressureData} />
                    <GlucoseChart data={mockGlucoseData} />
                    <NutrientsChart data={mockNutrientsData} />
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
