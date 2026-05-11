#!/usr/bin/env node

function normalizeBaseUrl(raw) {
  const url = new URL(String(raw).trim());
  url.pathname = '';
  url.search = '';
  url.hash = '';
  return url.toString().replace(/\/$/, '');
}

function buildError(response, payload, fallbackMessage, request) {
  const error = new Error(payload?.error?.message ?? fallbackMessage);
  error.statusCode = response.status;
  error.code = payload?.error?.code ?? null;
  error.payload = payload;
  error.method = request.method;
  error.url = request.url;
  return error;
}

export async function requestJson(baseUrl, pathname, { method = 'GET', token, payload } = {}) {
  const url =
    pathname.startsWith('http://') || pathname.startsWith('https://')
      ? pathname
      : `${normalizeBaseUrl(baseUrl)}${pathname}`;
  let response;

  try {
    response = await fetch(url, {
      method,
      headers: {
        accept: 'application/json',
        ...(payload === undefined ? {} : { 'content-type': 'application/json' }),
        ...(token ? { authorization: `Bearer ${token}` } : {}),
      },
      body: payload === undefined ? undefined : JSON.stringify(payload),
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    throw new Error(`failed to reach AquaClaw at ${url}: ${message}`);
  }

  const text = await response.text();
  let body = null;
  if (text) {
    try {
      body = JSON.parse(text);
    } catch {
      throw new Error(`invalid JSON response from ${url}`);
    }
  }

  if (!response.ok) {
    throw buildError(response, body, `request failed: ${response.status}`, { method, url });
  }

  return body;
}
