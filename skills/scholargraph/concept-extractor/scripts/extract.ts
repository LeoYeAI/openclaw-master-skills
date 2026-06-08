/**
 * Concept Extractor - 概念提取模块
 * 从综述论文中提取核心概念，分类并识别关系
 */

import { createAIProvider, type AIProvider } from '../../shared/ai-provider';
import { extractJson } from '../../shared/utils';
import { ApiInitializationError, getErrorMessage } from '../../shared/errors';
import type { PaperAnalysis } from '../../paper-analyzer/scripts/types';
import type {
  ExtractedConcept,
  ConceptRelation,
  ConceptTaxonomy,
  ConceptExtractionResult,
  ConceptExtractionOptions,
  ConceptCategory,
  MergedConcept,
  ConceptMergeResult
} from './types';

export default class ConceptExtractor {
  private ai: AIProvider | null = null;

  async initialize(): Promise<void> {
    if (!this.ai) {
      try {
        this.ai = await createAIProvider();
      } catch (error) {
        throw new ApiInitializationError(
          `Failed to initialize AI provider: ${getErrorMessage(error)}`,
          error instanceof Error ? error : undefined
        );
      }
    }
  }

  /**
   * 从论文分析结果中提取概念
   */
  async extractFromReview(
    analysis: PaperAnalysis,
    options: ConceptExtractionOptions = {}
  ): Promise<ConceptExtractionResult> {
    await this.initialize();

    const {
      minConcepts = 15,
      maxConcepts = 30,
      minImportance = 1,
      extractRelations = true
    } = options;

    // 提取概念
    const concepts = await this.extractConcepts(analysis, minConcepts, maxConcepts);

    // 过滤低重要性概念
    const filtered = concepts.filter(c => c.importance >= minImportance);

    // 提取关系
    let relations: ConceptRelation[] = [];
    if (extractRelations && filtered.length > 1) {
      relations = await this.extractRelations(filtered);
    }

    // 构建分类体系
    const taxonomy = this.buildTaxonomy(filtered);

    // 统计信息
    const byCategory: Record<ConceptCategory, number> = {
      foundation: 0, core: 0, advanced: 0, application: 0
    };
    const byImportance: Record<number, number> = {};
    for (const c of filtered) {
      byCategory[c.category]++;
      byImportance[c.importance] = (byImportance[c.importance] || 0) + 1;
    }

    return {
      sourceTitle: analysis.metadata.title,
      sourceUrl: analysis.metadata.url,
      concepts: filtered,
      relations,
      taxonomy,
      stats: {
        totalConcepts: filtered.length,
        byCategory,
        byImportance
      }
    };
  }

  /**
   * 使用AI提取概念
   */
  private async extractConcepts(
    analysis: PaperAnalysis,
    min: number,
    max: number
  ): Promise<ExtractedConcept[]> {
    const prompt = `从以下论文分析中提取${min}-${max}个核心学术概念。

论文标题: ${analysis.metadata.title}
关键词: ${analysis.metadata.keywords.join(', ')}
摘要: ${analysis.abstract}
要点: ${analysis.keyPoints.map(kp => kp.point).join('; ')}
贡献: ${analysis.contributions.map(c => c.description).join('; ')}

请提取核心概念并返回JSON格式:
{
  "concepts": [
    {
      "name": "概念名称",
      "nameEn": "English Name",
      "nameZh": "中文名称",
      "category": "foundation|core|advanced|application",
      "importance": 1-5,
      "definition": "简短定义",
      "frequency": "high|medium|low",
      "aliases": ["别名1", "别名2"]
    }
  ]
}

分类标准:
- foundation: 基础理论概念（如线性代数、概率论）
- core: 核心技术概念（如注意力机制、Transformer）
- advanced: 进阶概念（如多头注意力、位置编码）
- application: 应用概念（如机器翻译、文本生成）

重要性标准:
- 5: 论文核心主题
- 4: 论文重要组成部分
- 3: 论文中频繁提及
- 2: 论文中有涉及
- 1: 论文中偶尔提到`;

    const responseText = await this.ai!.chat([
      { role: 'system', content: '你是学术概念提取专家。只返回JSON格式。' },
      { role: 'user', content: prompt }
    ], { temperature: 0.2 });

    const result = extractJson<{
      concepts?: Array<{
        name: string;
        nameEn?: string;
        nameZh?: string;
        category?: string;
        importance?: number;
        definition?: string;
        frequency?: string;
        aliases?: string[];
      }>;
    }>(responseText);

    if (!result.success || !result.data?.concepts) {
      console.error('Failed to extract concepts:', result.error);
      return [];
    }

    return result.data.concepts.map((c, index) => ({
      id: `concept_${index}`,
      name: c.name,
      nameEn: c.nameEn,
      nameZh: c.nameZh,
      category: this.validateCategory(c.category),
      importance: Math.min(5, Math.max(1, c.importance || 3)),
      definition: c.definition || '',
      frequency: this.validateFrequency(c.frequency),
      relatedConcepts: [],
      aliases: c.aliases || []
    }));
  }

  /**
   * 提取概念间关系
   */
  private async extractRelations(concepts: ExtractedConcept[]): Promise<ConceptRelation[]> {
    const conceptNames = concepts.map(c => c.name).join(', ');

    const prompt = `分析以下概念之间的关系:

概念列表: ${conceptNames}

请返回JSON格式的关系列表:
{
  "relations": [
    {
      "source": "源概念名称",
      "target": "目标概念名称",
      "relationType": "prerequisite|related|derived|component|contrast",
      "strength": 0.0-1.0,
      "description": "关系描述"
    }
  ]
}

关系类型说明:
- prerequisite: 前置依赖关系
- related: 相关关系
- derived: 衍生关系
- component: 组成部分
- contrast: 对比关系`;

    const responseText = await this.ai!.chat([
      { role: 'system', content: '你是学术概念关系分析专家。只返回JSON格式。' },
      { role: 'user', content: prompt }
    ], { temperature: 0.2 });

    const result = extractJson<{
      relations?: Array<{
        source: string;
        target: string;
        relationType?: string;
        strength?: number;
        description?: string;
      }>;
    }>(responseText);

    if (!result.success || !result.data?.relations) {
      return [];
    }

    return result.data.relations
      .map(r => {
        const sourceConcept = concepts.find(c =>
          c.name === r.source || c.nameEn === r.source || c.nameZh === r.source
        );
        const targetConcept = concepts.find(c =>
          c.name === r.target || c.nameEn === r.target || c.nameZh === r.target
        );

        if (!sourceConcept || !targetConcept) return null;

        return {
          sourceId: sourceConcept.id,
          targetId: targetConcept.id,
          relationType: this.validateRelationType(r.relationType),
          strength: Math.min(1, Math.max(0, r.strength || 0.5)),
          description: r.description
        };
      })
      .filter((r): r is ConceptRelation => r !== null);
  }

  /**
   * 构建概念分类体系
   */
  private buildTaxonomy(concepts: ExtractedConcept[]): ConceptTaxonomy {
    return {
      foundation: concepts.filter(c => c.category === 'foundation'),
      core: concepts.filter(c => c.category === 'core'),
      advanced: concepts.filter(c => c.category === 'advanced'),
      application: concepts.filter(c => c.category === 'application')
    };
  }

  /**
   * 合并多个提取结果（去重）
   */
  mergeConcepts(results: ConceptExtractionResult[]): ConceptMergeResult {
    const conceptMap = new Map<string, MergedConcept>();
    const allRelations: ConceptRelation[] = [];
    let totalBefore = 0;

    for (const result of results) {
      totalBefore += result.concepts.length;

      for (const concept of result.concepts) {
        const key = this.normalizeConceptName(concept.name);
        const existing = conceptMap.get(key);

        if (existing) {
          // 合并已存在的概念
          existing.sources.push(result.sourceTitle);
          existing.occurrenceCount++;
          existing.mergedImportance = Math.max(existing.mergedImportance, concept.importance);
          // 合并别名
          for (const alias of concept.aliases) {
            if (!existing.aliases.includes(alias)) {
              existing.aliases.push(alias);
            }
          }
        } else {
          conceptMap.set(key, {
            ...concept,
            id: `merged_${conceptMap.size}`,
            sources: [result.sourceTitle],
            mergedImportance: concept.importance,
            occurrenceCount: 1
          });
        }
      }

      allRelations.push(...result.relations);
    }

    const mergedConcepts = Array.from(conceptMap.values());

    // 更新关系中的概念ID
    const nameToId = new Map<string, string>();
    for (const c of mergedConcepts) {
      nameToId.set(this.normalizeConceptName(c.name), c.id);
      for (const alias of c.aliases) {
        nameToId.set(this.normalizeConceptName(alias), c.id);
      }
    }

    // 去重关系
    const relationSet = new Set<string>();
    const dedupedRelations: ConceptRelation[] = [];
    for (const r of allRelations) {
      const key = `${r.sourceId}-${r.targetId}-${r.relationType}`;
      if (!relationSet.has(key)) {
        relationSet.add(key);
        dedupedRelations.push(r);
      }
    }

    return {
      concepts: mergedConcepts,
      relations: dedupedRelations,
      stats: {
        totalBefore,
        totalAfter: mergedConcepts.length,
        duplicatesRemoved: totalBefore - mergedConcepts.length,
        sourcesCount: results.length
      }
    };
  }

  /**
   * 标准化概念名称用于去重
   */
  private normalizeConceptName(name: string): string {
    return name.toLowerCase().replace(/[^a-z0-9\u4e00-\u9fa5]/g, '').trim();
  }

  private validateCategory(category?: string): ConceptCategory {
    const valid: ConceptCategory[] = ['foundation', 'core', 'advanced', 'application'];
    return valid.includes(category as ConceptCategory) ? category as ConceptCategory : 'core';
  }

  private validateFrequency(freq?: string): 'high' | 'medium' | 'low' {
    const valid = ['high', 'medium', 'low'];
    return valid.includes(freq as string) ? freq as 'high' | 'medium' | 'low' : 'medium';
  }

  private validateRelationType(type?: string): ConceptRelation['relationType'] {
    const valid = ['prerequisite', 'related', 'derived', 'component', 'contrast'];
    return valid.includes(type as string) ? type as ConceptRelation['relationType'] : 'related';
  }

  /**
   * 格式化概念提取结果
   */
  formatResult(result: ConceptExtractionResult): string {
    const lines: string[] = [
      `📚 概念提取结果 - ${result.sourceTitle}\n`,
      `📊 统计: ${result.stats.totalConcepts} 个概念\n`
    ];

    const categoryLabels: Record<ConceptCategory, string> = {
      foundation: '🔹 基础概念',
      core: '🔸 核心概念',
      advanced: '🔶 进阶概念',
      application: '🔷 应用概念'
    };

    for (const [category, label] of Object.entries(categoryLabels)) {
      const concepts = result.taxonomy[category as keyof ConceptTaxonomy];
      if (concepts.length > 0) {
        lines.push(`\n${label} (${concepts.length}):`);
        for (const c of concepts) {
          const stars = '★'.repeat(c.importance) + '☆'.repeat(5 - c.importance);
          lines.push(`  ${stars} ${c.name}${c.nameEn ? ` (${c.nameEn})` : ''}`);
          if (c.definition) {
            lines.push(`       ${c.definition}`);
          }
        }
      }
    }

    if (result.relations.length > 0) {
      lines.push(`\n🔗 概念关系 (${result.relations.length}):`);
      for (const r of result.relations.slice(0, 15)) {
        const source = result.concepts.find(c => c.id === r.sourceId);
        const target = result.concepts.find(c => c.id === r.targetId);
        if (source && target) {
          lines.push(`  ${source.name} --[${r.relationType}]--> ${target.name}`);
        }
      }
    }

    return lines.join('\n');
  }
}
