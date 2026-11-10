## 直接安装（不做 Homebrew SHA-256 校验）

开发分支新增 `Casks/autocad.rb`，固定 AutoCAD 2027.1 官方 CDN 地址，使用 `sha256 :no_check`。它绕过 Homebrew SHA-256 校验，但不绕过 macOS Gatekeeper/代码签名要求，也不跳过 Autodesk 授权。实机尚未验证 CDN 是否匿名可用及 Setup 路径是否与 2027 文档一致。

```sh
brew tap metalsandbox/apps
cd "$(brew --repository metalsandbox/apps)"
git fetch origin feat/autocad-local-cask
git switch --detach origin/feat/autocad-local-cask
brew install --cask ./Casks/autocad.rb
```

不要使用已过期或含 `session_id` 的下载地址。卸载配方只尝试删除主程序，其他共享 Autodesk 组件可能保留。

# AutoCAD for Mac via Homebrew (local Autodesk installer)

**Experimental / unverified on a Mac with AutoCAD installed.** This workflow is for a **legitimately obtained** Autodesk AutoCAD for Mac DMG from the user's own [Autodesk Account](https://manage.autodesk.com/). It does not bypass Autodesk licensing or distribute Autodesk binaries. Autodesk currently distributes AutoCAD for Mac through account-based downloads; this repository intentionally contains no fabricated public download URL or authentication token.

## Public-first distribution policy

**Priority 1: publicly shared, session-free Autodesk CDN links.** The Autodesk Community [2027 Product Download links](https://forums.autodesk.com/t5/installation-licensing-forum/2027-product-download-links/td-p/14055738) contains an AutoCAD 2027 Mac entry and is the current discovery source. The installation binary is downloaded directly from `efulfillment.autodesk.com`, never mirrored by this Tap.

```sh
python3 scripts/discover-autocad.py
python3 scripts/discover-autocad.py --json
```

The [weekly discovery workflow](../.github/workflows/discover-autocad.yml) checks this community thread and opens a **review issue** if it observes a newer release than the currently known 2027.1. It does **not** autonomously update the Cask, merge a PR, or download proprietary software. For future major releases, maintainers must update the thread source and baseline as needed. The community forum is user-maintained and may change HTML, split replies across pages, or lag behind Autodesk Account.

**Priority 2: private local DMG** as described below, if public downloading fails or an update has not appeared publicly.

Before shipping a public, directly installable `Casks/autocad.rb`, verify the URL without cookies/session ID, inspect the actual DMG, pin its SHA-256, audit code signing and `Setup` invocation, and test Homebrew installation/uninstallation on macOS. The current PR is discovery and local-install groundwork only; a verified public Cask is not yet available. Education licensing still requires Autodesk approval.

## Prepare and install

On macOS with Homebrew and Python 3:

```sh
brew tap metalsandbox/apps
cd "$(brew --repository metalsandbox/apps)"
python3 scripts/prepare-autocad-cask.py --dmg ~/Downloads/Autodesk_AutoCAD_2027_macOS.dmg --year 2027
brew install --cask ./Casks/autocad-local.rb
```

Use **your actual DMG filename** and product year. The script:
1. mounts the DMG read-only using macOS `hdiutil`;
2. discovers the actual vendor Setup executable (fails if missing or ambiguous);
3. calculates SHA-256 over the exact original DMG;
4. writes an **untracked, local-only** Cask with a `file://` URL and Autodesk's documented `Setup --silent` installer.

AutoCAD's Setup may request administrative authorization. A valid Autodesk account and license are still required for activation. Keep the original DMG: the Cask refers to its absolute path. The generated path and checksum may expose information about your machine, so **do not commit `Casks/autocad-local.rb`**. A source archive or Cask must never embed login cookies or Autodesk access tokens.

## Management and limitations

```sh
brew list --cask autocad-local
brew info --cask autocad-local
brew uninstall --cask autocad-local
```

**Caution:** Homebrew tracks this Cask and invokes Autodesk's installer; AutoCAD itself is installed by Autodesk Setup, which may place components outside the Caskroom. Uninstall currently targets only the expected version-specific app path; it does not clean shared Autodesk licensing services, user documents, or preferences. **Verify the exact installed app location before using the generated uninstall recipe.** If your installed AutoCAD includes an official `Remove AutoCAD` application, Autodesk recommends using it for complete product removal.

Upgrades are **not automatic**: download the newer official DMG, save it to a stable location, remove the old generated file after reviewing uninstall implications, regenerate with the new year or release, and use the vendor upgrade instructions. AutoCAD 2027.1 supports in-place updates within that release; major-year upgrades may install separately.

We have not yet verified whether your Homebrew version accepts a local `file://` Cask URL nor whether the latest installer layout matches the documented Setup path. Both are explicitly subject to a live macOS test. Do not use this for unattended fleet deployment without validation.

Sources:
- [Autodesk: Install AutoCAD for Mac](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-do-I-install-AutoCAD-for-MAC.html)
- [Autodesk: Deploy AutoCAD for Mac](https://www.autodesk.com/support/download-install/admins/account-deploy/deploy-autocad-for-mac)
- [Autodesk: Uninstall Autodesk software](https://www.autodesk.com/support/download-install/individuals/manage/uninstall-autodesk-software)
- [Homebrew: Cask Cookbook](https://docs.brew.sh/Cask-Cookbook)

## Immediate installation attempt: AutoCAD 2027.1

For a Mac with Homebrew, clone the development branch and run its installer. It downloads the session-free official Autodesk URL (the request may fail if Autodesk requires authentication), validates the DMG with `hdiutil verify`, computes its actual SHA-256, generates a local Cask and invokes Homebrew.

```sh
brew tap metalsandbox/apps
cd "$(brew --repository metalsandbox/apps)"
git fetch origin feat/autocad-local-cask
git switch --detach origin/feat/autocad-local-cask
bash scripts/install-autocad-2027.sh
```

**Warning:** this has not yet been tested against the real AutoCAD 2027.1 DMG on macOS. If Autodesk blocks the anonymous download, download the official DMG through Autodesk Account, then use `python3 scripts/prepare-autocad-cask.py --dmg /actual/path/Autodesk_AutoCAD_2027.1_macOS.dmg --year 2027` and `brew install --cask ./Casks/autocad-local.rb`. If you see an installation error, preserve the output for debugging rather than disabling security checks.

Keep the generated Cask, cached source DMG and Homebrew installation record together. This is not yet a fully tested direct `brew install metalsandbox/apps/autocad` implementation.
