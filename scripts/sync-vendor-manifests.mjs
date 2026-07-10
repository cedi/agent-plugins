#!/usr/bin/env node

// Mirrors canonical .claude-plugin manifests into generated .cursor-plugin files
// and Codex plugin manifests / marketplace entries.

import { promises as fs } from "node:fs";
import path from "node:path";
import process from "node:process";

import {
  requireSafeMarketplaceSource,
  isExternalMarketplaceSource,
} from "./normalize-marketplace-source.mjs";

const repoRoot = process.cwd();
const args = new Set(process.argv.slice(2));
const checkMode = args.has("--check");
const defaultHomepage = "https://github.com/cedi/agent-plugins";

const writes = [];
const stale = [];

const pluginMetadata = {
  "git-workflows": {
    category: "Productivity",
    defaultPrompt: [
      "Review this pull request and post inline comments.",
      "Draft a pull request description from this diff.",
      "Turn recent commits into release notes.",
    ],
  },
  documentation: {
    category: "Productivity",
    defaultPrompt: [
      "Draft a design doc from these notes.",
      "Turn this proposal into a structured document.",
      "Stress-test this document with strategic design questions.",
    ],
  },
  tpm: {
    category: "Productivity",
    defaultPrompt: [
      "Turn this plan into linked Jira issues.",
      "Create a task breakdown for this program.",
      "Review this delivery plan and find gaps.",
    ],
  },
  "product-design": {
    category: "Design",
    defaultPrompt: [
      "Critique this flow using product design principles.",
      "Reduce friction in this onboarding experience.",
      "Apply trust and behavior design to this screen.",
    ],
  },
  "mental-models": {
    category: "Productivity",
    defaultPrompt: [
      "Run a five-whys analysis on this problem.",
      "Map the dependencies in this system.",
      "Apply game-theory lenses to this decision.",
    ],
  },
  "second-brain": {
    category: "Productivity",
    defaultPrompt: [
      "Capture this into my vault.",
      "Draft a weekly review from recent notes.",
      "Plan my week from the current vault state.",
    ],
  },
};

async function readJson(filePath) {
  try {
    const raw = await fs.readFile(filePath, "utf8");
    return JSON.parse(raw);
  } catch (error) {
    throw new Error(`Failed to read ${filePath}: ${error.message}`);
  }
}

async function pathExists(targetPath) {
  try {
    await fs.access(targetPath);
    return true;
  } catch {
    return false;
  }
}

function stableStringify(value) {
  return `${JSON.stringify(value, null, 2)}\n`;
}

async function emit(targetPath, payload) {
  const content = stableStringify(payload);
  const relative = path.relative(repoRoot, targetPath);
  let existing = null;
  try {
    existing = await fs.readFile(targetPath, "utf8");
  } catch (error) {
    if (error.code !== "ENOENT") {
      throw error;
    }
  }

  if (existing === content) {
    return;
  }

  if (checkMode) {
    stale.push(relative);
    return;
  }

  await fs.mkdir(path.dirname(targetPath), { recursive: true });
  await fs.writeFile(targetPath, content);
  writes.push(relative);
}

function commonPathPrefix(paths) {
  if (paths.length === 0) {
    return "";
  }
  const split = paths.map((p) => p.split("/"));
  const first = split[0];
  let prefix = [];
  for (let i = 0; i < first.length; i += 1) {
    const segment = first[i];
    if (split.every((parts) => parts[i] === segment)) {
      prefix.push(segment);
    } else {
      break;
    }
  }

  while (prefix.length > 0 && split.some((parts) => parts.length === prefix.length)) {
    prefix.pop();
  }

  return prefix.join("/");
}

function buildCursorMarketplace(claudeMarketplace) {
  const localEntries = (claudeMarketplace.plugins ?? []).filter(
    (entry) => !isExternalMarketplaceSource(entry?.source)
  );

  const sources = localEntries
    .map((entry) =>
      requireSafeMarketplaceSource(
        entry?.source,
        `Marketplace entry "${entry?.name ?? "<unknown>"}".source`
      )
    )
    .filter((value) => typeof value === "string" && value.length > 0);

  const pluginRoot = commonPathPrefix(sources);
  const plugins = localEntries.map((entry) => {
    const normalized = requireSafeMarketplaceSource(
      entry?.source,
      `Marketplace entry "${entry?.name ?? "<unknown>"}".source`
    );
    let cursorSource = normalized;
    if (pluginRoot && (normalized === pluginRoot || normalized.startsWith(`${pluginRoot}/`))) {
      cursorSource = normalized.slice(pluginRoot.length).replace(/^\/+/, "");
    }
    return {
      name: entry.name,
      source: cursorSource,
      description: entry.description,
      ...(entry.version ? { version: entry.version } : {}),
    };
  });

  const metadata = {
    description: claudeMarketplace.description,
    version: claudeMarketplace.version ?? "1.0.0",
    ...(pluginRoot ? { pluginRoot } : {}),
  };

  return {
    name: claudeMarketplace.name,
    owner: claudeMarketplace.owner,
    metadata,
    plugins,
  };
}

function titleCaseKebab(value) {
  return String(value ?? "")
    .split("-")
    .filter(Boolean)
    .map((segment) =>
      segment.length <= 3
        ? segment.toUpperCase()
        : segment.charAt(0).toUpperCase() + segment.slice(1)
    )
    .join(" ");
}

function truncateSentence(value, maxLength = 110) {
  const text = String(value ?? "").replace(/\s+/g, " ").trim();
  if (text.length <= maxLength) {
    return text;
  }
  return `${text.slice(0, maxLength - 3).trimEnd()}...`;
}

function getPluginCategory(name) {
  return pluginMetadata[name]?.category ?? "Productivity";
}

function getDefaultPrompts(name, displayName) {
  return pluginMetadata[name]?.defaultPrompt ?? [`Use ${displayName} for this task.`];
}

function buildCodexMarketplace(claudeMarketplace) {
  const localEntries = (claudeMarketplace.plugins ?? []).filter(
    (entry) => !isExternalMarketplaceSource(entry?.source)
  );

  return {
    name: claudeMarketplace.name,
    interface: {
      displayName: titleCaseKebab(claudeMarketplace.name),
    },
    plugins: localEntries.map((entry) => ({
      name: entry.name,
      source: {
        source: "local",
        path: `./plugins/${entry.name}`,
      },
      policy: {
        installation: "AVAILABLE",
        authentication: "ON_INSTALL",
      },
      category: getPluginCategory(entry.name),
    })),
  };
}

function buildCodexPluginManifest(claudeManifest) {
  const displayName = claudeManifest.displayName || titleCaseKebab(claudeManifest.name);
  const developerName = claudeManifest.author?.name || "Unknown";
  const description = String(claudeManifest.description ?? "").trim();

  return {
    name: claudeManifest.name,
    version: claudeManifest.version ?? "0.1.0",
    description,
    author: {
      name: developerName,
      ...(claudeManifest.author?.email ? { email: claudeManifest.author.email } : {}),
    },
    homepage: defaultHomepage,
    repository: defaultHomepage,
    keywords: Array.from(new Set([...(claudeManifest.keywords ?? []), "codex", "cursor"])),
    skills: "./skills/",
    interface: {
      displayName,
      shortDescription: truncateSentence(description, 100),
      longDescription: description,
      developerName,
      category: getPluginCategory(claudeManifest.name),
      capabilities: ["Read", "Write"],
      websiteURL: defaultHomepage,
      defaultPrompt: getDefaultPrompts(claudeManifest.name, displayName),
      brandColor: "#1273EA",
      screenshots: [],
    },
  };
}

async function syncMarketplace() {
  const claudePath = path.join(repoRoot, ".claude-plugin", "marketplace.json");
  const claude = await readJson(claudePath);
  if (!claude) {
    throw new Error(`Missing source-of-truth marketplace file: ${claudePath}`);
  }

  const cursor = buildCursorMarketplace(claude);
  const cursorPath = path.join(repoRoot, ".cursor-plugin", "marketplace.json");
  await emit(cursorPath, cursor);

  const codex = buildCodexMarketplace(claude);
  const codexPath = path.join(repoRoot, ".agents", "plugins", "marketplace.json");
  await emit(codexPath, codex);
}

async function syncPluginManifests() {
  const claudeMarketplace = await readJson(
    path.join(repoRoot, ".claude-plugin", "marketplace.json")
  );

  for (const entry of claudeMarketplace.plugins ?? []) {
    if (isExternalMarketplaceSource(entry?.source)) {
      continue;
    }

    const normalized = requireSafeMarketplaceSource(
      entry?.source,
      `Marketplace entry "${entry?.name ?? "<unknown>"}".source`
    );
    if (!entry?.name || !normalized) {
      continue;
    }
    const pluginDir = path.join(repoRoot, normalized);
    const claudeManifestPath = path.join(pluginDir, ".claude-plugin", "plugin.json");

    if (!(await pathExists(claudeManifestPath))) {
      throw new Error(
        `Missing canonical plugin manifest for "${entry.name}": ${path.relative(repoRoot, claudeManifestPath)}`
      );
    }

    const claudeManifest = await readJson(claudeManifestPath);
    const cursorManifest = { ...claudeManifest };
    const cursorManifestPath = path.join(pluginDir, ".cursor-plugin", "plugin.json");
    await emit(cursorManifestPath, cursorManifest);

    const codexManifest = buildCodexPluginManifest(claudeManifest);
    const codexManifestPath = path.join(pluginDir, ".codex-plugin", "plugin.json");
    await emit(codexManifestPath, codexManifest);
  }
}

async function main() {
  await syncMarketplace();
  await syncPluginManifests();

  if (checkMode) {
    if (stale.length > 0) {
      console.error("Vendor manifests are out of date. Run `npm run sync` to regenerate:");
      for (const file of stale) {
        console.error(`- ${file}`);
      }
      process.exit(1);
    }
    console.log("Vendor manifests are up to date.");
    return;
  }

  if (writes.length === 0) {
    console.log("Vendor manifests already up to date. Nothing to write.");
    return;
  }

  console.log("Updated vendor manifests:");
  for (const file of writes) {
    console.log(`- ${file}`);
  }
}

try {
  await main();
} catch (error) {
  console.error(error.message);
  process.exit(1);
}
