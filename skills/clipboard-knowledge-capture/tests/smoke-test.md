# 剪贴板知识捕手 冒烟测试

## 测试目标
验证目录完整、脚本可运行、模板可生成、异常输入可被正确处理。

## 步骤
1. 检查目录包含必需文件：
   - `SKILL.md`
   - `README.md`
   - `SELF_CHECK.md`
   - `scripts/run.py`
   - `resources/spec.json`
   - `resources/template.md`
   - `examples/example-input.md`
2. 执行：
   ```bash
   python3 scripts/run.py --input examples/example-input.md --output out.md
   ```
3. 观察 `out.md` 是否成功生成，且至少包含以下章节：
   - 摘录内容
   - 来源
   - 建议归档位置
4. 执行异常路径：
   ```bash
   python3 scripts/run.py --input does-not-exist.md
   ```
5. 预期：
   - 正常路径返回 0 并生成结构化内容
   - 异常路径返回非 0，并输出可读错误信息

## 通过标准
- 脚本可执行
- 输出结构正确
- 错误处理清晰
