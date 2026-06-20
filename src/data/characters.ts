export interface Character {
  id: string;
  name: string;
  subtitle: string;
  avatar: string;
  greeting: string;
  hint: string;
  category: string[];
  group: "family" | "creatures" | "fantasy" | "rock";
}

export const characters: Character[] = [
  {
    id: "papa",
    name: "Papa the Wise Owl",
    subtitle: "The wise companion",
    avatar: "/characters/papa.png",
    greeting: "Hello there, young one! I'm Papa, your wise owl friend. What shall we explore today?",
    hint: "Tap the mic and say hello to Papa the Wise Owl.",
    category: ["all", "family"],
    group: "family",
  },
  {
    id: "gufo",
    name: "Gufo",
    subtitle: "Gufo means Owl in Italian",
    avatar: "/characters/gufo.png",
    greeting: "Ciao! I'm Gufo. Did you know that means 'owl' in Italian? Let's learn together!",
    hint: "Tap the mic and say ciao to Gufo.",
    category: ["all", "family"],
    group: "family",
  },
  {
    id: "wobble",
    name: "Wobble the Fraggl",
    subtitle: "The playful creature",
    avatar: "/characters/wobble.png",
    greeting: "Heeey! I'm Wobble! Wanna play? I know SO many fun games!",
    hint: "Tap the mic and say hey to Wobble the Fraggl.",
    category: ["all", "creatures"],
    group: "creatures",
  },
  {
    id: "stellino",
    name: "Stellino",
    subtitle: "The Dreamer",
    avatar: "/characters/stellino.png",
    greeting: "*sparkle sparkle* Oh! Hi there! I'm Stellino. I was just dreaming about the stars...",
    hint: "Tap the mic and say hi to Stellino.",
    category: ["all", "fantasy"],
    group: "fantasy",
  },
  {
    id: "rocco",
    name: "Rocco",
    subtitle: "Rock Frontman",
    avatar: "/characters/rocco.png",
    greeting: "YO! Rocco here! Ready to rock? Let's make some noise!",
    hint: "Tap the mic and say yo to Rocco.",
    category: ["all", "rock"],
    group: "rock",
  },
  {
    id: "onda",
    name: "Onda",
    subtitle: "The Surf Punk",
    avatar: "/characters/onda.png",
    greeting: "Hey hey, surfer! I'm Onda. The waves are calling, wanna chat?",
    hint: "Tap the mic and say hey to Onda.",
    category: ["all", "rock"],
    group: "rock",
  },
];

export type ModeCategory = "introduction" | "play" | "learn" | "support";

export interface CompanionMode {
  id: string;
  name: string;
  description: string;
  category: ModeCategory;
  icon: string;
}

export const companionModes: CompanionMode[] = [
  {
    id: "introduction",
    name: "Introduction",
    description: "Meet your companion and hear their voice",
    category: "introduction",
    icon: "Wand2",
  },
  {
    id: "story-time",
    name: "Story Time",
    description: "Listen to magical stories and adventures",
    category: "play",
    icon: "BookOpen",
  },
  {
    id: "music-rhythm",
    name: "Music & Rhythm",
    description: "Sing, dance, and explore musical worlds",
    category: "play",
    icon: "Music",
  },
  {
    id: "geography",
    name: "Geography",
    description: "Travel the world with your companion",
    category: "play",
    icon: "Globe",
  },
  {
    id: "stem-sparks",
    name: "STEM Sparks",
    description: "Explore science, tech, engineering, and math",
    category: "play",
    icon: "FlaskConical",
  },
  {
    id: "all-languages",
    name: "All Languages",
    description: "Learn words and phrases in any language",
    category: "learn",
    icon: "Star",
  },
  {
    id: "homework-helper",
    name: "Homework Helper",
    description: "Get help with school assignments",
    category: "learn",
    icon: "Pencil",
  },
  {
    id: "coding",
    name: "Coding",
    description: "Learn programming fundamentals",
    category: "learn",
    icon: "Code",
  },
  {
    id: "calm-breathe",
    name: "Calm & Breathe",
    description: "Guided breathing and relaxation",
    category: "support",
    icon: "HeartPulse",
  },
  {
    id: "milestones",
    name: "Milestones",
    description: "Track your learning achievements",
    category: "support",
    icon: "Trophy",
  },
  {
    id: "teaching-mode",
    name: "Teaching Mode",
    description: "Parent-guided lesson controls",
    category: "support",
    icon: "GraduationCap",
  },
];

export const categoryTabs = [
  { id: "all", label: "All Friends" },
  { id: "family", label: "Family" },
  { id: "creatures", label: "Creatures" },
  { id: "fantasy", label: "Fantasy" },
  { id: "rock", label: "Rock" },
];
