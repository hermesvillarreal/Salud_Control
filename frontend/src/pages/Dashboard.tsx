import React, { useState, useEffect } from 'react';
import { Scale, Activity, Droplets } from 'lucide-react';
import DashboardHeader from '../components/DashboardHeader';
import KpiCard from '../components/KpiCard';
import WeightChart from '../components/charts/WeightChart';
import PressureChart from '../components/charts/PressureChart';
import GlucoseChart from '../components/charts/GlucoseChart';
import NutrientsChart from '../components/charts/NutrientsChart';
import HealthModal from '../components/HealthModal';
import TelegramBotModal from '../components/TelegramBotModal';
import { useHealthStore } from '../stores/healthStore';
import { useAuthStore } from '../stores/authStore';
import api from '../services/api';

const Dashboard: React.FC = () => {
    const { metrics, fetchMetrics, fetchFoodLogs, foodLogs, fetchExerciseLogs } = useHealthStore();
    const { user, updateUser } = useAuthStore();

    // Modal states
    const [isWeightModalOpen, setIsWeightModalOpen] = useState(false);
    const [isPressureModalOpen, setIsPressureModalOpen] = useState(false);
    const [isGlucoseModalOpen, setIsGlucoseModalOpen] = useState(false);
    const [isTelegramModalOpen, setIsTelegramModalOpen] = useState(false);

    useEffect(() => {
        fetchMetrics();
        fetchFoodLogs();
        fetchExerciseLogs();
        refreshUser();
    }, [fetchMetrics, fetchFoodLogs, fetchExerciseLogs]);

    const refreshUser = async () => {
        try {
            const response = await api.get('/auth/me');
            updateUser(response.data);
        } catch (error) {
            console.error('Error refreshing user data:', error);
        }
    };

    const handleRegisterPeso = () => {
        setIsWeightModalOpen(true);
    };

    const handleRegisterPresion = () => {
        setIsPressureModalOpen(true);
    };

    const handleRegisterGlucosa = () => {
        setIsGlucoseModalOpen(true);
    };

    const handleUnlinkTelegram = async () => {
        if (!confirm('¿Estás seguro de que deseas desvincular el bot de Telegram?')) return;

        try {
            await api.post('/auth/telegram-unlink');
            updateUser({ is_telegram_linked: false });
            alert('Bot desvinculado correctamente.');
        } catch (error) {
            console.error('Error unlinking telegram:', error);
            alert('Error al desvincular el bot.');
        }
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
    const now = new Date();
    const offset = now.getTimezoneOffset() * 60000;
    const localDate = new Date(now.getTime() - offset);
    const today = localDate.toISOString().split('T')[0];
    const todaysFood = foodLogs.filter(f => f.fecha_hora?.startsWith(today));

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
                    onOpenTelegram={() => setIsTelegramModalOpen(true)}
                    isTelegramLinked={user?.is_telegram_linked || false}
                    onUnlinkTelegram={handleUnlinkTelegram}
                />

                {/* 1. Macronutrientes (Top) */}
                <div className="mb-8">
                    <NutrientsChart
                        data={nutrientsData}
                        totalCalories={totalCalories}
                        goals={{
                            calories: user?.daily_calories_goal,
                            protein: user?.daily_protein_goal,
                            carbs: user?.daily_carbs_goal,
                            fat: user?.daily_fat_goal,
                            current_goal: user?.current_goal
                        }}
                    />
                </div>

                {/* 2. Glucosa Section */}
                <div className="mb-8">
                    <h3 className="text-xl font-bold text-slate-800 mb-4 flex items-center gap-2">
                        <Droplets className="w-5 h-5 text-purple-600" />
                        Glucosa
                    </h3>
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        <div className="lg:col-span-1">
                            <KpiCard
                                title="Glucosa Actual"
                                value={latestGlucose.toString()}
                                unit="mg/dL"
                                trend="stable"
                                trendValue="--"
                                icon={<Droplets className="w-6 h-6" />}
                                color="purple"
                            />
                        </div>
                        <div className="lg:col-span-2">
                            <GlucoseChart data={glucoseData} />
                        </div>
                    </div>
                </div>

                {/* 3. Presión Section */}
                <div className="mb-8">
                    <h3 className="text-xl font-bold text-slate-800 mb-4 flex items-center gap-2">
                        <Activity className="w-5 h-5 text-red-600" />
                        Presión Arterial
                    </h3>
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        <div className="lg:col-span-1">
                            <KpiCard
                                title="Presión Actual"
                                value={latestBP.toString()}
                                unit="mmHg"
                                trend="stable"
                                trendValue="--"
                                icon={<Activity className="w-6 h-6" />}
                                color="red"
                            />
                        </div>
                        <div className="lg:col-span-2">
                            <PressureChart data={pressureData} />
                        </div>
                    </div>
                </div>

                {/* 4. Peso Section */}
                <div className="mb-8">
                    <h3 className="text-xl font-bold text-slate-800 mb-4 flex items-center gap-2">
                        <Scale className="w-5 h-5 text-blue-600" />
                        Control de Peso
                    </h3>
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        <div className="lg:col-span-1">
                            <KpiCard
                                title="Peso Actual"
                                value={latestWeight.toString()}
                                unit="kg"
                                trend="down"
                                trendValue="--"
                                icon={<Scale className="w-6 h-6" />}
                                color="blue"
                            />
                        </div>
                        <div className="lg:col-span-2">
                            <WeightChart data={weightData} />
                        </div>
                    </div>
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

            <TelegramBotModal
                isOpen={isTelegramModalOpen}
                onClose={() => setIsTelegramModalOpen(false)}
            />
        </div>
    );
};

export default Dashboard;
