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
  preview: {
    port: 4300,
    proxy: { "/api": { target: "http://localhost:8000", changeOrigin: true, rewrite: (p) => p.replace(/^\/api/, "") } },
  },
  build: {
    // NOTE: no manualChunks — splitting react/recharts into separate vendor
    // chunks broke module-initialization order in the production bundle
    // ("TypeError: n is not a function" on /chat). One bundle is boring and
    // correct; ~200kB gzip total does not justify the risk.
    chunkSizeWarningLimit: 900,
  },
});
