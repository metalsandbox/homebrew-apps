cask "canon-print" do
  version "2.0"
  sha256 "7b9abfbe4c05101203e86da490bf1c7bfe0a56063fef46f3e12f40af9a526fba"

  url "https://gdlp01.c-wss.com/gds/4/0200007744/01/mCSC-mac-2_0-ea21_3.dmg"
  name "Canon PRINT"
  desc "Access and manage compatible Canon inkjet printers"
  homepage "https://www.canon.com.cn/supports/download/simsdetail/0200774411.html?modelId=10157&channel=1"

  depends_on macos: :big_sur

  app "Canon Inkjet Smart Connect.app"
end
