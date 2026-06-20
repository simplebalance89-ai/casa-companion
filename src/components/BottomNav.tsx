import { Home, MessageCircle, Settings } from "lucide-react";
import { useLocation, useNavigate } from "react-router";

export default function BottomNav() {
  const location = useLocation();
  const navigate = useNavigate();

  const tabs = [
    { path: "/", icon: Home, label: "Home" },
    { path: "/chat", icon: MessageCircle, label: "Chat" },
    { path: "/settings", icon: Settings, label: "Settings" },
  ];

  const isActive = (path: string) => {
    if (path === "/chat") {
      return location.pathname.startsWith("/character/");
    }
    return location.pathname === path;
  };

  const handleNavigate = (path: string) => {
    if (path === "/chat") {
      // If on a character chat, stay there. Otherwise go to first character
      if (!location.pathname.startsWith("/character/")) {
        navigate("/character/papa");
      }
    } else {
      navigate(path);
    }
  };

  return (
    <nav className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50">
      <div className="flex items-center gap-1 bg-ink/90 backdrop-blur-xl border border-cloud/[0.08] rounded-full px-2 py-2 shadow-float">
        {tabs.map((tab) => {
          const active = isActive(tab.path);
          const Icon = tab.icon;
          return (
            <button
              key={tab.path}
              onClick={() => handleNavigate(tab.path)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-full transition-all duration-200 cursor-pointer ${
                active
                  ? "bg-amber text-void"
                  : "text-ash hover:text-cloud"
              }`}
              style={{
                transform: "scale(1)",
                transition:
                  "transform 0.15s cubic-bezier(0.175, 0.885, 0.32, 1.275), background-color 0.2s, color 0.2s",
              }}
              onMouseDown={(e) => {
                (e.currentTarget as HTMLElement).style.transform = "scale(0.96)";
              }}
              onMouseUp={(e) => {
                (e.currentTarget as HTMLElement).style.transform = "scale(1)";
              }}
              onTouchStart={(e) => {
                (e.currentTarget as HTMLElement).style.transform = "scale(0.96)";
              }}
              onTouchEnd={(e) => {
                (e.currentTarget as HTMLElement).style.transform = "scale(1)";
              }}
            >
              <Icon size={18} strokeWidth={active ? 2.5 : 1.5} />
              <span
                className={`text-sm font-medium ${active ? "font-semibold" : ""}`}
              >
                {active ? tab.label : ""}
              </span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}
