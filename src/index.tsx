import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import App from "./app";

createRoot(document.getElementById("app") as HTMLDivElement).render(
    <StrictMode>
        <App />
    </StrictMode>
);
