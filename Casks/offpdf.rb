cask "offpdf" do
  version "0.5.0"
  sha256 "ba9942cff43dc037c8a5771cf3839f5c0e001e3e5f6d8eed5c550866307b0416"

  url "https://github.com/McanKul/offpdf/releases/download/v#{version}/OffPDF_#{version}_aarch64.dmg"
  name "OffPDF"
  desc "Private, offline desktop PDF tools"
  homepage "https://github.com/McanKul/offpdf"

  livecheck do
    url :url
    strategy :github_latest
  end

  depends_on arch: :arm64
  depends_on macos: :big_sur

  app "OffPDF.app"
end
