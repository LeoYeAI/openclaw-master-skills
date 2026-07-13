import { readFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

interface SkillPackageJson {
  name?: string;
  version?: string;
  skillRequires?: Record<string, string>;
}

export interface CliMeta {
  skillName: string;
  skillVersion: string;
  walletConnectVersion: string;
}

export function loadCliMeta(): CliMeta {
  const __dirname = dirname(fileURLToPath(import.meta.url));
  const pkgPath = resolve(__dirname, "../../package.json");
  const pkg = JSON.parse(readFileSync(pkgPath, "utf8")) as SkillPackageJson;

  return {
    skillVersion: pkg.version || "0.1.0",
    skillName: pkg.name || "@lista-dao/lista-lending-skill",
    walletConnectVersion: pkg.skillRequires?.["lista-wallet-connect"] || ">=1.0.0",
  };
}
