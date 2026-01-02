// vite.config.ts
import path from "node:path";
import { fileURLToPath } from "node:url";

import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
    base: "./",
    root: ".",
    plugins: [react()],
    server: {
        host: "127.0.0.1", // or 'localhost'
        hmr: { host: "localhost" }, // May be needed for Safari
        fs: {
            strict: true, // optional, to avoid outside access
        },
        middlewareMode: false, // we're in normal dev mode
    },
    resolve: {
        alias: {
            src: path.resolve(__dirname, "./src/"),
        },
    },
    build: {
        target: "esnext",
        outDir: "dist",
        emptyOutDir: true,
        sourcemap: true, // optional: helps debugging
        minify: true, // ⛔ disable minification
        rollupOptions: {
            external: [],
            output: {
                // This will name the JS entry file like: index.[hash].js or result.[hash].js
                entryFileNames: "js/[name].js",
                chunkFileNames: "js/[name].js",
                assetFileNames: "assets/[name][extname]",
            },
        },
    },
});
