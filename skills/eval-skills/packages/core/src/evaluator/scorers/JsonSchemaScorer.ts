import Ajv from "ajv";
// @ts-ignore
import addFormats from "ajv-formats";
import type { Scorer, ScorerResult } from "./BaseScorer.js";
import type { ExpectedOutput } from "../../types/index.js";

// @ts-ignore
let _ajvInstance: any | null = null;

function createAjv() {
  // @ts-ignore
  const AjvClass = Ajv.default || Ajv;
  const ajv = new AjvClass({ allErrors: true });
  // @ts-ignore
  addFormats(ajv);
  return ajv;
}

function getAjv() {
  if (!_ajvInstance) {
    _ajvInstance = createAjv();
  }
  return _ajvInstance;
}

/**
 * JSON Schema 验证评分器
 *
 * 使用 ajv + ajv-formats 验证 output 是否符合 expected.schema。
 */
export class JsonSchemaScorer implements Scorer {
  readonly type = "json_schema";

  async score(output: unknown, expected: ExpectedOutput): Promise<ScorerResult> {
    const schema = expected.schema;

    if (!schema) {
      return {
        score: 0.0,
        passed: false,
        reason: "No schema provided in expected output",
      };
    }

    // If output is a string, attempt to parse as JSON
    let data: unknown = output;
    if (typeof output === "string") {
      try {
        data = JSON.parse(output);
      } catch {
        return {
          score: 0.0,
          passed: false,
          reason: `Output is not valid JSON: ${output}`,
        };
      }
    }

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const ajv = getAjv();
    const validate = ajv.compile(schema);
    const valid = validate(data);

    if (valid) {
      return { score: 1.0, passed: true };
    }

    const errors = validate.errors
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      ?.map((e: any) => `${e.instancePath || "/"} ${e.message}`)
      .join("; ");

    return {
      score: 0.0,
      passed: false,
      reason: `Schema validation failed: ${errors}`,
    };
  }
}
