cask "steam-arm64" do
  version "1792618285"
  sha256 "8bf4ce8b4bcbc50f642988c955559f605e7a877372116e7a2b3fd1355004bedb"

  url "https://client-update.steamstatic.com/appdmg_osx.zip.984652b88a9737e3f4e77c656d9ffa67d5042c2c"
  name "Steam ARM64"
  desc "Valve Steam bootstrapper with native Apple Silicon support"
  homepage "https://store.steampowered.com/about/"

  livecheck do
    skip "Bootstrapper updates are checked and verified by scripts/check-upstream.py"
  end

  auto_updates true
  conflicts_with cask: "steam"
  depends_on arch: :arm64
  depends_on macos: :monterey
  container nested: "SteamMacBootstrapper.tar.gz", type: :zip

  app "Steam.app"

  preflight_steps do
    run "/bin/sh", args: ["-c", <<~SH]
      /usr/bin/pgrep -x 'steam_osx|steamwebhelper|Steam' >/dev/null
      status=$?
      case "$status" in
        0) echo 'Quit Steam before installing or upgrading.' >&2; exit 1 ;;
        1) exit 0 ;;
        *) echo 'Unable to check running Steam processes; stopping.' >&2; exit 1 ;;
      esac
    SH
    run "/usr/bin/lipo", args: ["{{staged_path}}/Steam.app/Contents/MacOS/steam_osx", "-verify_arch", "arm64"]
    run "/usr/bin/codesign",
        args: [
          "--verify", "--deep", "--strict", "-R",
          "=anchor apple generic and certificate leaf[subject.OU] = MXGJJ98X76",
          "{{staged_path}}/Steam.app",
        ]
  end

  uninstall_preflight_steps do
    run "/bin/sh", args: ["-c", <<~SH]
      /usr/bin/pgrep -x 'steam_osx|steamwebhelper|Steam' >/dev/null
      status=$?
      case "$status" in
        0) echo 'Quit Steam before uninstalling.' >&2; exit 1 ;;
        1) exit 0 ;;
        *) echo 'Unable to check running Steam processes; stopping.' >&2; exit 1 ;;
      esac
    SH
  end

  caveats <<~EOS
    Launch Steam to download the full client from Valve.
    Existing update-channel preferences and game data are preserved.
    To upgrade the Homebrew bootstrapper, use:
      brew upgrade --cask --greedy metalsandbox/apps/steam-arm64
    Native client support does not imply native Apple Silicon game support.
  EOS
end
