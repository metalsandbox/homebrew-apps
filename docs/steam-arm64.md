# Steam ARM64 technical decision and validation record

Date: 2026-10-23 (Asia/Shanghai). Host: Apple Silicon arm64, macOS 27.0.1 (26A434), Homebrew 7.0.10.

## Research and decisions

- Keep the existing `metalsandbox/homebrew-apps` repository and its OffPDF cask. Canonical Steam name: `metalsandbox/apps/steam-arm64`.
- Read Valve's actual stable manifest (`steam_client_osx`), rather than assuming community README claims remain true. Manifest version: `1792618285`. Default `appdmg_osx.file`: `appdmg_osx.zip.984652b88a9737e3f4e77c656d9ffa67d5042c2c`; SHA-256: `8bf4ce8b4bcbc50f642988c955559f605e7a877372116e7a2b3fd1355004bedb`; size: 4,825,452 bytes.
- Manifest also contains component paths, sizes, SHA-256 (`sha2`), optional compressed variants (`zipvz`, `sha2vz`), alternate Steam China packages and signature blocks. The script does not independently authenticate Valve's manifest signature scheme; trust is TLS plus a reviewed, pinned SHA-256 and Apple's Valve Developer ID verification. Never claim the hash alone authenticates the publisher.
- Actual ZIP entries: `SteamMacBootstrapper.tar.gz`, `SteamMacBootstrapper.version`. TAR contains `Steam.app`. Apple's `ditto -x -k` rejects this ZIP variant, while system `unzip` and Homebrew's ZIP strategy succeed. `container nested: "SteamMacBootstrapper.tar.gz", type: :zip` works in an actual Homebrew installation.
- Actual bootstrapper binary is Universal x86_64 + arm64. Deep strict signature verification succeeds; Apple requirement and Valve Team ID `MXGJJ98X76` verification succeeds. Gatekeeper reports `accepted`, `source=Notarized Developer ID` outside the Homebrew flight sandbox.
- Official DMG downloaded from `https://cdn.fastly.steamstatic.com/client/installer/steam.dmg`, mounted read-only and inspected: its `Steam.app/Contents/MacOS/steam_osx` is x86_64 only. Image unmounted after inspection.
- Bootstrapper Info.plist declares macOS 10.13; this is not the full client's support floor. Set macOS 12 based on Valve's current client support policy.
- Stable bootstrapper itself contains arm64; no Beta files are written or changed. Full updated client's stable/Beta architecture and all helper process architectures remain unverified. Existing channel preferences remain intact.
- Homebrew 7 deprecates `url verified:` and string `depends_on macos: ">= :monterey"`; implementation uses current declarations. Use constrained `preflight_steps` and `uninstall_preflight_steps`, not legacy Ruby hooks or internal APIs.
- `codesign -R` inline requirements require the leading `=`. Initial PoC caught this error; fixed before successful installation.
- `spctl` inside Homebrew flight sandbox fails with `internal error in Code Signing subsystem` on this host. It is therefore a mandatory separate candidate-verification check, not an install hook. SHA-256, architecture and Valve signature remain mandatory in Cask install. Gatekeeper and quarantine remain enabled for first launch.
- `auto_updates true` separates Valve self-updates from bootstrapper updates. Use `--greedy`; the script tracks package changes, not unrelated whole-client manifest bumps.

## Actual results

| Check | Result |
| --- | --- |
| Cask Ruby syntax | PASS using existing Homebrew portable Ruby |
| Homebrew Cask DSL / JSON parsing | PASS |
| Four standard-library unit tests | PASS: default vs nested China selection; invalid path/hash; truncated/duplicate manifest; checksum mismatch before extraction |
| Actual Valve ZIP SHA-256 | PASS, matches manifest and Cask |
| `file` / `lipo` arm64 | PASS |
| `codesign --verify --deep --strict` | PASS outside sandbox and during Homebrew install |
| Apple anchor + Valve Team ID requirement | PASS during install and standalone verifier |
| `spctl --assess --type execute` | PASS on original staged app and Homebrew-installed app outside flight sandbox |
| Standalone `check-upstream.py --verify` | PASS, including ZIP/TAR layout/path checks |
| Fresh Homebrew install | PASS in isolated workspace appdir |
| Repeated install | PASS, already installed warning |
| Reinstall | PASS, uses the original configured appdir |
| Uninstall | PASS, isolated app removed |
| Existing manually installed app | PASS, Homebrew refused and preserved a sentinel inside the original directory |
| Running process guard | PASS, compiled harmless fixture named `steam_osx`; uninstall refused and app preserved |
| Ordinary and `--greedy` upgrade, same version | Both report current version already installed |
| Final Cask regression install/uninstall | PASS after adding fail-closed handling for process-enumeration errors |
| `git diff --check` | PASS |
| `brew style` / full strict audit | NOT RUN: required tooling absent; user explicitly declined dependency installation |
| Changed-version upgrade / rollback fault injection | NOT TESTED; same-version behavior is not evidence of upgrade success |
| Actual interrupted network / Cask checksum failure | NOT TESTED; script checksum rejection tested, Homebrew standard behavior relied upon |
| Existing official `steam` cask conflict | DSL declaration validated; not installed for destructive migration testing |
| Intel machine / older macOS | Requirement parsed; no physical machine test |
| Default `/Applications` placement | Standard Cask `app` target parsed; actual installs used isolated appdir |
| Full client first launch, self-update, login, native processes | NOT TESTED; Steam was never launched |
| Machine without Rosetta | Not tested; arm64 slice verified, no Rosetta installation requested |

The initial fake process fixture copied from `/bin/sleep` was killed by macOS and did not exercise the process guard. It was replaced by a small locally compiled C fixture; that valid fixture confirmed the guard. No misleading result from the failed fixture is counted as a passing test.

## Maintenance and remaining scope

Run `python3 scripts/check-upstream.py` to inspect changes, or `--verify` for the currently published package. `--write` verifies before atomically editing the Cask. Unknown package paths, malformed manifests, unexpected ZIP members, unsafe TAR paths/links, digest mismatches and failed signature/Gatekeeper checks abort the candidate update.

The scheduled workflow proposes a PR only after package verification and isolated Homebrew installation. It never merges automatically. CI's default validation does not install style/audit dependencies; a maintainer may explicitly opt into `full_audit` in a manual run. Local style/audit remain uncompleted per the user's dependency constraint.

Before claiming full native Steam support, test first-run update and inspect both the main Steam and helper process kinds in Activity Monitor; repeat signature and Gatekeeper checks after self-update. Test changed-version upgrade/rollback separately. Do not interpret successful bootstrapper installation as completion of these remaining acceptance items.

## Primary references

- [Homebrew Tap maintenance](https://docs.brew.sh/How-to-Create-and-Maintain-a-Tap)
- [Cask Cookbook: container, steps, conflicts, dependencies](https://docs.brew.sh/Cask-Cookbook)
- [Cask Language Reference](https://docs.brew.sh/Cask-Language-Reference) (web fetch unavailable; current Cookbook and installed Homebrew source inspected)
- [Tap Trust](https://docs.brew.sh/Tap-Trust)
- [Valve stable manifest](https://client-update.steamstatic.com/steam_client_osx)
- [Valve client macOS support](https://help.steampowered.com/en/faqs/view/659D-A19E-018A-81A6)
- [Community implementation](https://github.com/i1rr/steam-arm64-mac) (background reference only; no code or binary repackaging)
- [GitHub runner architecture labels](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)
