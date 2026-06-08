/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        mc: {
          bg: "#060a14",
          surface: "#0a0f1c",
          card: "#0f1528",
          elevated: "#1a2240",
          border: "rgba(255, 255, 255, 0.05)",
          accent: "#6366f1",
          "accent-hover": "#818cf8",
          success: "#10b981",
          warning: "#f59e0b",
          danger: "#ef4444",
          info: "#3b82f6",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "sans-serif"],
        mono: ["JetBrains Mono", "SF Mono", "monospace"],
      },
      borderRadius: {
        DEFAULT: "14px",
      },
    },
  },
  plugins: [],
};
