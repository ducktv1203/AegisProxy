const API_BASE_url = 'http://localhost:8080/v1';

export interface DashboardStats {
    total_requests: number;
    blocked_requests: number;
    pii_detected: number;
    injection_detected: number;
    start_time: string;
}

export interface ChartDataPoint {
    time: string;
    requests: number;
    blocked: number;
}

export interface DashboardData {
    summary: DashboardStats;
    chart_data: ChartDataPoint[];
}

export const fetchDashboardStats = async (): Promise<DashboardData> => {
    try {
        const response = await fetch(`${API_BASE_url}/dashboard/stats`);
        if (!response.ok) {
            throw new Error(`API Error: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error("Failed to fetch dashboard stats:", error);
        // Return fallback data if API is offline
        return {
            summary: {
                total_requests: 0,
                blocked_requests: 0,
                pii_detected: 0,
                injection_detected: 0,
                start_time: new Date().toISOString()
            },
            chart_data: []
        };
    }
};
