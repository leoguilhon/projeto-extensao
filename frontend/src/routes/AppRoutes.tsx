import { BrowserRouter, Route, Routes } from "react-router-dom";
import { LoginPage } from "../pages/LoginPage";
import { RegisterPage } from "../pages/RegisterPage";
import { DashboardPage } from "../pages/DashboardPage";
import { ClubDetailsPage } from "../pages/ClubDetailsPage";
import { ClubBooksPage } from "../pages/ClubBooksPage";
import { BookDetailsPage } from "../pages/BookDetailsPage";
import { MeetingsPage } from "../pages/MeetingsPage";
import { MeetingDetailsPage } from "../pages/MeetingDetailsPage";
import { ProfilePage } from "../pages/ProfilePage";
import { ProtectedRoute } from "../components/ProtectedRoute";
import { AppLayout } from "../components/AppLayout";

export function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route element={<ProtectedRoute />}>
          <Route element={<AppLayout />}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/clubs/:id" element={<ClubDetailsPage />} />
            <Route path="/clubs/:id/books" element={<ClubBooksPage />} />
            <Route path="/books/:id" element={<BookDetailsPage />} />
            <Route path="/clubs/:id/meetings" element={<MeetingsPage />} />
            <Route path="/clubs/:id/meetings/:meetingId" element={<MeetingDetailsPage />} />
            <Route path="/profile" element={<ProfilePage />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
