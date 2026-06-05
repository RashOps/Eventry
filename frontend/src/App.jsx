import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./App.css";

import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import ProtectedRoute from "./components/ProtectedRoute";

import Home from "./pages/Home";
import Events from "./pages/Events";
import EventDetail from "./pages/EventDetail";
import Login from "./pages/Login";
import Register from "./pages/Register";
import CreateEvent from "./pages/CreateEvent";
import MyReservations from "./pages/MyReservations";
import Dashboard from "./pages/Dashboard";
import Profile from "./pages/Profile";
import EditEvent from "./pages/EditEvent";
import EventStats from "./pages/EventStats";

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
          
          {/* Routes Protégées - Participant ou plus */}
          <Route 
            path="/profile" 
            element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/my-reservations" 
            element={
              <ProtectedRoute>
                <MyReservations />
              </ProtectedRoute>
            } 
          />
          
          {/* Routes Protégées - Organisateur uniquement */}
          <Route 
            path="/create-event" 
            element={
              <ProtectedRoute roleRequired="organisateur">
                <CreateEvent />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute roleRequired="organisateur">
                <Dashboard />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/events/:id/edit" 
            element={
              <ProtectedRoute roleRequired="organisateur">
                <EditEvent />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/events/:id/stats" 
            element={
              <ProtectedRoute roleRequired="organisateur">
                <EventStats />
              </ProtectedRoute>
            } 
          />
        </Routes>

        <Footer />
      </div>
    </BrowserRouter>
  );
}

export default App;