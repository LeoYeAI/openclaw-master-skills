const { MAX_RETRIES, RETRY_DELAY_MS, RETRYABLE_MESSAGE_PATTERNS } = require('./config');

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function getResultMessage(result) {
  return result?.resultStatus?.msg || result?.resultStatus?.message || '';
}

function isRetryableReservationResult(result) {
  const message = getResultMessage(result);
  return RETRYABLE_MESSAGE_PATTERNS.some((pattern) => message.includes(pattern));
}

async function withRetry(action, label) {
  let lastResult = null;
  let lastError = null;

  for (let attempt = 1; attempt <= MAX_RETRIES; attempt += 1) {
    try {
      const result = await action();
      lastResult = result;

      if (!isRetryableReservationResult(result) || attempt === MAX_RETRIES) {
        return result;
      }

      console.log(`⏳ ${label} 返回“${getResultMessage(result)}”，${RETRY_DELAY_MS / 1000} 秒后重试 (${attempt}/${MAX_RETRIES})...`);
    } catch (error) {
      lastError = error;
      if (attempt === MAX_RETRIES) {
        throw error;
      }
      console.log(`⏳ ${label} 请求异常：${error.message}，${RETRY_DELAY_MS / 1000} 秒后重试 (${attempt}/${MAX_RETRIES})...`);
    }

    await sleep(RETRY_DELAY_MS);
  }

  if (lastError) {
    throw lastError;
  }

  return lastResult;
}

function request(options, postData = null) {
  const https = require('https');

  return new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
      let data = '';

      res.on('data', (chunk) => {
        data += chunk;
      });
      res.on('end', () => {
        const statusCode = res.statusCode || 500;
        const contentType = (res.headers['content-type'] || '').toLowerCase();
        const bodySnippet = data.replace(/\s+/g, ' ').trim().slice(0, 200);
        const isJsonLikeBody = /^\s*[\[{]/.test(data);

        if (statusCode < 200 || statusCode >= 300) {
          reject(new Error(`请求失败 (HTTP ${statusCode})${bodySnippet ? `: ${bodySnippet}` : ''}`));
          return;
        }

        if (!data.trim()) {
          reject(new Error(`响应体为空 (HTTP ${statusCode})`));
          return;
        }

        if (!contentType.includes('application/json') && !isJsonLikeBody) {
          reject(new Error(`接口返回了非 JSON 响应 (HTTP ${statusCode}, Content-Type: ${contentType || 'unknown'})${bodySnippet ? `: ${bodySnippet}` : ''}`));
          return;
        }

        try {
          resolve(JSON.parse(data));
        } catch (error) {
          reject(new Error(`解析 JSON 失败: ${error.message}${bodySnippet ? `; 响应片段: ${bodySnippet}` : ''}`));
        }
      });
    });

    req.on('error', reject);

    if (postData) {
      req.write(postData);
    }

    req.end();
  });
}

module.exports = {
  sleep,
  getResultMessage,
  withRetry,
  request
};
