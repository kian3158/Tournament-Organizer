import React from "react";
import ReactDOM from "react-dom/client";
import {
  BrowserRouter,
  Link,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";
import "./index.css";
import { AuthProvider, useAuth } from "./auth/AuthContext";
import LoginPage from "./pages/LoginPage";
import TournamentsPage from "./pages/TournamentsPage";
import TournamentPage from "./pages/TournamentPage";

function Header() {
  const { user, logout } = useAuth();
  return (
    <header className="flex items-center justify-between border-b border-gray-800 px-8 py-4">
      <Link to="/" className="text-xl font-bold">
        🏆 Tournament Organizer
      </Link>
      {user ? (
        <div className="flex items-center gap-4 text-sm">
          <span className="text-gray-400">{user.email}</span>
          <button onClick={logout} className="text-blue-400 hover:underline">
            Log out
          </button>
        </div>
      ) : (
        <Link to="/login" className="text-sm text-blue-400 hover:underline">
          Log in
        </Link>
      )}
    </header>
  );
}

function RequireAuth({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <p className="text-gray-400">Loading…</p>;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <div className="min-h-screen">
          <Header />
          <main className="mx-auto max-w-5xl px-8 py-8">
            <Routes>
              <Route
                path="/"
                element={
                  <RequireAuth>
                    <TournamentsPage />
                  </RequireAuth>
                }
              />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/tournaments/:id" element={<TournamentPage />} />
            </Routes>
          </main>
        </div>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);
