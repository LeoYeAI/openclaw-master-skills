import { describe, it, expect } from '@jest/globals';
import { SerializationDetector } from '../detector';
import { ModuleConfig } from '../../../types';

describe('SerializationDetector', () => {
  const defaultConfig: ModuleConfig = {
    enabled: true
  };

  describe('constructor', () => {
    it('should create an instance with valid config', () => {
      const detector = new SerializationDetector(defaultConfig);
      expect(detector).toBeInstanceOf(SerializationDetector);
    });

    it('should throw error if config is invalid', () => {
      expect(() => new SerializationDetector(null as any)).toThrow();
    });
  });

  describe('scan', () => {
    describe('Java serialization', () => {
      it('should detect base64-encoded Java serialized object', async () => {
        const detector = new SerializationDetector(defaultConfig);
        const text = 'rO0ABXNyABFqYXZhLnV0aWwuSGFzaE1hcA==';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'java_serialized_base64')).toBe(true);
      });

      it('should detect hex-encoded Java serialized object', async () => {
        const detector = new SerializationDetector(defaultConfig);
        const text = 'aced00057372001164656d6f2e4d61696e436c617373';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'java_serialized_hex')).toBe(true);
      });

      it('should detect ObjectInputStream usage', async () => {
        const detector = new SerializationDetector(defaultConfig);
        const text = 'new ObjectInputStream(input).readObject()';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'java_objectinputstream')).toBe(true);
      });

      it('should detect Java gadget chain classes', async () => {
        const detector = new SerializationDetector(defaultConfig);
        const text = 'org.apache.commons.collections.functors.InvokerTransformer';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'java_gadget_chains')).toBe(true);
      });
    });

    describe('PHP serialization', () => {
      it('should detect PHP serialized object notation', async () => {
        const detector = new SerializationDetector(defaultConfig);
        const text = 'O:8:"stdClass":1:{s:4:"name";s:4:"test";}';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'php_serialized_object')).toBe(true);
      });

      it('should detect unserialize() call', async () => {
        const detector = new SerializationDetector(defaultConfig);
        const text = 'unserialize($user_input)';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'php_unserialize')).toBe(true);
      });
    });

    describe('Python pickle', () => {
      it('should detect pickle.loads()', async () => {
        const detector = new SerializationDetector(defaultConfig);
        const text = 'pickle.loads(user_data)';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'python_pickle_loads')).toBe(true);
      });

      it('should detect pickle magic bytes', async () => {
        const detector = new SerializationDetector(defaultConfig);
        const text = '\\x80\\x03cposix\\nsystem\\n';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'python_pickle_magic')).toBe(true);
      });
    });

    describe('YAML unsafe tags', () => {
      it('should detect !!python/object tag', async () => {
        const detector = new SerializationDetector(defaultConfig);
        const text = '!!python/object/apply:os.system ["id"]';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'yaml_unsafe_tags')).toBe(true);
      });

      it('should detect !!ruby/object tag', async () => {
        const detector = new SerializationDetector(defaultConfig);
        const text = '!!ruby/object:Gem::Installer';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'yaml_unsafe_tags')).toBe(true);
      });
    });

    describe('.NET serialization', () => {
      it('should detect BinaryFormatter', async () => {
        const detector = new SerializationDetector(defaultConfig);
        const text = 'new BinaryFormatter().Deserialize(stream)';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'dotnet_binaryformatter')).toBe(true);
      });

      it('should detect TypeNameHandling', async () => {
        const detector = new SerializationDetector(defaultConfig);
        const text = 'TypeNameHandling = TypeNameHandling.All';

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'dotnet_typenamehandling')).toBe(true);
      });

      it('should detect __VIEWSTATE', async () => {
        const detector = new SerializationDetector(defaultConfig);
        const text = '__VIEWSTATE=' + 'A'.repeat(60);

        const findings = await detector.scan(text);

        expect(findings.length).toBeGreaterThan(0);
        expect(findings.some(f => f.pattern.subcategory === 'dotnet_viewstate')).toBe(true);
      });
    });

    describe('Safe inputs', () => {
      it('should return empty array for safe text', async () => {
        const detector = new SerializationDetector(defaultConfig);
        const text = 'This is a normal JSON: {"name": "John", "age": 30}';

        const findings = await detector.scan(text);

        expect(findings).toEqual([]);
      });

      it('should return empty array for empty string', async () => {
        const detector = new SerializationDetector(defaultConfig);
        const findings = await detector.scan('');

        expect(findings).toEqual([]);
      });
    });

    describe('Error handling', () => {
      it('should throw error for null input', async () => {
        const detector = new SerializationDetector(defaultConfig);

        await expect(detector.scan(null as any)).rejects.toThrow();
      });

      it('should throw error for non-string input', async () => {
        const detector = new SerializationDetector(defaultConfig);

        await expect(detector.scan(123 as any)).rejects.toThrow();
      });
    });

    describe('Metadata', () => {
      it('should include metadata in findings', async () => {
        const detector = new SerializationDetector(defaultConfig);
        const text = 'rO0ABXNyABFqYXZhLnV0aWwuSGFzaE1hcA==';

        const findings = await detector.scan(text);

        expect(findings[0]).toHaveProperty('metadata');
        expect(findings[0].metadata).toBeDefined();
        expect(findings[0].metadata).toHaveProperty('patternId');
        expect(findings[0].metadata).toHaveProperty('category');
      });
    });
  });
});
