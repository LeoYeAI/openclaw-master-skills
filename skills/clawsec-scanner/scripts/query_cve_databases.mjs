import { normalizeSeverity, getTimestamp, uniqueStrings } from '../lib/utils.mjs';

/**
 * Query OSV API for vulnerability data.
 * OSV is the primary CVE source (free, no auth, broad ecosystem support).
 *
 * @param {string} packageName - Package name (e.g., 'lodash')
 * @param {string} ecosystem - Ecosystem identifier (e.g., 'npm', 'PyPI')
 * @param {string} [version] - Optional specific version to check
 * @returns {Promise<import('../lib/types.ts').Vulnerability[]>}
 */
export async function queryOSV(packageName, ecosystem, version = undefined) {
  const url = 'https://api.osv.dev/v1/query';

  const requestBody = {
    package: {
      name: packageName,
      ecosystem: ecosystem,
    },
  };

  if (version) {
    requestBody.version = version;
  }

  try {
    const controller = new globalThis.AbortController();
    const timeout = globalThis.setTimeout(() => controller.abort(), 10000);

    const response = await globalThis.fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody),
      signal: controller.signal,
    });

    globalThis.clearTimeout(timeout);

    if (!response.ok) {
      console.warn(`OSV API returned status ${response.status} for ${packageName}`);
      return [];
    }

    const data = await response.json();
    const vulns = data.vulns || [];

    return vulns.map((vuln) => normalizeOSVVulnerability(vuln, packageName, version || '*'));
  } catch (error) {
    if (error instanceof Error) {
      console.warn(`OSV API error for ${packageName}: ${error.message}`);
    }
    return [];
  }
}

/**
 * Query NVD API 2.0 for CVE data.
 * Gated behind CLAWSEC_NVD_API_KEY environment variable.
 * Enforces 6-second rate limiting without API key.
 *
 * @param {string} cveId - CVE identifier (e.g., 'CVE-2023-12345')
 * @returns {Promise<import('../lib/types.ts').Vulnerability | null>}
 */
export async function queryNVD(cveId) {
  const apiKey = process.env.CLAWSEC_NVD_API_KEY;
  const url = `https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=${cveId}`;

  const headers = {};
  if (apiKey) {
    headers['apiKey'] = apiKey;
  }

  try {
    const controller = new globalThis.AbortController();
    const timeout = globalThis.setTimeout(() => controller.abort(), 15000);

    const response = await globalThis.fetch(url, {
      method: 'GET',
      headers,
      signal: controller.signal,
    });

    globalThis.clearTimeout(timeout);

    // Rate limiting: 6-second delay required WITHOUT API key
    if (!apiKey) {
      await new Promise((r) => globalThis.setTimeout(r, 6000));
    }

    if (!response.ok) {
      console.warn(`NVD API returned status ${response.status} for ${cveId}`);
      return null;
    }

    const data = await response.json();

    if (!data.vulnerabilities || data.vulnerabilities.length === 0) {
      return null;
    }

    const cveItem = data.vulnerabilities[0].cve;
    return normalizeNVDVulnerability(cveItem);
  } catch (error) {
    if (error instanceof Error) {
      console.warn(`NVD API error for ${cveId}: ${error.message}`);
    }
    return null;
  }
}

/**
 * Query GitHub Advisory Database (optional - requires OAuth token).
 * Currently a placeholder for future implementation.
 *
 * @param {string} _packageName - Package name
 * @param {string} _ecosystem - Ecosystem (e.g., 'npm', 'pip')
 * @returns {Promise<import('../lib/types.ts').Vulnerability[]>}
 */
export async function queryGitHub(_packageName, _ecosystem) {
  const token = process.env.GITHUB_TOKEN;

  if (!token) {
    console.warn('GitHub Advisory Database query skipped: GITHUB_TOKEN not set');
    return [];
  }

  // TODO: Implement GitHub GraphQL advisory query
  // This requires GraphQL API integration with oauth token
  // Placeholder for future enhancement
  console.warn('GitHub Advisory Database integration not yet implemented');
  return [];
}

/**
 * Normalize OSV vulnerability data to unified schema.
 *
 * @param {any} osvVuln - Raw OSV vulnerability object
 * @param {string} packageName - Package name
 * @param {string} version - Package version
 * @returns {import('../lib/types.ts').Vulnerability}
 */
function normalizeOSVVulnerability(osvVuln, packageName, version) {
  const id = osvVuln.id || 'UNKNOWN';
  const summary = osvVuln.summary || 'No description available';
  const details = osvVuln.details || summary;

  // Extract severity from database_specific or severity array
  let severity = 'info';
  if (osvVuln.severity && Array.isArray(osvVuln.severity) && osvVuln.severity.length > 0) {
    severity = normalizeSeverity(osvVuln.severity[0].type || 'info');
  } else if (osvVuln.database_specific && osvVuln.database_specific.severity) {
    severity = normalizeSeverity(osvVuln.database_specific.severity);
  }

  // Extract references
  const references = [];
  if (Array.isArray(osvVuln.references)) {
    references.push(...osvVuln.references.map((ref) => ref.url).filter(Boolean));
  }

  // Extract fixed version from affected ranges
  let fixedVersion = undefined;
  if (Array.isArray(osvVuln.affected)) {
    for (const affected of osvVuln.affected) {
      if (Array.isArray(affected.ranges)) {
        for (const range of affected.ranges) {
          if (Array.isArray(range.events)) {
            for (const event of range.events) {
              if (event.fixed) {
                fixedVersion = event.fixed;
                break;
              }
            }
          }
        }
      }
    }
  }

  return {
    id,
    source: 'osv',
    severity,
    package: packageName,
    version,
    fixed_version: fixedVersion,
    title: summary,
    description: details,
    references: uniqueStrings(references),
    discovered_at: getTimestamp(),
  };
}

/**
 * Normalize NVD vulnerability data to unified schema.
 *
 * @param {any} nvdCve - Raw NVD CVE object
 * @returns {import('../lib/types.ts').Vulnerability}
 */
function normalizeNVDVulnerability(nvdCve) {
  const id = nvdCve.id || 'UNKNOWN';

  // Extract description
  let description = 'No description available';
  if (nvdCve.descriptions && Array.isArray(nvdCve.descriptions)) {
    const englishDesc = nvdCve.descriptions.find((d) => d.lang === 'en');
    if (englishDesc && englishDesc.value) {
      description = englishDesc.value;
    }
  }

  // Extract severity from CVSS metrics
  let severity = 'info';
  if (nvdCve.metrics) {
    // Try CVSS v3.1 first, then v3.0, then v2.0
    const cvssV31 = nvdCve.metrics.cvssMetricV31?.[0];
    const cvssV30 = nvdCve.metrics.cvssMetricV30?.[0];
    const cvssV2 = nvdCve.metrics.cvssMetricV2?.[0];

    const cvssData = cvssV31?.cvssData || cvssV30?.cvssData || cvssV2?.cvssData;
    if (cvssData && cvssData.baseSeverity) {
      severity = normalizeSeverity(cvssData.baseSeverity);
    }
  }

  // Extract references
  const references = [];
  if (nvdCve.references && Array.isArray(nvdCve.references)) {
    references.push(...nvdCve.references.map((ref) => ref.url).filter(Boolean));
  }

  return {
    id,
    source: 'nvd',
    severity,
    package: 'N/A',
    version: '*',
    fixed_version: undefined,
    title: description.slice(0, 100),
    description,
    references: uniqueStrings(references),
    discovered_at: getTimestamp(),
  };
}

/**
 * Enrich vulnerability data by querying multiple CVE databases.
 * OSV is primary, NVD is fallback for additional details.
 *
 * @param {string} packageName - Package name
 * @param {string} ecosystem - Ecosystem (e.g., 'npm', 'PyPI')
 * @param {string} [version] - Optional version
 * @returns {Promise<import('../lib/types.ts').Vulnerability[]>}
 */
export async function enrichVulnerability(packageName, ecosystem, version = undefined) {
  const results = [];

  // Query OSV first (primary source)
  const osvResults = await queryOSV(packageName, ecosystem, version);
  results.push(...osvResults);

  // Optionally query NVD for each CVE ID found in OSV results
  const nvdApiKey = process.env.CLAWSEC_NVD_API_KEY;
  if (nvdApiKey && results.length > 0) {
    for (const vuln of results) {
      if (vuln.id.startsWith('CVE-')) {
        const nvdData = await queryNVD(vuln.id);
        if (nvdData) {
          // Merge NVD references into OSV vulnerability
          vuln.references = uniqueStrings([...vuln.references, ...nvdData.references]);
        }
      }
    }
  }

  return results;
}

// CLI entry point for testing
if (import.meta.url === `file://${process.argv[1]}`) {
  const args = process.argv.slice(2);
  const packageName = args[0] || 'lodash';
  const ecosystem = args[1] || 'npm';
  const version = args[2];

  console.log(`Querying OSV for ${packageName}@${ecosystem}${version ? ` version ${version}` : ''}...`);

  const results = await queryOSV(packageName, ecosystem, version);
  console.log(JSON.stringify(results, null, 2));
  console.log(`\nFound ${results.length} vulnerabilities`);
}
