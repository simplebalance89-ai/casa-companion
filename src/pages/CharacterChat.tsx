import { useNavigate, useParams } from "react-router";
import { useState, useRef, useEffect } from "react";
import {
  ChevronLeft,
  Heart,
  Mic,
  Volume2,
  Send,
} from "lucide-react";
import { characters, companionModes, type ModeCategory } from "@/data/characters";
import { useVoiceChat } from "@/hooks/useVoiceChat";

interface LocalMessage {
  id: string;
  text: string;
  sender: "user" | "character";
  timestamp: Date;
}

export default function CharacterChat() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const character = characters.find((c) => c.id === id);

  const [isFavorited, setIsFavorited] = useState(() => {
    const favs = JSON.parse(localStorage.getItem("favorites") || "[]");
    return favs.includes(id);
  });
  const [showModePicker, setShowModePicker] = useState(false);
  const [showChat, setShowChat] = useState(false);
  const [textInput, setTextInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const voice = useVoiceChat(character || null);

  // Sync voice hook messages into the local chat view.
  const [localMessages, setLocalMessages] = useState<LocalMessage[]>([]);
  useEffect(() => {
    if (voice.messages.length === 0) return;
    const next = voice.messages[voice.messages.length - 1];
    const nextSender = next.role === 'user' ? 'user' : 'character';
    setLocalMessages((prev) => {
      const last = prev[prev.length - 1];
      // Stream into the existing message if the sender hasn't changed.
      if (last && last.sender === nextSender) {
        return [
          ...prev.slice(0, -1),
          { ...last, text: next.text, timestamp: new Date() },
        ];
      }
      return [
        ...prev,
        {
          id: Date.now().toString() + Math.random().toString(36).slice(2),
          text: next.text,
          sender: nextSender,
          timestamp: new Date(),
        },
      ];
    });
    setShowChat(true);
  }, [voice.messages]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [localMessages]);

  if (!character) {
    navigate("/");
    return null;
  }

  const toggleFavorite = () => {
    const favs = JSON.parse(localStorage.getItem("favorites") || "[]");
    if (isFavorited) {
      localStorage.setItem(
        "favorites",
        JSON.stringify(favs.filter((f: string) => f !== id))
      );
    } else {
      localStorage.setItem("favorites", JSON.stringify([...favs, id]));
    }
    setIsFavorited(!isFavorited);
  };

  const handleMicTap = () => {
    voice.toggleRecording();
  };

  const handleSendText = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!textInput.trim()) return;
    await voice.sendText(textInput);
    setTextInput("");
  };

  const statusText = () => {
    if (voice.errorMessage) return voice.errorMessage;
    if (!voice.isConnected) return "Connecting...";
    switch (voice.turnState) {
      case "listening":
        return "Listening...";
      case "processing":
        return "Thinking...";
      case "speaking":
        return "Speaking...";
      default:
        return "Tap mic or type below";
    }
  };

  const categoryLabels: Record<ModeCategory, string> = {
    introduction: "Introduction",
    play: "Play",
    learn: "Learn",
    support: "Support",
  };

  const modeCategories: ModeCategory[] = ["introduction", "play", "learn", "support"];
  const currentMode = companionModes.find((m) => m.id === "introduction");

  return (
    <div className="min-h-screen bg-void flex flex-col">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-void/80 backdrop-blur-xl border-b border-cloud/[0.06]">
        <div className="flex items-center justify-between px-4 py-3">
          <button
            onClick={() => {
              if (showChat) {
                setShowChat(false);
              } else {
                navigate("/");
              }
            }}
            className="w-10 h-10 flex items-center justify-center rounded-full hover:bg-surface transition-colors active:scale-95 cursor-pointer"
          >
            <ChevronLeft size={22} className="text-cloud" />
          </button>

          <div className="text-center flex-1 px-2">
            <h2 className="font-display text-base text-cloud leading-tight">
              {character.name}
            </h2>
            <p className="text-ash text-xs leading-tight">{character.subtitle}</p>
          </div>

          <button
            onClick={toggleFavorite}
            className={`w-10 h-10 flex items-center justify-center rounded-full hover:bg-surface transition-colors active:scale-95 cursor-pointer ${
              isFavorited ? "animate-heart-beat" : ""
            }`}
          >
            <Heart
              size={20}
              className={isFavorited ? "text-rose fill-rose" : "text-cloud"}
              strokeWidth={isFavorited ? 0 : 1.5}
            />
          </button>
        </div>

        {/* Mode Pill */}
        <div className="flex justify-center pb-3">
          <button
            onClick={() => setShowModePicker(!showModePicker)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-surface border border-cloud/[0.08] hover:border-amber/30 transition-colors cursor-pointer"
          >
            <span className="text-amber text-[11px] font-semibold uppercase tracking-wider">
              {currentMode?.name?.toUpperCase() || "INTRODUCTION"}
            </span>
            <Volume2 size={12} className="text-amber" />
          </button>
        </div>
      </header>

      {/* Mode Picker Dropdown */}
      {showModePicker && (
        <div className="absolute top-[90px] left-4 right-4 z-50 bg-ink border border-cloud/[0.12] rounded-2xl shadow-float p-4 max-h-[60vh] overflow-y-auto">
          <p className="text-ash text-xs uppercase tracking-wider mb-3 font-semibold">
            Choose a mode
          </p>
          {modeCategories.map((cat) => (
            <div key={cat} className="mb-3">
              <p className="text-amber text-[10px] uppercase tracking-widest mb-1.5 font-semibold">
                {categoryLabels[cat]}
              </p>
              <div className="space-y-1">
                {companionModes
                  .filter((m) => m.category === cat)
                  .map((mode) => (
                    <button
                      key={mode.id}
                      onClick={() => {
                        setShowModePicker(false);
                      }}
                      className={`w-full text-left px-3 py-2.5 rounded-xl transition-colors cursor-pointer ${
                        mode.id === "introduction"
                          ? "bg-amber/15 border border-amber/30"
                          : "hover:bg-surface border border-transparent"
                      }`}
                    >
                      <p className="text-cloud text-sm font-medium">{mode.name}</p>
                      <p className="text-ash text-xs">{mode.description}</p>
                    </button>
                  ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Status line */}
      <div className="shrink-0 text-center py-1">
        <p className={`text-xs font-medium ${voice.errorMessage ? "text-rose" : "text-ash"}`}>
          {statusText()}
        </p>
      </div>

      {/* Chat Content */}
      <div className="flex-1 overflow-y-auto px-4 pt-2 pb-4">
        {!showChat ? (
          /* Companion View - Character Portrait */
          <div className="flex flex-col items-center justify-center min-h-[45vh]">
            <div className="relative mb-4 animate-float">
              <img
                src={character.avatar}
                alt={character.name}
                className="w-52 h-64 object-cover rounded-3xl shadow-float"
              />
              {voice.isRecording && (
                <>
                  <div className="absolute inset-0 rounded-3xl border-2 border-mint animate-pulse-ring" />
                  <div
                    className="absolute inset-0 rounded-3xl border-2 border-mint animate-pulse-ring"
                    style={{ animationDelay: "0.5s" }}
                  />
                </>
              )}
            </div>
            <p className="text-ash text-sm mb-4">{character.hint}</p>
          </div>
        ) : (
          /* Chat Messages */
          <div className="space-y-3">
            {localMessages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${
                  msg.sender === "user" ? "justify-end" : "justify-start"
                }`}
              >
                {msg.sender === "character" && (
                  <img
                    src={character.avatar}
                    alt={character.name}
                    className="w-8 h-8 rounded-full object-cover mr-2 self-end border border-amber/30"
                  />
                )}
                <div
                  className={`max-w-[75%] px-4 py-2.5 rounded-2xl text-sm leading-relaxed ${
                    msg.sender === "user"
                      ? "bg-amber/15 text-cloud rounded-br-md"
                      : "bg-surface text-cloud rounded-bl-md"
                  }`}
                >
                  {msg.text}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Bottom Input Section */}
      <div className="shrink-0 pb-8 pt-2 bg-void flex flex-col items-center px-4">
        {/* Big centered mic button */}
        <button
          onClick={handleMicTap}
          className={`w-20 h-20 rounded-full flex items-center justify-center transition-all duration-300 active:scale-95 cursor-pointer mb-3 ${
            voice.isRecording
              ? "bg-surface border-2 border-mint shadow-[0_0_30px_rgba(93,184,141,0.4)]"
              : "bg-amber shadow-amber-glow hover:shadow-[0_0_30px_rgba(212,160,61,0.4)]"
          }`}
        >
          {voice.isRecording ? (
            <div className="w-6 h-6 bg-void rounded-md" />
          ) : (
            <Mic size={28} className="text-void" />
          )}
        </button>

        {/* Text input */}
        <form
          onSubmit={handleSendText}
          className="w-full max-w-md flex items-center gap-2 bg-surface border border-cloud/[0.08] rounded-full px-4 py-2"
        >
          <input
            type="text"
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            placeholder="Type a message..."
            className="flex-1 bg-transparent text-cloud text-sm outline-none placeholder:text-ash"
          />
          <button
            type="submit"
            disabled={!textInput.trim()}
            className="w-8 h-8 flex items-center justify-center rounded-full bg-amber text-void disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            <Send size={14} />
          </button>
        </form>
      </div>
    </div>
  );
}
