import { useState, useMemo } from 'react';
import api from '../../services/api';
import { getLocalISOString } from '../../utils/dateUtils';
import { useAuthStore } from '../../stores/authStore';
import { Search, Info, Plus, Trash2, AlertTriangle } from 'lucide-react';

interface Activity {
    id: string;
    name: string;
    met: number;
    category: 'reposo' | 'ligero' | 'moderado' | 'vigoroso' | 'deporte';
    position?: 'vertical' | 'reclinado';
    deporte?: string;
    description?: string;
}

const ACTIVITIES: Activity[] = [
    { id: '1', name: 'Dormir', met: 1.0, category: 'reposo' },
    { id: '2', name: 'Sentado (TV, charlar)', met: 1.3, category: 'reposo' },
    { id: '3', name: 'Conducir', met: 2.0, category: 'ligero' },
    { id: '4', name: 'Pasear (ritmo suave)', met: 2.1, category: 'ligero' },
    { id: '5', name: 'Caminar (ritmo medio)', met: 3.5, category: 'moderado' },
    { id: '6', name: 'Entrenamiento de Fuerza (Pesas)', met: 4.0, category: 'moderado' },
    { id: '7', name: 'Tenis', met: 6.1, category: 'vigoroso', deporte: 'tenis' },
    { id: '8', name: 'Ciclismo (moderado)', met: 6.7, category: 'vigoroso', position: 'vertical' },
    { id: '9', name: 'Bicicleta Reclinada', met: 5.0, category: 'moderado', position: 'reclinado' },
    { id: '10', name: 'Subir Montaña', met: 8.2, category: 'vigoroso' },
    { id: '11', name: 'Subir Escaleras', met: 13.3, category: 'vigoroso', position: 'vertical' },
    { id: '12', name: 'Correr alta velocidad (>20 km/h)', met: 23.0, category: 'vigoroso', position: 'vertical' },
    { id: '13', name: 'Cinta de Correr', met: 8.0, category: 'vigoroso', position: 'vertical' },
    { id: '14', name: 'Elíptica', met: 5.0, category: 'moderado', position: 'vertical' },
    { id: '15', name: 'Natación', met: 8.0, category: 'vigoroso' },
    { id: '16', name: 'Yoga / Pilates', met: 3.0, category: 'ligero' },
    { id: '17', name: 'Fútbol', met: 10.0, category: 'vigoroso' },
    { id: '18', name: 'Oficina / Trabajo de escritorio', met: 1.5, category: 'reposo' },
];

interface Calculation {
    id: string;
    activityName: string;
    met: number;
    duration: number;
    calories: number;
}

interface Props {
    onSaved?: () => void;
}

export default function CaloricExpenditureCalculator({ onSaved }: Props) {
    const user = useAuthStore((state: any) => state.user);
    const [weight, setWeight] = useState(user?.weight_kg?.toString() || '');
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedActivity, setSelectedActivity] = useState<Activity | null>(null);
    const [duration, setDuration] = useState('30');
    const [durationType, setDurationType] = useState<'min' | 'hours'>('min');
    const [rpe, setRpe] = useState('5');
    const [dailyLogs, setDailyLogs] = useState<Calculation[]>([]);
    const [loading, setLoading] = useState(false);
    const [lastRecord, setLastRecord] = useState<any>(null);

    const filteredActivities = useMemo(() => {
        if (!searchTerm) return [];
        return ACTIVITIES.filter(a =>
            a.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            a.category.toLowerCase().includes(searchTerm.toLowerCase())
        );
    }, [searchTerm]);

    const calculateCalories = (met: number, w: number, d: number, type: 'min' | 'hours') => {
        const mins = type === 'hours' ? d * 60 : d;
        // Formula: Kcal = 0.0175 * MET * Peso (kg) * Tiempo (min)
        return 0.0175 * met * w * mins;
    };

    const handleAddActivity = () => {
        if (!selectedActivity || !weight || !duration) return;

        const kcal = calculateCalories(
            selectedActivity.met,
            parseFloat(weight),
            parseFloat(duration),
            durationType
        );

        const newLog: Calculation = {
            id: Math.random().toString(36).substr(2, 9),
            activityName: selectedActivity.name,
            met: selectedActivity.met,
            duration: durationType === 'hours' ? parseFloat(duration) * 60 : parseFloat(duration),
            calories: kcal
        };

        setDailyLogs([...dailyLogs, newLog]);
        setSelectedActivity(null);
        setSearchTerm('');
    };

    const handleRemoveActivity = (id: string) => {
        setDailyLogs(dailyLogs.filter(log => log.id !== id));
    };

    const handleSaveAll = async () => {
        if (dailyLogs.length === 0) return;

        setLoading(true);
        try {
            const totalDuration = dailyLogs.reduce((acc: number, curr: Calculation) => acc + curr.duration, 0);
            const totalCalories = dailyLogs.reduce((acc: number, curr: Calculation) => acc + curr.calories, 0);
            const avgMet = dailyLogs.reduce((acc: number, curr: Calculation) => acc + (curr.met * curr.duration), 0) / totalDuration;

            const response = await api.post('/calculators/expenditure', {
                weight_kg: parseFloat(weight),
                duration_min: totalDuration,
                activity_met: avgMet,
                rpe: parseInt(rpe),
                fecha_hora: getLocalISOString(),
                notes: `Lista de actividades: ${dailyLogs.map(l => `${l.activityName} (${l.duration} min)`).join(', ')}`
            });

            setLastRecord(response.data.result);
            setDailyLogs([]);
            if (onSaved) onSaved();
        } catch (error) {
            console.error('Error saving expenditure:', error);
            alert('Error al guardar el gasto calórico');
        } finally {
            setLoading(false);
        }
    };

    const totalKcal = dailyLogs.reduce((acc, curr) => acc + curr.calories, 0);

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-start">
                <div>
                    <h2 className="text-2xl font-bold text-gray-800 mb-2">Gasto Calórico por Actividad</h2>
                    <p className="text-gray-600"> Basado en el Compendio Ainsworth (METs)</p>
                </div>
                <div className="bg-indigo-100 text-indigo-800 px-4 py-2 rounded-lg font-bold">
                    {totalKcal.toFixed(1)} kcal Totales
                </div>
            </div>

            <div className="grid lg:grid-cols-3 gap-6">
                {/* Inputs y Buscador */}
                <div className="lg:col-span-2 space-y-4">
                    <div className="grid md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Peso Corporal (kg)</label>
                            <input
                                type="number"
                                value={weight}
                                onChange={(e) => setWeight(e.target.value)}
                                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                                placeholder="70"
                            />
                        </div>
                        <div>
                            <div className="flex items-center gap-1 mb-1">
                                <label className="block text-sm font-medium text-gray-700">Percepción de Esfuerzo (RPE 1-10)</label>
                                <div className="group relative">
                                    <Info size={14} className="text-gray-400 cursor-help" />
                                    <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-48 p-2 bg-slate-800 text-white text-[10px] rounded shadow-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
                                        Escala de Esfuerzo Percibido. 1=Muy suave, 10=Esfuerzo máximo. Indica cómo sientes la intensidad.
                                        <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-slate-800"></div>
                                    </div>
                                </div>
                            </div>
                            <input
                                type="range"
                                min="1"
                                max="10"
                                value={rpe}
                                onChange={(e) => setRpe(e.target.value)}
                                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600 mt-3"
                            />
                            <div className="flex justify-between text-xs text-gray-500 mt-1">
                                <span>Suave</span>
                                <span className="font-bold text-indigo-600">RPE: {rpe}</span>
                                <span>Máximo</span>
                            </div>
                        </div>
                    </div>

                    <div className="relative">
                        <label className="block text-sm font-medium text-gray-700 mb-1">Buscar Actividad</label>
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
                            <input
                                type="text"
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                                placeholder="Escribe para buscar (ej. Correr, Pesas, Dormir...)"
                            />
                        </div>

                        {filteredActivities.length > 0 && !selectedActivity && (
                            <div className="absolute z-10 w-full mt-1 bg-white border rounded-lg shadow-xl max-h-60 overflow-y-auto">
                                {filteredActivities.map(activity => (
                                    <button
                                        key={activity.id}
                                        onClick={() => {
                                            setSelectedActivity(activity);
                                            setSearchTerm(activity.name);
                                        }}
                                        className="w-full text-left px-4 py-2 hover:bg-indigo-50 border-b last:border-0 flex justify-between items-center"
                                    >
                                        <div>
                                            <span className="font-medium text-gray-800">{activity.name}</span>
                                            <span className="ml-2 text-xs text-gray-500 uppercase">{activity.category}</span>
                                        </div>
                                        <div className="text-indigo-600 font-bold">{activity.met} METs</div>
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>

                    {selectedActivity && (
                        <div className="bg-white p-4 border-2 border-indigo-200 rounded-lg animate-in fade-in slide-in-from-top-2">
                            <div className="flex justify-between items-center mb-4">
                                <div>
                                    <h4 className="font-bold text-indigo-900">{selectedActivity.name}</h4>
                                    <div className="text-xs text-gray-500">Intensidad: {selectedActivity.met} METs</div>
                                </div>
                                <div className="flex items-center gap-2">
                                    <input
                                        type="number"
                                        value={duration}
                                        onChange={(e) => setDuration(e.target.value)}
                                        className="w-20 px-2 py-1 border rounded"
                                    />
                                    <select
                                        value={durationType}
                                        onChange={(e) => setDurationType(e.target.value as any)}
                                        className="px-2 py-1 border rounded bg-gray-50"
                                    >
                                        <option value="min">min</option>
                                        <option value="hours">h</option>
                                    </select>
                                    <button
                                        onClick={handleAddActivity}
                                        className="bg-indigo-600 text-white p-2 rounded-lg hover:bg-indigo-700 transition-colors"
                                    >
                                        <Plus className="w-5 h-5" />
                                    </button>
                                </div>
                            </div>

                            {selectedActivity.position === 'reclinado' && (
                                <div className="flex gap-2 text-xs bg-amber-50 text-amber-800 p-2 rounded border border-amber-200">
                                    <Info className="w-4 h-4 shrink-0" />
                                    <p>Las máquinas reclinadas queman menos calorías por el mismo esfuerzo debido al retorno sanguíneo facilitado y la menor carga gravitatoria.</p>
                                </div>
                            )}
                            {selectedActivity.position === 'vertical' && (
                                <div className="flex gap-2 text-xs bg-blue-50 text-blue-800 p-2 rounded border border-blue-200">
                                    <Info className="w-4 h-4 shrink-0" />
                                    <p>La posición vertical (cinta, escaleras) maximiza la quema calórica al trabajar contra la gravedad y demandar mayor esfuerzo cardiovascular.</p>
                                </div>
                            )}
                        </div>
                    )}
                </div>

                {/* Resumen Diario */}
                <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
                    <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
                        <span>📋</span> Registro de Actividades
                    </h3>

                    <div className="space-y-2 max-h-80 overflow-y-auto mb-4">
                        {dailyLogs.length === 0 ? (
                            <p className="text-center text-gray-400 py-8 text-sm italic">
                                No hay actividades añadidas.<br />Busca una arriba para empezar.
                            </p>
                        ) : (
                            dailyLogs.map((log: Calculation) => (
                                <div key={log.id} className="bg-white p-3 rounded-lg shadow-sm border border-gray-100 flex justify-between items-center group">
                                    <div>
                                        <div className="font-medium text-gray-800 text-sm">{log.activityName}</div>
                                        <div className="text-xs text-gray-500">{log.duration} min • {log.calories.toFixed(1)} kcal</div>
                                    </div>
                                    <button
                                        onClick={() => handleRemoveActivity(log.id)}
                                        className="text-gray-300 hover:text-red-500 transition-colors"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                </div>
                            ))
                        )}
                    </div>

                    {dailyLogs.length > 0 && (
                        <button
                            onClick={handleSaveAll}
                            disabled={loading}
                            className="w-full bg-green-600 text-white py-3 rounded-lg font-bold hover:bg-green-700 transition-colors disabled:bg-gray-400 shadow-lg"
                        >
                            {loading ? 'Guardando...' : 'Guardar Registro Diario'}
                        </button>
                    )}
                </div>
            </div>

            {/* Comparativa y Resultados Finales */}
            {lastRecord && (
                <div className="bg-white p-6 rounded-xl border-2 border-green-100 shadow-sm animate-in zoom-in-95 duration-300">
                    <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
                        <span>🚀</span> Resultado del Cálculo
                    </h3>
                    <div className="grid md:grid-cols-2 gap-8 items-center">
                        <div className="space-y-4">
                            <div className="text-center p-6 bg-green-50 rounded-2xl border border-green-100">
                                <div className="text-sm text-green-700 font-medium uppercase tracking-wider mb-1">Calorías Totales Quemadas</div>
                                <div className="text-5xl font-black text-green-600">{lastRecord.calories_burned.toLocaleString()} <span className="text-xl">kcal</span></div>
                            </div>
                        </div>

                        <div className="space-y-4">
                            <div className="flex items-center gap-4 bg-gray-50 p-4 rounded-xl">
                                <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center text-2xl shadow-sm">⚖️</div>
                                <div>
                                    <div className="text-xs text-gray-500 font-medium uppercase">Comparativa de Reposo</div>
                                    <div className="text-gray-800 font-bold">
                                        Esto equivale a <span className="text-indigo-600">{lastRecord.ratio_to_resting.toFixed(1)} veces</span> tu gasto en reposo absoluto.
                                    </div>
                                </div>
                            </div>

                            <div className="bg-blue-50 p-4 rounded-xl text-blue-800 text-sm">
                                <strong>💡 Sabías que:</strong> Tu gasto basal durante estos {lastRecord.duration_min} minutos habría sido de <strong>{lastRecord.resting_kcal_total} kcal</strong>. ¡La actividad aumentó tu gasto significativamente!
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Advertencia Obligatoria */}
            <div className="bg-amber-50 border-l-4 border-amber-400 p-4 rounded-r-lg flex gap-3">
                <AlertTriangle className="w-6 h-6 text-amber-500 shrink-0" />
                <div>
                    <h4 className="font-bold text-amber-800 text-sm">Advertencia Importante</h4>
                    <p className="text-amber-700 text-xs mt-1">
                        Esta calculadora ofrece una estimación basada en medias del Compendio de Ainsworth.
                        No considera composición corporal individual, masa muscular, nivel de condición física o adaptaciones metabólicas.
                        Consulte con un profesional de la salud o un deportólogo antes de iniciar programas de alta intensidad.
                    </p>
                </div>
            </div>
        </div>
    );
}
