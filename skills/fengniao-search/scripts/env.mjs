const ENV_KEY = "FN_API_KEY";
export const BASE_URL = "https://test.riskbird.com/test-qbb-api";

export async function getApiKey() {
  const key = process.env[ENV_KEY];
  if (key && key !== "YOUR_API_KEY") return key;
  return null;
}