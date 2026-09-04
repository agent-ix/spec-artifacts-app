#!/usr/bin/env node
// Stage the Filament-module payload for npm packaging.
//
// Non-destructive: copies the module payload from the inner
// `spec_*` Python package dir up to the repo root, so the published npm tarball
// IS the module root (manifest.yaml at the top, schema refs resolve relative to
// it). The inner dir remains the single source of truth; the staged copies are
// gitignored. Runs automatically via the `prepack` script before `npm pack` /
// `npm publish`. Node built-ins only, zero dependencies.
import {
  existsSync,
  readdirSync,
  statSync,
  rmSync,
  cpSync,
  readFileSync,
  writeFileSync,
} from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");

// Locate the inner module dir: a `spec_*` directory containing manifest.yaml.
const inner = readdirSync(root).find(
  (name) =>
    /^spec_/.test(name) &&
    statSync(join(root, name)).isDirectory() &&
    existsSync(join(root, name, "manifest.yaml")),
);
if (!inner) {
  console.error("stage-npm: no inner spec_* dir with manifest.yaml found");
  process.exit(1);
}

// The whole shipped payload, identical in the sdist, the wheel and the npm
// tarball (FR-002 Outputs). The TypeSpec toolchain is a build input and never
// ships.
// `postpack` passes --clean: remove the staged copies so the working tree goes
// back to having exactly one source of truth. Without it a `npm pack` leaves
// duplicates of the payload at the repo root, and the next reader has to know
// which of the two is authoritative.
const clean = process.argv.includes("--clean");

const PAYLOAD = [
  "manifest.yaml",
  "mappings.yaml",
  "mappings.schema.json",
  "schemas",
  "skeletons",
];
for (const item of PAYLOAD) {
  const to = join(root, item);
  if (clean) {
    if (existsSync(to)) {
      rmSync(to, { recursive: true, force: true });
      console.log(`stage-npm: removed staged ${item}`);
    }
    continue;
  }
  const from = join(root, inner, item);
  if (!existsSync(from)) continue;
  rmSync(to, { recursive: true, force: true });
  cpSync(from, to, { recursive: true });
  console.log(`stage-npm: ${inner}/${item} -> ${item}`);
}

if (clean) process.exit(0);

// Version sync: when packing from a CI tag (vX.Y.Z), stamp package.json so the
// tarball is named/published at the tag version. No-op locally (no env / no match).
const m = (process.env.GITHUB_REF_NAME ?? "").match(
  /^v?(\d+\.\d+\.\d+(?:[-+].+)?)$/,
);
if (m) {
  const pkgPath = join(root, "package.json");
  const pkg = JSON.parse(readFileSync(pkgPath, "utf8"));
  if (pkg.version !== m[1]) {
    pkg.version = m[1];
    writeFileSync(pkgPath, JSON.stringify(pkg, null, 2) + "\n");
    console.log(`stage-npm: version -> ${m[1]}`);
  }
}
