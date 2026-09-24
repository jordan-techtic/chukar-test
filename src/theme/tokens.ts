export const theme = {
  colors: {
    background: "#f7f8fa",
    foreground: "#111827",
    card: "#ffffff",
    popover: "#ffffff",
    primary: "#d80000",
    primaryForeground: "#ffffff",
    secondary: "#9c9c00",
    muted: "#f3f4f6",
    mutedForeground: "#6b7280",
    accent: "#180000",
    accentForeground: "#ffffff",
    destructive: "#dc2626",
    success: "#16a34a",
    warning: "#d97706",
    border: "#e5e7eb",
    input: "#e5e7eb",
    ring: "#d80000",
  },
  typography: {
    fontFamily: '"Inter", system-ui, sans-serif',
    heading: { fontSize: "28px", fontWeight: 600, lineHeight: "36px" },
    body: { fontSize: "16px", fontWeight: 400, lineHeight: "24px" },
  },
  spacing: {
    unit: "0.25rem",
  },
  radius: {
    sm: "4px",
    md: "8px",
    lg: "12px",
  },
} as const;
