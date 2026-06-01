/**
 * Crab 签名认证模块
 *
 * 使用 secp256k1 ECDSA 签名验证 API 请求。
 * 客户端对时间戳 + 地址签名，API 校验签名有效性及地址一致性。
 *
 * 请求头：
 *   X-Crab-Timestamp  — Unix 时间戳（秒）
 *   X-Crab-Signature  — ECDSA-SHA256 签名（hex）
 *   X-Crab-Key        — 公钥（base64 DER）
 *   X-Crab-Address    — 签名者地址（0x...）
 *
 * 签名消息格式：CRAB-AUTH:{timestamp}:{address}
 */

const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const CREDENTIALS_DIR = path.join(
  process.env.HOME || process.env.USERPROFILE || "~",
  ".config",
  "crab",
);
const CREDENTIALS_PATH = path.join(CREDENTIALS_DIR, "credentials.json");
const SIGN_PREFIX = "CRAB-AUTH:";
const TIMESTAMP_TOLERANCE_S = 86400; 


function generateWallet() {
  const { privateKey, publicKey } = crypto.generateKeyPairSync("ec", {
    namedCurve: "secp256k1",
  });

  const privPem = privateKey.export({ type: "pkcs8", format: "pem" });
  const pubDerBuf = publicKey.export({ type: "spki", format: "der" });
  const pubBase64 = pubDerBuf.toString("base64");

  const hash = crypto.createHash("sha256").update(pubDerBuf).digest("hex");
  const address = "0x" + hash.substring(0, 40);

  return { privateKey: privPem, publicKey: pubBase64, address };
}

function initCredentials() {
  if (fs.existsSync(CREDENTIALS_PATH)) {
    const existing = JSON.parse(fs.readFileSync(CREDENTIALS_PATH, "utf-8"));
    if (existing.privateKey && existing.publicKey && existing.address) {
      console.log(`[crab] 已有凭证: ${CREDENTIALS_PATH}`);
      console.log(`[crab] 地址: ${existing.address}`);
      return existing;
    }
  }

  const wallet = generateWallet();

  fs.mkdirSync(CREDENTIALS_DIR, { recursive: true });
  fs.writeFileSync(CREDENTIALS_PATH, JSON.stringify(wallet, null, 2), {
    mode: 0o600,
  });

  console.log(`[crab] 已生成新凭证: ${CREDENTIALS_PATH}`);
  console.log(`[crab] 地址: ${wallet.address}`);
  return wallet;
}

function loadCredentials() {
  if (!fs.existsSync(CREDENTIALS_PATH)) {
    return null;
  }
  return JSON.parse(fs.readFileSync(CREDENTIALS_PATH, "utf-8"));
}


function signRequest(privPem, timestamp, address) {
  const message = `${SIGN_PREFIX}${timestamp}:${address}`;
  const sig = crypto.sign("SHA256", Buffer.from(message), privPem);
  return sig.toString("hex");
}

function createAuthHeaders(credentials) {
  const timestamp = Math.floor(Date.now() / 1000).toString();
  const signature = signRequest(
    credentials.privateKey,
    timestamp,
    credentials.address,
  );
  return {
    "X-Crab-Timestamp": timestamp,
    "X-Crab-Signature": signature,
    "X-Crab-Key": credentials.publicKey,
    "X-Crab-Address": credentials.address,
  };
}


function verifySignature(timestamp, address, signatureHex, pubKeyBase64) {
  try {
    const message = `${SIGN_PREFIX}${timestamp}:${address}`;
    const publicKey = crypto.createPublicKey({
      key: Buffer.from(pubKeyBase64, "base64"),
      format: "der",
      type: "spki",
    });
    return crypto.verify(
      "SHA256",
      Buffer.from(message),
      publicKey,
      Buffer.from(signatureHex, "hex"),
    );
  } catch {
    return false;
  }
}

function deriveAddress(pubKeyBase64) {
  const pubDer = Buffer.from(pubKeyBase64, "base64");
  const hash = crypto.createHash("sha256").update(pubDer).digest("hex");
  return "0x" + hash.substring(0, 40);
}

// --------------- Express 中间件 ---------------

function crabAuth(req, res, next) {
  const timestamp = req.headers["x-crab-timestamp"];
  const signature = req.headers["x-crab-signature"];
  const pubKey = req.headers["x-crab-key"];
  const address = req.headers["x-crab-address"];

  if (!timestamp || !signature || !pubKey || !address) {
    return res.status(401).json({
      ok: false,
      error: {
        code: "auth_missing",
        message:
          "Missing auth headers: X-Crab-Timestamp, X-Crab-Signature, X-Crab-Key, X-Crab-Address.",
      },
    });
  }

  // 校验时间戳新鲜度
  const now = Math.floor(Date.now() / 1000);
  const ts = parseInt(timestamp, 10);
  if (Number.isNaN(ts) || Math.abs(now - ts) > TIMESTAMP_TOLERANCE_S) {
    return res.status(401).json({
      ok: false,
      error: {
        code: "auth_expired",
        message: "Timestamp expired or invalid.",
      },
    });
  }

  // 校验地址与公钥一致性
  const derivedAddress = deriveAddress(pubKey);
  if (derivedAddress !== address) {
    return res.status(401).json({
      ok: false,
      error: {
        code: "auth_address_mismatch",
        message: "Address does not match the provided public key.",
      },
    });
  }

  // 校验签名（签名消息包含地址）
  if (!verifySignature(timestamp, address, signature, pubKey)) {
    return res.status(401).json({
      ok: false,
      error: {
        code: "auth_invalid",
        message: "Signature verification failed.",
      },
    });
  }

  req.crabAddress = address;
  next();
}

module.exports = {
  generateWallet,
  initCredentials,
  loadCredentials,
  signRequest,
  createAuthHeaders,
  verifySignature,
  deriveAddress,
  crabAuth,
  CREDENTIALS_PATH,
};
