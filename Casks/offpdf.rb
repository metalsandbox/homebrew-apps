cask "offpdf" do
  version "0.4.0"
  sha256 "596659d480622ca10e42e37f016b852e70180f76b2f212f098f0df88ac8e247c"

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
