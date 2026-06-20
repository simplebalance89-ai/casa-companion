import { Routes, Route, Navigate } from "react-router";
import Onboarding from "./pages/Onboarding";
import Home from "./pages/Home";
import CharacterChat from "./pages/CharacterChat";
import CompanionSettings from "./pages/CompanionSettings";
import "./App.css";

function OnboardingGuard({ children }: { children: React.ReactNode }) {
  const onboardingComplete = localStorage.getItem("onboardingComplete") === "true";
  return onboardingComplete ? <Navigate to="/" replace /> : <>{children}</>;
}

function HomeGuard({ children }: { children: React.ReactNode }) {
  const onboardingComplete = localStorage.getItem("onboardingComplete") === "true";
  return onboardingComplete ? <>{children}</> : <Navigate to="/welcome" replace />;
}

export default function App() {
  return (
    <div className="app-wrapper">
      <div className="app-container">
        <Routes>
          <Route
            path="/welcome"
            element={
              <OnboardingGuard>
                <Onboarding />
              </OnboardingGuard>
            }
          />
          <Route
            path="/"
            element={
              <HomeGuard>
                <Home />
              </HomeGuard>
            }
          />
          <Route
            path="/character/:id"
            element={
              <HomeGuard>
                <CharacterChat />
              </HomeGuard>
            }
          />
          <Route
            path="/settings"
            element={
              <HomeGuard>
                <CompanionSettings />
              </HomeGuard>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </div>
  );
}
