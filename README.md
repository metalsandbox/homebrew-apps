# OffPDF Homebrew tap

This tap installs [OffPDF](https://github.com/McanKul/offpdf) on Apple Silicon Macs running macOS 11 or later. OffPDF does not publish an Intel Mac installer.

## Publish this tap

This directory is already a local Git repository. After signing in to GitHub CLI, publish it as a public repository named `homebrew-apps`:

```sh
git add Casks/offpdf.rb scripts/update_offpdf.py .github/workflows/update-offpdf.yml README.md
git commit -m "Add OffPDF Homebrew tap"
gh auth login
gh repo create homebrew-apps --public --source=. --remote=origin --push
```

In the repository's **Settings → Actions → General → Workflow permissions**, select **Read and write permissions** so the update workflow can commit new cask versions. If the default branch is protected, allow GitHub Actions to push to it or adapt the workflow to open pull requests.

Replace `YOUR_GITHUB_USERNAME` below with your GitHub username:

```sh
brew tap YOUR_GITHUB_USERNAME/apps
brew install --cask YOUR_GITHUB_USERNAME/apps/offpdf
```

To install a later version after the tap updates:

```sh
brew update
brew upgrade --cask YOUR_GITHUB_USERNAME/apps/offpdf
```

To uninstall:

```sh
brew uninstall --cask YOUR_GITHUB_USERNAME/apps/offpdf
```

The [update workflow](.github/workflows/update-offpdf.yml) checks the latest official release daily and can also be run from the Actions tab. It updates the cask version and SHA-256 only when an Apple Silicon DMG is available. OffPDF itself has no in-app auto-update; Homebrew upgrades occur when you run `brew upgrade` (or automate that command on your Mac).
