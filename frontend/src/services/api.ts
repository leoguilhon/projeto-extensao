import axios from "axios";
import type {
  AuthResponse,
  Book,
  Club,
  ClubMember,
  Comment,
  Meeting,
  MeetingAttendee,
  ReadingHistoryItem,
  ReadingStatus,
  User,
} from "../types";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("lendojuntos:token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export function getErrorMessage(error: unknown) {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    return typeof detail === "string" ? detail : "Não foi possível concluir a operação.";
  }
  return "Não foi possível concluir a operação.";
}

export const authService = {
  login(email: string, password: string) {
    return api.post<AuthResponse>("/auth/login", { email, password }).then((response) => response.data);
  },
  register(name: string, email: string, password: string) {
    return api.post<AuthResponse>("/auth/register", { name, email, password }).then((response) => response.data);
  },
  me() {
    return api.get<User>("/users/me").then((response) => response.data);
  },
  updateProfile(name: string, bio: string) {
    return api.put<User>("/users/me", { name, bio }).then((response) => response.data);
  },
};

export const clubService = {
  list() {
    return api.get<Club[]>("/clubs").then((response) => response.data);
  },
  create(name: string, description: string) {
    return api.post<Club>("/clubs", { name, description }).then((response) => response.data);
  },
  get(id: string | number) {
    return api.get<Club>(`/clubs/${id}`).then((response) => response.data);
  },
  update(id: string | number, payload: { name: string; description: string }) {
    return api.put<Club>(`/clubs/${id}`, payload).then((response) => response.data);
  },
  join(id: string | number) {
    return api.post<Club>(`/clubs/${id}/join`).then((response) => response.data);
  },
  favorite(id: string | number) {
    return api.post<Club>(`/clubs/${id}/favorite`).then((response) => response.data);
  },
  unfavorite(id: string | number) {
    return api.delete<Club>(`/clubs/${id}/favorite`).then((response) => response.data);
  },
  leave(id: string | number) {
    return api.delete<Club>(`/clubs/${id}/members/me`).then((response) => response.data);
  },
  remove(id: string | number) {
    return api.delete<void>(`/clubs/${id}`).then((response) => response.data);
  },
  members(id: string | number) {
    return api.get<ClubMember[]>(`/clubs/${id}/members`).then((response) => response.data);
  },
};

export const bookService = {
  listByClub(clubId: string | number) {
    return api.get<Book[]>(`/clubs/${clubId}/books`).then((response) => response.data);
  },
  create(clubId: string | number, payload: { title: string; author: string; description: string; status: ReadingStatus }) {
    return api.post<Book>(`/clubs/${clubId}/books`, payload).then((response) => response.data);
  },
  get(id: string | number) {
    return api.get<Book>(`/books/${id}`).then((response) => response.data);
  },
  updateStatus(id: string | number, status: ReadingStatus) {
    return api.patch<Book>(`/books/${id}/status`, { status }).then((response) => response.data);
  },
  like(id: string | number) {
    return api.post<Book>(`/books/${id}/like`).then((response) => response.data);
  },
  unlike(id: string | number) {
    return api.delete<Book>(`/books/${id}/like`).then((response) => response.data);
  },
  comments(id: string | number) {
    return api.get<Comment[]>(`/books/${id}/comments`).then((response) => response.data);
  },
  addComment(id: string | number, content: string) {
    return api.post<Comment>(`/books/${id}/comments`, { content }).then((response) => response.data);
  },
  meetings(id: string | number) {
    return api.get<Meeting[]>(`/books/${id}/meetings`).then((response) => response.data);
  },
  history(clubId: string | number) {
    return api.get<ReadingHistoryItem[]>(`/clubs/${clubId}/reading-history`).then((response) => response.data);
  },
};

export const meetingService = {
  listByClub(clubId: string | number) {
    return api.get<Meeting[]>(`/clubs/${clubId}/meetings`).then((response) => response.data);
  },
  get(id: string | number) {
    return api.get<Meeting>(`/meetings/${id}`).then((response) => response.data);
  },
  create(
    clubId: string | number,
    payload: { title: string; scheduled_for: string; location: string; agenda: string; book_id: number | null },
  ) {
    return api.post<Meeting>(`/clubs/${clubId}/meetings`, payload).then((response) => response.data);
  },
  update(
    id: string | number,
    payload: { title: string; scheduled_for: string; location: string; agenda: string; book_id: number | null },
  ) {
    return api.put<Meeting>(`/meetings/${id}`, payload).then((response) => response.data);
  },
  remove(id: string | number) {
    return api.delete<void>(`/meetings/${id}`).then((response) => response.data);
  },
  comments(id: string | number) {
    return api.get<Comment[]>(`/meetings/${id}/comments`).then((response) => response.data);
  },
  addComment(id: string | number, content: string) {
    return api.post<Comment>(`/meetings/${id}/comments`, { content }).then((response) => response.data);
  },
  attendees(id: string | number) {
    return api.get<MeetingAttendee[]>(`/meetings/${id}/attendees`).then((response) => response.data);
  },
  confirmAttendance(id: string | number) {
    return api.post<MeetingAttendee[]>(`/meetings/${id}/attendance`).then((response) => response.data);
  },
  cancelAttendance(id: string | number) {
    return api.delete<MeetingAttendee[]>(`/meetings/${id}/attendance`).then((response) => response.data);
  },
};
