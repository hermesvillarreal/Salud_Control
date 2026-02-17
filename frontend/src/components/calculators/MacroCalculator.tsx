import { useState } from 'react';
import api from '../../services/api';
import { getLocalISOString } from '../../utils/dateUtils';

interface MacroResult {
    calories: number;
    protein_g: number;
    protein_percentage: number;
    carbs_g: number;
    carbs_percentage: number;
    fat_g: number;
    fat_percentage: number;
    goal: string;
}

interface Props {
    onSaved?: () => void;
}

export default function MacroCalculator({ onSaved }: Props) {
    const [tdee, setTdee] = useState('');
    const [weight, setWeight] = useState('');
    const [goal, setGoal] = useState('maintenance');
    const [proteinPref, setProteinPref] = useState('moderate');
    const [result, setResult] = useState<MacroResult | null>(null);
    const [loading, setLoading] = useState(false);

    const goals = [
        { value: 'loss', label: 'Pérdida de peso', description: 'Déficit de 500 kcal' },
        { value: 'maintenance', label: 'Mantenimiento', description: 'Mantener peso actual' },
        { value: 'gain', label: 'Ganancia muscular', description: 'Superávit de 300 kcal' },
    ];

    const proteinLevels = [
        { value: 'low', label: 'Bajo (0.8 g/kg)', description: 'Sedentario' },
        { value: 'moderate', label: 'Moderado (1.6 g/kg)', description: 'Activo' },
        { value: 'high', label: 'Alto (2.2 g/kg)', description: 'Atleta/Construcción muscular' },
    ];

    const handleCalculate = async () => {
        if (!tdee || !weight) {
            alert('Por favor completa todos los campos');
            return;
        }

        setLoading(true);
        try {
            const response = await api.post('/calculators/macro', {
                tdee: parseFloat(tdee),
                weight_kg: parseFloat(weight),
                goal,
                protein_preference: proteinPref,
                fecha_hora: getLocalISOString(),
            });

            setResult(response.data.result);
            if (onSaved) onSaved();
        } catch (error) {
            console.error('Error calculating macros:', error);
            alert('Error al calcular macros');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold text-gray-800 mb-2">Calculadora de Macronutrientes</h2>
                <p className="text-gray-600">
                    Calcula la distribución óptima de proteínas, carbohidratos y grasas según tu objetivo
                </p>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
                {/* Input Form */}
                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            TDEE (kcal/día)
                        </label>
                        <input
                            type="number"
                            value={tdee}
                            onChange={(e) => setTdee(e.target.value)}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                            placeholder="2500"
                        />
                        <p className="text-xs text-gray-500 mt-1">Usa la calculadora TDEE si no conoces este valor</p>
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
                        <label className="block text-sm font-medium text-gray-700 mb-2">Objetivo</label>
                        <div className="space-y-2">
                            {goals.map((g) => (
                                <label key={g.value} className="flex items-start cursor-pointer">
                                    <input
                                        type="radio"
                                        name="goal"
                                        value={g.value}
                                        checked={goal === g.value}
                                        onChange={(e) => setGoal(e.target.value)}
                                        className="mt-1 mr-3"
                                    />
                                    <div>
                                        <div className="font-medium text-gray-800">{g.label}</div>
                                        <div className="text-sm text-gray-600">{g.description}</div>
                                    </div>
                                </label>
                            ))}
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Nivel de Proteína</label>
                        <div className="space-y-2">
                            {proteinLevels.map((level) => (
                                <label key={level.value} className="flex items-start cursor-pointer">
                                    <input
                                        type="radio"
                                        name="protein"
                                        value={level.value}
                                        checked={proteinPref === level.value}
                                        onChange={(e) => setProteinPref(e.target.value)}
                                        className="mt-1 mr-3"
                                    />
                                    <div>
                                        <div className="font-medium text-gray-800">{level.label}</div>
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
                        {loading ? 'Calculando...' : 'Calcular Macros'}
                    </button>
                </div>

                {/* Results */}
                {result && (
                    <div className="bg-gradient-to-br from-green-50 to-teal-50 p-6 rounded-lg">
                        <h3 className="text-xl font-bold text-gray-800 mb-4">Distribución de Macronutrientes</h3>

                        <div className="space-y-4">
                            <div className="bg-white p-4 rounded-lg shadow">
                                <div className="text-sm text-gray-600 mb-1">Calorías Objetivo</div>
                                <div className="text-3xl font-bold text-indigo-600">{result.calories.toLocaleString()} kcal/día</div>
                            </div>

                            {/* Protein */}
                            <div className="bg-white p-4 rounded-lg shadow">
                                <div className="flex justify-between items-center mb-2">
                                    <span className="font-semibold text-red-600">🥩 Proteínas</span>
                                    <span className="text-sm text-gray-600">{result.protein_percentage}%</span>
                                </div>
                                <div className="text-2xl font-bold text-gray-800">{result.protein_g}g</div>
                                <div className="text-sm text-gray-500">{result.protein_g * 4} kcal</div>
                                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                                    <div
                                        className="bg-red-500 h-2 rounded-full"
                                        style={{ width: `${result.protein_percentage}%` }}
                                    ></div>
                                </div>
                            </div>

                            {/* Carbs */}
                            <div className="bg-white p-4 rounded-lg shadow">
                                <div className="flex justify-between items-center mb-2">
                                    <span className="font-semibold text-yellow-600">🍞 Carbohidratos</span>
                                    <span className="text-sm text-gray-600">{result.carbs_percentage}%</span>
                                </div>
                                <div className="text-2xl font-bold text-gray-800">{result.carbs_g}g</div>
                                <div className="text-sm text-gray-500">{result.carbs_g * 4} kcal</div>
                                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                                    <div
                                        className="bg-yellow-500 h-2 rounded-full"
                                        style={{ width: `${result.carbs_percentage}%` }}
                                    ></div>
                                </div>
                            </div>

                            {/* Fat */}
                            <div className="bg-white p-4 rounded-lg shadow">
                                <div className="flex justify-between items-center mb-2">
                                    <span className="font-semibold text-blue-600">🥑 Grasas</span>
                                    <span className="text-sm text-gray-600">{result.fat_percentage}%</span>
                                </div>
                                <div className="text-2xl font-bold text-gray-800">{result.fat_g}g</div>
                                <div className="text-sm text-gray-500">{result.fat_g * 9} kcal</div>
                                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                                    <div
                                        className="bg-blue-500 h-2 rounded-full"
                                        style={{ width: `${result.fat_percentage}%` }}
                                    ></div>
                                </div>
                            </div>

                            <div className="bg-green-100 p-3 rounded text-sm text-green-800">
                                <strong>💡 Consejo:</strong> Distribuye estos macros en 3-5 comidas al día.
                                Ajusta según tu respuesta y preferencias personales.
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
