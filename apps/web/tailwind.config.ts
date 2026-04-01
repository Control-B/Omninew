import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#07111f",
        foreground: "#f5f7fb",
        border: "rgba(148, 163, 184, 0.18)",
        card: "rgba(15, 23, 42, 0.75)",
        muted: "#94a3b8",
        accent: "#6d5efc",
        accent2: "#00c6ff",
        success: "#10b981",
        warning: "#f59e0b",
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(109,94,252,.2), 0 20px 60px rgba(2,6,23,.45)",
      },
      backgroundImage: {
        grid: "radial-gradient(circle at 1px 1px, rgba(148,163,184,.15) 1px, transparent 0)",
      },
    },
  },
  plugins: [],
};

export default config;
