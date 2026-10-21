import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        cream: {
          50: "#FDFBF7",
          100: "#FAF8F5",
          200: "#F5F0E8",
          300: "#E9E4D8",
          400: "#D8D1C3",
          500: "#A8A093",
        },
        stone: {
          surface: "#FFFFFF",
          warm: "#F8F6F0",
          subtle: "#FBF9F5",
          text: "#1F2937",
          muted: "#6B7280",
          caption: "#857F76",
        },
        health: {
          low: {
            text: "#065F46",
            bg: "#ECFDF5",
            border: "#A7F3D0",
            accent: "#10B981",
          },
          moderate: {
            text: "#92400E",
            bg: "#FFFBEB",
            border: "#FDE68A",
            accent: "#F59E0B",
          },
          elevated: {
            text: "#991B1B",
            bg: "#FEF2F2",
            border: "#FECACA",
            accent: "#EF4444",
          },
        },
      },
      boxShadow: {
        warm: "0 1px 3px 0 rgba(45, 41, 38, 0.04), 0 1px 2px -1px rgba(45, 41, 38, 0.04)",
        "warm-md": "0 4px 6px -1px rgba(45, 41, 38, 0.06), 0 2px 4px -2px rgba(45, 41, 38, 0.06)",
        "warm-lg": "0 10px 15px -3px rgba(45, 41, 38, 0.08), 0 4px 6px -4px rgba(45, 41, 38, 0.04)",
      },
    },
  },
  plugins: [],
};

export default config;
