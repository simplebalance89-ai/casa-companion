import { useNavigate } from "react-router";
import { useState } from "react";
import {
  ChevronLeft,
  Volume2,
  Bell,
  Mic,
  Clock,
  Shield,
  Trash2,
} from "lucide-react";

interface ToggleSetting {
  id: string;
  label: string;
  description: string;
  enabled: boolean;
}

export default function CompanionSettings() {
  const navigate = useNavigate();
  const [toggles, setToggles] = useState<ToggleSetting[]>([
    {
      id: "voice-output",
      label: "Voice Output",
      description: "Character speaks responses",
      enabled: true,
    },
    {
      id: "wake-word",
      label: "Wake Word",
      description: 'Say "Hey Casa" to start',
      enabled: false,
    },
    {
      id: "jump-in",
      label: "Jump In",
      description: "Interrupt while speaking",
      enabled: false,
    },
  ]);
  const [parentPin, setParentPin] = useState("");
  const [timeLimit, setTimeLimit] = useState(60);

  const toggleSetting = (id: string) => {
    setToggles((prev) =>
      prev.map((t) => (t.id === id ? { ...t, enabled: !t.enabled } : t))
    );
  };

  const toggleIcons: Record<string, React.ElementType> = {
    "voice-output": Volume2,
    "wake-word": Bell,
    "jump-in": Mic,
  };

  return (
    <div className="min-h-screen bg-void pb-8">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-void/80 backdrop-blur-xl border-b border-cloud/[0.06]">
        <div className="flex items-center gap-3 px-4 py-3.5">
          <button
            onClick={() => navigate("/")}
            className="w-10 h-10 flex items-center justify-center rounded-full hover:bg-surface transition-colors active:scale-95 cursor-pointer"
          >
            <ChevronLeft size={22} className="text-cloud" />
          </button>
          <h1 className="font-display text-lg text-cloud">Settings</h1>
        </div>
      </header>

      <div className="px-4 pt-4 space-y-4">
        {/* Voice Controls */}
        <section className="bg-ink border border-cloud/[0.08] rounded-2xl p-4">
          <p className="text-ash text-[10px] uppercase tracking-widest font-semibold mb-3">
            Voice Controls
          </p>
          <div className="space-y-3">
            {toggles.map((toggle) => {
              const Icon = toggleIcons[toggle.id] || Volume2;
              return (
                <div
                  key={toggle.id}
                  className="flex items-center justify-between"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-full bg-surface flex items-center justify-center">
                      <Icon size={16} className="text-ash" />
                    </div>
                    <div>
                      <p className="text-cloud text-sm font-medium">
                        {toggle.label}
                      </p>
                      <p className="text-ash text-xs">{toggle.description}</p>
                    </div>
                  </div>
                  <button
                    onClick={() => toggleSetting(toggle.id)}
                    className={`relative w-12 h-7 rounded-full transition-colors cursor-pointer ${
                      toggle.enabled ? "bg-amber" : "bg-surface border border-cloud/[0.12]"
                    }`}
                  >
                    <div
                      className={`absolute top-0.5 w-6 h-6 rounded-full bg-cloud shadow-sm transition-transform ${
                        toggle.enabled ? "translate-x-5" : "translate-x-0.5"
                      }`}
                    />
                  </button>
                </div>
              );
            })}
          </div>
        </section>

        {/* Parental Controls */}
        <section className="bg-ink border border-cloud/[0.08] rounded-2xl p-4">
          <p className="text-ash text-[10px] uppercase tracking-widest font-semibold mb-3">
            Parental Controls
          </p>

          {/* Parent PIN */}
          <div className="flex items-center gap-3 mb-4">
            <div className="w-9 h-9 rounded-full bg-surface flex items-center justify-center">
              <Shield size={16} className="text-ash" />
            </div>
            <div className="flex-1">
              <p className="text-cloud text-sm font-medium">Parent PIN</p>
            </div>
          </div>
          <div className="flex gap-2 mb-4">
            <input
              type="password"
              placeholder="Set a 4-6 digit PIN"
              maxLength={6}
              value={parentPin}
              onChange={(e) => setParentPin(e.target.value)}
              className="flex-1 h-10 bg-surface border border-cloud/[0.08] rounded-full px-4 text-cloud text-sm text-center tracking-[0.5em] focus:outline-none focus:border-amber/40"
            />
            <button className="h-10 px-5 bg-amber rounded-full text-void text-sm font-semibold active:scale-95 transition-transform cursor-pointer">
              Set
            </button>
          </div>

          {/* Daily Time Limit */}
          <div className="flex items-center gap-3 mb-3">
            <div className="w-9 h-9 rounded-full bg-surface flex items-center justify-center">
              <Clock size={16} className="text-ash" />
            </div>
            <div className="flex-1">
              <p className="text-cloud text-sm font-medium">Daily Time Limit</p>
              <p className="text-ash text-xs">{timeLimit} minutes</p>
            </div>
            <span className="text-amber text-xs font-semibold">0m used</span>
          </div>
          <div className="px-2">
            <input
              type="range"
              min={10}
              max={180}
              step={5}
              value={timeLimit}
              onChange={(e) => setTimeLimit(Number(e.target.value))}
              className="w-full h-1.5 bg-surface rounded-full appearance-none cursor-pointer accent-amber"
            />
            <div className="flex justify-between mt-1">
              <span className="text-ash text-[10px]">10m</span>
              <span className="text-ash text-[10px]">180m</span>
            </div>
          </div>
        </section>

        {/* Session Info */}
        <section className="bg-ink border border-cloud/[0.08] rounded-2xl p-4">
          <p className="text-ash text-[10px] uppercase tracking-widest font-semibold mb-3">
            Session Info
          </p>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-cloud text-sm">Status</span>
              <span className="text-mint text-sm font-medium">Online</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-cloud text-sm">Messages</span>
              <span className="text-ash text-sm">0 this session</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-cloud text-sm">Voice Pipeline</span>
              <span className="text-ash text-xs">
                Deepgram → GPT-4o → OpenAI TTS
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-cloud text-sm">Estimated Cost</span>
              <span className="text-ash text-sm">$0.00</span>
            </div>
          </div>
        </section>

        {/* Danger Zone */}
        <section>
          <p className="text-rose text-[10px] uppercase tracking-widest font-semibold mb-3 px-1">
            Danger Zone
          </p>
          <button
            onClick={() => {
              if (window.confirm("Are you sure? This cannot be undone.")) {
                localStorage.clear();
                window.location.reload();
              }
            }}
            className="w-full bg-rose/10 border border-rose/20 rounded-2xl p-4 flex items-center gap-3 hover:bg-rose/15 transition-colors cursor-pointer active:scale-[0.98]"
          >
            <Trash2 size={18} className="text-rose" />
            <div className="text-left">
              <p className="text-rose text-sm font-medium">Reset All Data</p>
              <p className="text-rose/60 text-xs">
                Clear conversations and settings
              </p>
            </div>
          </button>
        </section>

        {/* Footer */}
        <div className="text-center pt-4 pb-8">
          <p className="text-ash/40 text-xs">
            Casa Companion v1.0
          </p>
          <p className="text-ash/30 text-[10px]">Powered by voice</p>
        </div>
      </div>
    </div>
  );
}
