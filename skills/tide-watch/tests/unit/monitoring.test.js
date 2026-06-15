const {
  parseMonitoringConfig,
  checkThresholdCrossed,
  generateWarningMessage,
  shouldTriggerBackup,
  generateResetPrompt
} = require('../../lib/monitoring');

const fs = require('fs');
const path = require('path');

describe('parseMonitoringConfig', () => {
  test('should parse default configuration', () => {
    const content = `
## 🌊 TIDE WATCH: Context Window Monitoring

**Monitoring schedule:**
- Check frequency: **Every 1 hour**

**Warning thresholds:**
- **75%**: 🟡 Warning
- **85%**: 🟠 Elevated
- **90%**: 🔴 High
- **95%**: 🚨 Critical

**Auto-backup:**
- Enabled: true
- Trigger at thresholds: [90, 95]
- Retention: 7 days
- Compress: false
    `;

    const config = parseMonitoringConfig(content);

    expect(config.checkFrequency).toBe(60);
    expect(config.thresholds).toEqual([75, 85, 90, 95]);
    expect(config.autoBackup.enabled).toBe(true);
    expect(config.autoBackup.triggerAt).toEqual([90, 95]);
    expect(config.autoBackup.retention).toBe(7);
    expect(config.autoBackup.compress).toBe(false);
  });

  test('should parse custom check frequency in minutes', () => {
    const content = 'Check frequency: **Every 30 minutes**';
    const config = parseMonitoringConfig(content);
    expect(config.checkFrequency).toBe(30);
  });

  test('should parse custom check frequency in hours', () => {
    const content = 'Check frequency: **Every 2 hours**';
    const config = parseMonitoringConfig(content);
    expect(config.checkFrequency).toBe(120);
  });

  test('should handle manual mode', () => {
    const content = 'Check frequency: **manual**';
    const config = parseMonitoringConfig(content);
    expect(config.checkFrequency).toBeNull();
  });

  test('should parse custom thresholds', () => {
    const content = `
**Warning thresholds:**
- **60%**: 🟡 Early warning
- **80%**: 🟠 Warning
- **95%**: 🚨 Critical
    `;
    const config = parseMonitoringConfig(content);
    expect(config.thresholds).toEqual([60, 80, 95]);
  });

  test('should parse backup disabled', () => {
    const content = 'Enabled: false';
    const config = parseMonitoringConfig(content);
    expect(config.autoBackup.enabled).toBe(false);
  });

  test('should parse backup compress enabled', () => {
    const content = 'Compress: true';
    const config = parseMonitoringConfig(content);
    expect(config.autoBackup.compress).toBe(true);
  });

  test('should use defaults for missing values', () => {
    const content = '';
    const config = parseMonitoringConfig(content);
    
    expect(config.checkFrequency).toBe(60);
    expect(config.thresholds).toEqual([75, 85, 90, 95]);
    expect(config.autoBackup.enabled).toBe(true);
  });
});

describe('checkThresholdCrossed', () => {
  const thresholds = [75, 85, 90, 95];

  test('should return threshold when crossed for first time', () => {
    expect(checkThresholdCrossed(76, thresholds, [])).toBe(75);
    expect(checkThresholdCrossed(86, thresholds, [])).toBe(85);
    expect(checkThresholdCrossed(91, thresholds, [])).toBe(90);
    expect(checkThresholdCrossed(96, thresholds, [])).toBe(95);
  });

  test('should return highest crossed threshold', () => {
    expect(checkThresholdCrossed(92, thresholds, [])).toBe(90);
  });

  test('should return null if threshold already warned', () => {
    expect(checkThresholdCrossed(76, thresholds, [75])).toBeNull();
    expect(checkThresholdCrossed(86, thresholds, [75, 85])).toBeNull();
  });

  test('should return next threshold when capacity increases', () => {
    expect(checkThresholdCrossed(91, thresholds, [75, 85])).toBe(90);
  });

  test('should return null when below all thresholds', () => {
    expect(checkThresholdCrossed(50, thresholds, [])).toBeNull();
    expect(checkThresholdCrossed(74, thresholds, [])).toBeNull();
  });

  test('should handle exact threshold values', () => {
    expect(checkThresholdCrossed(75, thresholds, [])).toBe(75);
    expect(checkThresholdCrossed(90, thresholds, [75, 85])).toBe(90);
  });
});

describe('generateWarningMessage', () => {
  const thresholds = [75, 85, 90, 95];

  test('should generate first threshold warning', () => {
    const message = generateWarningMessage(75, thresholds, 150000, 200000);
    expect(message).toContain('🟡');
    expect(message).toContain('75%');
    expect(message).toContain('150,000');
    expect(message).toContain('Consider wrapping up');
  });

  test('should generate middle threshold warning', () => {
    const message = generateWarningMessage(85, thresholds, 170000, 200000);
    expect(message).toContain('🟠');
    expect(message).toContain('85%');
  });

  test('should generate second-to-last threshold warning', () => {
    const message = generateWarningMessage(90, thresholds, 180000, 200000);
    expect(message).toContain('🔴');
    expect(message).toContain('90%');
    expect(message).toContain('Session will lock soon');
  });

  test('should generate critical threshold warning', () => {
    const message = generateWarningMessage(95, thresholds, 190000, 200000);
    expect(message).toContain('🚨');
    expect(message).toContain('CRITICAL');
    expect(message).toContain('95%');
    expect(message).toContain('NOW');
  });

  test('should include channel when provided', () => {
    const message = generateWarningMessage(75, thresholds, 150000, 200000, 'discord/#test');
    expect(message).toContain('discord/#test');
  });

  test('should format token numbers with commas', () => {
    const message = generateWarningMessage(75, thresholds, 150000, 200000);
    expect(message).toMatch(/150,000/);
    expect(message).toMatch(/200,000/);
  });
});

describe('shouldTriggerBackup', () => {
  const backupConfig = {
    enabled: true,
    triggerAt: [90, 95],
    retention: 7,
    compress: false
  };

  test('should trigger backup when threshold crossed', () => {
    expect(shouldTriggerBackup(91, backupConfig, [])).toBe(90);
    expect(shouldTriggerBackup(96, backupConfig, [])).toBe(95);
  });

  test('should return highest crossed trigger', () => {
    expect(shouldTriggerBackup(96, backupConfig, [])).toBe(95);
  });

  test('should not trigger if already backed up', () => {
    expect(shouldTriggerBackup(91, backupConfig, [90])).toBeNull();
    expect(shouldTriggerBackup(96, backupConfig, [90, 95])).toBeNull();
  });

  test('should return null when backups disabled', () => {
    const disabledConfig = { ...backupConfig, enabled: false };
    expect(shouldTriggerBackup(96, disabledConfig, [])).toBeNull();
  });

  test('should return null when below all triggers', () => {
    expect(shouldTriggerBackup(85, backupConfig, [])).toBeNull();
  });

  test('should trigger next threshold when capacity increases', () => {
    expect(shouldTriggerBackup(96, backupConfig, [90])).toBe(95);
  });
});

describe('generateResetPrompt', () => {
  test('should generate basic reset prompt', () => {
    const prompt = generateResetPrompt('test-session-123');
    expect(prompt).toContain('Session Reset');
    expect(prompt).toContain('Before resetting');
    expect(prompt).toContain('Save current work');
    expect(prompt).toContain('New session, please');
  });

  test('should include channel alternative when session data provided', () => {
    const sessionData = {
      channel: 'discord/#test',
      percentage: 90
    };
    const prompt = generateResetPrompt('test-session-123', sessionData);
    expect(prompt).toContain('Alternative');
    expect(prompt).toContain('discord/#test');
    expect(prompt).toContain('90%');
  });

  test('should include memory instructions', () => {
    const prompt = generateResetPrompt('test-session-123');
    expect(prompt).toContain('memory/YYYY-MM-DD.md');
    expect(prompt).toContain('After reset');
  });
});
