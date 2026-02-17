import React, { useState, useEffect, useRef } from 'react';
import { ArrowLeft, Send, Sparkles, Save, Edit2, Check, Utensils, PieChart, Pencil, Camera, Image as ImageIcon, X } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { useHealthStore, FoodRecord, MealType } from '../stores/healthStore';
import { formatLocalISO, normalizeToBackendISO } from '../utils/dateUtils';

const FoodLog: React.FC = () => {
    const navigate = useNavigate();
    const { foodLogs, addFoodLog, updateFoodLog, fetchFoodLogs, isLoading: storeLoading } = useHealthStore();

    // Form state
    const [description, setDescription] = useState('');
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [selectedImage, setSelectedImage] = useState<File | null>(null);
    const [previewUrl, setPreviewUrl] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    // Confirmation/Edit state
    const [estimatedFood, setEstimatedFood] = useState<Partial<FoodRecord> | null>(null);
    const [editMode, setEditMode] = useState(false);

    useEffect(() => {
        fetchFoodLogs();
    }, [fetchFoodLogs]);

    useEffect(() => {
        if (selectedImage) {
            const url = URL.createObjectURL(selectedImage);
            setPreviewUrl(url);
            return () => URL.revokeObjectURL(url);
        } else {
            setPreviewUrl(null);
        }
    }, [selectedImage]);

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setSelectedImage(e.target.files[0]);
        }
    };

    const handleAnalyze = async () => {
        if (!description.trim() && !selectedImage) return;

        setIsAnalyzing(true);
        try {
            let response;

            if (selectedImage) {
                const formData = new FormData();
                formData.append('file', selectedImage);
                if (description.trim()) {
                    formData.append('description', description);
                }

                response = await api.post('/food/analyze-image', formData, {
                    headers: { 'Content-Type': 'multipart/form-data' }
                });
            } else {
                response = await api.post('/food/analyze', null, {
                    params: { description }
                });
            }

            // Backend returns: { calories, protein, carbs, fat, meal_type }
            setEstimatedFood({
                description: response.data.food_name || description || "Comida detectada",
                calories: response.data.calories,
                protein: response.data.protein,
                carbs: response.data.carbs,
                fat: response.data.fat,
                meal_type: (['desayuno', 'merienda_manana', 'almuerzo', 'merienda_tarde', 'cena', 'merienda_postcena'].includes(response.data.meal_type?.toLowerCase())
                    ? response.data.meal_type.toLowerCase()
                    : 'almuerzo'),
                fecha_hora: formatLocalISO()
            });
            setEditMode(false);
            // Clear image after analysis if desired, or keep it? Let's clear to show we processed it.
            // actually keeping it might be confusing if we don't store it. For now let's clear.
            setSelectedImage(null);

        } catch (error) {
            console.error('Error analyzing food:', error);
            alert('Error al analizar la comida. Por favor intenta de nuevo.');
        } finally {
            setIsAnalyzing(false);
        }
    };

    const handleSave = async () => {
        if (!estimatedFood) return;

        setIsSaving(true);
        try {
            const dataToSave = {
                ...estimatedFood,
                fecha_hora: normalizeToBackendISO(estimatedFood.fecha_hora || '')
            };
            if (estimatedFood.id) {
                // Update existing record
                const response = await api.put(`/food/${estimatedFood.id}`, dataToSave);
                updateFoodLog(estimatedFood.id, response.data);
            } else {
                // Create new record
                const response = await api.post('/food/log', dataToSave);
                addFoodLog(response.data);
            }

            // Reset form
            setDescription('');
            setEstimatedFood(null);
            setEditMode(false);
        } catch (error) {
            console.error('Error saving food log:', error);
            alert('Error al guardar el registro.');
        } finally {
            setIsSaving(true);
            // Artificial delay for UX feel, though not strictly needed here
            setTimeout(() => setIsSaving(false), 500);
        }
    };

    const handleEdit = (log: FoodRecord) => {
        setEstimatedFood(log);
        setEditMode(true);
        // Scroll to top to see the form
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const handleEditChange = (field: keyof FoodRecord, value: any) => {
        if (!estimatedFood) return;
        setEstimatedFood({
            ...estimatedFood,
            [field]: value
        });
    };

    return (
        <div className="min-h-screen bg-slate-50 p-4 md:p-8">
            <div className="max-w-4xl mx-auto">
                <button
                    onClick={() => navigate('/dashboard')}
                    className="flex items-center gap-2 text-slate-500 hover:text-slate-800 transition-colors mb-6 group"
                >
                    <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
                    <span className="font-medium">Volver al Panel</span>
                </button>

                <div className="bg-white rounded-3xl shadow-xl shadow-slate-200/50 overflow-hidden mb-8 border border-slate-100">
                    <div className="p-6 md:p-8">
                        <div className="flex items-center gap-3 mb-6">
                            <div className="bg-green-100 p-3 rounded-2xl">
                                <Utensils className="w-6 h-6 text-green-600" />
                            </div>
                            <h1 className="text-2xl font-bold text-slate-900">Registro de Alimentos</h1>
                        </div>

                        {!estimatedFood ? (
                            <div className="space-y-4">
                                <label className="block text-sm font-semibold text-slate-700 mb-2">
                                    ¿Qué has comido hoy?
                                </label>

                                <div className="relative">
                                    <textarea
                                        value={description}
                                        onChange={(e) => setDescription(e.target.value)}
                                        placeholder="Describe tu comida o sube una foto..."
                                        className="w-full h-32 px-4 py-3 rounded-2xl border border-slate-200 focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all outline-none resize-none bg-slate-50/50"
                                    />

                                    {/* Image Preview Overlay */}
                                    {previewUrl && (
                                        <div className="absolute top-2 right-2 bottom-2 w-32 rounded-xl overflow-hidden border-2 border-green-500 shadow-md group">
                                            <img src={previewUrl} alt="Preview" className="w-full h-full object-cover" />
                                            <button
                                                onClick={() => setSelectedImage(null)}
                                                className="absolute top-1 right-1 bg-black/50 text-white p-1 rounded-full hover:bg-black/70 transition-colors"
                                            >
                                                <X className="w-4 h-4" />
                                            </button>
                                        </div>
                                    )}
                                </div>

                                <div className="flex gap-3">
                                    <input
                                        type="file"
                                        ref={fileInputRef}
                                        onChange={handleFileSelect}
                                        accept="image/*"
                                        className="hidden"
                                    />
                                    <button
                                        onClick={() => fileInputRef.current?.click()}
                                        className="bg-slate-100 hover:bg-slate-200 text-slate-600 p-4 rounded-2xl transition-all flex items-center justify-center gap-2 font-medium"
                                        title="Subir foto"
                                    >
                                        <Camera className="w-5 h-5" />
                                        <span className="hidden sm:inline">Foto</span>
                                    </button>

                                    <button
                                        onClick={handleAnalyze}
                                        disabled={isAnalyzing || (!description.trim() && !selectedImage)}
                                        className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-slate-300 text-white font-bold py-4 rounded-2xl transition-all shadow-lg shadow-green-200 flex items-center justify-center gap-2 transform active:scale-95"
                                    >
                                        {isAnalyzing ? (
                                            <div className="flex items-center gap-2">
                                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                                <span>Analizando...</span>
                                            </div>
                                        ) : (
                                            <>
                                                <Sparkles className="w-5 h-5" />
                                                <span>Analizar con IA</span>
                                            </>
                                        )}
                                    </button>
                                </div>
                            </div>
                        ) : (
                            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                                <div className="bg-slate-50 rounded-2xl p-6 border border-slate-100">
                                    <div className="flex justify-between items-start mb-6">
                                        <div>
                                            {editMode ? (
                                                <div className="mb-4 space-y-3">
                                                    <div>
                                                        <label className="block text-xs font-semibold text-slate-400 mb-1 uppercase tracking-wider">Descripción (Para re-calcular)</label>
                                                        <div className="flex gap-2">
                                                            <textarea
                                                                value={estimatedFood.description}
                                                                onChange={(e) => handleEditChange('description', e.target.value)}
                                                                className="w-full px-3 py-2 rounded-xl border border-slate-200 focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none bg-white transition-all font-medium text-sm resize-none h-20"
                                                                placeholder="Describe la comida para recalcular..."
                                                            />
                                                            <button
                                                                onClick={async () => {
                                                                    if (!estimatedFood.description?.trim()) return;
                                                                    setIsAnalyzing(true);
                                                                    try {
                                                                        const response = await api.post('/food/analyze', null, {
                                                                            params: { description: estimatedFood.description }
                                                                        });
                                                                        setEstimatedFood(prev => ({
                                                                            ...prev,
                                                                            ...response.data,
                                                                            // Ensure we keep the ID and existing date (unless distinct logic needed)
                                                                            id: prev?.id,
                                                                            user_id: prev?.user_id,
                                                                            fecha_hora: prev?.fecha_hora,
                                                                            // If backend returns meal_type, use it, else keep existing or default
                                                                            meal_type: (['desayuno', 'merienda_manana', 'almuerzo', 'merienda_tarde', 'cena', 'merienda_postcena'].includes(response.data.meal_type?.toLowerCase())
                                                                                ? response.data.meal_type.toLowerCase()
                                                                                : (prev?.meal_type || 'almuerzo'))
                                                                        }));
                                                                    } catch (error) {
                                                                        console.error("Error re-analyzing:", error);
                                                                        alert("Error al re-analizar.");
                                                                    } finally {
                                                                        setIsAnalyzing(false);
                                                                    }
                                                                }}
                                                                disabled={isAnalyzing || !estimatedFood.description?.trim()}
                                                                className="bg-green-100 hover:bg-green-200 text-green-700 p-3 rounded-xl transition-colors flex items-center justify-center disabled:opacity-50"
                                                                title="Re-analizar con IA"
                                                            >
                                                                {isAnalyzing ? <div className="w-5 h-5 border-2 border-green-600 border-t-transparent rounded-full animate-spin" /> : <Sparkles className="w-5 h-5" />}
                                                            </button>
                                                        </div>
                                                    </div>

                                                    <div>
                                                        <label className="block text-xs font-semibold text-slate-400 mb-1 uppercase tracking-wider">Tipo de Comida</label>
                                                        <select
                                                            value={estimatedFood.meal_type?.toLowerCase()}
                                                            onChange={(e) => handleEditChange('meal_type', e.target.value.toLowerCase())}
                                                            className="w-full px-3 py-2 rounded-xl border border-slate-200 focus:ring-2 focus:ring-green-500 focus:border-transparent outline-none bg-white transition-all font-medium text-sm"
                                                        >
                                                            <option value="desayuno">Desayuno</option>
                                                            <option value="merienda_manana">Merienda Mañana</option>
                                                            <option value="almuerzo">Almuerzo</option>
                                                            <option value="merienda_tarde">Merienda Tarde</option>
                                                            <option value="cena">Cena</option>
                                                            <option value="merienda_postcena">Merienda Postcena</option>
                                                        </select>
                                                    </div>
                                                </div>
                                            ) : (
                                                <>
                                                    <h3 className="font-bold text-slate-900 text-lg">{estimatedFood.description}</h3>
                                                    <p className="text-green-600 font-semibold text-sm capitalize">
                                                        {estimatedFood.meal_type?.replace('_', ' ')}
                                                    </p>
                                                </>
                                            )}
                                        </div>
                                        <button
                                            onClick={() => setEditMode(!editMode)}
                                            className="text-slate-400 hover:text-blue-600 transition-colors bg-white p-2 rounded-xl border border-slate-100 shadow-sm"
                                        >
                                            {editMode ? <Check className="w-5 h-5 text-green-600" /> : <Edit2 className="w-5 h-5" />}
                                        </button>
                                    </div>

                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                        <MacroField
                                            label="Calorías"
                                            value={estimatedFood.calories}
                                            unit="kcal"
                                            edit={editMode}
                                            onChange={(val) => handleEditChange('calories', parseInt(val))}
                                        />
                                        <MacroField
                                            label="Proteína"
                                            value={estimatedFood.protein}
                                            unit="g"
                                            edit={editMode}
                                            onChange={(val) => handleEditChange('protein', parseFloat(val))}
                                        />
                                        <MacroField
                                            label="Carbos"
                                            value={estimatedFood.carbs}
                                            unit="g"
                                            edit={editMode}
                                            onChange={(val) => handleEditChange('carbs', parseFloat(val))}
                                        />
                                        <MacroField
                                            label="Grasas"
                                            value={estimatedFood.fat}
                                            unit="g"
                                            edit={editMode}
                                            onChange={(val) => handleEditChange('fat', parseFloat(val))}
                                        />
                                    </div>

                                    {editMode && (
                                        <div className="mt-4 animate-in fade-in duration-300">
                                            <label className="block text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider">Fecha y Hora del Consumo</label>
                                            <input
                                                type="datetime-local"
                                                value={estimatedFood.fecha_hora ? estimatedFood.fecha_hora.slice(0, 16) : ''}
                                                onChange={(e) => handleEditChange('fecha_hora', e.target.value)}
                                                className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none bg-white transition-all font-medium"
                                            />
                                        </div>
                                    )}
                                </div>

                                <div className="flex gap-3">
                                    <button
                                        onClick={() => setEstimatedFood(null)}
                                        className="flex-1 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold py-4 rounded-2xl transition-all"
                                    >
                                        Descartar
                                    </button>
                                    <button
                                        onClick={handleSave}
                                        disabled={isSaving}
                                        className="flex-[2] bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 rounded-2xl transition-all shadow-lg shadow-blue-200 flex items-center justify-center gap-2 transform active:scale-95"
                                    >
                                        {isSaving ? (
                                            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                        ) : (
                                            <>
                                                <Save className="w-5 h-5" />
                                                <span>Guardar Registro</span>
                                            </>
                                        )}
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                <div className="bg-white rounded-3xl shadow-xl shadow-slate-200/50 overflow-hidden border border-slate-100">
                    <div className="p-6 md:p-8">
                        <div className="flex items-center gap-3 mb-6">
                            <div className="bg-blue-100 p-3 rounded-2xl">
                                <PieChart className="w-6 h-6 text-blue-600" />
                            </div>
                            <h2 className="text-xl font-bold text-slate-900">Historial de Hoy</h2>
                        </div>

                        <div className="space-y-4">
                            {storeLoading && foodLogs.length === 0 ? (
                                <div className="py-8 text-center text-slate-400">Cargando historial...</div>
                            ) : foodLogs.length === 0 ? (
                                <div className="py-8 text-center text-slate-400 italic">No hay comidas registradas hoy.</div>
                            ) : (
                                foodLogs.map((log) => (
                                    <div key={log.id} className="group p-4 rounded-2xl border border-slate-100 hover:border-blue-200 hover:bg-blue-50/30 transition-all flex items-center justify-between">
                                        <div className="flex items-center gap-4">
                                            <div className="bg-slate-50 p-3 rounded-xl group-hover:bg-white transition-colors">
                                                <Utensils className="w-5 h-5 text-slate-400" />
                                            </div>
                                            <div>
                                                <h4 className="font-bold text-slate-900">{log.description}</h4>
                                                <p className="text-xs text-slate-500 capitalize">
                                                    {log.meal_type?.replace('_', ' ')} • {log.fecha_hora && new Date(log.fecha_hora).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                                </p>
                                            </div>
                                        </div>
                                        <div className="hidden md:flex gap-4 text-right items-center">
                                            <div className="text-xs">
                                                <p className="text-slate-400">Calorías</p>
                                                <p className="font-bold text-slate-900">{log.calories} kcal</p>
                                            </div>
                                            <div className="text-xs">
                                                <p className="text-slate-400">Macros (P/C/G)</p>
                                                <p className="font-bold text-slate-900">{log.protein}g / {log.carbs}g / {log.fat}g</p>
                                            </div>
                                            <button
                                                onClick={() => handleEdit(log)}
                                                className="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                                                title="Editar registro"
                                            >
                                                <Pencil className="w-4 h-4" />
                                            </button>
                                        </div>
                                        <div className="md:hidden text-right flex flex-col items-end gap-2">
                                            <p className="font-bold text-slate-900 text-sm">{log.calories} kcal</p>
                                            <button
                                                onClick={() => handleEdit(log)}
                                                className="p-1 text-slate-400 hover:text-blue-600"
                                            >
                                                <Pencil className="w-4 h-4" />
                                            </button>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

interface MacroFieldProps {
    label: string;
    value?: number;
    unit: string;
    edit?: boolean;
    onChange?: (val: string) => void;
}

const MacroField: React.FC<MacroFieldProps> = ({ label, value, unit, edit, onChange }) => (
    <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-100">
        <p className="text-xs text-slate-400 mb-1">{label}</p>
        <div className="flex items-baseline gap-1">
            {edit ? (
                <input
                    type="number"
                    value={value || ''}
                    onChange={(e) => onChange && onChange(e.target.value)}
                    className="w-full font-bold text-slate-900 focus:outline-none bg-blue-50 rounded px-1"
                />
            ) : (
                <span className="text-lg font-bold text-slate-900">{value}</span>
            )}
            <span className="text-xs font-medium text-slate-500">{unit}</span>
        </div>
    </div>
);

export default FoodLog;
