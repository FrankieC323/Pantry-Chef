import { useState } from "react";
import { useAuth } from "@/auth/AuthContext";
import { ErrorBanner } from "@/components/Feedback";

export default function LoginPage() {
  const { login, register } = useAuth();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      if (mode === "login") {
        await login(username, password);
      } else {
        await register(username, password);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="card-paper w-full max-w-sm p-6 space-y-5">
        <div>
          <h1 className="font-display text-2xl font-semibold">PantryChef</h1>
          <p className="text-ink-soft text-sm mt-1">Food Bank Mode -- staff sign in</p>
        </div>

        <div className="flex rounded-md border border-ink/15 p-0.5 text-sm">
          <button
            type="button"
            onClick={() => setMode("login")}
            className={[
              "flex-1 rounded-sm py-1.5 font-medium transition-colors",
              mode === "login" ? "bg-cookbook-600 text-cream" : "text-ink-soft",
            ].join(" ")}
          >
            Sign in
          </button>
          <button
            type="button"
            onClick={() => setMode("register")}
            className={[
              "flex-1 rounded-sm py-1.5 font-medium transition-colors",
              mode === "register" ? "bg-cookbook-600 text-cream" : "text-ink-soft",
            ].join(" ")}
          >
            New account
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className="text-sm font-medium block mb-1">Username</label>
            <input
              type="text"
              required
              minLength={3}
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full rounded-md border border-ink/20 px-3 py-2 text-sm"
              autoComplete="username"
            />
          </div>
          <div>
            <label className="text-sm font-medium block mb-1">Password</label>
            <input
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-md border border-ink/20 px-3 py-2 text-sm"
              autoComplete={mode === "login" ? "current-password" : "new-password"}
            />
            {mode === "register" && (
              <p className="text-xs text-ink-soft/70 mt-1">At least 8 characters.</p>
            )}
          </div>

          {error && <ErrorBanner message={error} />}

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full rounded-md bg-cookbook-600 py-2.5 text-sm font-medium text-cream hover:bg-cookbook-700 transition-colors disabled:opacity-50"
          >
            {isSubmitting ? "Please wait..." : mode === "login" ? "Sign in" : "Create account"}
          </button>
        </form>
      </div>
    </div>
  );
}
