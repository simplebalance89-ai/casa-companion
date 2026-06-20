import { useNavigate } from "react-router";
import { useState, useEffect, useRef } from "react";
import { Sparkles, Search } from "lucide-react";
import { characters, categoryTabs } from "@/data/characters";
import BottomNav from "@/components/BottomNav";
import gsap from "gsap";

export default function Home() {
  const navigate = useNavigate();
  const [activeCategory, setActiveCategory] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const cardsRef = useRef<HTMLDivElement[]>([]);
  const headerRef = useRef<HTMLDivElement>(null);
  const founderRef = useRef<HTMLDivElement>(null);

  const founder = characters.find((c) => c.id === "pietro");

  const filteredCharacters = characters.filter((c) => {
    const matchesCategory =
      activeCategory === "all" || c.category.includes(activeCategory);
    const matchesSearch =
      !searchQuery ||
      c.name.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  useEffect(() => {
    if (headerRef.current) {
      gsap.fromTo(
        headerRef.current,
        { opacity: 0, y: -15 },
        { opacity: 1, y: 0, duration: 0.5, ease: "power2.out" }
      );
    }
    if (founderRef.current) {
      gsap.fromTo(
        founderRef.current,
        { opacity: 0, y: 20 },
        { opacity: 1, y: 0, duration: 0.5, ease: "power2.out", delay: 0.15 }
      );
    }
    if (cardsRef.current.length) {
      gsap.fromTo(
        cardsRef.current.filter(Boolean),
        { opacity: 0, y: 20, scale: 0.96 },
        {
          opacity: 1,
          y: 0,
          scale: 1,
          duration: 0.4,
          stagger: 0.06,
          ease: "power2.out",
          delay: 0.3,
        }
      );
    }
  }, [activeCategory]);

  return (
    <div className="min-h-screen bg-void pb-28">
      {/* Header */}
      <div ref={headerRef} className="px-4 pt-5 pb-3 opacity-0">
        <div className="flex items-center gap-2 mb-3">
          <Sparkles size={20} className="text-amber" />
          <h1 className="font-display text-lg text-cloud tracking-tight">
            Casa Companion
          </h1>
        </div>

        {/* Search Bar */}
        <div className="relative">
          <Search
            size={16}
            className="absolute left-3.5 top-1/2 -translate-y-1/2 text-ash/60"
          />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Find your friend..."
            className="w-full h-10 bg-surface border border-cloud/[0.08] rounded-full pl-10 pr-4 text-cloud text-sm placeholder:text-ash/40 focus:outline-none focus:border-amber/30 transition-colors"
          />
        </div>
      </div>

      {/* Featured Founder Card */}
      {founder && !searchQuery && (
        <div className="px-4 mb-4">
          <div
            ref={founderRef}
            onClick={() => navigate(`/character/${founder.id}`)}
            className="bg-ink border border-amber/20 rounded-2xl p-4 flex items-center gap-4 cursor-pointer active:scale-[0.98] transition-all hover:border-amber/40 opacity-0"
          >
            <div className="w-16 h-16 rounded-full overflow-hidden border-2 border-amber/40 shrink-0">
              <img
                src={founder.avatar}
                alt={founder.name}
                className="w-full h-full object-cover"
              />
            </div>
            <div className="flex-1">
              <p className="text-amber text-[10px] uppercase tracking-widest font-semibold mb-0.5">
                Meet the Founder
              </p>
              <h3 className="font-display text-lg text-cloud leading-tight">
                {founder.name}
              </h3>
              <p className="text-ash text-xs">{founder.subtitle}</p>
            </div>
            <span className="px-3 py-1 bg-amber/15 text-amber text-[11px] font-semibold rounded-full">
              Tap to chat
            </span>
          </div>
        </div>
      )}

      {/* Category Tabs */}
      {!searchQuery && (
        <div className="px-4 mb-4">
          <div className="flex gap-2 overflow-x-auto no-scrollbar pb-1">
            {categoryTabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveCategory(tab.id)}
                className={`shrink-0 px-4 py-2 rounded-full text-sm font-medium transition-all cursor-pointer ${
                  activeCategory === tab.id
                    ? "bg-amber text-void"
                    : "bg-surface text-ash hover:text-cloud border border-cloud/[0.08]"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Section Label */}
      <div className="px-4 mb-3">
        <p className="text-ash text-[11px] font-semibold uppercase tracking-widest">
          {searchQuery ? "Search Results" : "Pick Your Companion"}
        </p>
      </div>

      {/* Character Grid */}
      <div className="px-4 grid grid-cols-3 gap-3">
        {filteredCharacters.map((character, index) => (
          <div
            key={character.id}
            ref={(el) => {
              if (el) cardsRef.current[index] = el;
            }}
            onClick={() => navigate(`/character/${character.id}`)}
            className="bg-ink/80 border border-cloud/[0.06] rounded-2xl p-3 flex flex-col items-center gap-2 cursor-pointer transition-all duration-200 hover:border-amber/30 active:scale-[0.96] opacity-0"
          >
            <div className="relative">
              <img
                src={character.avatar}
                alt={character.name}
                className="w-16 h-16 rounded-full object-cover border border-amber/30"
              />
            </div>
            <div className="text-center">
              <p className="text-cloud text-[12px] font-semibold leading-tight">
                {character.name.split(" ").slice(0, 2).join(" ")}
              </p>
              <p className="text-ash text-[10px] leading-tight mt-0.5">
                {character.subtitle}
              </p>
            </div>
          </div>
        ))}
      </div>

      {filteredCharacters.length === 0 && (
        <div className="flex flex-col items-center justify-center py-16">
          <p className="text-ash text-sm">No companions found</p>
        </div>
      )}

      <BottomNav />
    </div>
  );
}
