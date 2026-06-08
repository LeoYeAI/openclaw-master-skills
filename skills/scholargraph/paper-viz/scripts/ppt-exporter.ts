/**
 * @module paper-viz/ppt-exporter
 * @description 通过 Python python-pptx 子进程导出 PPT 文件
 *
 * 将 PresentationData 序列化为 JSON，传递给内联 Python 脚本，
 * 由 python-pptx 生成 .pptx 文件。
 */

import { spawn } from 'child_process';
import { writeFileSync, unlinkSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { tmpdir } from 'os';
import type { PresentationData, PptExportOptions } from './types';

/** PPT 导出器 */
export class PptExporter {
  private pythonPath: string;

  constructor(pythonPath = 'python') {
    this.pythonPath = pythonPath;
  }

  /**
   * 检测 python-pptx 是否可用
   * @returns 是否已安装
   */
  async checkPptx(): Promise<boolean> {
    try {
      const result = await this.runCommand(this.pythonPath, [
        '-c', 'import pptx; print(pptx.__version__)',
      ]);
      return result.exitCode === 0;
    } catch {
      return false;
    }
  }

  /**
   * 安装 python-pptx
   * @returns 是否安装成功
   */
  async installPptx(): Promise<boolean> {
    try {
      const result = await this.runCommand(this.pythonPath, [
        '-m', 'pip', 'install', 'python-pptx', '--quiet',
      ]);
      return result.exitCode === 0;
    } catch {
      return false;
    }
  }

  /**
   * 导出 PresentationData 为 .pptx 文件
   * @param data - 演示文稿数据
   * @param options - 导出选项
   * @returns 输出文件路径
   */
  async export(data: PresentationData, options: PptExportOptions): Promise<string> {
    // 检测 python-pptx
    const available = await this.checkPptx();
    if (!available) {
      console.log('python-pptx not found, attempting to install...');
      const installed = await this.installPptx();
      if (!installed) {
        throw new Error('Failed to install python-pptx. Please run: pip install python-pptx');
      }
    }

    // 将数据序列化为临时 JSON
    const tempJsonPath = join(tmpdir(), `paper-viz-${Date.now()}.json`).replace(/\\/g, '/');
    const outputPath = options.outputPath.replace(/\\/g, '/');

    try {
      writeFileSync(tempJsonPath, JSON.stringify(this.serializeForPython(data)));

      const script = this.buildPythonScript(tempJsonPath, outputPath, options);
      const result = await this.runPython(script);

      if (result.exitCode !== 0) {
        throw new Error(`PPT export failed: ${result.stderr}`);
      }

      console.log(`PPT exported: ${options.outputPath}`);
      return options.outputPath;
    } finally {
      // 清理临时文件
      try {
        if (existsSync(tempJsonPath)) unlinkSync(tempJsonPath);
      } catch {}
    }
  }

  /** 序列化数据为 Python 友好格式 */
  private serializeForPython(data: PresentationData): PptSerializedData {
    return {
      title: data.title,
      authors: data.authors,
      date: data.date,
      url: data.url,
      theme: {
        primaryColor: data.theme.primaryColor,
        accentColor: data.theme.accentColor,
        backgroundColor: data.theme.backgroundColor,
        textColor: data.theme.textColor,
      },
      slides: data.slides.map((s) => ({
        type: s.type,
        title: s.title,
        subtitle: s.subtitle ?? '',
        layout: s.layout ?? 'default',
        blocks: s.blocks.map((b) => ({
          type: b.type,
          content: b.content,
          items: b.items ?? [],
          caption: b.caption ?? '',
          variant: b.variant ?? '',
        })),
        notes: s.notes ?? '',
      })),
    };
  }

  /** 构建 Python PPT 生成脚本 */
  private buildPythonScript(jsonPath: string, outputPath: string, options: PptExportOptions): string {
    const width = options.width ?? 13.333;
    const height = options.height ?? 7.5;
    const includeNotes = options.includeNotes !== false;

    return `
import json
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
import os

with open("${jsonPath}", "r", encoding="utf-8") as f:
    data = json.load(f)

prs = Presentation()
prs.slide_width = Inches(${width})
prs.slide_height = Inches(${height})

def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    return RGBColor(int(hex_str[0:2],16), int(hex_str[2:4],16), int(hex_str[4:6],16))

theme = data["theme"]
primary = hex_to_rgb(theme["primaryColor"])
accent = hex_to_rgb(theme["accentColor"])
bg_color = hex_to_rgb(theme["backgroundColor"])
text_color = hex_to_rgb(theme["textColor"])

def set_slide_bg(slide, color):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_text_box(slide, left, top, width, height, text, font_size=18, color=None, bold=False, alignment=PP_ALIGN.LEFT):
    txBox = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.color.rgb = color or text_color
    p.font.bold = bold
    p.alignment = alignment
    return txBox

for slide_data in data["slides"]:
    slide_layout = prs.slide_layouts[6]  # Blank layout
    slide = prs.slides.add_slide(slide_layout)
    set_slide_bg(slide, bg_color)

    slide_type = slide_data["type"]
    title = slide_data["title"]
    blocks = slide_data["blocks"]

    if slide_type == "title":
        # Title slide - centered
        y = 1.5
        for block in blocks:
            if block["type"] == "heading":
                add_text_box(slide, 1, y, 11.3, 1.5, block["content"],
                           font_size=36, color=primary, bold=True, alignment=PP_ALIGN.CENTER)
                y += 1.8
            elif block["type"] == "text":
                fs = 20 if "authors" in block.get("content","").lower() or len(block["content"]) < 80 else 14
                add_text_box(slide, 1, y, 11.3, 0.8, block["content"],
                           font_size=fs, color=accent if y < 4 else text_color, alignment=PP_ALIGN.CENTER)
                y += 0.9
            elif block["type"] == "list":
                items_text = " | ".join(block.get("items", []))
                add_text_box(slide, 1.5, y, 10.3, 0.6, items_text,
                           font_size=12, alignment=PP_ALIGN.CENTER)
                y += 0.7
    else:
        # Regular slide with title
        add_text_box(slide, 0.8, 0.3, 11.5, 0.8, title,
                   font_size=28, color=primary, bold=True)

        y = 1.4
        for block in blocks:
            if y > 6.8:
                break

            if block["type"] == "text":
                text = block["content"].replace("**", "")
                h = max(0.6, min(2.0, len(text) / 120 * 0.6))
                add_text_box(slide, 0.8, y, 11.5, h, text, font_size=16)
                y += h + 0.2

            elif block["type"] == "quote":
                add_text_box(slide, 1.2, y, 11, 1.2, block["content"],
                           font_size=14, color=accent)
                y += 1.4

            elif block["type"] == "list":
                if block["content"]:
                    add_text_box(slide, 0.8, y, 11.5, 0.4, block["content"],
                               font_size=16, color=primary, bold=True)
                    y += 0.45
                for item in block.get("items", []):
                    if y > 6.8:
                        break
                    add_text_box(slide, 1.2, y, 11, 0.4, "• " + item, font_size=14)
                    y += 0.38

    # Speaker notes
    ${includeNotes ? `
    if slide_data.get("notes"):
        notes_slide = slide.notes_slide
        notes_slide.notes_text_frame.text = slide_data["notes"]
    ` : ''}

output_dir = os.path.dirname("${outputPath}")
if output_dir and not os.path.exists(output_dir):
    os.makedirs(output_dir, exist_ok=True)

prs.save("${outputPath}")
print("OK")
`;
  }

  /** 执行 Python 代码 */
  private runPython(code: string): Promise<ProcessResult> {
    return this.runCommand(this.pythonPath, ['-c', code]);
  }

  /** 执行子进程命令 */
  private runCommand(cmd: string, args: string[]): Promise<ProcessResult> {
    return new Promise((resolve, reject) => {
      const proc = spawn(cmd, args, {
        stdio: ['pipe', 'pipe', 'pipe'],
        timeout: 60_000,
      });

      let stdout = '';
      let stderr = '';

      proc.stdout.on('data', (d) => { stdout += d.toString(); });
      proc.stderr.on('data', (d) => { stderr += d.toString(); });
      proc.on('close', (code) => resolve({ exitCode: code ?? 1, stdout, stderr }));
      proc.on('error', (err) => reject(err));
    });
  }
}

/** Python 序列化数据格式 */
interface PptSerializedData {
  title: string;
  authors: string[];
  date: string;
  url: string;
  theme: {
    primaryColor: string;
    accentColor: string;
    backgroundColor: string;
    textColor: string;
  };
  slides: Array<{
    type: string;
    title: string;
    subtitle: string;
    layout: string;
    blocks: Array<{
      type: string;
      content: string;
      items: string[];
      caption: string;
      variant: string;
    }>;
    notes: string;
  }>;
}

/** 子进程执行结果 */
interface ProcessResult {
  exitCode: number;
  stdout: string;
  stderr: string;
}
