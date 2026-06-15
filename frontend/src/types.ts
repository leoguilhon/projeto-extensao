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
  is_favorite: boolean;
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
  like_count: number;
  liked_by_current_user: boolean;
}

export interface Meeting {
  id: number;
  club_id: number;
  title: string;
  scheduled_for: string;
  location: string;
  agenda: string;
  book_id: number | null;
  book_title: string | null;
  created_by: number;
  created_at: string;
  comment_count: number;
}

export interface Comment {
  id: number;
  club_id: number;
  user_id: number;
  user_name: string;
  content: string;
  created_at: string;
  book_id: number | null;
  meeting_id: number | null;
}

export interface ReadingHistoryItem {
  club_id: number;
  club_name: string;
  book_id: number;
  title: string;
  author: string;
  finished_at: string;
}
