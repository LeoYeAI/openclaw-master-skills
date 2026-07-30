# OpenCode API Control Skill
version: 1.1.0
A high-performance orchestration skill for controlling the **Open Code CLI** through its native web server API. This skill acts as a professional bridge between autonomous agents and development environments.

## 🚀 Overview
This skill leverages the built-in local web server feature of OpenCode to manage coding sessions, process requests, and monitor task progress programmatically. It provides a significantly streamlined workflow compared to managing complex terminal sessions or multiplexers like `tmux`.

## ✨ Key Features
- **Session Management**: Effortlessly create, save, and restore project-specific sessions.
- **Task Orchestration**: Send complex coding prompts and manage agent responses via REST API.
- **Real-time Monitoring**: Follow progress and status updates (`idle`/`busy`) through dedicated scripts.
- **Workflow Automation**: Pre-configured bash scripts for common operations like updating providers and checking diffs.

## 🛡️ Privacy & Local-First Architecture
- **100% Local**: All communications occur strictly within your local environment or trusted local network.
- **No External Calls**: The skill does not communicate with any external servers or third-party cloud services.
- **Network Access**: By default, OpenCode binds to `127.0.0.1`. To enable access from other devices on the same network, start the server using:
  ```bash
  opencode web --hostname 0.0.0.0 --port 4099
  ```

## Why I built this
Developed by **Malek RSH**.

I started this project because I wanted a solid way to use the **OpenCode CLI** directly from **OpenCLAW** agent, but there wasn't a robust solution available at the time. 

After trying different approaches like reverse proxies, I started digging into the source code and schemas of the `opencode web` feature. I realized that while the web server is meant to be used in a browser, its API could be controlled programmatically. So, I spent some time reverse-engineering the endpoints and states to build this orchestration layer. It makes things much easier than fighting with terminal sessions.

---
*Built for simplicity and making local agents more useful.*

## 🤝 Contributions & Support
This project is open for improvement! If you have suggestions, find bugs, or want to contribute new scripts/patterns:
- **Repository**: [malek262/opencode-api-control-skill](https://github.com/malek262/opencode-api-control-skill)
- **Issues**: Feel free to open an issue on GitHub for any bugs or feature requests.
- **Pull Requests**: Contributions are always welcome.

**Author**: [Malek RSH](https://github.com/malek262)
