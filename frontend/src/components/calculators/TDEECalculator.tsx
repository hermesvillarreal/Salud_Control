import { useState } from 'react';
import api from '../../services/api';
import { getLocalISOString } from '../../utils/dateUtils';

interface TDEEResult {
    bmr: number;
    tdee: number;
    activity_factor: number;
    activity_level: string;
}

interface Props {
    onSaved?: () => void;
}

export default function TDEECalculator({ onSaved }: Props) {
    const [age, setAge] = useState('');
    const [gender, setGender] = useState('male');
    const [weight, setWeight] = useState('');
    const [height, setHeight] = useState('');
    const [activityLevel, setActivityLevel] = useState('moderate');
    const [result, setResult] = useState<TDEEResult | null>(null);
    const [loading, setLoading] = useState(false);

    const activityLevels = [
        { value: 'sedentary', label: 'Sedentario', description: 'Poco o ningún ejercicio', factor: '1.2' },
        { value: 'light', label: 'Ligeramente activo', description: 'Ejercicio ligero 1-3 días/semana', factor: '1.375' },
        { value: 'moderate', label: 'Moderadamente activo', description: 'Ejercicio moderado 3-5 días/semana', factor: '1.55' },
        { value: 'very_active', label: 'Muy activo', description: 'Ejercicio intenso 6-7 días/semana', factor: '1.725' },
        { value: 'extra_active', label: 'Extremadamente activo', description: 'Ejercicio muy intenso + trabajo físico', factor: '1.9' },
    ];

    const handleCalculate = async () => {
        if (!age || !weight || !height) {
            alert('Por favor completa todos los campos');
            return;
        }

        setLoading(true);
        try {
            const response = await api.post('/calculators/tdee', {
                age: parseInt(age),
                gender,
                weight_kg: parseFloat(weight),
                height_cm: parseFloat(height),
                activity_level: activityLevel,
                fecha_hora: getLocalISOString(),
            });

            setResult(response.data.result);
            if (onSaved) onSaved();
        } catch (error) {
            console.error('Error calculating TDEE:', error);
            alert('Error al calcular TDEE');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold text-gray-800 mb-2">Calculadora TDEE</h2>
                <p className="text-gray-600">
                    Calcula tu Gasto Energético Total Diario usando la ecuación Mifflin-St Jeor
                </p>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
                {/* Input Form */}
                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Edad (años)</label>
                        <input
                            type="number"
                            value={age}
                            onChange={(e) => setAge(e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                            placeholder="30"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Sexo</label>
                        <select
                            value={gender}
                            onChange={(e) => setGender(e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                        >
                            <option value="male">Masculino</option>
                            <option value="female">Femenino</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Peso (kg)</label>
                        <input
                            type="number"
                            step="0.1"
                            value={weight}
                            onChange={(e) => setWeight(e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                            placeholder="70"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Altura (cm)</label>
                        <input
                            type="number"
                            step="0.1"
                            value={height}
                            onChange={(e) => setHeight(e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                            placeholder="175"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Nivel de Actividad</label>
                        <div className="space-y-2">
                            {activityLevels.map((level) => (
                                <label key={level.value} className="flex items-start cursor-pointer">
                                    <input
                                        type="radio"
                                        name="activity"
                                        value={level.value}
                                        checked={activityLevel === level.value}
                                        onChange={(e) => setActivityLevel(e.target.value)}
                                        className="mt-1 mr-3"
                                    />
                                    <div>
                                        <div className="font-medium text-gray-800">
                                            {level.label} <span className="text-sm text-gray-500">(×{level.factor})</span>
                                        </div>
                                        <div className="text-sm text-gray-600">{level.description}</div>
                                    </div>
                                </label>
                            ))}
                        </div>
                    </div>

                    <button
                        onClick={handleCalculate}
                        disabled={loading}
                        className="w-full bg-indigo-600 text-white py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors disabled:bg-gray-400"
                    >
                        {loading ? 'Calculando...' : 'Calcular TDEE'}
                    </button>
                </div>

                {/* Results */}
                {result && (
                    <div className="bg-gradient-to-br from-indigo-50 to-purple-50 p-6 rounded-lg">
                        <h3 className="text-xl font-bold text-gray-800 mb-4">Resultados</h3>

                        <div className="space-y-4">
                            <div className="bg-white p-4 rounded-lg shadow">
                                <div className="text-sm text-gray-600 mb-1">Tasa Metabólica Basal (BMR)</div>
                                <div className="text-3xl font-bold text-indigo-600">{result.bmr.toLocaleString()} kcal/día</div>
                                <div className="text-xs text-gray-500 mt-1">Calorías en reposo total</div>
                            </div>

                            <div className="bg-white p-4 rounded-lg shadow">
                                <div className="text-sm text-gray-600 mb-1">Gasto Energético Total (TDEE)</div>
                                <div className="text-3xl font-bold text-purple-600">{result.tdee.toLocaleString()} kcal/día</div>
                                <div className="text-xs text-gray-500 mt-1">Calorías para mantener peso actual</div>
                            </div>

                            <div className="bg-indigo-100 p-4 rounded-lg">
                                <h4 className="font-semibold text-gray-800 mb-2">Guía de Objetivos</h4>
                                <div className="space-y-2 text-sm">
                                    <div className="flex justify-between">
                                        <span className="text-gray-700">Pérdida de peso:</span>
                                        <span className="font-semibold text-red-600">{(result.tdee - 500).toLocaleString()} kcal/día</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-700">Mantenimiento:</span>
                                        <span className="font-semibold text-gray-800">{result.tdee.toLocaleString()} kcal/día</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-700">Ganancia muscular:</span>
                                        <span className="font-semibold text-green-600">{(result.tdee + 300).toLocaleString()} kcal/día</span>
                                    </div>
                                </div>
                            </div>

                            <div className="bg-blue-50 p-3 rounded text-sm text-blue-800">
                                <strong>💡 Nota:</strong> Tu TDEE se calculó usando el factor de actividad {result.activity_factor}.
                                Ajusta según tus objetivos y monitorea tu progreso.
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
