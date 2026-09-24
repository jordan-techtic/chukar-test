import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

export function humanizeEnum(value: string): string {
  const cleaned = value.trim().replace(/[_-]+/g, " ");
  if (!cleaned) return "";
  return cleaned.replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export function joinMeta(parts: Array<string | null | undefined>): string {
  return parts
    .map((part) => (typeof part === "string" ? part.trim() : ""))
    .filter(Boolean)
    .join(" · ");
}

type Rgb = { r: number; g: number; b: number };

function parseHex(hex: string): Rgb | null {
  const raw = hex.trim().replace("#", "");
  const full =
    raw.length === 3
      ? raw
          .split("")
          .map((char) => char + char)
          .join("")
      : raw;
  if (!/^[0-9a-fA-F]{6}$/.test(full)) return null;
  return {
    r: Number.parseInt(full.slice(0, 2), 16),
    g: Number.parseInt(full.slice(2, 4), 16),
    b: Number.parseInt(full.slice(4, 6), 16),
  };
}

function channel(value: number): number {
  const s = value / 255;
  return s <= 0.03928 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
}

function luminance(color: Rgb): number {
  return 0.2126 * channel(color.r) + 0.7152 * channel(color.g) + 0.0722 * channel(color.b);
}

function contrast(a: Rgb, b: Rgb): number {
  const l1 = luminance(a);
  const l2 = luminance(b);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

function toHex(color: Rgb): string {
  const part = (value: number) =>
    Math.round(value).toString(16).padStart(2, "0");
  return `#${part(color.r)}${part(color.g)}${part(color.b)}`;
}

export type ActivityChipStyle = {
  backgroundColor: string;
  color: string;
  borderLeft?: string;
};

const INK: Rgb = { r: 17, g: 24, b: 39 };
const PAPER: Rgb = { r: 255, g: 255, b: 255 };

export function activityChipStyle(hex: string): ActivityChipStyle {
  const background = parseHex(hex);
  if (!background) {
    return { backgroundColor: "#f3f4f6", color: "#111827" };
  }
  const darkContrast = contrast(background, INK);
  const lightContrast = contrast(background, PAPER);
  if (darkContrast >= 4.5 || lightContrast >= 4.5) {
    return {
      backgroundColor: toHex(background),
      color: darkContrast >= lightContrast ? "#111827" : "#ffffff",
    };
  }
  const tint: Rgb = {
    r: background.r * 0.16 + PAPER.r * 0.84,
    g: background.g * 0.16 + PAPER.g * 0.84,
    b: background.b * 0.16 + PAPER.b * 0.84,
  };
  return {
    backgroundColor: toHex(tint),
    color: "#111827",
    borderLeft: `2px solid ${toHex(background)}`,
  };
}
