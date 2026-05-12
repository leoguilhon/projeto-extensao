export type ReadingStatus = "planejado" | "em_leitura" | "concluido";
export type ClubRole = "admin" | "membro";

export interface User {
  id: number;
  name: string;
  email: string;
  bio: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Club {
  id: number;
  name: string;
  description: string;
  owner_id: number;
  created_at: string;
  member_count: number;
  current_user_role: ClubRole | null;
  is_member: boolean;
}

export interface ClubMember {
  user_id: number;
  name: string;
  role: ClubRole;
}

export interface Book {
  id: number;
  club_id: number;
  title: string;
  author: string;
  description: string;
  status: ReadingStatus;
  added_by: number;
  created_at: string;
  finished_at: string | null;
}

export interface ReadingHistoryItem {
  club_id: number;
  club_name: string;
  book_id: number;
  title: string;
  author: string;
  finished_at: string;
}
