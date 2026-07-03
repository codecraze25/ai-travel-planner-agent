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
