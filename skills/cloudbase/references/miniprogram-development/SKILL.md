---
name: miniprogram-development
description: WeChat Mini Program development rules. Use this skill when developing WeChat mini programs, integrating CloudBase capabilities, and deploying mini program projects.
alwaysApply: false
---

## When to use this skill

Use this skill for **WeChat Mini Program development** when you need to:

- Develop WeChat mini program pages and components
- Integrate CloudBase capabilities (database, cloud functions, storage)
- Deploy and preview mini program projects
- Handle mini program authentication and user identity
- Call AI models in mini programs
- Get WeChat step count data

**Do NOT use for:**
- Web frontend development (use web-development skill)
- Backend service development (use cloudrun-development skill)
- UI design only (use ui-design skill, but may combine with this skill)

---

## How to use this skill (for a coding agent)

1. **Follow project structure conventions**
   - Mini program code in `miniprogram` directory
   - Cloud functions in `cloudfunctions` directory
   - Use latest base library version
   - Include page configuration files (e.g., index.json) when generating pages

2. **Understand authentication characteristics**
   - **Important**: Mini programs with CloudBase are naturally login-free
   - **Never generate login pages or login flows**
   - Get user identity via `cloud.getWXContext().OPENID` in cloud functions

3. **Use WeChat Developer Tools correctly**
   - Check `project.config.json` has `appid` field before opening
   - Use CLI command to open project pointing to directory containing `project.config.json`

4. **Handle resources properly**
   - **Icons8 (Recommended)**: Use Icons8 for icon images (e.g., tabbar iconPath)
     - URL format: `https://img.icons8.com/{style}/{size}/{color}/{icon-name}.png`
     - Parameters:
       - `style`: `ios` (outline style) or `ios-filled` (filled style)
       - `size`: `100` (recommended 100px, file size < 5KB)
       - `color`: hex color code without # (e.g., `8E8E93` for gray, `FF3B30` for red)
       - `icon-name`: icon name (e.g., `checked--v1`)
     - Examples:
       - Unselected (gray outline): `https://img.icons8.com/ios/100/8E8E93/checked--v1.png`
       - Selected (red filled): `https://img.icons8.com/ios-filled/100/FF3B30/checked--v1.png`
     - Advantages:
       - ✅ Very small file size (usually < 3KB)
       - ✅ Supports custom colors
       - ✅ Clean and professional icons
   - Use `downloadRemoteFile` tool to download resources
   - Avoid build errors by ensuring all referenced resources exist

---

# WeChat Mini Program Development Rules

## Project Structure

1. **CloudBase Integration**:
   - If user needs to develop mini program, you will use various WeChat CloudBase capabilities to develop the project
   - Mini program base library should use `latest` version

2. **Directory Organization**:
   - Mini program projects follow WeChat CloudBase best practices
   - Mini program code is generally in `miniprogram` directory
   - If developing cloud functions, they can be stored in `cloudfunctions` directory
   - Mini program's `project.config.json` needs to specify `miniprogramRoot` and other configurations

3. **Page Generation**:
   - When generating mini program pages, must include page configuration files such as `index.json`
   - Must comply with specifications to avoid compilation errors

## Development Tools

**WeChat Developer Tools Opening Project Workflow**:
- When detecting current project is a mini program project, suggest user to use WeChat Developer Tools for preview, debugging, and publishing
- Before opening, confirm `project.config.json` has `appid` field configured. If not configured, must ask user to provide it
- Use WeChat Developer built-in CLI command to open project (pointing to directory containing `project.config.json`):
  - Windows: `"C:\Program Files (x86)\Tencent\微信web开发者工具\cli.bat" open --project "项目根目录路径"`
  - macOS: `/Applications/wechatwebdevtools.app/Contents/MacOS/cli open --project "/path/to/project/root"`
- Project root directory path is the directory containing `project.config.json` file

## CloudBase Integration

1. **Environment Configuration**:
   - When using `wx.cloud` in mini program, need to specify environment ID
   - Environment ID can be queried via `envQuery` tool

2. **Resource Management**:
   - When generating mini program code, if material images are needed, such as tabbar's `iconPath` and other places, **prefer Icons8** (see section 4 above for details)
   - Use `downloadRemoteFile` tool to download resources
   - When generating mini program code, if using `iconPath` and similar, must simultaneously help user download icons to avoid build errors

## Mini Program Authentication Characteristics

**Important: Mini programs with CloudBase are naturally login-free. It is strictly forbidden to generate login pages or login flows!**

1. **Login-Free Feature**: Mini program CloudBase does not require user login, can get user identity in cloud functions via wx-server-sdk

2. **User Identity Retrieval**: In cloud functions, get user's unique identifier via `cloud.getWXContext().OPENID`

3. **User Data Management**: Manage user data in cloud functions based on openid, no login flow needed

```js
// Example of getting user identity in cloud function
exports.main = async (event, context) => {
  const wxContext = cloud.getWXContext();
  const openid = wxContext.OPENID;
  
  return { openid: openid };
};
```

## AI Model Invocation

Mini programs with base library version 3.7.1+ already support direct AI model invocation

```js
// Create model instance, here we use DeepSeek AI model
const model = wx.cloud.extend.AI.createModel("deepseek");

// First set AI's system prompt, here using seven-character quatrain generation as example
const p =
  "请严格按照七言绝句或七言律诗的格律要求创作，平仄需符合规则，押韵要和谐自然，韵脚字需在同一韵部。创作内容围绕用户给定的主题，七言绝句共四句，每句七个字；七言律诗共八句，每句七个字，颔联和颈联需对仗工整。同时，要融入生动的意象、丰富的情感与优美的意境，展现出古诗词的韵味与美感。";

// User's natural language input, e.g., '帮我写一首赞美玉龙雪山的诗'
const userInput = "帮我写一首赞美玉龙雪山的诗";

// Pass system prompt and user input to AI model
const res = await model.streamText({
  data: {
    model: "deepseek-v3", // Specify specific model
    messages: [
      { role: "system", content: p },
      { role: "user", content: userInput },
    ],
  },
});

// Receive AI model's response
// Since AI model's return result is streaming, we need to loop to receive complete response text
for await (let str of res.textStream) {
  console.log(str);
}
```

## WeChat Step Count Retrieval

**WeChat step count retrieval must use CloudID method (base library 2.7.0+)**:
- **Frontend**: `wx.getWeRunData()` to get cloudID, use `wx.cloud.CloudID(cloudID)` to pass to cloud function
- **Cloud Function**: Directly use `weRunData.data` to get decrypted step count data, check `weRunData.errCode` to handle errors
- **Forbidden**: Do not use session_key manual decryption method, CloudID is more secure and simple
- **Required**: Must implement fallback mechanism (simulated data) to handle cloudID retrieval failure cases

## Cloud Function Deployment and Permission Notes

- After AI automatically deploys cloud functions, special permissions like cloud invocation may be missing
- Recommend users to right-click cloud function in WeChat Developer Tools, select "Install Dependencies in Cloud"
- For functions requiring cloud invocation permissions (such as WeChat step count decryption), recommend manually deploying once via Developer Tools to get complete permissions
- If encountering permission issues, prompt user to check cloud function's service authorization and API permission configuration

## Development Workflow Guidance

- After completing mini program project development, proactively suggest user to use WeChat Developer Tools for preview, debugging, and publishing
- If user agrees, use CLI command to open WeChat Developer Tools, pointing to project root directory containing `project.config.json`
- Remind user to perform real device preview, debugging, and publishing operations in WeChat Developer Tools
