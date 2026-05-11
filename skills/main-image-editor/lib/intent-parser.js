import { spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

function toConfidence(raw, fallback = 0.9) {
  const num = Number(raw);
  if (!Number.isFinite(num)) return fallback;
  if (num < 0) return 0;
  if (num > 1) return 1;
  return num;
}

function expandHome(inputPath) {
  if (!inputPath) return "";
  const value = String(inputPath);
  if (value === "~") return os.homedir();
  if (value.startsWith("~/")) return path.join(os.homedir(), value.slice(2));
  return value;
}

function extractFileHintsFromText(text) {
  if (!text) return [];
  const matches = [];
  const pattern = /([^\s，。,;；"'`]+?\.(?:psd|psb))/gi;
  for (const match of String(text).matchAll(pattern)) {
    const raw = String(match[1] || "").trim();
    const token = raw
      .split(/[：:]/)
      .pop()
      ?.replace(/^[“"'`【\[]+|[”"'`】\]]+$/g, "")
      .trim();
    if (!token) continue;
    matches.push(token);
  }
  // Keep stable order while deduplicating.
  return Array.from(new Set(matches));
}

function runTesseractOcr(imagePath) {
  const result = spawnSync("tesseract", [imagePath, "stdout", "-l", "chi_sim+eng", "--psm", "6"], {
    encoding: "utf8",
    timeout: 20_000,
  });
  if (result.status === 0) {
    return (result.stdout || "").trim();
  }
  const fallback = spawnSync("tesseract", [imagePath, "stdout", "-l", "eng", "--psm", "6"], {
    encoding: "utf8",
    timeout: 20_000,
  });
  if (fallback.status === 0) {
    return (fallback.stdout || "").trim();
  }
  return "";
}

function runVisionOcr(imagePath) {
  const script = `
import Foundation
import Vision

if CommandLine.arguments.count < 2 {
  exit(0)
}
let imagePath = CommandLine.arguments[1]
let url = URL(fileURLWithPath: imagePath)
let request = VNRecognizeTextRequest()
request.recognitionLevel = .accurate
request.usesLanguageCorrection = true
request.recognitionLanguages = ["zh-Hans", "en-US"]
let handler = VNImageRequestHandler(url: url, options: [:])
do {
  try handler.perform([request])
  let lines = (request.results as? [VNRecognizedTextObservation] ?? []).compactMap { obs in
    obs.topCandidates(1).first?.string
  }
  print(lines.joined(separator: "\\n"))
} catch {
  exit(0)
}
`;
  const result = spawnSync("swift", ["-", imagePath], {
    encoding: "utf8",
    timeout: 120_000,
    input: script,
  });
  if (result.status === 0) {
    return (result.stdout || "").trim();
  }
  return "";
}

function extractFileHintsFromScreenshot(screenshotPath) {
  const resolvedPath = path.resolve(expandHome(screenshotPath));
  if (!resolvedPath || !fs.existsSync(resolvedPath)) return [];
  const tesseractText = runTesseractOcr(resolvedPath);
  const ocrText = tesseractText || runVisionOcr(resolvedPath);
  return extractFileHintsFromText(ocrText);
}

function extractScreenshotOcrText(screenshotPath) {
  const resolvedPath = path.resolve(expandHome(screenshotPath));
  if (!resolvedPath || !fs.existsSync(resolvedPath)) return "";
  const tesseractText = runTesseractOcr(resolvedPath);
  return tesseractText || runVisionOcr(resolvedPath);
}

function normalizeEdit(item) {
  const op = item?.op === "delete_text" ? "delete_text" : "replace_text";
  const layerName = String(item?.layerName || "").trim();
  const newText =
    op === "delete_text" ? "" : typeof item?.newText === "string" ? item.newText : "";
  return {
    op,
    layerName,
    newText,
    confidence: toConfidence(item?.confidence, op === "delete_text" ? 0.86 : 0.9),
    positionHint: typeof item?.positionHint === "string" ? item.positionHint.trim() : "",
  };
}

function parseEditsFromChinese(text) {
  const edits = [];
  const replacePattern =
    /(?:把)?([^，,。]+?)改成([\s\S]+?)(?=(?:，|,)?(?:把)?[^，,。]+?改成|(?:，|,)?(?:删除|移除|去掉|并保存|并导出|保存成|保存到|放置在|然后|$))/g;
  for (const match of text.matchAll(replacePattern)) {
    const layerName = (match[1] || "").trim();
    const newText = (match[2] || "").trim().replace(/[，,。]\s*$/, "");
    if (!layerName || !newText) continue;
    edits.push(
      normalizeEdit({
        op: "replace_text",
        layerName,
        newText,
      }),
    );
  }

  const deletePattern =
    /(?:删除|移除|去掉)(?:图层)?\s*["“]?([^"”。，,]+)["”]?(?:\s*(?:文字|文案|内容))?/g;
  for (const match of text.matchAll(deletePattern)) {
    const layerName = (match[1] || "").trim();
    if (!layerName) continue;
    edits.push(
      normalizeEdit({
        op: "delete_text",
        layerName,
      }),
    );
  }
  return edits;
}

function parseFileHint(text) {
  const fileMatch = text.match(/(?:找到|找)\s*([^\s，。,]+?\.(?:psd|psb))/i);
  return fileMatch?.[1]?.trim();
}

function parseAbsolutePath(text) {
  if (!text) return "";
  const match = String(text).match(/(\/[^\s，。,]+?\.(?:psd|psb))/i);
  const candidate = match?.[1]?.trim();
  if (!candidate) return "";
  return fs.existsSync(candidate) ? candidate : "";
}

function parseEditsFromOcrText(rawText) {
  const text = String(rawText || "").replaceAll("\r", "\n");
  const edits = [];
  const lines = text
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);

  for (const line of lines) {
    const replaceMatch = line.match(/^(.{1,40}?)(?:改成|改为|改到|改)(.{1,40})$/);
    if (replaceMatch) {
      const left = (replaceMatch[1] || "").trim();
      const right = (replaceMatch[2] || "").trim();
      if (left && right && left !== right) {
        edits.push(
          normalizeEdit({
            op: "replace_text",
            layerName: left,
            newText: right,
            confidence: 0.78,
            positionHint: "from_screenshot_ocr",
          }),
        );
      }
      continue;
    }
    const deleteMatch = line.match(/^(?:删除|移除|去掉)(.{1,40})$/);
    if (deleteMatch) {
      const target = (deleteMatch[1] || "").trim();
      if (target) {
        edits.push(
          normalizeEdit({
            op: "delete_text",
            layerName: target,
            confidence: 0.74,
            positionHint: "from_screenshot_ocr",
          }),
        );
      }
    }
  }
  // Expand short "X改成Y" edits using nearby full copy lines from screenshot OCR.
  // Example: "X60改成X50" + "X60旗舰上新" => layerName "X60旗舰上新", newText "X50旗舰上新"
  const instructionLinePattern = /(改成|改为|改到|文件名|保存|完成后|导出|打包|主图存放)/;
  const contentLines = lines.filter((line) => !instructionLinePattern.test(line));
  const replaceSourceInLine = (line, source, target) => {
    if (line.includes(source)) {
      return line.replace(source, target).trim();
    }
    if (source.length > 1) {
      const tail = source.slice(1).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
      const relaxed = new RegExp(`[A-Za-z&€¥￥]?${tail}`);
      if (relaxed.test(line)) {
        return line.replace(relaxed, target).trim();
      }
    }
    return "";
  };
  const shouldExpandByContext = (source) => {
    const s = String(source || "").trim();
    if (!s) return false;
    // Expand mostly for short alnum-like tokens where OCR gives shorthand
    // and we need full copy for precise layer targeting (e.g. X60, 15min).
    return /^[A-Za-z0-9&€¥￥._-]+$/i.test(s);
  };
  const expanded = edits.map((edit) => {
    if (edit.op !== "replace_text") return edit;
    const source = String(edit.layerName || "").trim();
    const target = String(edit.newText || "").trim();
    if (!shouldExpandByContext(source)) return edit;
    if (!source || !target) return edit;
    const relaxedSourceTail = source.length > 1 ? source.slice(1) : source;
    const candidates = contentLines
      .filter((line) => line.includes(source) || (relaxedSourceTail && line.includes(relaxedSourceTail)))
      .filter((line) => line.length > source.length)
      .filter((line) => line.length <= 48)
      .filter((line) => !line.includes("改成") && !line.includes("改为"));
    if (candidates.length === 0) return edit;
    const best = candidates.sort((a, b) => a.length - b.length)[0];
    const replaced = replaceSourceInLine(best, source, target);
    if (!replaced || replaced === best) return edit;
    return normalizeEdit({
      op: "replace_text",
      layerName: best,
      newText: replaced,
      confidence: 0.84,
      positionHint: "from_screenshot_ocr_context",
    });
  });
  // Keep order while removing duplicates.
  const seen = new Set();
  return expanded.filter((item) => {
    const key = `${item.op}|${item.layerName}|${item.newText}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function parseTaskFromText(text) {
  const fileHint = parseFileHint(text || "");
  const edits = parseEditsFromChinese(text || "");
  if (edits.length === 0) {
    return { ok: false, error: "未识别到修改项（支持“把X改成Y”或“删除X”）。" };
  }
  return {
    ok: true,
    task: {
      fileHint,
      modifications: edits,
    },
  };
}

export function parseIntentRequest(request = {}) {
  const text = typeof request.text === "string" ? request.text.trim() : "";
  const screenshotPath =
    typeof request.screenshotPath === "string" ? request.screenshotPath.trim() : "";
  const rawTasks = Array.isArray(request.tasks) ? request.tasks : [];
  const screenshotOcrText = extractScreenshotOcrText(screenshotPath);
  const screenshotEdits = parseEditsFromOcrText(screenshotOcrText);
  const textEdits = parseEditsFromChinese(text);
  const inferredEdits = textEdits.length > 0 ? textEdits : screenshotEdits;
  const parsedTasks = [];

  if (rawTasks.length > 0) {
    for (const item of rawTasks) {
      const modifications = Array.isArray(item?.modifications)
        ? item.modifications.map(normalizeEdit).filter((x) => x.layerName)
        : inferredEdits;
      if (modifications.length === 0) continue;
      const exactPath = item?.exactPath ? path.resolve(String(item.exactPath)) : undefined;
      const fileHint = item?.fileHint ? String(item.fileHint).trim() : undefined;
      parsedTasks.push({
        exactPath,
        fileHint,
        modifications,
      });
    }
  } else if (text) {
    const parsed = parseTaskFromText(text);
    if (parsed.ok) {
      parsedTasks.push(parsed.task);
    } else if (screenshotEdits.length > 0) {
      parsedTasks.push({
        exactPath: parseAbsolutePath(text) || undefined,
        fileHint: parseFileHint(text || ""),
        modifications: screenshotEdits,
      });
    } else {
      return { ok: false, code: "E_PARSE_FAILED", message: parsed.error };
    }
  } else {
    return { ok: false, code: "E_PARSE_FAILED", message: "请求缺少 text 或 tasks。" };
  }

  if (parsedTasks.length === 0) {
    return { ok: false, code: "E_PARSE_FAILED", message: "未生成任何有效任务。" };
  }

  const fileHintCandidates = [
    ...extractFileHintsFromText(screenshotOcrText),
    ...extractFileHintsFromText(text),
  ];
  const fallbackFileHint = fileHintCandidates[0] || "";
  if (fallbackFileHint) {
    for (const task of parsedTasks) {
      if (!task.exactPath && !task.fileHint) {
        task.fileHint = fallbackFileHint;
      }
    }
  }
  const missingFileHint = parsedTasks.some((task) => !task.exactPath && !task.fileHint);
  if (missingFileHint) {
    return {
      ok: false,
      code: "E_PARSE_FAILED",
      message:
        "未识别到 PSD/PSB 文件线索。请在文本写明文件名（如 xxx.psd），或确保截图内文件名可被 OCR 识别（tesseract 或 macOS Vision OCR）。",
    };
  }

  const taskPreviews = parsedTasks.map((task, idx) => {
    const edits = task.modifications.map((item) => ({
      layerName: item.layerName,
      op: item.op,
      newText: item.newText,
      confidence: item.confidence,
      positionHint: item.positionHint,
    }));
    const minConfidence = edits.reduce((min, item) => Math.min(min, item.confidence), 1);
    return {
      taskId: `main-image-${Date.now()}-${idx + 1}`,
      exactPath: task.exactPath,
      fileHint: task.fileHint,
      edits,
      minConfidence,
    };
  });

  return { ok: true, tasks: taskPreviews };
}
