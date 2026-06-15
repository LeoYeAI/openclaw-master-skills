/**
 * web-autopilot: Session Manager
 * Handles cookie-based HTTP sessions for any web application.
 * Supports REST JSON, GraphQL, form-urlencoded, multipart uploads.
 */

import * as fs from 'fs';
import * as path from 'path';
import * as https from 'https';
import * as http from 'http';
import { URL } from 'url';

export const DEFAULT_SESSION_DIR = path.join(process.env.HOME || '~', '.openclaw/rpa/sessions');

export class Session {
  private stored: { appDomain: string; ssoUrl: string; savedAt: number; cookies: Record<string, string>; persistentHeaders: Record<string, string>; sessionFields: Record<string, string> };
  private cookieFile: string;

  constructor(private appDomain: string, private ssoUrl: string = '', private sessionDir: string = DEFAULT_SESSION_DIR) {
    fs.mkdirSync(sessionDir, { recursive: true });
    this.cookieFile = path.join(sessionDir, `${appDomain.replace(/[^a-z0-9]/gi, '_')}.session.json`);
    this.stored = this.load();
  }

  private load() {
    if (fs.existsSync(this.cookieFile)) { try { return JSON.parse(fs.readFileSync(this.cookieFile, 'utf8')); } catch {} }
    return { appDomain: this.appDomain, ssoUrl: this.ssoUrl, savedAt: 0, cookies: {}, persistentHeaders: {}, sessionFields: {} };
  }

  save() { this.stored.savedAt = Date.now(); fs.writeFileSync(this.cookieFile, JSON.stringify(this.stored, null, 2)); }

  importCookies(cookies: { name: string; value: string; domain: string }[]) { for (const c of cookies) { this.stored.cookies[c.name] = c.value; } this.save(); }
  setCookie(name: string, value: string) { this.stored.cookies[name] = value; this.save(); }
  setHeader(name: string, value: string) { this.stored.persistentHeaders[name] = value; this.save(); }
  setSessionField(key: string, value: string) { this.stored.sessionFields[key] = value; this.save(); }
  getSessionField(key: string): string | undefined { return this.stored.sessionFields[key]; }
  getCookieValue(name: string): string | undefined { return this.stored.cookies[name]; }
  getCookieString(): string { return Object.entries(this.stored.cookies).map(([k, v]) => `${k}=${v}`).join('; '); }
  isExpired(maxAgeMs = 8 * 60 * 60 * 1000): boolean { return !this.stored.savedAt || Date.now() - this.stored.savedAt > maxAgeMs; }

  async get(url: string, extraHeaders: Record<string, string> = {}) { return this.request('GET', url, null, extraHeaders); }
  async post(url: string, body: any, extraHeaders: Record<string, string> = {}) { return this.request('POST', url, JSON.stringify(body), { 'Content-Type': 'application/json', ...extraHeaders }); }
  async postForm(url: string, fields: Record<string, string>, extraHeaders: Record<string, string> = {}) { return this.request('POST', url, new URLSearchParams(fields).toString(), { 'Content-Type': 'application/x-www-form-urlencoded', ...extraHeaders }); }
  async put(url: string, body: any, extraHeaders: Record<string, string> = {}) { return this.request('PUT', url, JSON.stringify(body), { 'Content-Type': 'application/json', ...extraHeaders }); }

  async graphql(url: string, query: string, variables: Record<string, any> = {}, operationName?: string, extraHeaders: Record<string, string> = {}) {
    const result = await this.request('POST', url, JSON.stringify({ query, variables, operationName }), { 'Content-Type': 'application/json', ...extraHeaders });
    if (typeof result.body === 'object' && result.body !== null) { (result as any).data = result.body.data; (result as any).errors = result.body.errors; }
    return result;
  }

  private request(method: string, urlStr: string, body: string | null, extraHeaders: Record<string, string>): Promise<{ status: number; body: any; raw: string; ok: boolean; headers: Record<string, string> }> {
    return new Promise((resolve, reject) => {
      const parsed = new URL(urlStr);
      const isHttps = parsed.protocol === 'https:';
      const headers: Record<string, string> = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Cookie': this.getCookieString(),
        ...this.stored.persistentHeaders, ...extraHeaders,
      };
      if (body) headers['Content-Length'] = Buffer.byteLength(body).toString();
      const protocol = isHttps ? https : http;
      const req = protocol.request({ hostname: parsed.hostname, port: parsed.port || (isHttps ? '443' : '80'), path: parsed.pathname + parsed.search, method, headers, rejectUnauthorized: false }, (res) => {
        const chunks: Buffer[] = [];
        res.on('data', (c: Buffer) => chunks.push(c));
        res.on('end', () => {
          const raw = Buffer.concat(chunks).toString('utf8');
          const setCookie = res.headers['set-cookie'];
          if (setCookie) { for (const s of setCookie) { const [nv] = s.split(';'); const eq = nv.indexOf('='); if (eq > 0) this.stored.cookies[nv.substring(0, eq).trim()] = nv.substring(eq + 1).trim(); } this.save(); }
          let parsedBody: any = raw;
          try { parsedBody = JSON.parse(raw); } catch {}
          const rh: Record<string, string> = {};
          for (const [k, v] of Object.entries(res.headers)) { rh[k] = Array.isArray(v) ? v.join(', ') : (v || ''); }
          resolve({ status: res.statusCode || 0, body: parsedBody, raw, ok: (res.statusCode || 0) >= 200 && (res.statusCode || 0) < 300, headers: rh });
        });
      });
      req.on('error', reject);
      req.setTimeout(30_000, () => req.destroy(new Error('timeout')));
      if (body) req.write(body);
      req.end();
    });
  }
}

export function createSession(appDomain: string, ssoUrl?: string) { return new Session(appDomain, ssoUrl); }
export function loadSession(appDomain: string) { return new Session(appDomain); }
