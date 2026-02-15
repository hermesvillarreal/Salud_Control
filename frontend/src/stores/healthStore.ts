import { create } from 'zustand';

interface HealthMetric {
    type: 'peso' | 'presion' | 'glucosa';
    value: number;
    unit: string;
    timestamp: string;
}

interface HealthState {
    metrics: HealthMetric[];
    lastUpdate: string | null;
    isLoading: boolean;
    error: string | null;
    setMetrics: (metrics: HealthMetric[]) => void;
    addMetric: (metric: HealthMetric) => void;
    setLoading: (isLoading: boolean) => void;
    setError: (error: string | null) => void;
}

export const useHealthStore = create<HealthState>((set) => ({
    metrics: [],
    lastUpdate: null,
    isLoading: false,
    error: null,
    setMetrics: (metrics) => set({ metrics, lastUpdate: new Date().toISOString() }),
    addMetric: (metric) => set((state) => ({
        metrics: [metric, ...state.metrics],
        lastUpdate: new Date().toISOString()
    })),
    setLoading: (isLoading) => set({ isLoading }),
    setError: (error) => set({ error }),
}));
