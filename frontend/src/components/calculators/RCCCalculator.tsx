import { useState } from 'react';
import api from '../../services/api';
import { getLocalISOString, getLocalDateString } from '../../utils/dateUtils';
import { useAuthStore } from '../../stores/authStore';

interface Props {
    onSaved?: () => void;
}

export default function RCCCalculator({ onSaved }: Props) {
    const { user } = useAuthStore();
    const [waist, setWaist] = useState('');
    const [hip, setHip] = useState('');
    const [date, setDate] = useState(getLocalDateString());
    const [result, setResult] = useState<{ rcc: number; classification: string; riskColor: string } | null>(null);
    const [loading, setLoading] = useState(false);

    const calculateRisk = (rcc: number, waistVal: number, gender: string) => {
        let classification = "Saludable";
        let riskColor = "text-green-600";
        const isMale = gender === 'male';

        // NCC (Cintura) Risk
        let waistRisk = "Bajo";
        if (isMale) {
            if (waistVal > 102) waistRisk = "Alto";
            else if (waistVal > 94) waistRisk = "Aumentado";
        } else {
            if (waistVal > 88) waistRisk = "Alto";
            else if (waistVal > 80) waistRisk = "Aumentado";
        }

        // RCC Risk
        const rccHealthy = isMale ? rcc < 0.90 : rcc < 0.85;

        if (!rccHealthy || waistRisk === "Alto") {
            classification = "Alto Riesgo";
            riskColor = "text-red-600";
        } else if (waistRisk === "Aumentado") {
            classification = "Riesgo Aumentado";
            riskColor = "text-yellow-600";
        }

        return { classification, riskColor };
    };

    const handleCalculate = async () => {
        if (!waist || !hip) {
            alert('Por favor completa los campos de cintura y cadera');
            return;
        }

        const waistVal = parseFloat(waist);
        const hipVal = parseFloat(hip);
        const rcc = waistVal / hipVal;

        const { classification, riskColor } = calculateRisk(rcc, waistVal, user?.gender || 'male');
        setResult({ rcc: parseFloat(rcc.toFixed(2)), classification, riskColor });

        setLoading(true);
        try {
            const [year, month, day] = date.split('-').map(Number);
            const now = new Date();
            const targetDate = new Date(year, month - 1, day, now.getHours(), now.getMinutes(), now.getSeconds());
            const fecha_hora = getLocalISOString(targetDate);

            // 1. Save to specific table for history/charts (already implemented)
            await api.post('/health/waist_hip', {
                waist_cm: waistVal,
                hip_cm: hipVal,
                rcc: parseFloat(rcc.toFixed(2)),
                fecha_hora,
                notes: `Clasificación: ${classification}`
            });

            // 2. Save to general calculators history table
            await api.post('/calculators/rcc', {
                waist_cm: waistVal,
                hip_cm: hipVal,
                gender: user?.gender || 'male',
                fecha_hora,
                notes: `Clasificación: ${classification}`
            });

            if (onSaved) onSaved();
        } catch (error) {
            console.error('Error saving RCC:', error);
            alert('Error al guardar la medición');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold text-gray-800 mb-2">Relación Cintura-Cadera (RCC)</h2>
                <p className="text-gray-600">
                    Evalúa la distribución de grasa corporal y el riesgo cardiometabólico.
                </p>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Circunferencia de Cintura (cm)</label>
                        <input
                            type="number"
                            step="0.1"
                            value={waist}
                            onChange={(e) => setWaist(e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                            placeholder="Ej: 90"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Circunferencia de Cadera (cm)</label>
                        <input
                            type="number"
                            step="0.1"
                            value={hip}
                            onChange={(e) => setHip(e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                            placeholder="Ej: 100"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Fecha de Medición</label>
                        <input
                            type="date"
                            value={date}
                            onChange={(e) => setDate(e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                        />
                    </div>

                    <button
                        onClick={handleCalculate}
                        disabled={loading}
                        className="w-full bg-indigo-600 text-white py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors disabled:bg-gray-400"
                    >
                        {loading ? 'Guardando...' : 'Calcular y Guardar'}
                    </button>
                </div>

                <div className="bg-slate-50 p-6 rounded-lg space-y-4">
                    {result ? (
                        <div className="text-center space-y-2">
                            <div className="text-sm text-gray-600">Tu Relación Cintura-Cadera</div>
                            <div className={`text-5xl font-bold ${result.riskColor}`}>{result.rcc}</div>
                            <div className={`text-xl font-semibold ${result.riskColor}`}>{result.classification}</div>
                            <div className="text-sm text-gray-500 mt-4 p-3 bg-white rounded border border-slate-200">
                                Según la OMS, un RCC {user?.gender === 'female' ? '> 0.85 en mujeres' : '> 0.90 en hombres'} indica riesgo sustancial de complicaciones metabólicas.
                            </div>
                        </div>
                    ) : (
                        <div className="h-full flex flex-col items-center justify-center text-gray-400 text-center p-4">
                            <svg className="w-12 h-12 mb-2 opacity-20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                            </svg>
                            <p>Ingresa tus mediciones para obtener el análisis de riesgo.</p>
                        </div>
                    )}
                </div>
            </div>

            <div className="bg-blue-50 border-l-4 border-blue-400 p-4 rounded text-sm text-blue-800">
                <strong>📌 Monitoreo Recomendado:</strong> Se recomienda realizar estas mediciones de forma semanal para un seguimiento efectivo de los cambios en la composición corporal.
            </div>
        </div>
    );
}
