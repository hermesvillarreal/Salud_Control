import { create } from 'zustand';
import api from '../services/api';

export type MealType = 'desayuno' | 'almuerzo' | 'cena' | 'snack';

export interface FoodRecord {
    id?: number;
    user_id?: number;
    date?: string;
    meal_type: MealType;
    description: string;
    calories?: number;
    protein?: number;
    carbs?: number;
    fat?: number;
    image_url?: string;
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
    lastUpdate: string | null;
    isLoading: boolean;
    error: string | null;
    setMetrics: (metrics: HealthMetric[]) => void;
    addMetric: (metric: HealthMetric) => void;
    setFoodLogs: (logs: FoodRecord[]) => void;
    addFoodLog: (log: FoodRecord) => void;
    fetchFoodLogs: () => Promise<void>;
    fetchMetrics: () => Promise<void>;
    setLoading: (isLoading: boolean) => void;
    setError: (error: string | null) => void;
}

export const useHealthStore = create<HealthState>((set, get) => ({
    metrics: [],
    foodLogs: [],
    lastUpdate: null,
    isLoading: false,
    error: null,
    setMetrics: (metrics) => set({ metrics, lastUpdate: new Date().toISOString() }),
    addMetric: (metric) => set((state) => ({
        metrics: [metric, ...state.metrics],
        lastUpdate: new Date().toISOString()
    })),
    setFoodLogs: (foodLogs) => set({ foodLogs, lastUpdate: new Date().toISOString() }),
    addFoodLog: (log) => set((state) => ({
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
    fetchMetrics: async () => {
        set({ isLoading: true, error: null });
        try {
            const [weights, bp, glucose] = await Promise.all([
                api.get('/health/weight'),
                api.get('/health/bp'),
                api.get('/health/glucose')
            ]);

            const allMetrics: HealthMetric[] = [
                ...weights.data.map((w: any) => ({ type: 'peso' as const, value: w.weight, unit: 'kg', timestamp: w.date })),
                ...bp.data.map((b: any) => ({ type: 'presion' as const, value: b.systolic, unit: 'mmHg', timestamp: b.date })),
                ...glucose.data.map((g: any) => ({ type: 'glucosa' as const, value: g.glucose_level, unit: 'mg/dL', timestamp: g.date }))
            ];

            set({ metrics: allMetrics, isLoading: false, lastUpdate: new Date().toISOString() });
        } catch (error: any) {
            set({ error: error.message || 'Error fetching metrics', isLoading: false });
        }
    },
    setLoading: (isLoading) => set({ isLoading }),
    setError: (error) => set({ error }),
}));
