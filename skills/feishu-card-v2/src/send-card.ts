import { sendCardFeishu, updateCardFeishu } from "openclaw/plugin-sdk/feishu/send";
import type { ClawdbotConfig } from "openclaw/plugin-sdk/feishu";

export type FeishuCardField = {
  /** Field name (used as `name` in form components) */
  name: string;
  /** Label shown to the user */
  label: string;
  /** Component type */
  type: "text" | "date" | "select" | "textarea";
  /** Placeholder text */
  placeholder?: string;
  /** Options for select type */
  options?: Array<{ label: string; value: string }>;
  /** Whether field is required */
  required?: boolean;
};

/** Build a schema 2.0 interactive card with a form */
export function buildFormCard(params: {
  title: string;
  description?: string;
  fields: FeishuCardField[];
  submitLabel?: string;
  resetLabel?: string;
  headerColor?: string;
  actionValue?: Record<string, unknown>;
}): Record<string, unknown> {
  const {
    title,
    description,
    fields,
    submitLabel = "提交",
    resetLabel = "重置",
    headerColor = "blue",
    actionValue = { action: "form_submit" },
  } = params;

  const formElements: unknown[] = [];

  if (description) {
    formElements.push({ tag: "markdown", content: description });
  }

  for (const field of fields) {
    // Label as markdown (date_picker and select_static don't support label prop)
    formElements.push({
      tag: "markdown",
      content: `**${field.label}**${field.required ? " *" : ""}`,
      margin: "8px 0px 2px 0px",
    });

    if (field.type === "date") {
      formElements.push({
        tag: "date_picker",
        element_id: field.name,
        name: field.name,
        placeholder: { tag: "plain_text", content: field.placeholder ?? "请选择日期" },
        width: "default",
        required: field.required ?? false,
      });
    } else if (field.type === "select" && field.options) {
      formElements.push({
        tag: "select_static",
        element_id: field.name,
        name: field.name,
        placeholder: { tag: "plain_text", content: field.placeholder ?? "请选择" },
        width: "default",
        required: field.required ?? false,
        options: field.options.map((o) => ({
          text: { tag: "plain_text", content: o.label },
          value: o.value,
        })),
      });
    } else if (field.type === "textarea") {
      formElements.push({
        tag: "input",
        element_id: field.name,
        name: field.name,
        placeholder: { tag: "plain_text", content: field.placeholder ?? "请输入" },
        width: "default",
        required: field.required ?? false,
        input_type: "multiline_text",
        rows: 3,
        auto_resize: true,
      });
    } else {
      // text
      formElements.push({
        tag: "input",
        element_id: field.name,
        name: field.name,
        placeholder: { tag: "plain_text", content: field.placeholder ?? "请输入" },
        width: "default",
        required: field.required ?? false,
      });
    }
  }

  // Submit / Reset buttons
  formElements.push({
    tag: "column_set",
    flex_mode: "none",
    background_style: "default",
    horizontal_spacing: "default",
    margin: "12px 0px 0px 0px",
    columns: [
      {
        tag: "column",
        width: "auto",
        vertical_align: "top",
        elements: [
          {
            tag: "button",
            text: { tag: "plain_text", content: submitLabel },
            type: "primary",
            form_action_type: "submit", // JSON 2.0 正确字段（旧 action_type: "form_submit" 已废弃）
            name: "submit_btn",
            behaviors: [{ type: "callback", value: actionValue }],
          },
        ],
      },
      {
        tag: "column",
        width: "auto",
        vertical_align: "top",
        elements: [
          {
            tag: "button",
            text: { tag: "plain_text", content: resetLabel },
            type: "default",
            form_action_type: "reset", // JSON 2.0 正确字段（旧 action_type: "form_reset" 已废弃）
            name: "reset_btn",
          },
        ],
      },
    ],
  });

  return {
    schema: "2.0",
    config: { update_multi: true },
    header: {
      title: { tag: "plain_text", content: title },
      template: headerColor,
    },
    body: {
      elements: [
        {
          tag: "form",
          element_id: "main_form",
          name: "main_form",
          elements: formElements,
        },
      ],
    },
  };
}

export async function sendFormCard(params: {
  cfg: ClawdbotConfig;
  to: string;
  title: string;
  description?: string;
  fields: FeishuCardField[];
  submitLabel?: string;
  resetLabel?: string;
  headerColor?: string;
  actionValue?: Record<string, unknown>;
  accountId?: string;
}): Promise<{ messageId: string }> {
  const { cfg, to, accountId, ...cardParams } = params;
  const card = buildFormCard(cardParams);
  const result = await sendCardFeishu({ cfg, to, card, accountId });
  return { messageId: result.messageId };
}

export async function sendRawCard(params: {
  cfg: ClawdbotConfig;
  to: string;
  card: Record<string, unknown>;
  accountId?: string;
}): Promise<{ messageId: string }> {
  const result = await sendCardFeishu(params);
  return { messageId: result.messageId };
}

export async function updateCard(params: {
  cfg: ClawdbotConfig;
  messageId: string;
  card: Record<string, unknown>;
  accountId?: string;
}): Promise<void> {
  return updateCardFeishu(params);
}
