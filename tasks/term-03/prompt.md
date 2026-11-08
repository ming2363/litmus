# term-03: 修复损坏的发布打包脚本 `build.sh`

## 背景与需求
工作目录中有一个用于打包发布的脚本 `build.sh`，它需要读取 `config/release.env`、`templates/service.conf.tpl`、`src/modules/` 和 `assets/`，并在 `dist/` 目录下生成完整的发布产物。但当前 `build.sh` 存在多处错误且无法正常运行。

请修复 `build.sh`（**不要修改** `config/`、`templates/`、`src/`、`assets/` 下的任何文件），赋予其可执行权限，并执行 `./build.sh` 使 `dist/` 产出正确的发布产物。

## 产物规范
1. `build.sh` 必须具备可执行权限（`chmod +x build.sh`），且无论从工作目录直接执行 `./build.sh` 还是清空 `dist/` 后重新执行都能以退出码 `0` 完成构建。
2. `dist/config/service.conf`：基于 `templates/service.conf.tpl` 替换以下占位符：
   - `{{APP_NAME}}` -> `APP_NAME` 的值
   - `{{API_BASE}}` -> `API_BASE` 的值
   - `{{BUILD_TAG}}` -> `BUILD_TAG` 的值
   - `{{MODULE_LIST}}` -> 将 `ENABLED_MODULES` 按出现顺序用英文逗号 `,` 拼接（例如 `auth,metrics,rate_limit`）
3. `dist/bundle.txt`：仅打包 `ENABLED_MODULES` 中列出的模块，并严格按 `ENABLED_MODULES` 的顺序拼接；每个模块前插入一行 `=== <模块名> ===`（后接换行符），紧接着拼接 `src/modules/<模块名>.txt` 的原始内容。未列入 `ENABLED_MODULES` 的模块文件不得包含在内。
4. `dist/assets/`：完整保留 `assets/` 下的目录结构与文件内容（如 `dist/assets/banner.txt`、`dist/assets/notes/readme.txt`）。
5. `dist/manifest.json`：合法的 JSON 对象，包含以下字段：
   - `app_name`（字符串）
   - `build_tag`（字符串）
   - `api_base`（字符串）
   - `modules`（字符串数组，按 `ENABLED_MODULES` 顺序）
   - `files`（字符串数组，列出 `dist/` 下除 `manifest.json` 外所有文件的相对路径，如 `"assets/banner.txt"`，按字典序升序排列）

## 如何自测
- 在工作目录删除 `dist/` 后执行 `./build.sh`，检查退出码是否为 `0` 及 `dist/` 内容是否符合上述规范。
- 完成后可执行 `python3 litmus.py check` 检查工作目录无违规符号链接。
