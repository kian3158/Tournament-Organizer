import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import "./index.css";
import TournamentsPage from "./pages/TournamentsPage";
import TournamentPage from "./pages/TournamentPage";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <div className="min-h-screen">
        <header className="border-b border-gray-800 px-8 py-4">
          <a href="/" className="text-xl font-bold">
            🏆 Tournament Organizer
          </a>
        </header>
        <main className="mx-auto max-w-5xl px-8 py-8">
          <Routes>
            <Route path="/" element={<TournamentsPage />} />
            <Route path="/tournaments/:id" element={<TournamentPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  </React.StrictMode>
);
