export type VulnerabilitySource = 'npm-audit' | 'pip-audit' | 'osv' | 'nvd' | 'github' | 'sast' | 'dast';

export type SeverityLevel = 'critical' | 'high' | 'medium' | 'low' | 'info';

export interface Vulnerability {
  id: string;
  source: VulnerabilitySource;
  severity: SeverityLevel;
  package: string;
  version: string;
  fixed_version?: string;
  title: string;
  description: string;
  references: string[];
  discovered_at: string;
}

export interface ScanReport {
  scan_id: string;
  timestamp: string;
  target: string;
  vulnerabilities: Vulnerability[];
  summary: {
    critical: number;
    high: number;
    medium: number;
    low: number;
    info: number;
  };
}

export type HookEvent = {
  type?: string;
  action?: string;
  messages?: Array<{
    role: string;
    content: string;
  }>;
};

export type HookContext = {
  skillPath?: string;
  agentPlatform?: string;
  [key: string]: unknown;
};
