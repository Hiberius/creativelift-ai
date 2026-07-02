import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#03070b",
        graphite: "#0b1117",
        panel: "#101820",
        line: "#22303a",
        cyan: "#20e7f6",
        mint: "#63f584",
        lime: "#a4ff5f"
      },
      boxShadow: {
        glow: "0 0 42px rgba(32, 231, 246, 0.18)"
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"]
      }
    }
  },
  plugins: []
};

export default config;
