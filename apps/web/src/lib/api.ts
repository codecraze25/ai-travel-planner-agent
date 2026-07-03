import type { HealthResponse, ReadyResponse, Trip, TripStatus } from "@shared/index";

export type { HealthResponse, ReadyResponse, Trip, TripStatus };

export interface TripCreatePayload {
  origin: string;
  destination: string;
  start_date: string;
  end_date: string;
  travelers: number;
  budget_usd: number;
  preferences?: {
    style?: string[];
    hotel_prefs?: string;
    flight_prefs?: string;
    food_prefs?: string;
    activity_prefs?: string;
    accessibility?: string;
    visa_notes?: string;
    constraints?: string;
  };
}

export interface TripListResponse {
  items: Trip[];
}

export function getApiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
}

export function isClerkEnabled(): boolean {
  return Boolean(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY);
}

async function buildHeaders(token?: string | null): Promise<HeadersInit> {
  const headers: HeadersInit = { "Content-Type": "application/json" };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return headers;
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null,
): Promise<T> {
  const headers = await buildHeaders(token);
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    ...options,
    headers: { ...headers, ...(options.headers ?? {}) },
    cache: "no-store",
  });
  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || `Request failed: ${response.status}`);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

export async function fetchHealth(): Promise<HealthResponse> {
  return apiFetch<HealthResponse>("/health");
}

export async function fetchReady(): Promise<ReadyResponse> {
  return apiFetch<ReadyResponse>("/ready");
}

export async function listTrips(token?: string | null): Promise<Trip[]> {
  const data = await apiFetch<TripListResponse>("/trips", {}, token);
  return data.items;
}

export async function createTrip(
  payload: TripCreatePayload,
  token?: string | null,
): Promise<Trip> {
  return apiFetch<Trip>(
    "/trips",
    { method: "POST", body: JSON.stringify(payload) },
    token,
  );
}

export async function getTrip(id: string, token?: string | null): Promise<Trip> {
  return apiFetch<Trip>(`/trips/${id}`, {}, token);
}

export interface Flight {
  id: string;
  trip_id: string;
  external_id: string;
  airline: string;
  flight_number: string;
  departure_time: string;
  arrival_time: string;
  duration_minutes: number;
  stops: number;
  price_usd: number;
  baggage_info?: string | null;
  booking_link?: string | null;
  cancellation_policy?: string | null;
  selected: boolean;
}

export interface Hotel {
  id: string;
  trip_id: string;
  external_id: string;
  name: string;
  price_per_night_usd: number;
  total_price_usd: number;
  rating?: number | null;
  location?: string | null;
  amenities?: string[] | null;
  cancellation_policy?: string | null;
  photo_urls?: string[] | null;
  booking_link?: string | null;
  selected: boolean;
}

export interface Budget {
  trip_budget_usd: number;
  flight_cost_usd: number;
  hotel_cost_usd: number;
  other_cost_usd: number;
  committed_usd: number;
  remaining_usd: number;
  utilization_pct: number;
  warning?: string | null;
}

export interface FlightSearchResult {
  items: Flight[];
  tradeoffs: {
    best_value_id?: string | null;
    fastest_id?: string | null;
    cheapest_id?: string | null;
    explanations: string[];
  };
}

export async function searchFlights(
  tripId: string,
  payload: { cabin_class?: string; max_price?: number; nonstop_only?: boolean } = {},
  token?: string | null,
): Promise<FlightSearchResult> {
  return apiFetch<FlightSearchResult>(
    `/trips/${tripId}/flights/search`,
    { method: "POST", body: JSON.stringify(payload) },
    token,
  );
}

export async function listFlights(tripId: string, token?: string | null): Promise<Flight[]> {
  return apiFetch<Flight[]>(`/trips/${tripId}/flights`, {}, token);
}

export async function selectFlight(
  tripId: string,
  flightId: string,
  token?: string | null,
): Promise<{ flight: Flight; budget: Budget }> {
  return apiFetch(
    `/trips/${tripId}/flights/${flightId}/select`,
    { method: "POST", body: "{}" },
    token,
  );
}

export async function searchHotels(
  tripId: string,
  payload: { rooms?: number; max_price_per_night?: number; min_rating?: number } = {},
  token?: string | null,
): Promise<{ items: Hotel[] }> {
  return apiFetch(
    `/trips/${tripId}/hotels/search`,
    { method: "POST", body: JSON.stringify(payload) },
    token,
  );
}

export async function listHotels(tripId: string, token?: string | null): Promise<Hotel[]> {
  return apiFetch<Hotel[]>(`/trips/${tripId}/hotels`, {}, token);
}

export async function selectHotel(
  tripId: string,
  hotelId: string,
  token?: string | null,
): Promise<{ hotel: Hotel; budget: Budget }> {
  return apiFetch(
    `/trips/${tripId}/hotels/${hotelId}/select`,
    { method: "POST", body: "{}" },
    token,
  );
}

export async function getBudget(tripId: string, token?: string | null): Promise<Budget> {
  return apiFetch<Budget>(`/trips/${tripId}/budget`, {}, token);
}
