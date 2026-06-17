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
import SpectatorPage from "./pages/SpectatorPage";
import StatsPage from "./pages/StatsPage";
import ThemeToggle from "./components/ThemeToggle";
import ThemeSettings from "./components/ThemeSettings";

function BrandMark() {
  return (
    <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-accent text-accent-fg">
      <svg
        viewBox="0 0 24 24"
        className="h-4 w-4"
        fill="none"
        stroke="currentColor"
        strokeWidth="2.2"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
      >
        <path d="M6 4v4h5M6 20v-4h5M11 12h4M15 12l4-4M15 12l4 4" />
      </svg>
    </span>
  );
}

function Header() {
  const { user, logout } = useAuth();
  return (
    <header className="border-b bg-surface">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-3.5">
        <Link to="/" className="flex items-center gap-2.5">
          <BrandMark />
          <span className="text-lg font-semibold tracking-tight">
            Tournament Organizer
          </span>
        </Link>
        <div className="flex items-center gap-3 text-sm">
          <ThemeSettings />
          <ThemeToggle />
          {user ? (
            <>
              <Link
                to="/stats"
                className="font-medium text-accent transition-colors hover:opacity-80"
              >
                Stats
              </Link>
              <span className="hidden text-muted sm:inline">{user.email}</span>
              <button
                onClick={logout}
                className="font-medium text-accent transition-colors hover:opacity-80"
              >
                Log out
              </button>
            </>
          ) : (
            <Link to="/login" className="font-medium text-accent transition-colors hover:opacity-80">
              Log in
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}

function RequireAuth({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <p className="text-muted">Loading…</p>;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <div className="min-h-screen">
          <Header />
          <main className="mx-auto max-w-5xl px-6 py-8">
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
              <Route
                path="/stats"
                element={
                  <RequireAuth>
                    <StatsPage />
                  </RequireAuth>
                }
              />
              <Route path="/tournaments/:id" element={<TournamentPage />} />
              <Route path="/watch/:id" element={<SpectatorPage />} />
            </Routes>
          </main>
        </div>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);
