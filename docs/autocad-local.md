# AutoCAD for Mac via Homebrew (local Autodesk installer)

**Experimental / unverified on a Mac with AutoCAD installed.** This workflow is for a **legitimately obtained** Autodesk AutoCAD for Mac DMG from the user's own [Autodesk Account](https://manage.autodesk.com/). It does not bypass Autodesk licensing or distribute Autodesk binaries. Autodesk currently distributes AutoCAD for Mac through account-based downloads; this repository intentionally contains no fabricated public download URL or authentication token.

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
