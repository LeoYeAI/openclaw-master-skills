## 鉴权与环境变量约定

- 所有 HTTP 请求都必须带 Header：
  - `Authorization: Bearer $VECTCUT_API_KEY`
- 必须在终端中配置：VECTCUT_API_KEY

```bash
export VECTCUT_BASE_URL="http://open.vectcut.com/cut_jianying"
```

这样既方便在终端里统一配置，也方便在其他脚本或工具里统一读取。
