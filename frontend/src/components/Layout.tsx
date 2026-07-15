import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "@/auth/AuthContext";

const navItems = [
  { to: "/", label: "Pantry", index: "01" },
  { to: "/suggestions", label: "Suggestions", index: "02" },
  { to: "/history", label: "History", index: "03" },
  { to: "/foodbank", label: "Food Bank Mode", index: "04" },
];

export default function Layout() {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b-2 border-ink/10 bg-cream-deep/60">
        <div className="mx-auto max-w-5xl px-6 py-5 flex items-center justify-between gap-4 flex-wrap">
          <div className="flex items-baseline gap-3">
            <h1 className="font-display text-2xl font-semibold tracking-tight text-cookbook-700">
              PantryChef
            </h1>
            <span className="hidden sm:inline text-sm text-ink-soft italic font-display">
              cook what you have
            </span>
          </div>
          <nav className="flex gap-1 items-center">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === "/"}
                className={({ isActive }) =>
                  [
                    "group flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-cookbook-600 text-cream"
                      : "text-ink-soft hover:bg-cookbook-50 hover:text-cookbook-700",
                  ].join(" ")
                }
              >
                <span className="font-display text-xs opacity-60">{item.index}</span>
                {item.label}
              </NavLink>
            ))}
            <div className="flex items-center gap-2 pl-3 ml-2 border-l border-ink/10">
              {user && <span className="text-xs text-ink-soft/70">{user.username}</span>}
              <button
                onClick={logout}
                className="text-xs font-medium text-ink-soft hover:text-cookbook-700 transition-colors"
              >
                Sign out
              </button>
            </div>
          </nav>
        </div>
      </header>

      <main className="flex-1">
        <div className="mx-auto max-w-5xl px-6 py-8">
          <Outlet />
        </div>
      </main>

      <footer className="border-t border-ink/10 py-6">
        <div className="mx-auto max-w-5xl px-6 text-xs text-ink-soft/70 text-center">
          Built by Frankie — pantry-aware recipe matching powered by Claude
        </div>
      </footer>
    </div>
  );
}
