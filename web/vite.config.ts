import react from "@vitejs/plugin-react";
import path from "node:path";
import { defineConfig } from "vite";

// Dev server proxies /api to the FastAPI backend so the client code can use
// same-origin URLs in every environment (nginx does the same in Docker).
export default defineConfig({
  plugins: [react()],
  resolve: { alias: { "@": path.resolve(__dirname, "src") } },
  server: {
    port: 5173,
    proxy: { "/api": { target: "http://localhost:8000", changeOrigin: true, rewrite: (p) => p.replace(/^\/api/, "") } },
  },
  build: {
    rollupOptions: {
      output: {
        // Split heavy vendors so the app shell stays small
        manualChunks: { charts: ["recharts"], react: ["react", "react-dom", "react-router-dom"] },
      },
    },
  },
});
