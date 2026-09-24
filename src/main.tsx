import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "@/App";
import { installInterceptors } from "@/lib/api/interceptors";
import "@/index.css";

installInterceptors();

const root = document.getElementById("root");
if (!root) {
  throw new Error("Root element was not found.");
}

createRoot(root).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
