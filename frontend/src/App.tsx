import { Routes, Route } from "react-router-dom";
import Layout from "@/components/Layout";
import PantryPage from "@/pages/PantryPage";
import SuggestionsPage from "@/pages/SuggestionsPage";
import HistoryPage from "@/pages/HistoryPage";
import FoodBankPage from "@/pages/FoodBankPage";
import LoginPage from "@/pages/LoginPage";
import { useAuth } from "@/auth/AuthContext";
import { Spinner } from "@/components/Feedback";

export default function App() {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Spinner label="Checking your session..." />
      </div>
    );
  }

  if (!user) {
    return <LoginPage />;
  }

  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<PantryPage />} />
        <Route path="/suggestions" element={<SuggestionsPage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/foodbank" element={<FoodBankPage />} />
      </Route>
    </Routes>
  );
}
