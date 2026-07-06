import type { Command } from "commander";
import { SkillCreator } from "@eval-skills/core";
import type { TemplateType } from "@eval-skills/core";
import { log } from "../utils/output.js";

export function registerCreateCommand(program: Command): void {
  program
    .command("create")
    .description("Generate a Skill skeleton from a template or OpenAPI spec")
    .requiredOption("--name <name>", "Skill name")
    .option("--from-template <template>", "Template: http_request | python_script | mcp_tool", "http_request")
    .option("--from-openapi <path>", "Create from OpenAPI spec file")
    .option("--output-dir <dir>", "Output directory", "./skills")
    .option("--description <text>", "Skill description")
    .action(async (opts) => {
      try {
        const result = await SkillCreator.create({
          name: opts.name,
          template: opts.fromTemplate as TemplateType,
          outputDir: opts.outputDir,
          description: opts.description,
          openapiSpec: opts.fromOpenapi,
        });

        log.success(`Skill "${opts.name}" created at ${result.skillDir}`);
        log.info("Generated files:");
        for (const f of result.files) {
          log.dim(`  ${f}`);
        }
      } catch (err) {
        log.error((err as Error).message);
        process.exit(1);
      }
    });
}
