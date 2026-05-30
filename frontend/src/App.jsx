import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./App.css";

import Navbar from "./components/Navbar";
import Footer from "./components/Footer";

import Home from "./pages/Home";
import Events from "./pages/Events";
import EventDetail from "./pages/EventDetail";
import Login from "./pages/Login";
import Register from "./pages/Register";
import CreateEvent from "./pages/CreateEvent";
import MyReservations from "./pages/MyReservations";
import Dashboard from "./pages/Dashboard";

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <Navbar />

        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/events" element={<Events />} />
          <Route path="/events/:id" element={<EventDetail />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/create-event" element={<CreateEvent />} />
          <Route path="/my-reservations" element={<MyReservations />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>

        <Footer />
      </div>
    </BrowserRouter>
  );
}

export default App;