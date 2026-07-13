/**
 * feishu-cards plugin for OpenClaw
 * Provides tools to send interactive Feishu card forms.
 * Requires the built-in feishu plugin for card action callbacks.
 */

type FeishuCardField = {
  name: string;
  label: string;
  type: "text" | "date" | "select" | "textarea";
  placeholder?: string;
  options?: Array<{ label: string; value: string }>;
  required?: boolean;
};

function buildFormCard(params: {
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

  formElements.push({
    tag: "column_set",
    flex_mode: "none",
    horizontal_spacing: "8px",
    horizontal_align: "right",
    margin: "12px 0px 0px 0px",
    columns: [
      {
        tag: "column",
        width: "auto",
        elements: [
          {
            tag: "button",
            text: { tag: "plain_text", content: submitLabel },
            type: "primary",
            width: "default",
            form_action_type: "submit",
            name: "submit_btn",
            behaviors: [{ type: "callback", value: actionValue }],
          },
        ],
      },
      {
        tag: "column",
        width: "auto",
        elements: [
          {
            tag: "button",
            text: { tag: "plain_text", content: resetLabel },
            type: "default",
            width: "default",
            form_action_type: "reset",
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

async function getFeishuToken(appId: string, appSecret: string): Promise<string> {
  const res = await fetch("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ app_id: appId, app_secret: appSecret }),
  });
  const data = await res.json() as { tenant_access_token?: string; code?: number; msg?: string };
  if (!data.tenant_access_token) {
    throw new Error(`Failed to get Feishu token: ${data.msg ?? "unknown"}`);
  }
  return data.tenant_access_token;
}

function resolveReceiveIdType(to: string): string {
  if (to.startsWith("ou_")) return "open_id";
  if (to.startsWith("oc_")) return "chat_id";
  if (to.startsWith("on_")) return "union_id";
  if (to.includes("@")) return "email";
  return "open_id";
}

async function sendCard(params: {
  appId: string;
  appSecret: string;
  to: string;
  card: Record<string, unknown>;
}): Promise<{ messageId: string }> {
  const token = await getFeishuToken(params.appId, params.appSecret);
  const receiveIdType = resolveReceiveIdType(params.to);

  const res = await fetch(
    `https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=${receiveIdType}`,
    {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        receive_id: params.to,
        msg_type: "interactive",
        content: JSON.stringify(params.card),
      }),
    },
  );
  const data = await res.json() as { code?: number; msg?: string; data?: { message_id?: string } };
  if (data.code !== 0) {
    throw new Error(`Feishu send card failed: ${data.msg ?? "unknown"} (code ${data.code})`);
  }
  return { messageId: data.data?.message_id ?? "" };
}

async function updateCard(params: {
  appId: string;
  appSecret: string;
  messageId: string;
  card: Record<string, unknown>;
}): Promise<void> {
  const token = await getFeishuToken(params.appId, params.appSecret);
  const res = await fetch(
    `https://open.feishu.cn/open-apis/im/v1/messages/${params.messageId}`,
    {
      method: "PATCH",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ content: JSON.stringify(params.card) }),
    },
  );
  const data = await res.json() as { code?: number; msg?: string };
  if (data.code !== 0) {
    throw new Error(`Feishu update card failed: ${data.msg ?? "unknown"} (code ${data.code})`);
  }
}

function resolveFeishuCredentials(cfg: any, accountId?: string): { appId: string; appSecret: string } {
  const id = accountId ?? "default";
  const accounts = cfg?.channels?.feishu?.accounts;
  const account = accounts?.[id];
  if (!account?.appId || !account?.appSecret) {
    throw new Error(`Feishu account "${id}" not configured`);
  }
  return { appId: account.appId, appSecret: account.appSecret };
}

export default function (api: any) {
  const cfg = api.config;

  api.registerTool({
    name: "feishu_send_card",
    description:
      "Send a Feishu interactive card (schema 2.0 JSON) to a user or group. " +
      "Use feishu_send_form for a higher-level form builder.",
    parameters: {
      type: "object",
      required: ["to", "card"],
      properties: {
        to: {
          type: "string",
          description: "Recipient: open_id (ou_xxx), chat_id (oc_xxx), or user email",
        },
        card: {
          type: "object",
          description: "Full Feishu card JSON (schema 2.0 recommended)",
        },
        accountId: {
          type: "string",
          description: "Feishu account ID (defaults to 'default')",
        },
      },
    },
    async execute(_id: string, params: { to: string; card: Record<string, unknown>; accountId?: string }) {
      const creds = resolveFeishuCredentials(cfg, params.accountId);
      const result = await sendCard({ ...creds, to: params.to, card: params.card });
      return { ok: true, messageId: result.messageId };
    },
  });

  api.registerTool({
    name: "feishu_send_form",
    description:
      "Build and send a Feishu interactive form card. " +
      "Supports text inputs, date pickers, and dropdowns. " +
      "When the user submits the form, the field values arrive as a [CARD_ACTION] message. " +
      "Requires the built-in feishu plugin to handle card action callbacks.",
    parameters: {
      type: "object",
      required: ["to", "title", "fields"],
      properties: {
        to: {
          type: "string",
          description: "Recipient: open_id (ou_xxx), chat_id (oc_xxx), or user email",
        },
        title: { type: "string", description: "Card header title" },
        description: { type: "string", description: "Optional description above the form fields" },
        fields: {
          type: "array",
          description: "Form field definitions",
          items: {
            type: "object",
            required: ["name", "label", "type"],
            properties: {
              name: { type: "string", description: "Field key (used in form_value callback)" },
              label: { type: "string", description: "Label shown to the user" },
              type: {
                type: "string",
                enum: ["text", "date", "select", "textarea"],
                description: "text=plain input, date=date picker, select=dropdown, textarea=multiline",
              },
              placeholder: { type: "string" },
              required: { type: "boolean" },
              options: {
                type: "array",
                description: "Options for select type",
                items: {
                  type: "object",
                  required: ["label", "value"],
                  properties: {
                    label: { type: "string" },
                    value: { type: "string" },
                  },
                },
              },
            },
          },
        },
        submitLabel: { type: "string", description: "Submit button text (default: 提交)" },
        resetLabel: { type: "string", description: "Reset button text (default: 重置)" },
        headerColor: {
          type: "string",
          description: "Header color: blue|green|red|orange|yellow|turquoise|violet|purple|indigo|carmine|wathet|grey|default",
        },
        actionValue: {
          type: "object",
          description: "Custom callback value merged into form_value on submit",
        },
        accountId: { type: "string" },
      },
    },
    async execute(_id: string, params: {
      to: string;
      title: string;
      description?: string;
      fields: FeishuCardField[];
      submitLabel?: string;
      resetLabel?: string;
      headerColor?: string;
      actionValue?: Record<string, unknown>;
      accountId?: string;
    }) {
      const creds = resolveFeishuCredentials(cfg, params.accountId);
      const card = buildFormCard(params);
      const result = await sendCard({ ...creds, to: params.to, card });
      return { ok: true, messageId: result.messageId };
    },
  });

  api.registerTool({
    name: "feishu_update_card",
    description: "Update (patch) an existing Feishu interactive card by message ID.",
    parameters: {
      type: "object",
      required: ["messageId", "card"],
      properties: {
        messageId: { type: "string", description: "Message ID of the card to update (om_xxx)" },
        card: { type: "object", description: "New card JSON to replace the card content" },
        accountId: { type: "string" },
      },
    },
    async execute(_id: string, params: { messageId: string; card: Record<string, unknown>; accountId?: string }) {
      const creds = resolveFeishuCredentials(cfg, params.accountId);
      await updateCard({ ...creds, ...params });
      return { ok: true };
    },
  });
}
