import { useState, useRef } from "react";
import { useNavigate } from "react-router";
import { Mic, Keyboard } from "lucide-react";
import gsap from "gsap";

export default function Onboarding() {
  const navigate = useNavigate();
  const [userName, setUserName] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [showNameInput, setShowNameInput] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleMicTap = () => {
    if (isRecording) {
      setIsRecording(false);
      // Simulate voice recognition
      setTimeout(() => {
        saveAndProceed("Friend");
      }, 500);
    } else {
      setIsRecording(true);
      setTimeout(() => {
        setIsRecording(false);
        saveAndProceed("Friend");
      }, 2500);
    }
  };

  const handleNameSubmit = () => {
    if (userName.trim()) {
      saveAndProceed(userName.trim());
    }
  };

  const saveAndProceed = (name: string) => {
    localStorage.setItem("userName", name);
    localStorage.setItem("onboardingComplete", "true");

    // Fade out animation
    if (containerRef.current) {
      gsap.to(containerRef.current, {
        opacity: 0,
        y: -30,
        duration: 0.4,
        ease: "power2.in",
        onComplete: () => navigate("/", { replace: true }),
      });
    } else {
      navigate("/", { replace: true });
    }
  };

  return (
    <div
      ref={containerRef}
      className="min-h-screen bg-void flex flex-col items-center justify-center px-8"
    >
      {/* Character Portrait */}
      <div className="mb-6">
        <div className="w-32 h-32 rounded-3xl overflow-hidden border-2 border-amber/30 shadow-amber-glow">
          <img
            src="/characters/papa.png"
            alt="Papa the Wise Owl"
            className="w-full h-full object-cover"
          />
        </div>
      </div>

      {/* Title & Subtitle */}
      <h1 className="font-display text-2xl text-cloud mb-2 text-center">
        Introduce yourself!
      </h1>
      <p className="text-amber text-sm mb-10">
        {showNameInput ? "Type your name below" : "Say your name below"}
      </p>

      {/* Mic Button or Name Input */}
      {!showNameInput ? (
        <>
          <button
            onClick={handleMicTap}
            className={`w-20 h-20 rounded-full flex items-center justify-center transition-all duration-300 active:scale-95 cursor-pointer mb-3 ${
              isRecording
                ? "bg-surface border-2 border-mint shadow-[0_0_30px_rgba(93,184,141,0.4)]"
                : "bg-amber shadow-amber-glow hover:shadow-[0_0_30px_rgba(212,160,61,0.4)]"
            }`}
          >
            {isRecording ? (
              <div className="w-6 h-6 bg-void rounded-md" />
            ) : (
              <Mic size={28} className="text-void" />
            )}
          </button>
          <p className="text-ash text-xs mb-4">
            {isRecording ? "Listening..." : "Tap to talk"}
          </p>
          <button
            onClick={() => setShowNameInput(true)}
            className="flex items-center gap-1.5 text-ash/60 text-xs hover:text-ash transition-colors cursor-pointer"
          >
            <Keyboard size={14} />
            Type your name
          </button>
        </>
      ) : (
        <>
          <input
            type="text"
            value={userName}
            onChange={(e) => setUserName(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleNameSubmit()}
            placeholder="Your name"
            autoFocus
            className="w-56 h-12 bg-surface border border-cloud/[0.12] rounded-full px-5 text-cloud text-center text-base placeholder:text-ash/50 focus:outline-none focus:border-amber/40 mb-4"
          />
          <button
            onClick={handleNameSubmit}
            disabled={!userName.trim()}
            className="w-56 h-11 bg-amber rounded-full text-void font-semibold text-sm disabled:opacity-40 disabled:cursor-not-allowed active:scale-95 transition-all cursor-pointer"
          >
            Get Started
          </button>
          <button
            onClick={() => setShowNameInput(false)}
            className="mt-4 text-ash/60 text-xs hover:text-ash transition-colors cursor-pointer"
          >
            Go back
          </button>
        </>
      )}
    </div>
  );
}
