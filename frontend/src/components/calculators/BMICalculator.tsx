import { useState } from 'react';
import api from '../../services/api';
import { getLocalISOString } from '../../utils/dateUtils';

interface BMIResult {
    bmi: number;
    category: string;
    health_risk: string;
    healthy_weight_min_kg: number;
    healthy_weight_max_kg: number;
}

interface Props {
    onSaved?: () => void;
}

export default function BMICalculator({ onSaved }: Props) {
    const [weight, setWeight] = useState('');
    const [height, setHeight] = useState('');
    const [result, setResult] = useState<BMIResult | null>(null);
    const [loading, setLoading] = useState(false);

    const handleCalculate = async () => {
        if (!weight || !height) {
            alert('Por favor completa todos los campos');
            return;
        }

        setLoading(true);
        try {
            const response = await api.post('/calculators/bmi', {
                weight_kg: parseFloat(weight),
                height_cm: parseFloat(height),
                fecha_hora: getLocalISOString(),
            });

            setResult(response.data.result);
            if (onSaved) onSaved();
        } catch (error) {
            console.error('Error calculating BMI:', error);
            alert('Error al calcular BMI');
        } finally {
            setLoading(false);
        }
    };

    const getBMIColor = (bmi: number) => {
        if (bmi < 18.5) return 'text-blue-600';
        if (bmi < 25) return 'text-green-600';
        if (bmi < 30) return 'text-yellow-600';
        if (bmi < 35) return 'text-orange-600';
        return 'text-red-600';
    };

    const getBMIPosition = (bmi: number) => {
        // Map BMI to percentage position (15-40 range)
        const minBMI = 15;
        const maxBMI = 40;
        const position = ((bmi - minBMI) / (maxBMI - minBMI)) * 100;
        return Math.min(Math.max(position, 0), 100);
    };

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold text-gray-800 mb-2">Calculadora de IMC (BMI)</h2>
                <p className="text-gray-600">
                    Calcula tu Índice de Masa Corporal y conoce tu categoría según la OMS
                </p>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
                {/* Input Form */}
                <div className="space-y-4">
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

                    <button
                        onClick={handleCalculate}
                        disabled={loading}
                        className="w-full bg-indigo-600 text-white py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors disabled:bg-gray-400"
                    >
                        {loading ? 'Calculando...' : 'Calcular IMC'}
                    </button>

                    {/* BMI Scale Reference */}
                    <div className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="font-semibold text-gray-800 mb-3">Clasificación OMS</h4>
                        <div className="space-y-2 text-sm">
                            <div className="flex justify-between">
                                <span className="text-blue-600">Bajo peso</span>
                                <span className="text-gray-600">&lt; 18.5</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-green-600">Normal</span>
                                <span className="text-gray-600">18.5 - 24.9</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-yellow-600">Sobrepeso</span>
                                <span className="text-gray-600">25.0 - 29.9</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-orange-600">Obesidad I</span>
                                <span className="text-gray-600">30.0 - 34.9</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-orange-700">Obesidad II</span>
                                <span className="text-gray-600">35.0 - 39.9</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-red-600">Obesidad III</span>
                                <span className="text-gray-600">≥ 40.0</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Results */}
                {result && (
                    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-6 rounded-lg">
                        <h3 className="text-xl font-bold text-gray-800 mb-4">Resultados</h3>

                        <div className="space-y-4">
                            <div className="bg-white p-6 rounded-lg shadow text-center">
                                <div className="text-sm text-gray-600 mb-2">Tu IMC</div>
                                <div className={`text-5xl font-bold ${getBMIColor(result.bmi)}`}>
                                    {result.bmi}
                                </div>
                                <div className="text-lg font-semibold text-gray-800 mt-2">{result.category}</div>
                                <div className="text-sm text-gray-600 mt-1">{result.health_risk}</div>
                            </div>

                            {/* BMI Visual Scale */}
                            <div className="bg-white p-4 rounded-lg shadow">
                                <div className="text-sm font-medium text-gray-700 mb-2">Escala Visual</div>
                                <div className="relative h-8 rounded-full overflow-hidden">
                                    <div className="absolute inset-0 flex">
                                        <div className="flex-1 bg-blue-400"></div>
                                        <div className="flex-1 bg-green-400"></div>
                                        <div className="flex-1 bg-yellow-400"></div>
                                        <div className="flex-1 bg-orange-400"></div>
                                        <div className="flex-1 bg-red-400"></div>
                                    </div>
                                    <div
                                        className="absolute top-0 bottom-0 w-1 bg-black"
                                        style={{ left: `${getBMIPosition(result.bmi)}%` }}
                                    >
                                        <div className="absolute -top-6 left-1/2 transform -translate-x-1/2 text-xs font-bold">
                                            ▼
                                        </div>
                                    </div>
                                </div>
                                <div className="flex justify-between text-xs text-gray-600 mt-1">
                                    <span>15</span>
                                    <span>18.5</span>
                                    <span>25</span>
                                    <span>30</span>
                                    <span>35</span>
                                    <span>40</span>
                                </div>
                            </div>

                            {/* Healthy Weight Range */}
                            <div className="bg-green-50 p-4 rounded-lg">
                                <h4 className="font-semibold text-gray-800 mb-2">Rango de Peso Saludable</h4>
                                <div className="text-center">
                                    <div className="text-2xl font-bold text-green-600">
                                        {result.healthy_weight_min_kg.toFixed(1)} - {result.healthy_weight_max_kg.toFixed(1)} kg
                                    </div>
                                    <div className="text-sm text-gray-600 mt-1">
                                        Para tu altura ({height} cm)
                                    </div>
                                </div>
                            </div>

                            <div className="bg-blue-50 p-3 rounded text-sm text-blue-800">
                                <strong>💡 Nota:</strong> El IMC es una herramienta de screening. No distingue entre masa muscular y grasa.
                                Consulta con un profesional para una evaluación completa.
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
