import React, { useState, useEffect, useRef } from 'react';
import { ArrowLeft, Sparkles, Save, Edit2, Check, Dumbbell, Activity, Camera, Pencil, Info } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { useHealthStore, ExerciseRecord } from '../stores/healthStore';
import { formatLocalISO, normalizeToBackendISO } from '../utils/dateUtils';

const ExerciseLog: React.FC = () => {
    const navigate = useNavigate();
    const { exerciseLogs, addExerciseLog, updateExerciseLog, fetchExerciseLogs, isLoading: storeLoading } = useHealthStore();

    // Form state
    const [description, setDescription] = useState('');
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const recalcDescRef = useRef<HTMLTextAreaElement>(null);

    // Confirmation/Edit state
    const [estimatedExercise, setEstimatedExercise] = useState<any | null>(null);
    const [editMode, setEditMode] = useState(false);

    useEffect(() => {
        console.log('Fetching exercise logs...');
        fetchExerciseLogs();
    }, [fetchExerciseLogs]);

    useEffect(() => {
        console.log('Exercise logs updated:', exerciseLogs);
    }, [exerciseLogs]);

    const handleAnalyze = async () => {
        if (!description.trim()) return;

        setIsAnalyzing(true);
        try {
            const response = await api.post('/exercise/analyze', null, {
                params: { description }
            });

            setEstimatedExercise({
                ...response.data,
                fecha_hora: formatLocalISO()
            });
            setEditMode(false);
        } catch (error) {
            console.error('Error analyzing exercise:', error);
            alert('No pudimos analizar el ejercicio con IA, pero puedes ingresar los datos manualmente.');
            setEstimatedExercise({
                exercise_type: description || "Nuevo ejercicio",
                duration_minutes: 0,
                calories_burned: 0,
                intensity: 'media',
                met: 0,
                rpe: 0,
                fecha_hora: formatLocalISO()
            });
            setEditMode(true);
        } finally {
            setIsAnalyzing(false);
        }
    };

    const handleImageUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);
        if (description) formData.append('description', description);

        setIsAnalyzing(true);
        try {
            const response = await api.post('/exercise/analyze-image', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            setEstimatedExercise({
                ...response.data,
                fecha_hora: formatLocalISO()
            });
            setEditMode(false);
        } catch (error) {
            console.error('Error analyzing image:', error);
            alert('No pudimos analizar la imagen con IA, pero puedes ingresar los datos manualmente.');
            setEstimatedExercise({
                exercise_type: description || "Nuevo ejercicio (desde imagen)",
                duration_minutes: 0,
                calories_burned: 0,
                intensity: 'media',
                met: 0,
                rpe: 0,
                fecha_hora: formatLocalISO()
            });
            setEditMode(true);
        } finally {
            setIsAnalyzing(false);
        }
    };

    const handleSave = async () => {
        if (!estimatedExercise) return;

        setIsSaving(true);
        try {
            const dataToSave = {
                ...estimatedExercise,
                fecha_hora: normalizeToBackendISO(estimatedExercise.fecha_hora || '')
            };
            if (estimatedExercise.id) {
                // Update existing record
                const response = await api.put(`/exercise/${estimatedExercise.id}`, dataToSave);
                updateExerciseLog(estimatedExercise.id, response.data);
            } else {
                // Create new record
                const response = await api.post('/exercise', dataToSave);
                addExerciseLog(response.data);
            }

            // Reset form
            setDescription('');
            setEstimatedExercise(null);
            setEditMode(false);
        } catch (error) {
            console.error('Error saving exercise log:', error);
            alert('Error al guardar el registro.');
        } finally {
            setIsSaving(false);
        }
    };

    const handleEdit = (log: ExerciseRecord) => {
        setEstimatedExercise(log);
        setEditMode(true);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const handleEditChange = (field: keyof ExerciseRecord, value: any) => {
        if (!estimatedExercise) return;
        setEstimatedExercise({
            ...estimatedExercise,
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
                            <div className="bg-orange-100 p-3 rounded-2xl">
                                <Dumbbell className="w-6 h-6 text-orange-600" />
                            </div>
                            <h1 className="text-2xl font-bold text-slate-900">Registro de Ejercicio</h1>
                        </div>

                        {!estimatedExercise ? (
                            <div className="space-y-4">
                                <label className="block text-sm font-semibold text-slate-700 mb-2">
                                    ¿Qué ejercicio has hecho?
                                </label>
                                <div className="relative">
                                    <textarea
                                        value={description}
                                        onChange={(e) => setDescription(e.target.value)}
                                        placeholder="Ej: Corrí 30 minutos a ritmo moderado por el parque..."
                                        className="w-full h-32 px-4 py-3 rounded-2xl border border-slate-200 focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all outline-none resize-none bg-slate-50/50"
                                    />
                                    <button
                                        onClick={() => fileInputRef.current?.click()}
                                        className="absolute bottom-4 right-4 bg-white p-2 rounded-xl shadow-sm border border-slate-100 text-slate-400 hover:text-orange-500 transition-colors"
                                        title="Subir foto del ejercicio"
                                    >
                                        <Camera className="w-5 h-5" />
                                    </button>
                                    <input
                                        type="file"
                                        ref={fileInputRef}
                                        onChange={handleImageUpload}
                                        className="hidden"
                                        accept="image/*"
                                    />
                                </div>
                                <button
                                    onClick={handleAnalyze}
                                    disabled={isAnalyzing || !description.trim()}
                                    className="w-full bg-orange-600 hover:bg-orange-700 disabled:bg-slate-300 text-white font-bold py-4 rounded-2xl transition-all shadow-lg shadow-orange-200 flex items-center justify-center gap-2 transform active:scale-95"
                                >
                                    {isAnalyzing ? (
                                        <div className="flex items-center gap-2">
                                            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                            <span>Analizando con IA...</span>
                                        </div>
                                    ) : (
                                        <>
                                            <Sparkles className="w-5 h-5" />
                                            <span>Analizar con IA</span>
                                        </>
                                    )}
                                </button>
                            </div>
                        ) : (
                            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                                <div className="bg-slate-50 rounded-2xl p-6 border border-slate-100">
                                    <div className="flex justify-between items-start mb-6">
                                        <div>
                                            {editMode ? (
                                                <div className="mb-4 space-y-3">
                                                    <div>
                                                        <label className="block text-xs font-semibold text-slate-400 mb-1 uppercase tracking-wider">Re-calcular con IA</label>
                                                        <div className="flex gap-2">
                                                            <textarea
                                                                ref={recalcDescRef}
                                                                placeholder="Ej: Corrí 45 minutos..."
                                                                className="w-full px-3 py-2 rounded-xl border border-slate-200 focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none bg-white transition-all font-medium text-sm resize-none h-20"
                                                            />
                                                            <button
                                                                onClick={async () => {
                                                                    const val = recalcDescRef.current?.value;
                                                                    if (!val?.trim()) return;

                                                                    setIsAnalyzing(true);
                                                                    try {
                                                                        const response = await api.post('/exercise/analyze', null, {
                                                                            params: { description: val }
                                                                        });
                                                                        setEstimatedExercise(prev => ({
                                                                            ...prev,
                                                                            ...response.data,
                                                                            id: prev?.id,
                                                                            user_id: prev?.user_id,
                                                                            fecha_hora: prev?.fecha_hora
                                                                        }));
                                                                    } catch (error) {
                                                                        console.error("Error re-analyzing:", error);
                                                                        alert("Error al re-analizar. Puedes seguir editando los datos manualmente.");
                                                                    } finally {
                                                                        setIsAnalyzing(false);
                                                                    }
                                                                }}
                                                                disabled={isAnalyzing}
                                                                className="bg-orange-100 hover:bg-orange-200 text-orange-700 p-3 rounded-xl transition-colors flex items-center justify-center disabled:opacity-50"
                                                                title="Re-analizar con IA"
                                                            >
                                                                {isAnalyzing ? <div className="w-5 h-5 border-2 border-orange-600 border-t-transparent rounded-full animate-spin" /> : <Sparkles className="w-5 h-5" />}
                                                            </button>
                                                        </div>
                                                    </div>

                                                    <div className="mb-2">
                                                        <label className="block text-xs font-semibold text-slate-400 mb-1 uppercase tracking-wider">Tipo de Ejercicio</label>
                                                        <input
                                                            type="text"
                                                            value={estimatedExercise.exercise_type}
                                                            onChange={(e) => handleEditChange('exercise_type', e.target.value)}
                                                            className="w-full px-3 py-2 rounded-xl border border-slate-200 focus:ring-2 focus:ring-orange-500 focus:border-transparent outline-none bg-white transition-all font-medium text-sm"
                                                        />
                                                    </div>
                                                </div>
                                            ) : (
                                                <>
                                                    <h3 className="font-bold text-slate-900 text-lg">{estimatedExercise.exercise_type}</h3>
                                                    <p className="text-orange-600 font-semibold text-sm capitalize">
                                                        Intensidad {estimatedExercise.intensity}
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

                                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                                        <ExerciseField
                                            label="Duración"
                                            value={estimatedExercise.duration_minutes}
                                            unit="min"
                                            edit={editMode}
                                            onChange={(val) => handleEditChange('duration_minutes', parseInt(val))}
                                        />
                                        <ExerciseField
                                            label="Calorías"
                                            value={estimatedExercise.calories_burned}
                                            unit="kcal"
                                            edit={editMode}
                                            onChange={(val) => handleEditChange('calories_burned', parseInt(val))}
                                        />
                                        <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-100">
                                            <p className="text-xs text-slate-400 mb-1">Intensidad</p>
                                            {editMode ? (
                                                <select
                                                    value={estimatedExercise.intensity}
                                                    onChange={(e) => handleEditChange('intensity', e.target.value)}
                                                    className="w-full font-bold text-slate-900 focus:outline-none bg-orange-50 rounded px-1"
                                                >
                                                    <option value="baja">Baja</option>
                                                    <option value="media">Media</option>
                                                    <option value="alta">Alta</option>
                                                </select>
                                            ) : (
                                                <span className="text-lg font-bold text-slate-900 capitalize">{estimatedExercise.intensity}</span>
                                            )}
                                        </div>
                                        <ExerciseField
                                            label="MET Estimado"
                                            value={estimatedExercise.met}
                                            unit="METs"
                                            tooltip="Metabolic Equivalent of Task. 1=Reposo, 3-5=Moderado, 8+=Intenso. Es la intensidad relativa de la actividad."
                                            edit={editMode}
                                            onChange={(val) => handleEditChange('met', parseFloat(val))}
                                        />
                                        {editMode && (
                                            <ExerciseField
                                                label="RPE (1-10)"
                                                value={estimatedExercise.rpe}
                                                unit=""
                                                tooltip="Escala de Esfuerzo Percibido. 1=Muy suave, 10=Esfuerzo máximo. Indica cómo sentiste la intensidad del ejercicio."
                                                edit={editMode}
                                                onChange={(val) => handleEditChange('rpe', parseInt(val))}
                                            />
                                        )}
                                    </div>

                                    {!editMode && estimatedExercise.ratio_to_resting && (
                                        <div className="mt-4 p-4 bg-orange-50 rounded-xl border border-orange-100 flex items-center gap-3">
                                            <div className="bg-white p-2 rounded-lg shadow-sm">🚀</div>
                                            <div className="text-sm">
                                                <p className="text-slate-600">
                                                    Este ejercicio equivale a <span className="font-bold text-orange-600">{estimatedExercise.ratio_to_resting.toFixed(1)} veces</span> tu gasto en reposo.
                                                    Usa un <span className="font-bold">MET de {estimatedExercise.met}</span> y un <span className="font-bold">RPE de {estimatedExercise.rpe}</span>.
                                                </p>
                                            </div>
                                        </div>
                                    )}

                                    {editMode && (
                                        <div className="mt-4 animate-in fade-in duration-300">
                                            <label className="block text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider">Fecha y Hora</label>
                                            <input
                                                type="datetime-local"
                                                value={estimatedExercise.fecha_hora ? estimatedExercise.fecha_hora.slice(0, 16) : ''}
                                                onChange={(e) => handleEditChange('fecha_hora', e.target.value)}
                                                className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none bg-white transition-all font-medium"
                                            />
                                        </div>
                                    )}
                                </div>

                                <div className="flex gap-3">
                                    <button
                                        onClick={() => setEstimatedExercise(null)}
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
                            <div className="bg-orange-100 p-3 rounded-2xl">
                                <Activity className="w-6 h-6 text-orange-600" />
                            </div>
                            <h2 className="text-xl font-bold text-slate-900">Historial de Ejercicio</h2>
                        </div>

                        <div className="space-y-4">
                            {storeLoading && exerciseLogs.length === 0 ? (
                                <div className="py-8 text-center text-slate-400">Cargando historial...</div>
                            ) : exerciseLogs.length === 0 ? (
                                <div className="py-8 text-center text-slate-400 italic">No hay ejercicios registrados hoy.</div>
                            ) : (
                                exerciseLogs.map((log) => (
                                    <div key={log.id} className="group p-4 rounded-2xl border border-slate-100 hover:border-orange-200 hover:bg-orange-50/30 transition-all flex items-center justify-between">
                                        <div className="flex items-center gap-4">
                                            <div className="bg-slate-50 p-3 rounded-xl group-hover:bg-white transition-colors">
                                                <Dumbbell className="w-5 h-5 text-slate-400" />
                                            </div>
                                            <div>
                                                <h4 className="font-bold text-slate-900">{log.exercise_type || 'Ejercicio'}</h4>
                                                <p className="text-xs text-slate-500 capitalize">
                                                    {log.duration_minutes || 0} min • {log.intensity || 'media'} • {(() => {
                                                        try {
                                                            if (!log.fecha_hora) return 'Sin hora';
                                                            return new Date(log.fecha_hora).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                                                        } catch (e) {
                                                            console.error('Error parsing date for log:', log.id, e);
                                                            return 'Error hora';
                                                        }
                                                    })()}
                                                </p>
                                            </div>
                                        </div>
                                        <div className="hidden md:flex gap-4 text-right items-center">
                                            <div className="text-xs">
                                                <p className="text-slate-400">Quema</p>
                                                <p className="font-bold text-slate-900">{log.calories_burned} kcal</p>
                                            </div>
                                            <button
                                                onClick={() => handleEdit(log)}
                                                className="p-2 text-slate-400 hover:text-orange-600 hover:bg-orange-50 rounded-lg transition-colors"
                                                title="Editar registro"
                                            >
                                                <Pencil className="w-4 h-4" />
                                            </button>
                                        </div>
                                        <div className="md:hidden text-right flex flex-col items-end gap-2">
                                            <p className="font-bold text-slate-900 text-sm">{log.calories_burned} kcal</p>
                                            <button
                                                onClick={() => handleEdit(log)}
                                                className="p-1 text-slate-400 hover:text-orange-600"
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

interface ExerciseFieldProps {
    label: string;
    value?: number;
    unit: string;
    edit?: boolean;
    tooltip?: string;
    onChange?: (val: string) => void;
}

const ExerciseField: React.FC<ExerciseFieldProps> = ({ label, value, unit, edit, tooltip, onChange }) => (
    <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-100 group relative">
        <div className="flex items-center gap-1 mb-1">
            <p className="text-xs text-slate-400">{label}</p>
            {tooltip && (
                <div className="relative group/tooltip">
                    <Info size={12} className="text-slate-300 cursor-help" />
                    <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-48 p-2 bg-slate-800 text-white text-[10px] rounded shadow-lg opacity-0 group-hover/tooltip:opacity-100 transition-opacity pointer-events-none z-50">
                        {tooltip}
                        <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-slate-800"></div>
                    </div>
                </div>
            )}
        </div>
        <div className="flex items-baseline gap-1">
            {edit ? (
                <input
                    type="number"
                    value={value || ''}
                    onChange={(e) => onChange && onChange(e.target.value)}
                    className="w-full font-bold text-slate-900 focus:outline-none bg-orange-50 rounded px-1"
                />
            ) : (
                <span className="text-lg font-bold text-slate-900">{value}</span>
            )}
            <span className="text-xs font-medium text-slate-500">{unit}</span>
        </div>
    </div>
);

export default ExerciseLog;
