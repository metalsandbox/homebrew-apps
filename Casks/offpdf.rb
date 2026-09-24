cask "offpdf" do
  version "0.3.2"
  sha256 "db147a93566cc0348e1dd7f5a9def9afb217e81894a01237f2232a58926bece9"

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
