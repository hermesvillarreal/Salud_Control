import React, { useState, useEffect } from 'react';
import { Scale, Activity, Droplets } from 'lucide-react';
import DashboardHeader from '../components/DashboardHeader';
import KpiCard from '../components/KpiCard';
import WeightChart from '../components/charts/WeightChart';
import PressureChart from '../components/charts/PressureChart';
import GlucoseChart from '../components/charts/GlucoseChart';
import NutrientsChart from '../components/charts/NutrientsChart';
import HealthModal from '../components/HealthModal';
import { useHealthStore } from '../stores/healthStore';

const Dashboard: React.FC = () => {
    const { metrics, fetchMetrics, fetchFoodLogs, foodLogs } = useHealthStore();

    // Modal states
    const [isWeightModalOpen, setIsWeightModalOpen] = useState(false);
    const [isPressureModalOpen, setIsPressureModalOpen] = useState(false);
    const [isGlucoseModalOpen, setIsGlucoseModalOpen] = useState(false);

    useEffect(() => {
        fetchMetrics();
        fetchFoodLogs();
    }, [fetchMetrics, fetchFoodLogs]);

    const handleRegisterPeso = () => {
        setIsWeightModalOpen(true);
    };

    const handleRegisterPresion = () => {
        setIsPressureModalOpen(true);
    };

    const handleRegisterGlucosa = () => {
        setIsGlucoseModalOpen(true);
    };

    // Derived data for charts (fallback to mock if empty for demonstration, but aiming for real)
    const weightData = metrics
        .filter(m => m.type === 'peso')
        .map(m => ({ date: new Date(m.timestamp).toLocaleDateString([], { day: '2-digit', month: 'short' }), weight: m.value }))
        .reverse() || [];

    const pressureData = metrics
        .filter(m => m.type === 'presion')
        .map(m => ({ date: new Date(m.timestamp).toLocaleDateString([], { day: '2-digit', month: 'short' }), systolic: m.value, diastolic: 80 })) // Diastolic logic needs improvement but good for now
        .reverse() || [];

    const glucoseData = metrics
        .filter(m => m.type === 'glucosa')
        .map(m => ({ date: new Date(m.timestamp).toLocaleDateString([], { day: '2-digit', month: 'short' }), glucose: m.value }))
        .reverse() || [];

    // Calculate nutrients for today
    const today = new Date().toISOString().split('T')[0];
    const todaysFood = foodLogs.filter(f => f.date?.startsWith(today));

    const nutrientsData = [
        { name: 'Proteína', value: todaysFood.reduce((acc, f) => acc + (f.protein || 0), 0), color: '#3b82f6' },
        { name: 'Carbos', value: todaysFood.reduce((acc, f) => acc + (f.carbs || 0), 0), color: '#22c55e' },
        { name: 'Grasas', value: todaysFood.reduce((acc, f) => acc + (f.fat || 0), 0), color: '#f59e0b' },
    ];

    const totalCalories = todaysFood.reduce((acc, f) => acc + (f.calories || 0), 0);

    const latestWeight = metrics.find(m => m.type === 'peso')?.value || 0;
    const latestBP = metrics.find(m => m.type === 'presion')?.value || '0/0';
    const latestGlucose = metrics.find(m => m.type === 'glucosa')?.value || 0;

    return (
        <div className="min-h-screen bg-slate-50 p-4 md:p-8">
            <div className="max-w-7xl mx-auto">
                <DashboardHeader
                    onRegisterPeso={handleRegisterPeso}
                    onRegisterPresion={handleRegisterPresion}
                    onRegisterGlucosa={handleRegisterGlucosa}
                />

                {/* Tarjetas KPI */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <KpiCard
                        title="Peso Actual"
                        value={latestWeight.toString()}
                        unit="kg"
                        trend="down"
                        trendValue="--"
                        icon={<Scale className="w-6 h-6" />}
                        color="blue"
                    />
                    <KpiCard
                        title="Última Presión"
                        value={latestBP.toString()}
                        unit="mmHg"
                        trend="stable"
                        trendValue="--"
                        icon={<Activity className="w-6 h-6" />}
                        color="red"
                    />
                    <KpiCard
                        title="Promedio Glucosa"
                        value={latestGlucose.toString()}
                        unit="mg/dL"
                        trend="stable"
                        trendValue="--"
                        icon={<Droplets className="w-6 h-6" />}
                        color="purple"
                    />
                </div>

                {/* Gráficos */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <WeightChart data={weightData} />
                    <PressureChart data={pressureData} />
                    <GlucoseChart data={glucoseData} />
                    <NutrientsChart data={nutrientsData} totalCalories={totalCalories} />
                </div>
            </div>

            <HealthModal
                isOpen={isWeightModalOpen}
                onClose={() => setIsWeightModalOpen(false)}
                type="peso"
            />
            <HealthModal
                isOpen={isPressureModalOpen}
                onClose={() => setIsPressureModalOpen(false)}
                type="presion"
            />
            <HealthModal
                isOpen={isGlucoseModalOpen}
                onClose={() => setIsGlucoseModalOpen(false)}
                type="glucosa"
            />
        </div>
    );
};

export default Dashboard;
