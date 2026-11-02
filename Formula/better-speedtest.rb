class BetterSpeedtest < Formula
  desc "Multi-source command-line network speed test"
  homepage "https://github.com/Gaimoydev/better-speedtest"
  version "0.0.3"
  license "MIT"

  depends_on :macos

  on_macos do
    on_arm do
      url "https://github.com/Gaimoydev/better-speedtest/releases/download/v#{version}/better-speedtest-darwin-arm64.tar.gz"
      sha256 "c7c12fee0baa964b2618f2c887c08bbd9235046a891c239d8430770b6a31c26b"
    end
    on_intel do
      url "https://github.com/Gaimoydev/better-speedtest/releases/download/v#{version}/better-speedtest-darwin-amd64.tar.gz"
      sha256 "e884391522c942939bf3593312eae726461513dacef2c926f85594cd23845f58"
    end
  end

  def install
    arch = Hardware::CPU.arm? ? "arm64" : "amd64"
    bin.install "better-speedtest-darwin-#{arch}" => "better-speedtest"
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/better-speedtest version")
    (testpath/"invalid.json").write("{")
    ENV["BETTER_SPEEDTEST_CONFIG"] = testpath/"invalid.json"
    assert_match "配置加载失败", shell_output("#{bin}/better-speedtest nodes --src cdn 2>&1", 1)
  end
end
