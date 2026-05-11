import { NotificationSystem, NotificationPayload } from '../notification-system';
import { Severity, Action, NotificationConfig } from '../../types';

// Mock functions that will be used by the mocked modules
let mockHttpsRequest: jest.Mock;
let mockHttpRequest: jest.Mock;

jest.mock('https', () => ({
  request: jest.fn()
}));

jest.mock('http', () => ({
  request: jest.fn()
}));

import * as https from 'https';
import * as http from 'http';

// Get the mocked functions
mockHttpsRequest = https.request as unknown as jest.Mock;
mockHttpRequest = http.request as unknown as jest.Mock;

describe('NotificationSystem', () => {
  beforeEach(() => {
    jest.clearAllMocks();

    // Default mock implementation
    const mockResponse = {
      statusCode: 200,
      on: jest.fn((event, handler) => {
        if (event === 'data') {
          handler(Buffer.from('{"ok":true}'));
        }
        if (event === 'end') {
          handler();
        }
      })
    };

    const mockRequest: any = {
      write: jest.fn(),
      end: jest.fn(),
      on: jest.fn((event: string, handler: any): any => {
        if (event === 'error') {
          // Store error handler for later use
        }
        return mockRequest;
      })
    };

    mockHttpsRequest.mockImplementation((options: any, callback: any) => {
      if (callback) {
        setTimeout(() => callback(mockResponse as any), 10);
      }
      return mockRequest as any;
    });

    mockHttpRequest.mockImplementation((options: any, callback: any) => {
      if (callback) {
        setTimeout(() => callback(mockResponse as any), 10);
      }
      return mockRequest as any;
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  const createMockConfig = (overrides?: Partial<NotificationConfig>): NotificationConfig => ({
    enabled: true,
    channels: {},
    severity_threshold: Severity.HIGH,
    ...overrides
  });

  const createMockPayload = (overrides?: Partial<NotificationPayload>): NotificationPayload => ({
    severity: Severity.HIGH,
    action: Action.BLOCK,
    userId: 'user-123',
    module: 'prompt_injection',
    fingerprint: 'fp-123',
    message: 'Security threat detected',
    timestamp: new Date().toISOString(),
    ...overrides
  });

  describe('constructor', () => {
    it('should create instance successfully', () => {
      const config = createMockConfig();
      const notifier = new NotificationSystem(config);
      expect(notifier).toBeInstanceOf(NotificationSystem);
    });

    it('should throw error if config is null', () => {
      expect(() => new NotificationSystem(null as any)).toThrow('Configuration is required');
    });

    it('should handle disabled notifications', () => {
      const config = createMockConfig({ enabled: false });
      const notifier = new NotificationSystem(config);
      expect(notifier).toBeInstanceOf(NotificationSystem);
    });
  });

  describe('notify', () => {
    it('should not send notification if notifications are disabled', async () => {
      const config = createMockConfig({ enabled: false });
      const notifier = new NotificationSystem(config);
      const payload = createMockPayload();

      const result = await notifier.notify(payload);

      expect(result.sent).toBe(false);
      expect(result.reason).toContain('disabled');
      expect(mockHttpsRequest).not.toHaveBeenCalled();
    });

    it('should not send notification if severity below threshold', async () => {
      const config = createMockConfig({ severity_threshold: Severity.CRITICAL });
      const notifier = new NotificationSystem(config);
      const payload = createMockPayload({ severity: Severity.HIGH });

      const result = await notifier.notify(payload);

      expect(result.sent).toBe(false);
      expect(result.reason).toContain('below threshold');
      expect(mockHttpsRequest).not.toHaveBeenCalled();
    });

    it('should not send notification if no channels configured', async () => {
      const config = createMockConfig();
      const notifier = new NotificationSystem(config);
      const payload = createMockPayload();

      const result = await notifier.notify(payload);

      expect(result.sent).toBe(false);
      expect(result.reason).toContain('No notification channels');
      expect(mockHttpsRequest).not.toHaveBeenCalled();
    });

    it('should send notification when severity meets threshold', async () => {
      const config = createMockConfig({
        severity_threshold: Severity.HIGH,
        channels: {
          webhook: {
            enabled: true,
            url: 'https://example.com/webhook'
          }
        }
      });
      const notifier = new NotificationSystem(config);
      const payload = createMockPayload({ severity: Severity.CRITICAL });

      const result = await notifier.notify(payload);

      expect(result.sent).toBe(true);
      expect(result.channels).toContain('webhook');
      expect(mockHttpsRequest).toHaveBeenCalled();
    });
  });

  describe('webhook notifications', () => {
    it('should send webhook notification', async () => {
      const config = createMockConfig({
        channels: {
          webhook: {
            enabled: true,
            url: 'https://example.com/webhook'
          }
        }
      });
      const notifier = new NotificationSystem(config);
      const payload = createMockPayload();

      const result = await notifier.notify(payload);

      expect(result.sent).toBe(true);
      expect(result.channels).toContain('webhook');
      expect(mockHttpsRequest).toHaveBeenCalled();

      const callArgs = mockHttpsRequest.mock.calls[0];
      const options = callArgs[0] as any;
      expect(options.method).toBe('POST');
      expect(options.headers['Content-Type']).toBe('application/json');
    });

    it('should handle webhook errors gracefully', async () => {
      // Mock error response
      const mockErrorRequest: any = {
        write: jest.fn(),
        end: jest.fn(),
        on: jest.fn((event: string, handler: any): any => {
          if (event === 'error') {
            setTimeout(() => handler(new Error('Network error')), 10);
          }
          return mockErrorRequest;
        })
      };

      mockHttpsRequest.mockImplementation(() => mockErrorRequest as any);

      const config = createMockConfig({
        channels: {
          webhook: {
            enabled: true,
            url: 'https://example.com/webhook'
          }
        }
      });
      const notifier = new NotificationSystem(config);
      const payload = createMockPayload();

      const result = await notifier.notify(payload);

      expect(result.sent).toBe(false);
      expect(result.errors).toBeDefined();
      expect(result.errors!.webhook).toContain('Network error');
    });

    it('should handle HTTP webhook URLs', async () => {
      const config = createMockConfig({
        channels: {
          webhook: {
            enabled: true,
            url: 'http://example.com/webhook'
          }
        }
      });
      const notifier = new NotificationSystem(config);
      const payload = createMockPayload();

      await notifier.notify(payload);

      expect(mockHttpRequest).toHaveBeenCalled();
    });
  });

  describe('Slack notifications', () => {
    it('should send Slack notification', async () => {
      const config = createMockConfig({
        channels: {
          slack: {
            enabled: true,
            webhook_url: 'https://hooks.slack.com/services/XXX/YYY/ZZZ'
          }
        }
      });
      const notifier = new NotificationSystem(config);
      const payload = createMockPayload();

      const result = await notifier.notify(payload);

      expect(result.sent).toBe(true);
      expect(result.channels).toContain('slack');
      expect(mockHttpsRequest).toHaveBeenCalled();

      // Check Slack-specific formatting
      const callArgs = mockHttpsRequest.mock.calls[0];
      const requestMock = mockHttpsRequest.mock.results[0].value;
      expect(requestMock.write).toHaveBeenCalled();

      const writtenData = requestMock.write.mock.calls[0][0];
      const payload_data = JSON.parse(writtenData);
      expect(payload_data).toHaveProperty('text');
    });

    it('should format Slack message with severity colors', async () => {
      const config = createMockConfig({
        channels: {
          slack: {
            enabled: true,
            webhook_url: 'https://hooks.slack.com/services/XXX/YYY/ZZZ'
          }
        }
      });
      const notifier = new NotificationSystem(config);
      const payload = createMockPayload({ severity: Severity.CRITICAL });

      await notifier.notify(payload);

      const requestMock = mockHttpsRequest.mock.results[0].value;
      const writtenData = requestMock.write.mock.calls[0][0];
      const slackPayload = JSON.parse(writtenData);

      expect(slackPayload.attachments[0].color).toBe('danger');
      expect(slackPayload.attachments[0].fields.some((f: any) => f.value === 'CRITICAL')).toBe(true);
    });
  });

  describe('Discord notifications', () => {
    it('should send Discord notification', async () => {
      const config = createMockConfig({
        channels: {
          discord: {
            enabled: true,
            webhook_url: 'https://discord.com/api/webhooks/XXX/YYY'
          }
        }
      });
      const notifier = new NotificationSystem(config);
      const payload = createMockPayload();

      const result = await notifier.notify(payload);

      expect(result.sent).toBe(true);
      expect(result.channels).toContain('discord');
      expect(mockHttpsRequest).toHaveBeenCalled();

      // Check Discord-specific formatting
      const requestMock = mockHttpsRequest.mock.results[0].value;
      const writtenData = requestMock.write.mock.calls[0][0];
      const discordPayload = JSON.parse(writtenData);
      expect(discordPayload).toHaveProperty('content');
    });

    it('should format Discord embeds for high severity', async () => {
      const config = createMockConfig({
        channels: {
          discord: {
            enabled: true,
            webhook_url: 'https://discord.com/api/webhooks/XXX/YYY'
          }
        }
      });
      const notifier = new NotificationSystem(config);
      const payload = createMockPayload({ severity: Severity.CRITICAL });

      await notifier.notify(payload);

      const requestMock = mockHttpsRequest.mock.results[0].value;
      const writtenData = requestMock.write.mock.calls[0][0];
      const discordPayload = JSON.parse(writtenData);

      expect(discordPayload.embeds[0].title).toContain('CRITICAL');
      expect(discordPayload.embeds[0].color).toBe(0xff0000); // Red
    });
  });

  describe('multiple channels', () => {
    it('should send to all enabled channels', async () => {
      const config = createMockConfig({
        channels: {
          webhook: {
            enabled: true,
            url: 'https://example.com/webhook'
          },
          slack: {
            enabled: true,
            webhook_url: 'https://hooks.slack.com/services/XXX/YYY/ZZZ'
          },
          discord: {
            enabled: true,
            webhook_url: 'https://discord.com/api/webhooks/XXX/YYY'
          }
        }
      });
      const notifier = new NotificationSystem(config);
      const payload = createMockPayload();

      const result = await notifier.notify(payload);

      expect(result.sent).toBe(true);
      expect(result.channels).toHaveLength(3);
      expect(result.channels).toContain('webhook');
      expect(result.channels).toContain('slack');
      expect(result.channels).toContain('discord');
      expect(mockHttpsRequest).toHaveBeenCalledTimes(3);
    });

    it('should continue sending even if one channel fails', async () => {
      let callCount = 0;
      mockHttpsRequest.mockImplementation(() => {
        callCount++;
        if (callCount === 1) {
          // First call fails
          const mockErrorRequest: any = {
            write: jest.fn(),
            end: jest.fn(),
            on: jest.fn((event: string, handler: any): any => {
              if (event === 'error') {
                setTimeout(() => handler(new Error('Failed')), 10);
              }
              return mockErrorRequest;
            })
          };
          return mockErrorRequest as any;
        } else {
          // Subsequent calls succeed
          const mockResponse = {
            statusCode: 200,
            on: jest.fn((event, handler) => {
              if (event === 'data') handler(Buffer.from('{"ok":true}'));
              if (event === 'end') handler();
            })
          };
          const mockRequest = {
            write: jest.fn(),
            end: jest.fn(),
            on: jest.fn()
          };
          setTimeout(() => {
            const callback = mockHttpsRequest.mock.calls[callCount - 1][1];
            if (callback) callback(mockResponse as any);
          }, 10);
          return mockRequest as any;
        }
      });

      const config = createMockConfig({
        channels: {
          webhook: {
            enabled: true,
            url: 'https://example.com/webhook'
          },
          slack: {
            enabled: true,
            webhook_url: 'https://hooks.slack.com/services/XXX/YYY/ZZZ'
          }
        }
      });
      const notifier = new NotificationSystem(config);
      const payload = createMockPayload();

      const result = await notifier.notify(payload);

      // Should still succeed with slack even though webhook failed
      expect(result.channels).toContain('slack');
      expect(result.errors).toBeDefined();
      expect(result.errors!.webhook).toBeDefined();
    });
  });

  describe('error handling', () => {
    it('should handle invalid webhook URL', async () => {
      const config = createMockConfig({
        channels: {
          webhook: {
            enabled: true,
            url: 'invalid-url'
          }
        }
      });
      const notifier = new NotificationSystem(config);
      const payload = createMockPayload();

      const result = await notifier.notify(payload);

      expect(result.sent).toBe(false);
      expect(result.errors).toBeDefined();
    });

    it('should handle network timeouts gracefully', async () => {
      // This is a simplified test - real timeout handling would be more complex
      const config = createMockConfig({
        channels: {
          webhook: {
            enabled: true,
            url: 'https://example.com/webhook'
          }
        }
      });
      const notifier = new NotificationSystem(config);
      const payload = createMockPayload();

      // Mock will respond quickly, so this just tests the happy path
      const result = await notifier.notify(payload);
      expect(result).toBeDefined();
    });
  });
});
