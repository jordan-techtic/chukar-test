export const MUTATION_ROLES = ["marketing_team_member", "admin", "super_admin"] as const;

export function canMutateActivities(role: string | undefined): boolean {
  if (!role) return false;
  return (MUTATION_ROLES as readonly string[]).includes(role);
}

export function textOnColor(hex: string): string {
  const normalized = hex.trim().replace("#", "");
  if (!/^[0-9a-fA-F]{6}$/.test(normalized)) return "#ffffff";
  const r = parseInt(normalized.slice(0, 2), 16);
  const g = parseInt(normalized.slice(2, 4), 16);
  const b = parseInt(normalized.slice(4, 6), 16);
  const luminance = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255;
  return luminance > 0.62 ? "#111827" : "#ffffff";
}

export function parseIsoDate(value: string): Date {
  const [year, month, day] = value.split("-").map((part) => Number(part));
  return new Date(year, (month ?? 1) - 1, day ?? 1);
}

export function formatIsoDate(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

export function formatDisplayDate(value: string): string {
  if (!value) return "";
  return parseIsoDate(value).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export const MONTH_NAMES = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
] as const;

export function humanize(value: string): string {
  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}
