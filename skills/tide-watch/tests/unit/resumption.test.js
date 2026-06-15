const fs = require('fs');
const path = require('path');
const os = require('os');
const {
  getResumePromptPath,
  getDefaultResumePromptPath,
  hasResumePrompt,
  loadResumePrompt,
  saveResumePrompt,
  deleteResumePrompt,
  listResumePrompts,
  generateResumePromptTemplate,
  getResumePromptInfo
} = require('../../lib/resumption');

// Use temp directory for tests
const TEST_RESUME_DIR = path.join(os.tmpdir(), 'tide-watch-test-restore');

describe('getResumePromptPath', () => {
  test('should return correct path for session', () => {
    const sessionId = 'test-session-123';
    const promptPath = getResumePromptPath(sessionId, TEST_RESUME_DIR);
    expect(promptPath).toBe(path.join(TEST_RESUME_DIR, 'test-session-123.md'));
  });
});

describe('getDefaultResumePromptPath', () => {
  test('should return correct path for default prompt', () => {
    const promptPath = getDefaultResumePromptPath(TEST_RESUME_DIR);
    expect(promptPath).toBe(path.join(TEST_RESUME_DIR, 'default.md'));
  });
});

describe('hasResumePrompt', () => {
  beforeEach(() => {
    // Clean up test directory
    if (fs.existsSync(TEST_RESUME_DIR)) {
      fs.rmSync(TEST_RESUME_DIR, { recursive: true });
    }
    fs.mkdirSync(TEST_RESUME_DIR, { recursive: true });
  });

  afterEach(() => {
    // Clean up
    if (fs.existsSync(TEST_RESUME_DIR)) {
      fs.rmSync(TEST_RESUME_DIR, { recursive: true });
    }
  });

  test('should return false when prompt does not exist', () => {
    expect(hasResumePrompt('test-session', TEST_RESUME_DIR)).toBe(false);
  });

  test('should return true when prompt exists', () => {
    const sessionId = 'test-session';
    const promptPath = getResumePromptPath(sessionId, TEST_RESUME_DIR);
    fs.writeFileSync(promptPath, 'Test prompt', 'utf8');
    
    expect(hasResumePrompt(sessionId, TEST_RESUME_DIR)).toBe(true);
  });
});

describe('loadResumePrompt', () => {
  beforeEach(() => {
    if (fs.existsSync(TEST_RESUME_DIR)) {
      fs.rmSync(TEST_RESUME_DIR, { recursive: true });
    }
    fs.mkdirSync(TEST_RESUME_DIR, { recursive: true });
  });

  afterEach(() => {
    if (fs.existsSync(TEST_RESUME_DIR)) {
      fs.rmSync(TEST_RESUME_DIR, { recursive: true });
    }
  });

  test('should return null when prompt does not exist', () => {
    expect(loadResumePrompt('test-session', TEST_RESUME_DIR)).toBeNull();
  });

  test('should load session-specific prompt', () => {
    const sessionId = 'test-session';
    const content = '# Test Prompt\nSession-specific content';
    const promptPath = getResumePromptPath(sessionId, TEST_RESUME_DIR);
    fs.writeFileSync(promptPath, content, 'utf8');
    
    expect(loadResumePrompt(sessionId, TEST_RESUME_DIR)).toBe(content);
  });

  test('should fall back to default prompt', () => {
    const sessionId = 'test-session';
    const defaultContent = '# Default Prompt\nDefault content';
    const defaultPath = getDefaultResumePromptPath(TEST_RESUME_DIR);
    fs.writeFileSync(defaultPath, defaultContent, 'utf8');
    
    expect(loadResumePrompt(sessionId, TEST_RESUME_DIR)).toBe(defaultContent);
  });

  test('should prefer session-specific over default', () => {
    const sessionId = 'test-session';
    const sessionContent = '# Session Prompt';
    const defaultContent = '# Default Prompt';
    
    fs.writeFileSync(getResumePromptPath(sessionId, TEST_RESUME_DIR), sessionContent, 'utf8');
    fs.writeFileSync(getDefaultResumePromptPath(TEST_RESUME_DIR), defaultContent, 'utf8');
    
    expect(loadResumePrompt(sessionId, TEST_RESUME_DIR)).toBe(sessionContent);
  });
});

describe('saveResumePrompt', () => {
  beforeEach(() => {
    if (fs.existsSync(TEST_RESUME_DIR)) {
      fs.rmSync(TEST_RESUME_DIR, { recursive: true });
    }
  });

  afterEach(() => {
    if (fs.existsSync(TEST_RESUME_DIR)) {
      fs.rmSync(TEST_RESUME_DIR, { recursive: true });
    }
  });

  test('should create directory if it does not exist', () => {
    const sessionId = 'test-session';
    const content = 'Test content';
    
    saveResumePrompt(sessionId, content, TEST_RESUME_DIR);
    
    expect(fs.existsSync(TEST_RESUME_DIR)).toBe(true);
  });

  test('should save resumption prompt', () => {
    const sessionId = 'test-session';
    const content = 'Test content';
    
    saveResumePrompt(sessionId, content, TEST_RESUME_DIR);
    
    const promptPath = getResumePromptPath(sessionId, TEST_RESUME_DIR);
    expect(fs.existsSync(promptPath)).toBe(true);
    expect(fs.readFileSync(promptPath, 'utf8')).toBe(content);
  });
});

describe('deleteResumePrompt', () => {
  beforeEach(() => {
    if (fs.existsSync(TEST_RESUME_DIR)) {
      fs.rmSync(TEST_RESUME_DIR, { recursive: true });
    }
    fs.mkdirSync(TEST_RESUME_DIR, { recursive: true });
  });

  afterEach(() => {
    if (fs.existsSync(TEST_RESUME_DIR)) {
      fs.rmSync(TEST_RESUME_DIR, { recursive: true });
    }
  });

  test('should return false when prompt does not exist', () => {
    expect(deleteResumePrompt('test-session', TEST_RESUME_DIR)).toBe(false);
  });

  test('should delete existing prompt and return true', () => {
    const sessionId = 'test-session';
    const promptPath = getResumePromptPath(sessionId, TEST_RESUME_DIR);
    fs.writeFileSync(promptPath, 'Test content', 'utf8');
    
    expect(deleteResumePrompt(sessionId, TEST_RESUME_DIR)).toBe(true);
    expect(fs.existsSync(promptPath)).toBe(false);
  });
});

describe('listResumePrompts', () => {
  beforeEach(() => {
    if (fs.existsSync(TEST_RESUME_DIR)) {
      fs.rmSync(TEST_RESUME_DIR, { recursive: true });
    }
    fs.mkdirSync(TEST_RESUME_DIR, { recursive: true });
  });

  afterEach(() => {
    if (fs.existsSync(TEST_RESUME_DIR)) {
      fs.rmSync(TEST_RESUME_DIR, { recursive: true });
    }
  });

  test('should return empty array when directory does not exist', () => {
    fs.rmSync(TEST_RESUME_DIR, { recursive: true });
    expect(listResumePrompts(TEST_RESUME_DIR)).toEqual([]);
  });

  test('should return empty array when no prompts exist', () => {
    expect(listResumePrompts(TEST_RESUME_DIR)).toEqual([]);
  });

  test('should list all resumption prompts', () => {
    fs.writeFileSync(path.join(TEST_RESUME_DIR, 'session1.md'), 'Content 1', 'utf8');
    fs.writeFileSync(path.join(TEST_RESUME_DIR, 'session2.md'), 'Content 2', 'utf8');
    fs.writeFileSync(path.join(TEST_RESUME_DIR, 'default.md'), 'Default', 'utf8');
    
    const prompts = listResumePrompts(TEST_RESUME_DIR);
    
    expect(prompts).toHaveLength(3);
    expect(prompts.map(p => p.sessionId).sort()).toEqual(['default', 'session1', 'session2']);
  });

  test('should include metadata for each prompt', () => {
    fs.writeFileSync(path.join(TEST_RESUME_DIR, 'session1.md'), 'Content', 'utf8');
    
    const prompts = listResumePrompts(TEST_RESUME_DIR);
    
    expect(prompts[0]).toHaveProperty('sessionId');
    expect(prompts[0]).toHaveProperty('path');
    expect(prompts[0]).toHaveProperty('size');
    expect(prompts[0]).toHaveProperty('modified');
  });

  test('should ignore non-markdown files', () => {
    fs.writeFileSync(path.join(TEST_RESUME_DIR, 'session1.md'), 'Content', 'utf8');
    fs.writeFileSync(path.join(TEST_RESUME_DIR, 'other.txt'), 'Other', 'utf8');
    
    const prompts = listResumePrompts(TEST_RESUME_DIR);
    
    expect(prompts).toHaveLength(1);
    expect(prompts[0].sessionId).toBe('session1');
  });
});

describe('generateResumePromptTemplate', () => {
  test('should generate template with session ID', () => {
    const template = generateResumePromptTemplate('test-session-123');
    
    expect(template).toContain('test-session-123');
    expect(template).toContain('# Session Restoration Prompt');
  });

  test('should include all template sections', () => {
    const template = generateResumePromptTemplate('test-session');
    
    expect(template).toContain('Project Context');
    expect(template).toContain('Technical Details');
    expect(template).toContain('Current Focus');
    expect(template).toContain('Important Files');
    expect(template).toContain('Active Work');
    expect(template).toContain('Team & Communication');
    expect(template).toContain('Custom Instructions');
  });
});

describe('getResumePromptInfo', () => {
  beforeEach(() => {
    if (fs.existsSync(TEST_RESUME_DIR)) {
      fs.rmSync(TEST_RESUME_DIR, { recursive: true });
    }
    fs.mkdirSync(TEST_RESUME_DIR, { recursive: true });
  });

  afterEach(() => {
    if (fs.existsSync(TEST_RESUME_DIR)) {
      fs.rmSync(TEST_RESUME_DIR, { recursive: true });
    }
  });

  test('should return null when prompt does not exist', () => {
    expect(getResumePromptInfo('test-session', TEST_RESUME_DIR)).toBeNull();
  });

  test('should return metadata for existing prompt', () => {
    const sessionId = 'test-session';
    const content = '# Test\nLine 2\nLine 3';
    const promptPath = getResumePromptPath(sessionId, TEST_RESUME_DIR);
    fs.writeFileSync(promptPath, content, 'utf8');
    
    const info = getResumePromptInfo(sessionId, TEST_RESUME_DIR);
    
    expect(info).toBeDefined();
    expect(info.sessionId).toBe(sessionId);
    expect(info.lines).toBe(3);
    expect(info.estimatedTokens).toBeGreaterThan(0);
  });

  test('should estimate tokens correctly', () => {
    const sessionId = 'test-session';
    const content = 'a'.repeat(400); // 400 characters ≈ 100 tokens
    const promptPath = getResumePromptPath(sessionId, TEST_RESUME_DIR);
    fs.writeFileSync(promptPath, content, 'utf8');
    
    const info = getResumePromptInfo(sessionId, TEST_RESUME_DIR);
    
    expect(info.estimatedTokens).toBe(100);
  });
});
