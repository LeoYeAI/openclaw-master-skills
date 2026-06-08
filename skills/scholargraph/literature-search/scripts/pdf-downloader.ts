/**
 * PDF Downloader - Multi-strategy PDF download module
 * PDF 下载器 - 多策略 PDF 下载模块
 */

import { existsSync, mkdirSync, writeFileSync, readFileSync } from 'fs';
import { join, resolve } from 'path';
import type { SearchResult, PdfDownloadOptions, PdfDownloadResult, PdfMetadataIndex } from './types';
import type { UnpaywallAdapter } from './adapters/unpaywall-adapter';
import type { SearchSourceRegistry } from './adapters/registry';
import { getErrorMessage } from '../../shared/errors';

const DEFAULT_OPTIONS: Required<PdfDownloadOptions> = {
  outputDir: './downloads/pdfs',
  maxFileSize: 50 * 1024 * 1024, // 50MB
  skipExisting: true,
  concurrency: 3,
  namingStrategy: 'title'
};

/** PDF magic bytes check */
const PDF_MAGIC = '%PDF';

export class PdfDownloader {
  private options: Required<PdfDownloadOptions>;
  private registry?: SearchSourceRegistry;
  private unpaywallAdapter?: UnpaywallAdapter;

  constructor(options?: PdfDownloadOptions, registry?: SearchSourceRegistry) {
    this.options = { ...DEFAULT_OPTIONS, ...options };
    this.registry = registry;

    // Try to get Unpaywall adapter from registry
    if (registry) {
      const unpaywall = registry.get('unpaywall');
      if (unpaywall && 'getPdfUrl' in unpaywall) {
        this.unpaywallAdapter = unpaywall as UnpaywallAdapter;
      }
    }
  }

  /**
   * Download PDFs for search results
   */
  async downloadResults(results: SearchResult[]): Promise<PdfDownloadResult[]> {
    // Ensure output directory exists
    const outputDir = resolve(this.options.outputDir);
    if (!existsSync(outputDir)) {
      mkdirSync(outputDir, { recursive: true });
    }

    const downloadResults: PdfDownloadResult[] = [];

    // Process in batches based on concurrency limit
    for (let i = 0; i < results.length; i += this.options.concurrency) {
      const batch = results.slice(i, i + this.options.concurrency);
      const batchPromises = batch.map(result =>
        this.downloadSingle(result, outputDir)
          .then(dlResult => {
            if (dlResult) downloadResults.push(dlResult);
          })
          .catch(err => {
            console.error(`Failed to download "${result.title}":`, getErrorMessage(err));
          })
      );
      await Promise.allSettled(batchPromises);
    }

    // Update metadata index
    this.updateMetadataIndex(outputDir, downloadResults, results);

    return downloadResults;
  }

  /**
   * Download a single PDF
   */
  private async downloadSingle(
    result: SearchResult,
    outputDir: string
  ): Promise<PdfDownloadResult | null> {
    const filename = this.generateFilename(result);
    const filePath = join(outputDir, filename);

    // Skip existing
    if (this.options.skipExisting && existsSync(filePath)) {
      console.log(`  Skipping (exists): ${filename}`);
      return null;
    }

    // Resolve PDF URL
    const pdfUrl = await this.resolvePdfUrl(result);
    if (!pdfUrl) {
      console.log(`  No PDF URL found for: ${result.title}`);
      return null;
    }

    try {
      console.log(`  Downloading: ${filename}`);
      const response = await fetch(pdfUrl, {
        headers: {
          'User-Agent': 'ScholarGraph/1.0 (academic research tool)',
          'Accept': 'application/pdf'
        },
        redirect: 'follow'
      });

      if (!response.ok) {
        console.error(`  HTTP ${response.status} for ${pdfUrl}`);
        return null;
      }

      // Check content length
      const contentLength = response.headers.get('content-length');
      if (contentLength && parseInt(contentLength) > this.options.maxFileSize) {
        console.error(`  File too large (${contentLength} bytes): ${filename}`);
        return null;
      }

      const buffer = Buffer.from(await response.arrayBuffer());

      // Size check on actual content
      if (buffer.length > this.options.maxFileSize) {
        console.error(`  File too large (${buffer.length} bytes): ${filename}`);
        return null;
      }

      // PDF magic bytes verification
      const header = buffer.slice(0, 4).toString('ascii');
      if (!header.startsWith(PDF_MAGIC)) {
        console.error(`  Not a valid PDF (header: ${header}): ${filename}`);
        return null;
      }

      writeFileSync(filePath, buffer);
      console.log(`  Saved: ${filename} (${(buffer.length / 1024).toFixed(1)} KB)`);

      return {
        filePath,
        title: result.title,
        source: result.source,
        size: buffer.length,
        doi: result.doi
      };
    } catch (error) {
      console.error(`  Download error: ${getErrorMessage(error)}`);
      return null;
    }
  }

  /**
   * Multi-strategy PDF URL resolution
   */
  private async resolvePdfUrl(result: SearchResult): Promise<string | undefined> {
    // Strategy 1: Direct pdfUrl from search result
    if (result.pdfUrl) return result.pdfUrl;

    // Strategy 2: Unpaywall lookup by DOI
    if (result.doi && this.unpaywallAdapter?.isAvailable()) {
      const url = await this.unpaywallAdapter.getPdfUrl(result);
      if (url) return url;
    }

    // Strategy 3: OpenAlex OA location (already in pdfUrl if from OpenAlex)

    // Strategy 4: CORE full text
    if (result.doi && this.registry) {
      const coreAdapter = this.registry.get('core');
      if (coreAdapter && 'getPdfUrl' in coreAdapter && coreAdapter.isAvailable()) {
        const url = await (coreAdapter as any).getPdfUrl(result);
        if (url) return url;
      }
    }

    return undefined;
  }

  /**
   * Generate filename from result
   */
  private generateFilename(result: SearchResult): string {
    let baseName: string;

    switch (this.options.namingStrategy) {
      case 'doi':
        baseName = result.doi ? result.doi.replace(/[/\\:]/g, '_') : this.sanitizeTitle(result.title);
        break;
      case 'id':
        baseName = result.id.replace(/[/\\:]/g, '_');
        break;
      case 'title':
      default:
        baseName = this.sanitizeTitle(result.title);
        break;
    }

    return `${baseName}.pdf`;
  }

  /**
   * Sanitize title for use as filename
   */
  private sanitizeTitle(title: string): string {
    return title
      .replace(/[<>:"/\\|?*]/g, '')
      .replace(/\s+/g, '_')
      .substring(0, 100)
      .replace(/_+$/, '');
  }

  /**
   * Update metadata.json index
   */
  private updateMetadataIndex(
    outputDir: string,
    downloadResults: PdfDownloadResult[],
    searchResults: SearchResult[]
  ): void {
    const indexPath = join(outputDir, 'metadata.json');

    let index: PdfMetadataIndex = { files: [] };

    // Load existing index
    try {
      if (existsSync(indexPath)) {
        index = JSON.parse(readFileSync(indexPath, 'utf-8'));
      }
    } catch { /* ignore */ }

    // Add new entries
    for (const dl of downloadResults) {
      const searchResult = searchResults.find(r => r.title === dl.title);
      if (!searchResult) continue;

      // Check if already indexed
      if (index.files.some(f => f.filePath === dl.filePath)) continue;

      index.files.push({
        filePath: dl.filePath,
        title: dl.title,
        authors: searchResult.authors,
        source: dl.source,
        doi: dl.doi,
        url: searchResult.url,
        downloadedAt: new Date().toISOString()
      });
    }

    writeFileSync(indexPath, JSON.stringify(index, null, 2));
  }
}
