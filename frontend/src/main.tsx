import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";

function App() {
  return (
    <div className="p-10">
      <h1 className="text-3xl font-bold">Tournament Organizer Frontend</h1>
      <p className="mt-4">This frontend is alive!</p>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")!).render(<App />);