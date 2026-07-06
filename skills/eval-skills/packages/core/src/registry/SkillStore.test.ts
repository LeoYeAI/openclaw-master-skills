import { mkdtempSync, writeFileSync, rmSync, mkdirSync, realpathSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { SkillStore } from "./SkillStore.js";
import type { Skill } from "../types/index.js";

function createMockSkill(overrides: Partial<Skill> = {}): Skill {
  return {
    id: "test_skill",
    name: "Test Skill",
    version: "1.0.0",
    description: "A test skill for unit testing",
    tags: ["test", "mock"],
    inputSchema: { type: "object" },
    outputSchema: { type: "object" },
    adapterType: "http",
    entrypoint: "http://localhost:3000",
    metadata: {},
    ...overrides,
  };
}

describe("SkillStore", () => {
  let store: SkillStore;

  beforeEach(() => {
    store = new SkillStore();
  });

  describe("register & get", () => {
    it("registers and retrieves a skill by id", () => {
      const skill = createMockSkill();
      store.register(skill);
      expect(store.get("test_skill")).toEqual(skill);
    });

    it("returns undefined for non-existent id", () => {
      expect(store.get("nonexistent")).toBeUndefined();
    });

    it("overwrites skill with same id", () => {
      store.register(createMockSkill({ description: "v1" }));
      store.register(createMockSkill({ description: "v2" }));
      expect(store.get("test_skill")?.description).toBe("v2");
    });
  });

  describe("list", () => {
    beforeEach(() => {
      store.register(createMockSkill({ id: "s1", tags: ["web", "search"], adapterType: "http" }));
      store.register(createMockSkill({ id: "s2", tags: ["math"], adapterType: "subprocess" }));
      store.register(createMockSkill({ id: "s3", tags: ["web", "crawl"], adapterType: "http" }));
    });

    it("returns all skills without filters", () => {
      expect(store.list()).toHaveLength(3);
    });

    it("filters by tag", () => {
      const results = store.list({ tag: "web" });
      expect(results).toHaveLength(2);
      expect(results.map((s) => s.id).sort()).toEqual(["s1", "s3"]);
    });

    it("filters by adapterType", () => {
      const results = store.list({ adapterType: "subprocess" });
      expect(results).toHaveLength(1);
      expect(results[0]!.id).toBe("s2");
    });

    it("filters by both tag and adapterType", () => {
      const results = store.list({ tag: "web", adapterType: "http" });
      expect(results).toHaveLength(2);
    });

    it("returns empty for unmatched filter", () => {
      expect(store.list({ tag: "nonexistent" })).toHaveLength(0);
    });
  });

  describe("remove", () => {
    it("removes an existing skill", () => {
      store.register(createMockSkill());
      expect(store.remove("test_skill")).toBe(true);
      expect(store.get("test_skill")).toBeUndefined();
    });

    it("returns false for non-existent skill", () => {
      expect(store.remove("nope")).toBe(false);
    });
  });

  describe("clear & count", () => {
    it("clears all skills", () => {
      store.register(createMockSkill({ id: "a" }));
      store.register(createMockSkill({ id: "b" }));
      expect(store.count()).toBe(2);
      store.clear();
      expect(store.count()).toBe(0);
      expect(store.list()).toHaveLength(0);
    });
  });

  describe("search", () => {
    beforeEach(() => {
      store.register(createMockSkill({ id: "web_search", name: "Web Search", description: "Search the web", tags: ["web"] }));
      store.register(createMockSkill({ id: "calc", name: "Calculator", description: "Math operations", tags: ["math", "calculator"] }));
      store.register(createMockSkill({ id: "translate", name: "Translator", description: "Translate text", tags: ["nlp", "search"] }));
    });

    it("searches by name (case insensitive)", () => {
      const results = store.search("calculator");
      expect(results).toHaveLength(1);
      expect(results[0]!.id).toBe("calc");
    });

    it("searches by description", () => {
      const results = store.search("Math");
      expect(results).toHaveLength(1);
      expect(results[0]!.id).toBe("calc");
    });

    it("searches by tags", () => {
      const results = store.search("search");
      expect(results).toHaveLength(2);
    });

    it("returns empty for no match", () => {
      expect(store.search("zzzzz")).toHaveLength(0);
    });
  });

  describe("loadDir", () => {
    let tmpDir: string;

    beforeEach(() => {
      tmpDir = realpathSync(mkdtempSync(path.join(tmpdir(), "eval-skills-test-")));
    });

    afterEach(() => {
      rmSync(tmpDir, { recursive: true, force: true });
    });

    it("loads skill.json from directory", () => {
      const skillDir = path.join(tmpDir, "my_skill");
      mkdirSync(skillDir);
      writeFileSync(
        path.join(skillDir, "skill.json"),
        JSON.stringify(createMockSkill({ id: "loaded_skill" })),
      );

      const loaded = store.loadDir(tmpDir);
      expect(loaded).toHaveLength(1);
      expect(loaded[0]!.id).toBe("loaded_skill");
      expect(store.get("loaded_skill")).toBeDefined();
    });

    it("loads from nested directories", () => {
      const dir1 = path.join(tmpDir, "a", "b");
      mkdirSync(dir1, { recursive: true });
      writeFileSync(
        path.join(dir1, "skill.json"),
        JSON.stringify(createMockSkill({ id: "nested" })),
      );

      const loaded = store.loadDir(tmpDir);
      expect(loaded).toHaveLength(1);
      expect(loaded[0]!.id).toBe("nested");
    });

    it("returns empty for non-existent directory", () => {
      expect(store.loadDir("/nonexistent/path")).toHaveLength(0);
    });

    it.skip("resolves subprocess entrypoint to absolute path", () => {
      const skillDir = path.join(tmpDir, "py_skill");
      mkdirSync(skillDir);
      writeFileSync(path.join(skillDir, "skill.py"), "# dummy");
      writeFileSync(
        path.join(skillDir, "skill.json"),
        JSON.stringify(
          createMockSkill({
            id: "py_skill",
            adapterType: "subprocess",
            entrypoint: "python3 skill.py",
          }),
        ),
      );

      const loaded = store.loadDir(tmpDir);
      expect(loaded[0]!.entrypoint).toContain(skillDir);
      expect(path.isAbsolute(loaded[0]!.entrypoint.split(" ")[1]!)).toBe(true);
    });
  });
});
