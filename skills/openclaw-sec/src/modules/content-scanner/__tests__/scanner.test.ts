import { describe, it, expect } from '@jest/globals';
import { ContentScanner } from '../scanner';
import { ModuleConfig } from '../../../types';

describe('ContentScanner', () => {
  const defaultConfig: ModuleConfig = {
    enabled: true
  };

  describe('constructor', () => {
    it('should create an instance with valid config', () => {
      const scanner = new ContentScanner(defaultConfig);
      expect(scanner).toBeInstanceOf(ContentScanner);
    });

    it('should throw error if config is invalid', () => {
      expect(() => new ContentScanner(null as any)).toThrow();
    });
  });

  describe('scan', () => {
    describe('Base64 encoding', () => {
      it('should detect base64 encoded strings', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const text = 'SGVsbG8gV29ybGQhIFRoaXMgaXMgYSBsb25nIGJhc2U2NCBlbmNvZGVkIHN0cmluZy4=';

        const findings = await scanner.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings[0].module).toBe('content_scanner');
        expect(findings[0].pattern.subcategory).toBe('base64_encoded');
      });

      it('should detect base64 in longer text', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const text = 'Some text SGVsbG8gV29ybGQhIFRoaXMgaXMgYSBsb25nIGJhc2U2NCBlbmNvZGVkIHN0cmluZy4= more text';

        const findings = await scanner.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'base64_encoded')).toBe(true);
      });
    });

    describe('Hexadecimal encoding', () => {
      it('should detect long hex strings', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const text = '48656c6c6f20576f726c6421205468697320697320612074657374206d6573736167652e';

        const findings = await scanner.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'hex_encoded')).toBe(true);
      });

      it('should detect hex with 0x prefix', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const text = '0x' + 'a'.repeat(64);

        const findings = await scanner.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'hex_encoded')).toBe(true);
      });
    });

    describe('Unicode escape sequences', () => {
      it('should detect Unicode escape sequences', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const text = '\\u0048\\u0065\\u006c\\u006c\\u006f';

        const findings = await scanner.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings[0].pattern.subcategory).toBe('unicode_escape');
      });

      it('should detect multiple Unicode escapes', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const text = 'Text with \\u0041\\u0042\\u0043\\u0044\\u0045 escapes';

        const findings = await scanner.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'unicode_escape')).toBe(true);
      });
    });

    describe('Homoglyph attacks', () => {
      it('should detect Cyrillic-Latin mix (homoglyphs)', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const text = 'рауpal account'; // 'рау' is Cyrillic, 'pal' is Latin (looks like 'paypal')

        const findings = await scanner.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings[0].pattern.subcategory).toBe('unicode_homoglyphs');
        expect(findings[0].severity).toBe('HIGH');
      });

      it('should detect homoglyph in domain names', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const text = 'Visit Gооgle.com'; // Contains Cyrillic 'о'

        const findings = await scanner.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'unicode_homoglyphs')).toBe(true);
      });
    });

    describe('Zero-width characters', () => {
      it('should detect zero-width space', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const text = 'admin\u200Buser';

        const findings = await scanner.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings[0].pattern.subcategory).toBe('zero_width_chars');
        expect(findings[0].severity).toBe('HIGH');
      });

      it('should detect zero-width non-joiner', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const text = 'pass\u200Cword';

        const findings = await scanner.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'zero_width_chars')).toBe(true);
      });

      it('should detect zero-width joiner', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const text = 'api\u200Dkey';

        const findings = await scanner.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'zero_width_chars')).toBe(true);
      });
    });

    describe('RTL override attacks', () => {
      it('should detect right-to-left override', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const text = 'file\u202Etxt.exe';

        const findings = await scanner.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings[0].pattern.subcategory).toBe('rtl_override');
        expect(findings[0].severity).toBe('HIGH');
      });

      it('should detect left-to-right override', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const text = 'admin\u202Duser';

        const findings = await scanner.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'rtl_override')).toBe(true);
      });
    });

    describe('JavaScript obfuscation', () => {
      it('should detect eval() usage', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const text = 'eval("alert(1)")';

        const findings = await scanner.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings[0].pattern.subcategory).toBe('eval_function');
        expect(findings[0].severity).toBe('HIGH');
      });

      it('should detect String.fromCharCode obfuscation', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const text = 'String.fromCharCode(72, 101, 108, 108, 111)';

        const findings = await scanner.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'javascript_obfuscation')).toBe(true);
      });

      it('should detect unescape() with encoded content', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const text = 'unescape("%48%65%6c%6c%6f")';

        const findings = await scanner.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'javascript_unescape')).toBe(true);
      });

      it('should detect atob() base64 decoding', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const text = 'atob("SGVsbG8gV29ybGQ=")';

        const findings = await scanner.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'atob_btoa')).toBe(true);
      });

      it('should detect btoa() base64 encoding', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const text = 'btoa("Hello World")';

        const findings = await scanner.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'atob_btoa')).toBe(true);
      });
    });

    describe('Escape sequence obfuscation', () => {
      it('should detect excessive hex escaping', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const text = '\\x48\\x65\\x6c\\x6c\\x6f\\x20\\x57\\x6f\\x72\\x6c\\x64';

        const findings = await scanner.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings[0].pattern.subcategory).toBe('excessive_escaping');
      });

      it('should detect octal escape sequences', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const text = '\\110\\145\\154\\154\\157\\040\\127\\157\\162\\154\\144';

        const findings = await scanner.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'octal_escaping')).toBe(true);
      });
    });

    describe('HTML entity encoding', () => {
      it('should detect excessive HTML entity encoding', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const text = '&#72;&#101;&#108;&#108;&#111;&#32;&#87;&#111;&#114;&#108;&#100;';

        const findings = await scanner.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings[0].pattern.subcategory).toBe('html_entities');
      });

      it('should detect hex HTML entities', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const text = '&#x48;&#x65;&#x6c;&#x6c;&#x6f;&#x20;&#x57;&#x6f;&#x72;&#x6c;&#x64;';

        const findings = await scanner.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'html_entities')).toBe(true);
      });
    });

    describe('URL encoding', () => {
      it('should detect excessive URL encoding', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const text = '%48%65%6c%6c%6f%20%57%6f%72%6c%64%21%20%54%65%73%74';

        const findings = await scanner.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings[0].pattern.subcategory).toBe('url_encoding_excessive');
      });

      it('should detect double URL encoding', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const text = '%2527%253C%253E';

        const findings = await scanner.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'double_encoding')).toBe(true);
        expect(findings.some(f => f.severity === 'HIGH')).toBe(true);
      });
    });

    describe('Language-specific obfuscation', () => {
      it('should detect PHP chr() concatenation', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const text = 'chr(72).chr(101).chr(108).chr(108).chr(111)';

        const findings = await scanner.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings[0].pattern.subcategory).toBe('php_chr_concat');
        expect(findings[0].severity).toBe('HIGH');
      });

      it('should detect Python chr() usage', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const text = 'chr(72), chr(101), chr(108), chr(108), chr(111)';

        const findings = await scanner.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'python_chr_join')).toBe(true);
      });
    });

    describe('Invisible separators', () => {
      it('should detect invisible Unicode separators', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const text = 'admin\u2000user';

        const findings = await scanner.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'invisible_separator')).toBe(true);
        expect(findings.some(f => f.severity === 'HIGH')).toBe(true);
      });

      it('should detect thin space separator', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const text = 'pass\u2009word';

        const findings = await scanner.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'invisible_separator')).toBe(true);
      });
    });

    describe('Multiple obfuscation techniques', () => {
      it('should detect multiple obfuscation methods in same text', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const text = 'eval(atob("SGVsbG8=")) and \\u0041\\u0042\\u0043\\u0044';

        const findings = await scanner.scan(text);

        expect(findings.length).toBeGreaterThan(1);
        expect(findings.some(f => f.pattern.subcategory === 'eval_function')).toBe(true);
        expect(findings.some(f => f.pattern.subcategory === 'atob_btoa')).toBe(true);
        expect(findings.some(f => f.pattern.subcategory === 'unicode_escape')).toBe(true);
      });

      it('should find all instances of same pattern', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const text = 'eval(x) and later eval(y) and eval(z)';

        const findings = await scanner.scan(text);

        const evalFindings = findings.filter(f => f.pattern.subcategory === 'eval_function');
        expect(evalFindings.length).toBe(3);
      });
    });

    describe('Safe content', () => {
      it('should return empty array for normal text', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const text = 'This is a normal string without any obfuscation.';

        const findings = await scanner.scan(text);

        expect(findings).toEqual([]);
      });

      it('should not flag short hex strings', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const text = 'Color: #ff0000';

        const findings = await scanner.scan(text);

        expect(findings).toEqual([]);
      });

      it('should not flag normal base64 in reasonable context', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const text = 'Short: abc123';

        const findings = await scanner.scan(text);

        expect(findings).toEqual([]);
      });
    });

    describe('Edge cases and error handling', () => {
      it('should handle empty string', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const findings = await scanner.scan('');

        expect(findings).toEqual([]);
      });

      it('should throw error for null input', async () => {
        const scanner = new ContentScanner(defaultConfig);

        await expect(scanner.scan(null as any)).rejects.toThrow();
      });

      it('should throw error for non-string input', async () => {
        const scanner = new ContentScanner(defaultConfig);

        await expect(scanner.scan(123 as any)).rejects.toThrow();
      });

      it('should handle very long strings', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const text = 'a'.repeat(10000) + 'eval(1)' + 'b'.repeat(10000);

        const findings = await scanner.scan(text);

        expect(findings.length).toBeGreaterThan(0);
      });

      it('should truncate very long matches', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const text = 'a'.repeat(200);

        const findings = await scanner.scan(text);

        if (findings.length > 0) {
          expect(findings[0].matchedText.length).toBeLessThanOrEqual(103); // 100 + '...'
          expect(findings[0].metadata!.truncated).toBe(true);
        }
      });
    });

    describe('Metadata', () => {
      it('should include metadata in findings', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const text = 'eval("test")';

        const findings = await scanner.scan(text);

        expect(findings[0]).toHaveProperty('metadata');
        expect(findings[0].metadata).toBeDefined();
        expect(findings[0].metadata).toHaveProperty('position');
        expect(findings[0].metadata).toHaveProperty('patternId');
        expect(findings[0].metadata).toHaveProperty('encodingType');
      });

      it('should detect encoding type in metadata', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const text = 'SGVsbG8gV29ybGQhIFRoaXMgaXMgYSBsb25nIGJhc2U2NCBlbmNvZGVkIHN0cmluZy4=';

        const findings = await scanner.scan(text);

        expect(findings[0].metadata!.encodingType).toBe('base64');
      });

      it('should detect invisible characters in metadata', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const text = 'admin\u200Buser';

        const findings = await scanner.scan(text);

        expect(findings[0].metadata!.hasInvisibleChars).toBe(true);
      });

      it('should include correct position for matches', async () => {
        const scanner = new ContentScanner(defaultConfig);
        const text = 'Some text eval(x) more text';

        const findings = await scanner.scan(text);

        expect(findings[0].metadata!.position).toBe(10);
      });
    });
  });
});
