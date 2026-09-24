import { Toaster as SonnerToaster } from "sonner";
import { toast as notify } from "@/components/ui/toast";

export const toast = notify;

export function Toaster() {
  return <SonnerToaster richColors closeButton duration={4000} position="top-right" />;
}
