const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export async function api(path, options = {}) {
    const response = await fetch(`${API_BASE}${path}`, {
        ...options,
        credentials: "include",
        headers: {
            ...(options.body ? { "Content-Type": "application/json" } : {}),
            ...options.headers,
        },
    });

    if (!response.ok) {
        let message = `Request failed (${response.status})`;
        try {
            const error = await response.json();
            message = error.detail || message;
        } catch {
            // Keep the HTTP status message when the response has no JSON body.
        }
        const error = new Error(message);
        error.status = response.status;
        throw error;
    }

    if (response.status === 204) return null;
    return response.json();
}

export const dashboardRequests = [
    ["summary", "/dashboard/summary"],
    ["customers", "/customers?limit=100"],
    ["bookings", "/bookings?limit=100"],
    ["cases", "/support-cases?limit=100"],
];