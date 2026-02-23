// Helper function to get local date in ISO format for backend
// Helper function to get local date in ISO format (YYYY-MM-DDTHH:mm:ss) for backend
export const getLocalISOString = (date: Date = new Date()): string => {
    const offset = date.getTimezoneOffset() * 60000;
    const localDate = new Date(date.getTime() - offset);
    return localDate.toISOString().slice(0, 19);
};

// Returns date in YYYY-MM-DDTHH:mm format for datetime-local inputs
export const formatLocalISO = (date: Date = new Date()): string => {
    const offset = date.getTimezoneOffset() * 60000;
    const localDate = new Date(date.getTime() - offset);
    return localDate.toISOString().slice(0, 16);
};

// Normalizes an input string (from datetime-local) to YYYY-MM-DDTHH:mm:ss for backend
export const normalizeToBackendISO = (input: string): string => {
    if (!input) return getLocalISOString();
    // If it's already a full ISO string from the input, just ensure it has seconds if needed
    // but usually backend accepts YYYY-MM-DDTHH:mm
    return input.length === 16 ? `${input}:00` : input;
};

// Returns date in YYYY-MM-DD format for date inputs
export const getLocalDateString = (date: Date = new Date()): string => {
    const offset = date.getTimezoneOffset() * 60000;
    const localDate = new Date(date.getTime() - offset);
    return localDate.toISOString().split('T')[0];
};
