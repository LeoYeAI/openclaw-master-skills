import { describe, it, expect, vi, beforeEach } from "vitest";
import { writeReports } from "./reportWriter.js";
import * as fs from "node:fs";
import { ReporterFactory } from "@eval-skills/core";

vi.mock("node:fs");
vi.mock("@eval-skills/core", () => ({
  ReporterFactory: {
    create: vi.fn(),
  },
}));

describe("reportWriter", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (fs.existsSync as any).mockReturnValue(false);
    (fs.mkdirSync as any).mockImplementation(() => {});
    (fs.writeFileSync as any).mockImplementation(() => {});
  });

  it("should create output directory if not exists", async () => {
    await writeReports({
      reports: [],
      outputDir: "/out",
      formats: [],
    });
    expect(fs.mkdirSync).toHaveBeenCalledWith("/out", { recursive: true });
  });

  it("should write requested formats", async () => {
    const reports = [{ skillId: "s1" }] as any;
    const mockReporter = { writeToFile: vi.fn() };
    (ReporterFactory.create as any).mockReturnValue(mockReporter);
    
    await writeReports({
      reports,
      outputDir: "/out",
      formats: ["json", "markdown"],
      timestamp: "2023",
    });

    expect(ReporterFactory.create).toHaveBeenCalledTimes(2);
    expect(ReporterFactory.create).toHaveBeenCalledWith("json");
    expect(ReporterFactory.create).toHaveBeenCalledWith("markdown");
    
    expect(mockReporter.writeToFile).toHaveBeenCalledTimes(2);
    expect(mockReporter.writeToFile).toHaveBeenCalledWith(reports, expect.stringContaining(".json"));
    expect(mockReporter.writeToFile).toHaveBeenCalledWith(reports, expect.stringContaining(".md"));
  });

  it("should handle unknown format gracefully", async () => {
    // If ReporterFactory throws, catch it.
    (ReporterFactory.create as any).mockImplementation(() => { throw new Error("Unknown format"); });

    await writeReports({
      reports: [],
      outputDir: "/out",
      formats: ["unknown" as any],
    });
    // Should not throw and not write file
    expect(fs.writeFileSync).not.toHaveBeenCalled();
  });
});
