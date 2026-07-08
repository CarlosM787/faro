/** Brand tokens from brand/BRAND.md — keep in sync. */
/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        navy: { 950: "#0B1220", 900: "#111A2E", 800: "#1E2A44" },
        beam: "#FFB020",
        teal: "#2DD4BF",
        loss: "#F87171",
        ink: "#E6EDF7",
        muted: "#8B98AC",
      },
      fontFamily: {
        display: ['"Space Grotesk"', "sans-serif"],
        body: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
