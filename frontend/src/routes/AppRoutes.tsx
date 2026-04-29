import { BrowserRouter, Route, Routes } from "react-router-dom";
import { LoginPage } from "../pages/LoginPage";
import { RegisterPage } from "../pages/RegisterPage";
import { DashboardPage } from "../pages/DashboardPage";
import { ClubDetailsPage } from "../pages/ClubDetailsPage";
import { BookDetailsPage } from "../pages/BookDetailsPage";
import { MeetingsPage } from "../pages/MeetingsPage";
import { ProfilePage } from "../pages/ProfilePage";

export function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/clubs/:id" element={<ClubDetailsPage />} />
        <Route path="/books/:id" element={<BookDetailsPage />} />
        <Route path="/clubs/:id/meetings" element={<MeetingsPage />} />
        <Route path="/profile" element={<ProfilePage />} />
      </Routes>
    </BrowserRouter>
  );
}