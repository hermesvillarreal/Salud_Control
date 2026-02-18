import { useState } from 'react';
import api from '../../services/api';
import { useAuthStore } from '../../stores/authStore';
import { Dumbbell, Info, Heart, Zap } from 'lucide-react';

interface Props {
    onSaved?: () => void;
}

export default function WeightsCalculator({ onSaved }: Props) {
    const { user } = useAuthStore();
    const [weight, setWeight] = useState(user?.weight_kg?.toString() || '');
    const [duration, setDuration] = useState('');
    const [intensity, setIntensity] = useState<'baja' | 'media' | 'alta' | ''>('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<{ calories: number; intensityLabel: string } | null>(null);

    const intensityHelp = {
        'baja': 'Cargas ligeras, muchas reps, descansos cortos (< 1 min). El tiempo es muy efectivo.',
        'media': 'Entrenamiento estándar de hipertrofia/fuerza con descansos moderados (1-2 min).',
        'alta': 'Cargas muy pesadas, pocas reps, descansos largos (> 3 min). Menos tiempo bajo tensión por minuto total.'
    };

    const handleCalculate = async () => {
        if (!weight || !duration) {
            alert('Por favor completa el peso y la duración');
            return;
        }

        setLoading(true);
        try {
            const response = await api.post('/calculators/weights', {
                weight_kg: parseFloat(weight),
                time_min: parseInt(duration),
                intensity: intensity || null, // null will trigger average fallback
                fecha_hora: new Date().toISOString()
            });

            const intensityLabel = intensity === 'baja' ? 'Baja' :
                intensity === 'media' ? 'Moderada' :
                    intensity === 'alta' ? 'Alta' : 'Promedio';

            setResult({
                calories: response.data.result.calories,
                intensityLabel
            });

            if (onSaved) onSaved();
        } catch (error) {
            console.error('Error calculating weights:', error);
            alert('Error al calcular el gasto calórico');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center gap-3">
                <div className="p-3 bg-indigo-100 rounded-lg">
                    <Dumbbell className="w-6 h-6 text-indigo-600" />
                </div>
                <div>
                    <h2 className="text-2xl font-bold text-gray-800">Gasto Calórico en Pesas</h2>
                    <p className="text-gray-600 text-sm">
                        Estima las calorías quemadas según el tiempo total en el gimnasio y la intensidad.
                    </p>
                </div>
            </div>

            <div className="grid md:grid-cols-2 gap-8">
                <div className="space-y-5">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Peso Corporal (kg)</label>
                        <input
                            type="number"
                            value={weight}
                            onChange={(e) => setWeight(e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                            placeholder="Ej: 75"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Tiempo Total (minutos)</label>
                        <input
                            type="number"
                            value={duration}
                            onChange={(e) => setDuration(e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                            placeholder="Ej: 60"
                        />
                        <p className="text-xs text-gray-500 mt-1">
                            Incluye descansos y preparación de material.
                        </p>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Nivel de Intensidad</label>
                        <div className="grid grid-cols-3 gap-2">
                            {(['baja', 'media', 'alta'] as const).map((level) => (
                                <button
                                    key={level}
                                    onClick={() => setIntensity(level)}
                                    className={`py-2 px-3 rounded-md border text-sm font-medium transition-all ${intensity === level
                                            ? 'bg-indigo-600 border-indigo-600 text-white shadow-md'
                                            : 'bg-white border-gray-200 text-gray-600 hover:border-indigo-300'
                                        }`}
                                >
                                    {level.charAt(0).toUpperCase() + level.slice(1)}
                                </button>
                            ))}
                        </div>
                        {intensity && (
                            <div className="mt-2 flex gap-2 items-start p-2 bg-slate-50 rounded border border-slate-100 text-xs text-slate-600">
                                <Info className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
                                <span>{intensityHelp[intensity]}</span>
                            </div>
                        )}
                        {!intensity && (
                            <p className="text-xs text-gray-400 mt-2 italic">
                                Si no seleccionas intensidad, se usará un promedio de 6 kcal/min.
                            </p>
                        )}
                    </div>

                    <button
                        onClick={handleCalculate}
                        disabled={loading}
                        className="w-full bg-indigo-600 text-white py-3 rounded-lg font-bold hover:bg-indigo-700 transition-all shadow-lg hover:shadow-indigo-200 disabled:bg-gray-400"
                    >
                        {loading ? 'Calculando...' : 'Calcular y Guardar'}
                    </button>
                </div>

                <div className="space-y-4">
                    <div className="bg-gradient-to-br from-slate-800 to-slate-900 p-6 rounded-2xl text-white shadow-xl min-h-[200px] flex flex-col justify-center items-center text-center">
                        {result ? (
                            <div className="animate-in fade-in zoom-in duration-300">
                                <span className="text-slate-400 text-sm block mb-1">Gasto Estimado</span>
                                <div className="text-6xl font-black text-indigo-400 mb-2">
                                    {result.calories} <span className="text-2xl font-normal text-slate-300 italic">kcal</span>
                                </div>
                                <div className="inline-block px-3 py-1 bg-white/10 rounded-full text-xs font-medium border border-white/5">
                                    Intensidad: {result.intensityLabel}
                                </div>
                            </div>
                        ) : (
                            <div className="opacity-40 flex flex-col items-center">
                                <Dumbbell className="w-16 h-16 mb-4" />
                                <p className="text-slate-300">Completa los datos para ver el gasto estimado</p>
                            </div>
                        )}
                    </div>

                    <div className="grid grid-cols-1 gap-3">
                        <div className="p-4 bg-green-50 border border-green-100 rounded-xl flex gap-3 items-start">
                            <Heart className="w-5 h-5 text-green-600 shrink-0 mt-0.5" />
                            <div>
                                <h4 className="text-sm font-bold text-green-800">Recomendación ACSM</h4>
                                <p className="text-xs text-green-700">Se recomienda un gasto mínimo de 1000 kcal semanales para salud general.</p>
                            </div>
                        </div>
                        <div className="p-4 bg-blue-50 border border-blue-100 rounded-xl flex gap-3 items-start">
                            <Zap className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
                            <div>
                                <h4 className="text-sm font-bold text-blue-800">Beneficio Metabólico</h4>
                                <p className="text-xs text-blue-700">Las pesas son esenciales para mantener la masa libre de grasa y la salud endocrina.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
