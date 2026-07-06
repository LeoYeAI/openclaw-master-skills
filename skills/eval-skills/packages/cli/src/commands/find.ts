import type { Command } from "commander";
import { SkillStore, SkillFinder } from "@eval-skills/core";
import { log, printTable } from "../utils/output.js";

export function registerFindCommand(program: Command): void {
  program
    .command("find")
    .description("Search for Skills in the registry")
    .option("-q, --query <string>", "Keyword search")
    .option("-t, --tag <tags...>", "Filter by tags (intersection)")
    .option("-a, --adapter <type>", "Filter by adapter type")
    .option("--limit <n>", "Max results", "20")
    .option("--min-completion <rate>", "Min completion rate (0.0~1.0)")
    .option("--skills-dir <dir>", "Skills directory to scan", "./skills")
    .action((opts) => {
      try {
        const store = new SkillStore();
        store.loadDir(opts.skillsDir);
        const finder = new SkillFinder(store);

        const result = finder.find({
          query: opts.query,
          tags: opts.tag,
          adapterType: opts.adapter,
          limit: parseInt(opts.limit, 10),
          minCompletion: opts.minCompletion ? parseFloat(opts.minCompletion) : undefined,
        });

        if (result.skills.length === 0) {
          log.warn("No skills found matching the criteria.");
          return;
        }

        log.info(`Found ${result.total} skills (showing ${result.skills.length}):`);
        printTable(
          ["ID", "Name", "Version", "Adapter", "Tags"],
          result.skills.map((s) => [
            s.id,
            s.name,
            s.version,
            s.adapterType,
            s.tags.join(", "),
          ]),
        );
      } catch (err) {
        log.error((err as Error).message);
        process.exit(1);
      }
    });
}
