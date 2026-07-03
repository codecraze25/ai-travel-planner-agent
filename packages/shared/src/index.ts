export type TripStatus = "draft" | "planning" | "ready" | "archived";

export interface TripPreferences {
  style?: string[];
  hotel_prefs?: string;
  flight_prefs?: string;
  food_prefs?: string;
  activity_prefs?: string;
  accessibility?: string;
  visa_notes?: string;
  constraints?: string;
}

export interface Trip {
  id: string;
  user_id: string;
  origin: string;
  destination: string;
  start_date: string;
  end_date: string;
  travelers: number;
  budget_usd: number;
  status: TripStatus;
  preferences?: TripPreferences;
  created_at: string;
  updated_at: string;
}

export interface HealthResponse {
  status: string;
}

export interface ReadyResponse {
  status: string;
  checks: Record<string, boolean>;
}
