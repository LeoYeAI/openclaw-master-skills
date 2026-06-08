/**
 * @module paper-viz/slide-builder
 * @description 将 PaperAnalysis 转换为 PresentationData 幻灯片数据
 */

import type { PaperAnalysis, KeyPoint, Contribution } from '../../paper-analyzer/scripts/types';
import type {
  PresentationData,
  PresentationSlide,
  ContentBlock,
  ExtractedFigure,
  PresentationTheme,
} from './types';
import { ACADEMIC_DARK_THEME } from './types';

/** SlideBuilder 配置选项 */
export interface SlideBuilderOptions {
  /** 使用的主题 */
  theme?: PresentationTheme;
  /** 每页关键要点最大数量 */
  maxPointsPerSlide?: number;
  /** 每页实验结果最大数量 */
  maxExperimentsPerSlide?: number;
  /** 是否包含参考文献页 */
  includeReferences?: boolean;
  /** 已提取的图表列表 */
  figures?: ExtractedFigure[];
}

const DEFAULT_OPTIONS: Required<SlideBuilderOptions> = {
  theme: ACADEMIC_DARK_THEME,
  maxPointsPerSlide: 4,
  maxExperimentsPerSlide: 3,
  includeReferences: true,
  figures: [],
};

/**
 * SlideBuilder — 将论文分析结果转换为演示文稿数据
 *
 * @example
 * ```ts
 * const builder = new SlideBuilder();
 * const presentation = builder.buildFromAnalysis(analysis);
 * ```
 */
export class SlideBuilder {
  private options: Required<SlideBuilderOptions>;
  private slideCounter = 0;

  constructor(options?: SlideBuilderOptions) {
    this.options = { ...DEFAULT_OPTIONS, ...options };
  }

  /**
   * 从 PaperAnalysis 构建完整的演示文稿数据
   * @param analysis - 论文分析结果
   * @returns 演示文稿数据
   */
  buildFromAnalysis(analysis: PaperAnalysis): PresentationData {
    this.slideCounter = 0;

    const slides: PresentationSlide[] = [
      this.buildTitleSlide(analysis),
      this.buildAbstractSlide(analysis),
      ...this.buildKeyPointsSlides(analysis.keyPoints),
      this.buildMethodologySlide(analysis),
      ...this.buildExperimentsSlides(analysis),
      this.buildContributionsSlide(analysis.contributions),
      this.buildLimitationsSlide(analysis),
    ];

    if (this.options.includeReferences && analysis.relatedWork.length > 0) {
      slides.push(this.buildReferencesSlide(analysis));
    }

    return {
      title: analysis.metadata.title,
      authors: analysis.metadata.authors,
      date: analysis.metadata.year,
      url: analysis.metadata.url,
      slides,
      figures: this.options.figures,
      theme: this.options.theme,
      generatedAt: new Date().toISOString(),
    };
  }

  /** 生成唯一幻灯片 ID */
  private nextId(prefix: string): string {
    return `${prefix}-${++this.slideCounter}`;
  }

  /** 标题页 */
  private buildTitleSlide(analysis: PaperAnalysis): PresentationSlide {
    const blocks: ContentBlock[] = [
      { type: 'heading', content: analysis.metadata.title },
    ];

    if (analysis.metadata.authors.length > 0) {
      blocks.push({
        type: 'text',
        content: analysis.metadata.authors.join(', '),
        className: 'authors',
      });
    }

    const metaItems: string[] = [];
    if (analysis.metadata.venue) metaItems.push(analysis.metadata.venue);
    if (analysis.metadata.year) metaItems.push(analysis.metadata.year);
    if (analysis.metadata.doi) metaItems.push(`DOI: ${analysis.metadata.doi}`);

    if (metaItems.length > 0) {
      blocks.push({
        type: 'text',
        content: metaItems.join(' · '),
        className: 'meta',
      });
    }

    if (analysis.metadata.keywords.length > 0) {
      blocks.push({
        type: 'list',
        content: 'Keywords',
        items: analysis.metadata.keywords,
        className: 'keywords',
      });
    }

    return {
      id: this.nextId('title'),
      type: 'title',
      title: analysis.metadata.title,
      blocks,
      layout: 'center',
      notes: `Paper URL: ${analysis.metadata.url}`,
    };
  }

  /** 摘要页 */
  private buildAbstractSlide(analysis: PaperAnalysis): PresentationSlide {
    const blocks: ContentBlock[] = [];

    if (analysis.summary) {
      blocks.push({
        type: 'text',
        content: analysis.summary,
        className: 'summary',
      });
    }

    if (analysis.abstract) {
      blocks.push({
        type: 'quote',
        content: analysis.abstract,
      });
    }

    return {
      id: this.nextId('abstract'),
      type: 'abstract',
      title: 'Abstract & Summary',
      blocks,
      layout: 'default',
    };
  }

  /** 关键要点页（可能拆分为多页） */
  private buildKeyPointsSlides(keyPoints: KeyPoint[]): PresentationSlide[] {
    if (keyPoints.length === 0) {
      return [
        {
          id: this.nextId('keypoints'),
          type: 'key-points',
          title: 'Key Points',
          blocks: [{ type: 'text', content: 'No key points extracted.' }],
          layout: 'default',
        },
      ];
    }

    const max = this.options.maxPointsPerSlide;
    const chunks = this.chunk(keyPoints, max);

    return chunks.map((chunk, i) => {
      const blocks: ContentBlock[] = chunk.map((kp) => ({
        type: 'list' as const,
        content: kp.point,
        items: [kp.explanation],
        variant: kp.importance as ContentBlock['variant'],
        className: `importance-${kp.importance}`,
      }));

      const suffix = chunks.length > 1 ? ` (${i + 1}/${chunks.length})` : '';

      return {
        id: this.nextId('keypoints'),
        type: 'key-points' as const,
        title: `Key Points${suffix}`,
        blocks,
        layout: 'default' as const,
      };
    });
  }

  /** 方法论页 */
  private buildMethodologySlide(analysis: PaperAnalysis): PresentationSlide {
    const m = analysis.methodology;
    const blocks: ContentBlock[] = [];

    if (m.overview) {
      blocks.push({ type: 'text', content: m.overview });
    }

    if (m.approach) {
      blocks.push({
        type: 'text',
        content: `**Approach:** ${m.approach}`,
        className: 'approach',
      });
    }

    if (m.novelty) {
      blocks.push({
        type: 'quote',
        content: `Novelty: ${m.novelty}`,
      });
    }

    if (m.strengths.length > 0) {
      blocks.push({
        type: 'list',
        content: 'Strengths',
        items: m.strengths,
        className: 'strengths',
      });
    }

    if (m.weaknesses.length > 0) {
      blocks.push({
        type: 'list',
        content: 'Weaknesses',
        items: m.weaknesses,
        className: 'weaknesses',
      });
    }

    return {
      id: this.nextId('methodology'),
      type: 'methodology',
      title: 'Methodology',
      blocks,
      layout: 'default',
    };
  }

  /** 实验结果页（可能拆分为多页，含图表） */
  private buildExperimentsSlides(analysis: PaperAnalysis): PresentationSlide[] {
    const exp = analysis.experiments;
    const slides: PresentationSlide[] = [];
    const blocks: ContentBlock[] = [];

    if (exp.mainResults) {
      blocks.push({ type: 'text', content: exp.mainResults });
    }

    if (exp.datasets.length > 0) {
      blocks.push({
        type: 'list',
        content: 'Datasets',
        items: exp.datasets,
      });
    }

    if (exp.metrics.length > 0) {
      blocks.push({
        type: 'list',
        content: 'Metrics',
        items: exp.metrics,
      });
    }

    if (exp.baselines.length > 0) {
      blocks.push({
        type: 'list',
        content: 'Baselines',
        items: exp.baselines,
      });
    }

    slides.push({
      id: this.nextId('experiments'),
      type: 'experiments',
      title: 'Experiments & Results',
      blocks,
      layout: 'default',
    });

    // 图表幻灯片
    const figures = this.options.figures;
    if (figures.length > 0) {
      const figChunks = this.chunk(figures, 2);
      for (const chunk of figChunks) {
        const figBlocks: ContentBlock[] = chunk.map((fig) => ({
          type: 'image' as const,
          content: fig.caption || 'Figure',
          src: fig.base64
            ? `data:${fig.mimeType};base64,${fig.base64}`
            : fig.path,
          caption: fig.caption,
        }));

        slides.push({
          id: this.nextId('experiments'),
          type: 'experiments',
          title: 'Figures',
          blocks: figBlocks,
          layout: figBlocks.length === 1 ? 'full-image' : 'two-column',
        });
      }
    }

    // 消融实验
    if (exp.ablations.length > 0) {
      slides.push({
        id: this.nextId('experiments'),
        type: 'experiments',
        title: 'Ablation Studies',
        blocks: [
          {
            type: 'list',
            content: 'Ablation Results',
            items: exp.ablations,
          },
          ...(exp.analysis
            ? [{ type: 'text' as const, content: exp.analysis }]
            : []),
        ],
        layout: 'default',
      });
    }

    return slides;
  }

  /** 贡献页 */
  private buildContributionsSlide(contributions: Contribution[]): PresentationSlide {
    const blocks: ContentBlock[] = contributions.map((c) => ({
      type: 'list' as const,
      content: c.description,
      items: [`Type: ${c.type}`, `Significance: ${c.significance}`],
      variant: c.significance as ContentBlock['variant'],
      className: `significance-${c.significance}`,
    }));

    if (blocks.length === 0) {
      blocks.push({ type: 'text', content: 'No explicit contributions listed.' });
    }

    return {
      id: this.nextId('contributions'),
      type: 'contributions',
      title: 'Contributions',
      blocks,
      layout: 'default',
    };
  }

  /** 局限与展望页 */
  private buildLimitationsSlide(analysis: PaperAnalysis): PresentationSlide {
    const blocks: ContentBlock[] = [];

    if (analysis.limitations.length > 0) {
      blocks.push({
        type: 'list',
        content: 'Limitations',
        items: analysis.limitations.map(
          (l) => `[${l.impact.toUpperCase()}] ${l.description}${l.potentialSolution ? ` → ${l.potentialSolution}` : ''}`
        ),
        className: 'limitations',
      });
    }

    if (analysis.futureWork.length > 0) {
      blocks.push({
        type: 'list',
        content: 'Future Work',
        items: analysis.futureWork,
        className: 'future-work',
      });
    }

    if (blocks.length === 0) {
      blocks.push({ type: 'text', content: 'No limitations or future work discussed.' });
    }

    return {
      id: this.nextId('limitations'),
      type: 'limitations',
      title: 'Limitations & Future Work',
      blocks,
      layout: 'default',
    };
  }

  /** 参考文献页 */
  private buildReferencesSlide(analysis: PaperAnalysis): PresentationSlide {
    const blocks: ContentBlock[] = [];

    for (const rw of analysis.relatedWork) {
      blocks.push({
        type: 'list',
        content: rw.category,
        items: [...rw.papers, rw.comparison ? `Comparison: ${rw.comparison}` : ''].filter(Boolean),
      });
    }

    if (analysis.citations.keyReferences.length > 0) {
      blocks.push({
        type: 'list',
        content: 'Key References',
        items: analysis.citations.keyReferences,
      });
    }

    if (analysis.recommendations.furtherReading.length > 0) {
      blocks.push({
        type: 'list',
        content: 'Further Reading',
        items: analysis.recommendations.furtherReading,
      });
    }

    return {
      id: this.nextId('references'),
      type: 'references',
      title: 'Related Work & References',
      blocks,
      layout: 'default',
    };
  }

  /** 数组分块工具 */
  private chunk<T>(arr: T[], size: number): T[][] {
    const result: T[][] = [];
    for (let i = 0; i < arr.length; i += size) {
      result.push(arr.slice(i, i + size));
    }
    return result;
  }
}
