cask "autocad" do
  version "2027.1"
  sha256 :no_check

  url "https://efulfillment.autodesk.com/NetSWDLD/ODIS/prd/2027/ACDMAC/DA13C2BB-9635-3AD7-9E72-CB16D8C17DB6/SFX/Autodesk_AutoCAD_2027.1_macOS.dmg"
  name "Autodesk AutoCAD 2027 for Mac"
  desc "Autodesk 2D and 3D CAD design software"
  homepage "https://www.autodesk.com/products/autocad/overview"

  generated_script "install-autocad.sh", content: <<~SH
    #!/bin/sh
    set -eu
    staged_dir='#{staged_path}'
    setup_path=''
    while IFS= read -r candidate; do
      if [ -n "$setup_path" ]; then
        echo "Multiple Autodesk Setup executables found; refusing ambiguous install." >&2
        exit 1
      fi
      setup_path="$candidate"
    done <<EOF
    $(/usr/bin/find "$staged_dir" -type f -path '*/Contents/Helper/Setup.app/Contents/MacOS/Setup' -print)
    EOF
    if [ -z "$setup_path" ]; then
      echo "Autodesk Setup executable missing from downloaded DMG." >&2
      exit 1
    fi
    exec "$setup_path" --silent
  SH

  installer script: {
    executable: "install-autocad.sh",
    sudo:       true,
  }

  uninstall delete: "/Applications/Autodesk/AutoCAD 2027/AutoCAD 2027.app"

  livecheck do
    skip "Community-published official download links are reviewed separately"
  end

  caveats <<~EOS
    An eligible Autodesk account or license is required to activate AutoCAD.
    This Cask uses a public Autodesk CDN URL without a session identifier.
    If Autodesk restricts the URL or changes the installer layout, installation may fail.
    Uninstall may leave Autodesk licensing components and user data installed.
  EOS
end
