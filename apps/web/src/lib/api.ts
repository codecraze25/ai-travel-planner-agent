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

export interface ExtractedFields {
  dates: string[];
  times: string[];
  locations: string[];
  reservation_numbers: string[];
  passenger_names: string[];
  confirmation_codes: string[];
  check_in?: string | null;
  check_out?: string | null;
  policy_rules: string[];
}

export interface DocumentItem {
  id: string;
  trip_id: string;
  filename: string;
  mime_type: string;
  size_bytes: number;
  status: "uploaded" | "parsing" | "ready" | "failed";
  extracted_fields?: ExtractedFields | null;
  error_message?: string | null;
  injection_flagged: boolean;
  created_at: string;
}

export interface DocumentCitation {
  document_id: string;
  filename: string;
  chunk_index: number;
  content: string;
  score: number;
}

export async function listDocuments(
  tripId: string,
  token?: string | null,
): Promise<DocumentItem[]> {
  const data = await apiFetch<{ items: DocumentItem[] }>(
    `/trips/${tripId}/documents`,
    {},
    token,
  );
  return data.items;
}

export async function uploadDocument(
  tripId: string,
  file: File,
  token?: string | null,
): Promise<DocumentItem> {
  const form = new FormData();
  form.append("file", file);
  const headers: HeadersInit = {};
  if (token) headers.Authorization = `Bearer ${token}`;
  const response = await fetch(`${getApiBaseUrl()}/trips/${tripId}/documents`, {
    method: "POST",
    headers,
    body: form,
  });
  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || `Upload failed: ${response.status}`);
  }
  return response.json() as Promise<DocumentItem>;
}

export async function parseDocument(
  tripId: string,
  documentId: string,
  token?: string | null,
): Promise<DocumentItem> {
  return apiFetch<DocumentItem>(
    `/trips/${tripId}/documents/${documentId}/parse`,
    { method: "POST", body: "{}" },
    token,
  );
}

export async function deleteDocument(
  tripId: string,
  documentId: string,
  token?: string | null,
): Promise<void> {
  await apiFetch<void>(
    `/trips/${tripId}/documents/${documentId}`,
    { method: "DELETE" },
    token,
  );
}

export async function searchDocuments(
  tripId: string,
  query: string,
  token?: string | null,
): Promise<{ citations: DocumentCitation[]; facts_note: string }> {
  return apiFetch(
    `/trips/${tripId}/documents/search`,
    { method: "POST", body: JSON.stringify({ query, limit: 5 }) },
    token,
  );
}

export interface ItineraryItem {
  id: string;
  day_number: number;
  time_block: string;
  title: string;
  description: string;
  location?: string | null;
  est_cost_usd: number;
  map_url?: string | null;
  backup_option?: string | null;
}

export interface Itinerary {
  id: string;
  trip_id: string;
  version: number;
  total_est_cost_usd: number;
  created_at: string;
  items: ItineraryItem[];
}

export async function getItinerary(
  tripId: string,
  token?: string | null,
): Promise<Itinerary> {
  return apiFetch<Itinerary>(`/trips/${tripId}/itinerary`, {}, token);
}

export async function generateItinerary(
  tripId: string,
  regenerateDay?: number,
  token?: string | null,
): Promise<Itinerary> {
  return apiFetch<Itinerary>(
    `/trips/${tripId}/itinerary/generate`,
    {
      method: "POST",
      body: JSON.stringify({ regenerate_day: regenerateDay ?? null }),
    },
    token,
  );
}

export type AgentStreamEvent = {
  type: string;
  role?: string;
  content?: string;
  tool?: string;
  input?: unknown;
  output?: unknown;
  data?: unknown;
};

export type EmailStatus = "draft" | "approved" | "rejected" | "exported" | "sent";
export type EmailTemplate = "itinerary_summary" | "family_share";

export interface EmailDraft {
  id: string;
  trip_id: string;
  template: EmailTemplate;
  status: EmailStatus;
  recipients: string;
  subject: string;
  body_text: string;
  body_html: string;
  approved_at?: string | null;
  sent_at?: string | null;
  provider_message_id?: string | null;
  created_at: string;
  updated_at: string;
}

export async function getLatestEmail(
  tripId: string,
  token?: string | null,
): Promise<EmailDraft> {
  return apiFetch<EmailDraft>(`/trips/${tripId}/emails/latest`, {}, token);
}

export async function draftEmail(
  tripId: string,
  template: EmailTemplate = "itinerary_summary",
  recipients?: string,
  token?: string | null,
): Promise<EmailDraft> {
  return apiFetch<EmailDraft>(
    `/trips/${tripId}/emails/draft`,
    {
      method: "POST",
      body: JSON.stringify({ template, recipients: recipients ?? null }),
    },
    token,
  );
}

export async function updateEmail(
  tripId: string,
  emailId: string,
  payload: {
    recipients?: string;
    subject?: string;
    body_text?: string;
    body_html?: string;
  },
  token?: string | null,
): Promise<EmailDraft> {
  return apiFetch<EmailDraft>(
    `/trips/${tripId}/emails/${emailId}`,
    { method: "PATCH", body: JSON.stringify(payload) },
    token,
  );
}

export async function approveEmail(
  tripId: string,
  emailId: string,
  token?: string | null,
): Promise<EmailDraft> {
  return apiFetch<EmailDraft>(
    `/trips/${tripId}/emails/${emailId}/approve`,
    { method: "POST", body: "{}" },
    token,
  );
}

export async function rejectEmail(
  tripId: string,
  emailId: string,
  token?: string | null,
): Promise<EmailDraft> {
  return apiFetch<EmailDraft>(
    `/trips/${tripId}/emails/${emailId}/reject`,
    { method: "POST", body: "{}" },
    token,
  );
}

export async function exportEmail(
  tripId: string,
  emailId: string,
  token?: string | null,
): Promise<{ email: EmailDraft; eml: string; filename: string }> {
  return apiFetch(
    `/trips/${tripId}/emails/${emailId}/export`,
    { method: "POST", body: "{}" },
    token,
  );
}

export async function sendEmail(
  tripId: string,
  emailId: string,
  token?: string | null,
): Promise<{ email: EmailDraft; provider: string; message_id: string; mock: boolean }> {
  return apiFetch(
    `/trips/${tripId}/emails/${emailId}/send`,
    { method: "POST", body: "{}" },
    token,
  );
}

export interface CalendarEvent {
  title: string;
  start: string;
  end: string;
  location: string;
  source: string;
}

export async function getCalendar(
  tripId: string,
  token?: string | null,
): Promise<{ source: string; items: CalendarEvent[]; note?: string | null }> {
  return apiFetch(`/trips/${tripId}/calendar`, {}, token);
}

export interface ActivityItem {
  id: string;
  kind: string;
  action: string;
  success?: boolean | null;
  details?: Record<string, unknown> | null;
  error_message?: string | null;
  created_at: string;
}

export async function listActivity(
  tripId: string,
  token?: string | null,
): Promise<ActivityItem[]> {
  const data = await apiFetch<{ items: ActivityItem[] }>(
    `/trips/${tripId}/activity`,
    {},
    token,
  );
  return data.items;
}

export async function streamAgentChat(
  tripId: string,
  message: string,
  onEvent: (event: AgentStreamEvent) => void,
  signal?: AbortSignal,
  token?: string | null,
): Promise<void> {
  const headers: HeadersInit = { "Content-Type": "application/json" };
  if (token) headers.Authorization = `Bearer ${token}`;

  const response = await fetch(`${getApiBaseUrl()}/trips/${tripId}/agent/chat`, {
    method: "POST",
    headers,
    body: JSON.stringify({ message }),
    signal,
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || `Chat failed: ${response.status}`);
  }

  const reader = response.body?.getReader();
  if (!reader) throw new Error("No response stream");

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";
    for (const line of lines) {
      if (line.startsWith("data: ")) {
        try {
          onEvent(JSON.parse(line.slice(6)) as AgentStreamEvent);
        } catch {
          // skip malformed chunks
        }
      }
    }
  }
}
