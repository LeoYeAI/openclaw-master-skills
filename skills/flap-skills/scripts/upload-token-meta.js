#!/usr/bin/env node
/**
 * 上传代币元数据到 Flap API，获取 IPFS CID 作为 createToken 的 _meta。
 * 文档：https://docs.flap.sh/flap/developers/token-launcher-developers/launch-token-through-portal
 * API：https://funcs.flap.sh/api/upload（必须用此 API 固定到 Flap 网关，索引才能拉取）
 */

import axios from "axios";
import FormData from "form-data";
import fs from "fs";
import path from "path";

const FLAP_UPLOAD_API = "https://funcs.flap.sh/api/upload";

const MUTATION_CREATE = `
  mutation Create($file: Upload!, $meta: MetadataInput!) {
    create(file: $file, meta: $meta)
  }
`;

/**
 * 上传代币元数据到 Flap API（含官网、简介等），见 https://docs.flap.sh/flap/developers/token-launcher-developers/launch-token-through-portal
 * @param {Object} opts
 * @param {string} opts.imagePath - 图片本地路径（如 logo.png）
 * @param {string} [opts.description] - 简介/代币描述（提交到 meta.description）
 * @param {string} [opts.website] - 官网（提交到 meta.website）
 * @param {string} [opts.twitter]
 * @param {string} [opts.telegram]
 * @param {string} [opts.creator] - 创作者地址，默认零地址
 * @returns {Promise<string>} IPFS CID，即 _meta
 */
export async function uploadTokenMeta(opts) {
  const {
    imagePath,
    description = "",
    website = null,
    twitter = null,
    telegram = null,
    creator = "0x0000000000000000000000000000000000000000",
  } = opts;

  const form = new FormData();

  form.append(
    "operations",
    JSON.stringify({
      query: MUTATION_CREATE,
      variables: {
        file: null,
        meta: {
          website: website ?? "",
          twitter: twitter ?? "",
          telegram: telegram ?? "",
          description: description ?? "",
          creator,
        },
      },
    })
  );

  form.append("map", JSON.stringify({ "0": ["variables.file"] }));

  const imageBuf = fs.readFileSync(imagePath);
  const ext = path.extname(imagePath) || ".png";
  const mime = ext === ".png" ? "image/png" : ext === ".jpg" || ext === ".jpeg" ? "image/jpeg" : "image/png";
  form.append("0", imageBuf, {
    filename: path.basename(imagePath) || "image.png",
    contentType: mime,
  });

  const res = await axios.post(FLAP_UPLOAD_API, form, {
    headers: form.getHeaders(),
    maxBodyLength: Infinity,
    maxContentLength: Infinity,
  });

  if (res.status !== 200) {
    throw new Error(`上传失败: ${res.status} ${res.statusText}`);
  }

  const cid = res.data?.data?.create;
  if (!cid || typeof cid !== "string") {
    throw new Error("响应中无 create CID: " + JSON.stringify(res.data));
  }

  return cid;
}

async function main() {
  const args = process.argv.slice(2);
  const imagePath = args[0];
  if (!imagePath) {
    console.error("用法: node upload-token-meta.js <图片路径> [简介] [官网] [twitter] [telegram]");
    console.error("示例: node upload-token-meta.js ./logo.png \"代币简介\" \"https://example.com\"");
    process.exit(1);
  }

  const [description, website, twitter, telegram] = args.slice(1);
  const cid = await uploadTokenMeta({
    imagePath,
    description: description ?? "",
    website: website || null,
    twitter: twitter || null,
    telegram: telegram || null,
  });
  console.log(cid);
}

main().catch((err) => {
  console.error(err.message || err);
  process.exit(1);
});
