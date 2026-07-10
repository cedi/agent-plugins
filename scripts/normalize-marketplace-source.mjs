import path from "node:path";

const EXTERNAL_SOURCE_KINDS = new Set(["github", "url", "git-subdir", "npm"]);

/** Classify a marketplace `source`: `"local"` (string path), `"external"` (object referencing a remote plugin), or `"invalid"`. External sources are Claude-only and skipped by the Cursor manifest generator. */
export function getMarketplaceSourceKind(source) {
  if (typeof source === "string" && source.length > 0) {
    return "local";
  }
  if (
    source &&
    typeof source === "object" &&
    !Array.isArray(source) &&
    typeof source.source === "string" &&
    EXTERNAL_SOURCE_KINDS.has(source.source)
  ) {
    return "external";
  }
  return "invalid";
}

export function isExternalMarketplaceSource(source) {
  return getMarketplaceSourceKind(source) === "external";
}

/** Repo-relative marketplace `source` path: POSIX, no `./` prefix, no trailing `/`. */
export function normalizeMarketplaceSource(source) {
  if (typeof source !== "string" || source.length === 0) {
    return null;
  }

  const normalized = source.replace(/\\/g, "/").replace(/^(?:\.\/)+/, "").replace(/\/+$/, "");
  return normalized.length > 0 ? normalized : null;
}

export function isSafeMarketplaceSource(source) {
  const normalized = normalizeMarketplaceSource(source);
  if (!normalized) {
    return false;
  }

  if (path.posix.isAbsolute(normalized) || /^[A-Za-z]:\//.test(normalized)) {
    return false;
  }

  return normalized.split("/").every((segment) => segment.length > 0 && segment !== "..");
}

export function requireSafeMarketplaceSource(source, context) {
  const normalized = normalizeMarketplaceSource(source);
  if (!isSafeMarketplaceSource(normalized)) {
    throw new Error(`${context} must be a relative path without ".." or absolute prefixes.`);
  }
  return normalized;
}
