/* eslint-disable react-refresh/only-export-components */
import { Toaster as SonnerToaster } from "sonner";
import { toast as appToast } from "@/components/ui/toast";

export const toast = appToast;

export function Toaster() {
  return <SonnerToaster richColors closeButton position="top-right" duration={4000} />;
}
