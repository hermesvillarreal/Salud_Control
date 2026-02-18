import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
    id: string;
    email: string;
    name: string;
    role?: string;
    is_telegram_linked: boolean;
    daily_calories_goal?: number;
    daily_protein_goal?: number;
    daily_carbs_goal?: number;
    daily_fat_goal?: number;
    current_goal?: string;
}

interface AuthState {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
    setAuth: (user: User, token: string) => void;
    updateUser: (userData: Partial<User>) => void;
    logout: () => void;
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            user: null,
            token: null,
            isAuthenticated: false,
            setAuth: (user, token) => set({ user, token, isAuthenticated: true }),
            updateUser: (userData) => set((state) => ({
                user: state.user ? { ...state.user, ...userData } : null
            })),
            logout: () => {
                set({ user: null, token: null, isAuthenticated: false });
                localStorage.removeItem('auth-storage'); // Limpiar persistencia si es necesario
            },
        }),
        {
            name: 'auth-storage',
        }
    )
);
