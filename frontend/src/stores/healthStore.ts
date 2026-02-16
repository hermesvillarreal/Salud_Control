import { create } from 'zustand';
import api from '../services/api';

export type MealType = 'desayuno' | 'merienda_manana' | 'almuerzo' | 'merienda_tarde' | 'cena' | 'merienda_postcena';

export interface FoodRecord {
    id?: number;
    user_id?: number;
    fecha_hora?: string;
    meal_type: MealType;
    description: string;
    calories?: number;
    protein?: number;
    carbs?: number;
    fat?: number;
    image_url?: string;
}

export interface ExerciseRecord {
    id?: number;
    user_id?: number;
    fecha_hora?: string;
    exercise_type: string;
    duration_minutes: number;
    calories_burned?: number;
    intensity: 'baja' | 'media' | 'alta';
}

interface HealthMetric {
    type: 'peso' | 'presion' | 'glucosa';
    value: number;
    unit: string;
    timestamp: string;
}

interface HealthState {
    metrics: HealthMetric[];
    foodLogs: FoodRecord[];
    exerciseLogs: ExerciseRecord[];
    lastUpdate: string | null;
    isLoading: boolean;
    error: string | null;
    setMetrics: (metrics: HealthMetric[]) => void;
    addMetric: (metric: HealthMetric) => void;
    setFoodLogs: (logs: FoodRecord[]) => void;
    addFoodLog: (log: FoodRecord) => void;
    fetchFoodLogs: () => Promise<void>;
    setExerciseLogs: (logs: ExerciseRecord[]) => void;
    addExerciseLog: (log: ExerciseRecord) => void;
    fetchExerciseLogs: () => Promise<void>;
    fetchMetrics: () => Promise<void>;
    setLoading: (isLoading: boolean) => void;
    setError: (error: string | null) => void;
}

export const useHealthStore = create<HealthState>((set) => ({
    metrics: [],
    foodLogs: [],
    exerciseLogs: [],
    lastUpdate: null,
    isLoading: false,
    error: null,
    setMetrics: (metrics: HealthMetric[]) => set({ metrics, lastUpdate: new Date().toISOString() }),
    addMetric: (metric: HealthMetric) => set((state: HealthState) => ({
        metrics: [metric, ...state.metrics],
        lastUpdate: new Date().toISOString()
    })),
    setFoodLogs: (foodLogs: FoodRecord[]) => set({ foodLogs, lastUpdate: new Date().toISOString() }),
    addFoodLog: (log: FoodRecord) => set((state: HealthState) => ({
        foodLogs: [log, ...state.foodLogs],
        lastUpdate: new Date().toISOString()
    })),
    fetchFoodLogs: async () => {
        set({ isLoading: true, error: null });
        try {
            const response = await api.get('/food');
            set({ foodLogs: response.data, isLoading: false });
        } catch (error: any) {
            set({ error: error.message || 'Error fetching food logs', isLoading: false });
        }
    },
    setExerciseLogs: (exerciseLogs: ExerciseRecord[]) => set({ exerciseLogs, lastUpdate: new Date().toISOString() }),
    addExerciseLog: (log: ExerciseRecord) => set((state: HealthState) => ({
        exerciseLogs: [log, ...state.exerciseLogs],
        lastUpdate: new Date().toISOString()
    })),
    fetchExerciseLogs: async () => {
        set({ isLoading: true, error: null });
        try {
            const response = await api.get('/exercise');
            set({ exerciseLogs: response.data, isLoading: false });
        } catch (error: any) {
            set({ error: error.message || 'Error fetching exercise logs', isLoading: false });
        }
    },
    fetchMetrics: async () => {
        set({ isLoading: true, error: null });
        try {
            const [weights, bp, glucose] = await Promise.all([
                api.get('/health/weight'),
                api.get('/health/bp'),
                api.get('/health/glucose')
            ]);

            const allMetrics: HealthMetric[] = [
                ...weights.data.map((w: any) => ({ type: 'peso' as const, value: w.weight, unit: 'kg', timestamp: w.fecha_hora })),
                ...bp.data.map((b: any) => ({ type: 'presion' as const, value: b.systolic, unit: 'mmHg', timestamp: b.fecha_hora })),
                ...glucose.data.map((g: any) => ({ type: 'glucosa' as const, value: g.glucose_level, unit: 'mg/dL', timestamp: g.fecha_hora }))
            ];

            set({ metrics: allMetrics, isLoading: false, lastUpdate: new Date().toISOString() });
        } catch (error: any) {
            set({ error: error.message || 'Error fetching metrics', isLoading: false });
        }
    },
    setLoading: (isLoading: boolean) => set({ isLoading }),
    setError: (error: string | null) => set({ error }),
}));
