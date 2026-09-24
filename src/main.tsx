import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { QueryClientProvider } from "@tanstack/react-query";
import { App } from "@/App";
import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { attachInterceptors } from "@/lib/api/interceptors";
import { queryClient } from "@/lib/queryClient";
import { AppProvider } from "@/stores/AppContext";
import "@/index.css";

attachInterceptors();

const root = document.getElementById("root");
if (!root) {
  throw new Error("Root element was not found.");
}

createRoot(root).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <AppProvider>
        <TooltipProvider>
          <App />
          <Toaster />
        </TooltipProvider>
      </AppProvider>
    </QueryClientProvider>
  </StrictMode>,
);
