export const tokens = {
  background: "#f7f8fa",
  foreground: "#111827",
  card: "#ffffff",
  cardForeground: "#111827",
  popover: "#ffffff",
  popoverForeground: "#111827",
  primary: "#d80000",
  primaryForeground: "#ffffff",
  secondary: "#9c9c00",
  secondaryForeground: "#ffffff",
  muted: "#f3f4f6",
  mutedForeground: "#6b7280",
  accent: "#180000",
  accentForeground: "#ffffff",
  destructive: "#dc2626",
  destructiveForeground: "#ffffff",
  border: "#e5e7eb",
  input: "#e5e7eb",
  ring: "#d80000",
  success: "#16a34a",
  warning: "#d97706",
  radius: "0.5rem",
  fontFamily: "Inter, ui-sans-serif, system-ui, sans-serif",
} as const;

export const theme = {
  colors: tokens,
  typography: {
    fontFamily: tokens.fontFamily,
    heading: { fontSize: "28px", fontWeight: 600, lineHeight: "36px" },
    body: { fontSize: "16px", fontWeight: 400, lineHeight: "24px" },
  },
  spacing: {
    small: "8px",
    medium: "16px",
    large: "24px",
  },
  radius: {
    sm: "4px",
    md: "8px",
    lg: "12px",
  },
} as const;
