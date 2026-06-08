/**
 * @module paper-viz/types
 * @description 论文可视化演示的数据类型定义
 */

/** 幻灯片类型 */
export type SlideType =
  | 'title'
  | 'abstract'
  | 'key-points'
  | 'methodology'
  | 'experiments'
  | 'contributions'
  | 'limitations'
  | 'references';

/** 幻灯片内容块 */
export interface ContentBlock {
  /** 块类型 */
  type: 'heading' | 'text' | 'list' | 'quote' | 'image' | 'table' | 'badge';
  /** 文本内容（image 类型时为 alt 文本） */
  content: string;
  /** 列表项（type='list' 时使用） */
  items?: string[];
  /** 图片路径或 base64（type='image' 时使用） */
  src?: string;
  /** 图片标题 */
  caption?: string;
  /** 徽章变体（type='badge' 时使用） */
  variant?: 'critical' | 'important' | 'supporting' | 'major' | 'moderate' | 'minor';
  /** 附加 CSS 类名 */
  className?: string;
}

/** 单张幻灯片 */
export interface PresentationSlide {
  /** 幻灯片唯一 ID */
  id: string;
  /** 幻灯片类型 */
  type: SlideType;
  /** 幻灯片标题 */
  title: string;
  /** 副标题 */
  subtitle?: string;
  /** 内容块列表 */
  blocks: ContentBlock[];
  /** 演讲者备注 */
  notes?: string;
  /** 自定义布局类名 */
  layout?: 'center' | 'two-column' | 'full-image' | 'default';
}

/** 演示主题配置 */
export interface PresentationTheme {
  /** 主题名称 */
  name: string;
  /** 主色调 */
  primaryColor: string;
  /** 强调色 */
  accentColor: string;
  /** 背景色 */
  backgroundColor: string;
  /** 表面色（卡片等） */
  surfaceColor: string;
  /** 文本色 */
  textColor: string;
  /** 次要文本色 */
  textSecondaryColor: string;
  /** 代码/引用背景色 */
  codeBackground: string;
  /** 字体族 */
  fontFamily: string;
  /** 标题字体族 */
  headingFontFamily: string;
}

/** 提取的图表信息 */
export interface ExtractedFigure {
  /** 图片文件路径（相对或绝对） */
  path: string;
  /** base64 编码数据（用于内嵌 HTML） */
  base64?: string;
  /** MIME 类型 */
  mimeType: string;
  /** 图表标题/描述 */
  caption: string;
  /** 在 PDF 中的页码 */
  pageNumber: number;
  /** 图片宽度（px） */
  width: number;
  /** 图片高度（px） */
  height: number;
}

/** 完整演示文稿数据 */
export interface PresentationData {
  /** 演示文稿标题 */
  title: string;
  /** 论文作者列表 */
  authors: string[];
  /** 论文发表日期 */
  date: string;
  /** 论文原文 URL */
  url: string;
  /** 幻灯片列表 */
  slides: PresentationSlide[];
  /** 提取的图表 */
  figures: ExtractedFigure[];
  /** 主题配置 */
  theme: PresentationTheme;
  /** 生成时间 */
  generatedAt: string;
}

/** PPT 导出选项 */
export interface PptExportOptions {
  /** 输出文件路径 */
  outputPath: string;
  /** 幻灯片宽度（英寸） */
  width?: number;
  /** 幻灯片高度（英寸） */
  height?: number;
  /** 是否包含演讲者备注 */
  includeNotes?: boolean;
}

/** 预定义学术主题 */
export const ACADEMIC_DARK_THEME: PresentationTheme = {
  name: 'Academic Dark',
  primaryColor: '#60A5FA',
  accentColor: '#F59E0B',
  backgroundColor: '#0F172A',
  surfaceColor: '#1E293B',
  textColor: '#F1F5F9',
  textSecondaryColor: '#94A3B8',
  codeBackground: '#1E293B',
  fontFamily: "'Inter', 'Noto Sans SC', system-ui, sans-serif",
  headingFontFamily: "'Inter', 'Noto Sans SC', system-ui, sans-serif",
};

/** 预定义学术浅色主题 */
export const ACADEMIC_LIGHT_THEME: PresentationTheme = {
  name: 'Academic Light',
  primaryColor: '#2563EB',
  accentColor: '#D97706',
  backgroundColor: '#FFFFFF',
  surfaceColor: '#F8FAFC',
  textColor: '#1E293B',
  textSecondaryColor: '#64748B',
  codeBackground: '#F1F5F9',
  fontFamily: "'Inter', 'Noto Sans SC', system-ui, sans-serif",
  headingFontFamily: "'Inter', 'Noto Sans SC', system-ui, sans-serif",
};
