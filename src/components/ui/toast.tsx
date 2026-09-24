import { toast as sonnerToast } from "sonner";

const DEFAULT_DURATION = 4000;

type ToastOptions = {
  duration?: number;
  id?: string | number;
};

function optionsWithDuration(options?: ToastOptions): ToastOptions {
  return { duration: DEFAULT_DURATION, ...options };
}

export const toast = {
  success(message: string, options?: ToastOptions) {
    return sonnerToast.success(message, optionsWithDuration(options));
  },
  error(message: string, options?: ToastOptions) {
    return sonnerToast.error(message, optionsWithDuration(options));
  },
  info(message: string, options?: ToastOptions) {
    return sonnerToast.info(message, optionsWithDuration(options));
  },
  message(message: string, options?: ToastOptions) {
    return sonnerToast(message, optionsWithDuration(options));
  },
  dismiss(id?: string | number) {
    return sonnerToast.dismiss(id);
  },
};
