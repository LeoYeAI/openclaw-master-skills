/**
 * @module paper-viz/pdf-figure-extractor
 * @description 使用 Python pymupdf 从 PDF 中提取图表
 *
 * 通过子进程调用 Python 脚本，利用 pymupdf (fitz) 库
 * 提取 PDF 中的图片和图表。提取失败时优雅降级。
 */

import { spawn } from 'child_process';
import { existsSync, mkdirSync, readFileSync } from 'fs';
import { join, basename, dirname } from 'path';
import type { ExtractedFigure } from './types';

/** 图表提取选项 */
export interface FigureExtractorOptions {
  /** 输出图片目录（默认: PDF 同级 figures/ 目录） */
  outputDir?: string;
  /** 最小图片尺寸（宽或高，px），过滤小图标 */
  minSize?: number;
  /** 是否返回 base64 编码（用于内嵌 HTML） */
  embedBase64?: boolean;
  /** Python 可执行文件路径 */
  pythonPath?: string;
}

const DEFAULT_OPTIONS: Required<FigureExtractorOptions> = {
  outputDir: '',
  minSize: 100,
  embedBase64: true,
  pythonPath: 'python',
};

/**
 * PdfFigureExtractor — 从 PDF 提取图表
 *
 * @example
 * ```ts
 * const extractor = new PdfFigureExtractor();
 * const figures = await extractor.extract('/path/to/paper.pdf');
 * ```
 */
export class PdfFigureExtractor {
  private options: Required<FigureExtractorOptions>;

  constructor(options?: FigureExtractorOptions) {
    this.options = { ...DEFAULT_OPTIONS, ...options };
  }

  /**
   * 检测 pymupdf 是否可用
   * @returns 是否已安装
   */
  async checkPymupdf(): Promise<boolean> {
    try {
      const result = await this.runPython(
        'import fitz; print(fitz.version)'
      );
      return result.exitCode === 0;
    } catch {
      return false;
    }
  }

  /**
   * 安装 pymupdf（pip install pymupdf）
   * @returns 是否安装成功
   */
  async installPymupdf(): Promise<boolean> {
    try {
      const result = await this.runCommand(this.options.pythonPath, [
        '-m', 'pip', 'install', 'pymupdf', '--quiet',
      ]);
      return result.exitCode === 0;
    } catch {
      return false;
    }
  }

  /**
   * 从 PDF 文件提取所有图表
   * @param pdfPath - PDF 文件路径
   * @returns 提取的图表列表
   */
  async extract(pdfPath: string): Promise<ExtractedFigure[]> {
    if (!existsSync(pdfPath)) {
      console.error(`PDF file not found: ${pdfPath}`);
      return [];
    }

    // 确保 pymupdf 可用
    const available = await this.checkPymupdf();
    if (!available) {
      console.log('pymupdf not found, attempting to install...');
      const installed = await this.installPymupdf();
      if (!installed) {
        console.error('Failed to install pymupdf. Please run: pip install pymupdf');
        return [];
      }
    }

    // 确定输出目录
    const outputDir = this.options.outputDir || join(dirname(pdfPath), 'figures');
    if (!existsSync(outputDir)) {
      mkdirSync(outputDir, { recursive: true });
    }

    // 构建 Python 提取脚本
    const script = this.buildExtractScript(pdfPath, outputDir);

    try {
      const result = await this.runPython(script);

      if (result.exitCode !== 0) {
        console.error('Figure extraction failed:', result.stderr);
        return [];
      }

      // 解析提取结果 JSON
      const jsonMatch = result.stdout.match(/\[FIGURES_JSON\]([\s\S]*?)\[\/FIGURES_JSON\]/);
      if (!jsonMatch) {
        console.error('Failed to parse extraction results');
        return [];
      }

      const rawFigures: RawFigure[] = JSON.parse(jsonMatch[1]);

      // 转换为 ExtractedFigure 格式
      return rawFigures
        .filter((f) => f.width >= this.options.minSize || f.height >= this.options.minSize)
        .map((f) => this.toExtractedFigure(f));
    } catch (err) {
      console.error('Figure extraction error:', err);
      return [];
    }
  }

  /** 构建 Python 提取脚本 */
  private buildExtractScript(pdfPath: string, outputDir: string): string {
    // 转义路径中的反斜杠
    const safePdfPath = pdfPath.replace(/\\/g, '/');
    const safeOutputDir = outputDir.replace(/\\/g, '/');

    return `
import fitz
import json
import os
import base64

pdf_path = "${safePdfPath}"
output_dir = "${safeOutputDir}"
embed_base64 = ${this.options.embedBase64 ? 'True' : 'False'}

doc = fitz.open(pdf_path)
figures = []
img_index = 0

for page_num in range(len(doc)):
    page = doc[page_num]
    image_list = page.get_images(full=True)

    for img_info in image_list:
        xref = img_info[0]
        try:
            pix = fitz.Pixmap(doc, xref)

            # 转换 CMYK 为 RGB
            if pix.n > 4:
                pix = fitz.Pixmap(fitz.csRGB, pix)

            width = pix.width
            height = pix.height

            # 保存图片
            img_index += 1
            filename = f"figure_{img_index}_p{page_num + 1}.png"
            filepath = os.path.join(output_dir, filename)
            pix.save(filepath)

            # 可选 base64 编码
            b64_data = ""
            if embed_base64:
                with open(filepath, "rb") as f:
                    b64_data = base64.b64encode(f.read()).decode("utf-8")

            figures.append({
                "path": filepath.replace("\\\\", "/"),
                "base64": b64_data,
                "mimeType": "image/png",
                "caption": f"Figure {img_index} (Page {page_num + 1})",
                "pageNumber": page_num + 1,
                "width": width,
                "height": height
            })

            pix = None
        except Exception as e:
            pass

doc.close()

# 尝试从文本中提取图表标题
doc2 = fitz.open(pdf_path)
for fig in figures:
    page = doc2[fig["pageNumber"] - 1]
    text = page.get_text()
    lines = text.split("\\n")
    for line in lines:
        line_stripped = line.strip()
        if line_stripped.lower().startswith(("figure", "fig.", "fig ")):
            # 匹配包含图片编号的标题
            fig_num = figures.index(fig) + 1
            if str(fig_num) in line_stripped[:20]:
                fig["caption"] = line_stripped
                break
doc2.close()

print("[FIGURES_JSON]")
print(json.dumps(figures, ensure_ascii=False))
print("[/FIGURES_JSON]")
`;
  }

  /** 将原始提取结果转为 ExtractedFigure */
  private toExtractedFigure(raw: RawFigure): ExtractedFigure {
    return {
      path: raw.path,
      base64: raw.base64 || undefined,
      mimeType: raw.mimeType,
      caption: raw.caption,
      pageNumber: raw.pageNumber,
      width: raw.width,
      height: raw.height,
    };
  }

  /** 执行 Python 代码 */
  private runPython(code: string): Promise<ProcessResult> {
    return this.runCommand(this.options.pythonPath, ['-c', code]);
  }

  /** 执行子进程命令 */
  private runCommand(cmd: string, args: string[]): Promise<ProcessResult> {
    return new Promise((resolve, reject) => {
      const proc = spawn(cmd, args, {
        stdio: ['pipe', 'pipe', 'pipe'],
        timeout: 120_000,
      });

      let stdout = '';
      let stderr = '';

      proc.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      proc.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      proc.on('close', (code) => {
        resolve({ exitCode: code ?? 1, stdout, stderr });
      });

      proc.on('error', (err) => {
        reject(err);
      });
    });
  }
}

/** Python 脚本返回的原始图表数据 */
interface RawFigure {
  path: string;
  base64: string;
  mimeType: string;
  caption: string;
  pageNumber: number;
  width: number;
  height: number;
}

/** 子进程执行结果 */
interface ProcessResult {
  exitCode: number;
  stdout: string;
  stderr: string;
}
