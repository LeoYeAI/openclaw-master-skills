import { Severity, Action, NotificationConfig } from '../types';
import * as https from 'https';
import * as http from 'http';
import { URL } from 'url';

/**
 * Notification payload
 */
export interface NotificationPayload {
  severity: Severity;
  action: Action;
  userId: string;
  module: string;
  fingerprint: string;
  message: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

/**
 * Result of notification delivery
 */
export interface NotificationResult {
  sent: boolean;
  channels: string[];
  reason?: string;
  errors?: Record<string, string>;
}

/**
 * NotificationSystem handles async delivery of security notifications
 * to various channels (webhook, Slack, Discord).
 *
 * Features:
 * - Multiple channel support (webhook, Slack, Discord)
 * - Async delivery with error handling
 * - Severity threshold filtering
 * - Graceful degradation on channel failures
 *
 * @example
 * ```typescript
 * const notifier = new NotificationSystem(config);
 * const result = await notifier.notify({
 *   severity: Severity.CRITICAL,
 *   action: Action.BLOCK_NOTIFY,
 *   userId: 'user-123',
 *   module: 'prompt_injection',
 *   fingerprint: 'fp-123',
 *   message: 'Critical security threat detected',
 *   timestamp: new Date().toISOString()
 * });
 * ```
 */
export class NotificationSystem {
  private readonly config: NotificationConfig;
  private readonly severityWeight: Record<Severity, number> = {
    [Severity.SAFE]: 0,
    [Severity.LOW]: 1,
    [Severity.MEDIUM]: 2,
    [Severity.HIGH]: 3,
    [Severity.CRITICAL]: 4
  };

  /**
   * Creates a new NotificationSystem instance
   *
   * @param config - Notification configuration
   * @throws Error if config is missing
   */
  constructor(config: NotificationConfig) {
    if (!config) {
      throw new Error('Configuration is required');
    }
    this.config = config;
  }

  /**
   * Send notification to all enabled channels
   *
   * @param payload - Notification payload
   * @returns NotificationResult with delivery status
   */
  async notify(payload: NotificationPayload): Promise<NotificationResult> {
    // Check if notifications are enabled
    if (!this.config.enabled) {
      return {
        sent: false,
        channels: [],
        reason: 'Notifications are disabled in configuration'
      };
    }

    // Check severity threshold
    if (!this.meetsThreshold(payload.severity)) {
      return {
        sent: false,
        channels: [],
        reason: `Severity ${payload.severity} is below threshold ${this.config.severity_threshold}`
      };
    }

    // Collect enabled channels
    const enabledChannels = this.getEnabledChannels();
    if (enabledChannels.length === 0) {
      return {
        sent: false,
        channels: [],
        reason: 'No notification channels are configured or enabled'
      };
    }

    // Send to all channels
    const results = await Promise.allSettled(
      enabledChannels.map(channel => this.sendToChannel(channel, payload))
    );

    // Collect successful channels and errors
    const successfulChannels: string[] = [];
    const errors: Record<string, string> = {};

    results.forEach((result, index) => {
      const channel = enabledChannels[index];
      if (result.status === 'fulfilled' && result.value) {
        successfulChannels.push(channel);
      } else if (result.status === 'rejected') {
        errors[channel] = result.reason?.message || 'Unknown error';
      }
    });

    return {
      sent: successfulChannels.length > 0,
      channels: successfulChannels,
      errors: Object.keys(errors).length > 0 ? errors : undefined
    };
  }

  /**
   * Check if severity meets threshold
   * @private
   */
  private meetsThreshold(severity: Severity): boolean {
    return this.severityWeight[severity] >= this.severityWeight[this.config.severity_threshold];
  }

  /**
   * Get list of enabled channels
   * @private
   */
  private getEnabledChannels(): string[] {
    const channels: string[] = [];

    if (this.config.channels.webhook?.enabled) {
      channels.push('webhook');
    }
    if (this.config.channels.slack?.enabled) {
      channels.push('slack');
    }
    if (this.config.channels.discord?.enabled) {
      channels.push('discord');
    }

    return channels;
  }

  /**
   * Send notification to a specific channel
   * @private
   */
  private async sendToChannel(channel: string, payload: NotificationPayload): Promise<boolean> {
    switch (channel) {
      case 'webhook':
        return this.sendWebhook(payload);
      case 'slack':
        return this.sendSlack(payload);
      case 'discord':
        return this.sendDiscord(payload);
      default:
        throw new Error(`Unknown channel: ${channel}`);
    }
  }

  /**
   * Send generic webhook notification
   * @private
   */
  private async sendWebhook(payload: NotificationPayload): Promise<boolean> {
    const webhookUrl = this.config.channels.webhook?.url;
    if (!webhookUrl) {
      throw new Error('Webhook URL not configured');
    }

    const data = JSON.stringify(payload);

    return this.sendHttpRequest(webhookUrl, data);
  }

  /**
   * Send Slack notification
   * @private
   */
  private async sendSlack(payload: NotificationPayload): Promise<boolean> {
    const webhookUrl = this.config.channels.slack?.webhook_url;
    if (!webhookUrl) {
      throw new Error('Slack webhook URL not configured');
    }

    // Format Slack message
    const slackPayload = {
      text: `*OpenClaw Security Alert*`,
      attachments: [
        {
          color: this.getSeverityColor(payload.severity),
          fields: [
            {
              title: 'Severity',
              value: payload.severity,
              short: true
            },
            {
              title: 'Action',
              value: payload.action,
              short: true
            },
            {
              title: 'Module',
              value: payload.module,
              short: true
            },
            {
              title: 'User ID',
              value: payload.userId,
              short: true
            },
            {
              title: 'Message',
              value: payload.message,
              short: false
            },
            {
              title: 'Fingerprint',
              value: payload.fingerprint,
              short: false
            }
          ],
          footer: 'OpenClaw Security Suite',
          ts: Math.floor(new Date(payload.timestamp).getTime() / 1000)
        }
      ]
    };

    const data = JSON.stringify(slackPayload);
    return this.sendHttpRequest(webhookUrl, data);
  }

  /**
   * Send Discord notification
   * @private
   */
  private async sendDiscord(payload: NotificationPayload): Promise<boolean> {
    const webhookUrl = this.config.channels.discord?.webhook_url;
    if (!webhookUrl) {
      throw new Error('Discord webhook URL not configured');
    }

    // Format Discord message
    const discordPayload = {
      content: `**OpenClaw Security Alert**`,
      embeds: [
        {
          title: `${payload.severity} Severity Event`,
          description: payload.message,
          color: this.getDiscordColor(payload.severity),
          fields: [
            {
              name: 'Severity',
              value: payload.severity,
              inline: true
            },
            {
              name: 'Action',
              value: payload.action,
              inline: true
            },
            {
              name: 'Module',
              value: payload.module,
              inline: true
            },
            {
              name: 'User ID',
              value: payload.userId,
              inline: true
            },
            {
              name: 'Fingerprint',
              value: payload.fingerprint,
              inline: false
            }
          ],
          timestamp: payload.timestamp,
          footer: {
            text: 'OpenClaw Security Suite'
          }
        }
      ]
    };

    const data = JSON.stringify(discordPayload);
    return this.sendHttpRequest(webhookUrl, data);
  }

  /**
   * Send HTTP request to webhook URL
   * @private
   */
  private async sendHttpRequest(url: string, data: string): Promise<boolean> {
    return new Promise((resolve, reject) => {
      try {
        const parsedUrl = new URL(url);
        const httpModule = parsedUrl.protocol === 'https:' ? https : http;

        const options = {
          hostname: parsedUrl.hostname,
          port: parsedUrl.port || (parsedUrl.protocol === 'https:' ? 443 : 80),
          path: parsedUrl.pathname + parsedUrl.search,
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Content-Length': Buffer.byteLength(data)
          }
        };

        const req = httpModule.request(options, (res) => {
          let responseData = '';

          res.on('data', (chunk) => {
            responseData += chunk;
          });

          res.on('end', () => {
            if (res.statusCode && res.statusCode >= 200 && res.statusCode < 300) {
              resolve(true);
            } else {
              reject(new Error(`HTTP ${res.statusCode}: ${responseData}`));
            }
          });
        });

        req.on('error', (error) => {
          reject(error);
        });

        req.write(data);
        req.end();
      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * Get Slack color for severity
   * @private
   */
  private getSeverityColor(severity: Severity): string {
    switch (severity) {
      case Severity.CRITICAL:
        return 'danger'; // Red
      case Severity.HIGH:
        return 'danger'; // Red
      case Severity.MEDIUM:
        return 'warning'; // Orange
      case Severity.LOW:
        return 'good'; // Green
      case Severity.SAFE:
        return 'good'; // Green
      default:
        return '#cccccc'; // Gray
    }
  }

  /**
   * Get Discord color (decimal) for severity
   * @private
   */
  private getDiscordColor(severity: Severity): number {
    switch (severity) {
      case Severity.CRITICAL:
        return 0xff0000; // Red
      case Severity.HIGH:
        return 0xff6600; // Orange-red
      case Severity.MEDIUM:
        return 0xffaa00; // Orange
      case Severity.LOW:
        return 0xffdd00; // Yellow
      case Severity.SAFE:
        return 0x00ff00; // Green
      default:
        return 0xcccccc; // Gray
    }
  }
}
