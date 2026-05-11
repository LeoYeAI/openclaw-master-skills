/**
 * Security Scanner — API wrapper for Claw0x Gateway
 * Free skill that calls Claw0x Gateway for security scanning
 * Requires CLAW0X_API_KEY but costs nothing to use
 */

// Environment variable access wrapper
function env(key: string): string {
  if (typeof process !== 'undefined' && process.env) {
    return process.env[key] || '';
  }
  return '';
}

interface ScanInput {
  repo_url?: string;
  skill_slug?: string;
  code?: string;
  dependencies?: Record<string, string>;
  skill_md?: string;
}

interface ScanOutput {
  overall_risk: string;
  risk_score: number;
  input_mode: string;
  repo_url: string | null;
  dependency_scan: {
    packages_scanned: number;
    vulnerabilities: Array<{
      id: string;
      summary: string;
      severity: string;
      package_name: string;
      package_version: string;
    }>;
    vulnerability_counts: {
      critical: number;
      high: number;
      medium: number;
      low: number;
    };
  };
  code_scan: {
    findings: Array<{
      rule_id: string;
      name: string;
      severity: string;
      file: string;
      line: number;
      match: string;
      description: string;
    }>;
    finding_counts: {
      critical: number;
      high: number;
      medium: number;
      low: number;
    };
    rules_checked: number;
  };
  permission_audit: {
    declared_permissions: string[];
    detected_permissions: string[];
    undeclared_risks: string[];
  };
  recommendations: string[];
  scanned_at: string;
  scan_duration_ms: number;
}

export async function run(input: ScanInput): Promise<ScanOutput> {
  // Get API key
  const apiKey = env('CLAW0X_API_KEY');
  
  if (!apiKey) {
    throw new Error(
      'CLAW0X_API_KEY is required. Get your key at https://claw0x.com\n' +
      'Sign up → Dashboard → Create API Key → Set as environment variable'
    );
  }
  
  // Validate input
  const modes = ['repo_url', 'skill_slug', 'code'];
  const provided = modes.filter(m => input[m as keyof ScanInput] !== undefined && input[m as keyof ScanInput] !== null && input[m as keyof ScanInput] !== '');
  
  if (provided.length === 0) {
    throw new Error('Exactly one of repo_url, skill_slug, or code must be provided');
  }
  
  if (provided.length > 1) {
    throw new Error('Input fields are mutually exclusive: provide exactly one');
  }
  
  // Call Claw0x Gateway API
  const response = await fetch('https://api.claw0x.com/v1/call', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      skill: 'security-scanner',
      input
    })
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ 
      error: response.statusText 
    }));
    throw new Error(
      `Claw0x API error (${response.status}): ${error.error || response.statusText}`
    );
  }
  
  return await response.json();
}

export default run;
