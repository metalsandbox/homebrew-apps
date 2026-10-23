# metalsandbox/apps

个人维护的开源 Homebrew Tap，提供 OffPDF 与 Steam ARM64 bootstrapper。与 Valve、Homebrew 或 OffPDF 作者无隶属关系。Tap 源码使用 MIT 许可证，应用本身遵循各自许可。

## Steam ARM64

Apple Silicon（M1 及更新芯片）、macOS 12 Monterey 及更新版本，需要支持 `preflight_steps` 的当前 Homebrew（本机验证版本 7.0.10）。最低系统要求以 [Valve 支持页面](https://help.steampowered.com/en/faqs/view/659D-A19E-018A-81A6) 为准。

**状态：bootstrapper 安装已在 Apple Silicon 实测；完整客户端首次更新、登录及所有子进程架构尚未完成验证，暂不宣称端到端原生支持已验收。**

```sh
brew install --cask metalsandbox/apps/steam-arm64
```

Tap 是 `metalsandbox/apps`，无需另建任务书中的 `homebrew-steam-arm64` 仓库。已添加 Tap 的用户也使用上述全名，避免同名冲突。Homebrew 6+ 的全名安装会授予该 Cask 信任，详见 [Tap Trust](https://docs.brew.sh/Tap-Trust)。

### 安装了什么

当前官方 DMG 的 `steam_osx` 经实测只有 x86_64。本 Cask 从 **Valve 官方 CDN 稳定更新清单**取得 Universal（arm64 + x86_64）bootstrapper，默认安装到 `/Applications/Steam.app`。首次打开后由 Steam 下载完整客户端。下载地址固定到具体包，SHA-256 固定在 Cask；不通过远程 shell 脚本安装，不重新签名或修改官方程序。

安装时强制验证 SHA-256、arm64 slice、Apple 信任锚与 Valve Team ID `MXGJJ98X76` 的深度严格代码签名。Gatekeeper 在候选发布时单独验证；在本机 Homebrew flight 沙盒内调用 `spctl` 返回安全服务内部错误，因此没有把它放入安装 hook。正常保留 Homebrew 隔离属性和 macOS 首次启动检查，不关闭 Gatekeeper，不移除 quarantine。

包中的 `SteamMacBootstrapper.tar.gz` 使用 Homebrew 原生 `container nested:` 解包。没有 Formula、常驻服务或额外安装依赖。

### 更新、重装、卸载

```sh
brew update
brew upgrade --cask --greedy metalsandbox/apps/steam-arm64
brew reinstall --cask metalsandbox/apps/steam-arm64
brew uninstall --cask metalsandbox/apps/steam-arm64
```

Homebrew 管理 bootstrapper，Steam 自己管理完整客户端。`auto_updates true` 的 Cask 默认不参加普通批量升级；明确使用 `--greedy` 以检查 bootstrapper 新版本。Steam 自更新不会改写 Homebrew 的安装版本记录。卸载仅移除应用及 Homebrew 管理记录；本 Cask 不包含 `zap`，不会清除 `~/Library/Application Support/Steam`、游戏、存档或账号配置。

安装、升级、重装、卸载前请完全退出 Steam。运行中的 `steam_osx`、`steamwebhelper` 或 `Steam` 会令操作中止。进程检查存在启动竞态，操作过程中不要重新启动 Steam。

### 已有 Steam 的迁移

1. 完全退出 Steam，并备份重要存档与 Steam 数据目录。
2. 若由官方 Cask 安装，执行 `brew uninstall --cask steam`，**不使用 `--zap`**。
3. 若手动安装，将 `/Applications/Steam.app` 移到一个安全备份位置，保留用户数据目录。
4. 执行本文安装命令，然后打开 Steam。

与官方 `steam` Cask 声明冲突；同一路径已有应用时由 Homebrew 标准 App 机制拒绝覆盖。不要用 `--force`、`--adopt` 或 `--zap` 绕过迁移检查。Homebrew 的 `--force` 是用户显式绕过标准保护的选项，本项目不对它提供覆盖安全保证。

下载或签名验证失败会中止操作。升级与重装遵循 Homebrew 标准备份/恢复机制；不能保证断电、磁盘损坏等情况下绝对回滚。请保留重要数据备份。

### Beta 与回退

当前 bootstrapper 来自稳定通道，含 arm64；安装器**不创建或改写 Beta 配置**，已有更新通道偏好保留。bootstrapper 含 arm64 并不能证明更新后的全部客户端也原生运行；若客户端仍以 Intel 运行，可在 Steam 设置 → 界面 → 客户端测试参与选择 Steam Beta Update 后重启，再验证。Beta 可用性和完整客户端架构取决于 Valve，尚未在本项目端到端验收。

回退：先在 Steam 设置中退出 Beta（如果曾加入），完全退出 Steam，然后：

```sh
brew uninstall --cask metalsandbox/apps/steam-arm64
brew install --cask steam
```

保留数据目录，官方 DMG bootstrapper 当前是 Intel 版本，启动可能需要 Rosetta。回退不会自动改变用户手动选择的 Beta 通道。

### 检查原生运行与签名

```sh
file /Applications/Steam.app/Contents/MacOS/steam_osx
lipo -archs /Applications/Steam.app/Contents/MacOS/steam_osx
codesign --verify --deep --strict --verbose=2 /Applications/Steam.app
codesign --verify --strict -R '=anchor apple generic and certificate leaf[subject.OU] = MXGJJ98X76' /Applications/Steam.app
spctl --assess --type execute --verbose /Applications/Steam.app
```

打开活动监视器，显示“种类”列，分别检查 Steam 主进程与 Steam Helper 是否为 Apple。Universal 文件包含 arm64 不代表当前进程使用 arm64。Steam 客户端原生运行也不代表所有 Steam 游戏支持 Apple Silicon，部分游戏仍需要 Rosetta 或完全不能在 macOS 运行。

### 故障排除

- **已有 Steam.app / Cask 冲突**：按迁移步骤处理，不强制覆盖。
- **Steam 正在运行**：退出菜单中的 Steam 并确认 Helper 结束后重试。
- **SHA-256、签名或 Gatekeeper 拒绝**：停止安装；保留错误信息，报告问题。不要改成 `:no_check`、重签名或关闭安全检查。
- **网络中断 / Valve CDN 不可达**：恢复网络后重试，不运行下载了一半的文件。
- **Intel Mac**：Cask 明确拒绝该架构，请使用官方 `steam`。
- **brew 不认识 `preflight_steps`**：更新 Homebrew 后重试。

## 维护

```sh
python3 -m unittest discover -s tests -v
python3 scripts/check-upstream.py            # 只报告变化
python3 scripts/check-upstream.py --verify   # macOS：下载并验证当前包
python3 scripts/check-upstream.py --write    # 验证成功后才写入候选更新
brew style --cask metalsandbox/apps/steam-arm64
brew audit --cask --strict metalsandbox/apps/steam-arm64
```

脚本只使用 Python 标准库及 macOS 自带工具；不运行 Steam。更新清单包含完整客户端的其他组件；只跟踪默认 `appdmg_osx` 包，不误选嵌套的 steamchina 包。包不变时不会因整个客户端 manifest 版本变化而更新 Cask。`livecheck` 明确跳过，实际检查由脚本执行。

[验证工作流](.github/workflows/validate-steam.yml) 在 ARM64 macOS 上执行单元测试、语法检查、隔离安装/重装/卸载；style/audit 仅在手动运行勾选 full_audit 后启用（可能在一次性 runner 上安装 Homebrew 校验工具）。[更新工作流](.github/workflows/update-steam.yml) 每天检查上游；候选必须经过下载 SHA-256、arm64、Valve 签名、Gatekeeper 以及 Homebrew 安装验证，才创建 PR；style/audit 需维护者另行选择手动验证，**不自动合并**。不重新分发 Valve 二进制。

仓库 Settings → Actions → General 必须允许 GitHub Actions 创建 Pull Request；工作流仅为更新 job 申请 contents/pull-requests 写权限。默认 `GITHUB_TOKEN` 创建的 PR 不会触发另一个 PR 工作流，因此更新 job 自身先完成校验；如需独立必需检查，可由维护者人工触发或改用最小权限 GitHub App。定时检查在工作流合入默认分支后生效。

技术记录与实际验证结果见 [docs/steam-arm64.md](docs/steam-arm64.md)。

## OffPDF

原有 OffPDF Cask 与更新流程保留。适用于 Apple Silicon、macOS 11 及更新版本。

```sh
brew install --cask metalsandbox/apps/offpdf
brew update
brew upgrade --cask metalsandbox/apps/offpdf
brew uninstall --cask metalsandbox/apps/offpdf
```

[OffPDF 上游](https://github.com/McanKul/offpdf)；[现有更新工作流](.github/workflows/update-offpdf.yml) 每日检查其官方发布。
