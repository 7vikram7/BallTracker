#!/bin/bash
# Install the BallTracker camera app on an iPhone connected by cable (free Apple ID signing).
#
#   mobile/scripts/install_ios.sh            # the iPhone on the cable (asks if there are several)
#   mobile/scripts/install_ios.sh <udid>     # a specific one
#
# A new iPhone takes about 2-4 minutes: Trust this Mac, turn on Developer Mode (the phone restarts),
# the phone is added to the signing profile (the Mac needs internet for that), build, install.
# Afterwards on the phone: Settings > General > VPN & Device Management > trust the developer.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
MOBILE="$(dirname "$HERE")"
source "$HERE/env.sh"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

devices() {  # udid<TAB>name<TAB>pairing<TAB>transport<TAB>developer mode
  xcrun devicectl list devices --json-output "$TMP/d.json" >/dev/null 2>&1
  python3 - "$TMP/d.json" <<'EOF'
import json, sys
for x in json.load(open(sys.argv[1]))["result"]["devices"]:
    h, c, p = x.get("hardwareProperties", {}), x.get("connectionProperties", {}), x.get("deviceProperties", {})
    if h.get("platform") == "iOS" and h.get("udid"):
        print("\t".join(str(v) for v in (h["udid"], p.get("name", "?"), c.get("pairingState"), c.get("transportType"), p.get("developerModeStatus"))))
EOF
}

UDID="${1:-}"
if [ -z "$UDID" ]; then
  WIRED="$(devices | awk -F'\t' '$4=="wired"')"
  if [ -z "$WIRED" ]; then echo "No iPhone on the cable. Plug it in, unlock it, and run again."; exit 1; fi
  if [ "$(echo "$WIRED" | wc -l)" -gt 1 ]; then
    echo "Several iPhones on cables:"; echo "$WIRED" | awk -F'\t' '{print "  " $1 "  " $2}'
    echo "Run again with the udid of the one to install."; exit 1
  fi
  UDID="$(echo "$WIRED" | cut -f1)"
fi
row() { devices | awk -F'\t' -v u="$UDID" '$1==u'; }
echo "iPhone: $(row | cut -f2) ($UDID)"

if [ "$(row | cut -f3)" != "paired" ]; then
  echo ">> On the iPhone: tap 'Trust This Computer' and enter the passcode."
  xcrun devicectl manage pair --device "$UDID" >/dev/null
fi
if [ "$(row | cut -f5)" != "enabled" ]; then
  echo ">> On the iPhone: Settings > Privacy & Security > Developer Mode > On, restart, then 'Turn On'."
  echo "   (If Developer Mode is not in the list yet, close and reopen Settings.) Waiting..."
  until [ "$(row | cut -f5)" = "enabled" ]; do sleep 5; done
  echo "   Developer Mode is on. Unlock the phone."
fi

echo ">> Building (adds this iPhone to the signing profile)..."
LOG="$TMP/build.log"
if ! xcodebuild -workspace "$MOBILE/ios/BallTrackerCam.xcworkspace" -scheme BallTrackerCam -configuration Release \
    -destination "id=$UDID" -allowProvisioningUpdates -allowProvisioningDeviceRegistration \
    COCOAPODS_PARALLEL_CODE_SIGN=true COMPILER_INDEX_STORE_ENABLE=NO build >"$LOG" 2>&1; then
  grep -E "error:|❌" "$LOG" | sort -u | head -10
  echo "Build failed (full log above). If it mentions the device limit: a free Apple ID can only"
  echo "sign a few devices; remove an old one in Xcode > Settings > Accounts, or use the web link."
  exit 1
fi
APP="$(grep -m1 -oE 'CODESIGNING_FOLDER_PATH\\?=.*/BallTrackerCam\.app' "$LOG" | sed -E 's/.*=//')"
[ -d "$APP" ] || APP="$(ls -dt ~/Library/Developer/Xcode/DerivedData/BallTrackerCam-*/Build/Products/Release-iphoneos/BallTrackerCam.app | head -1)"

echo ">> Installing (keep the phone unlocked)..."
until xcrun devicectl device install app --device "$UDID" "$APP" >"$TMP/inst.log" 2>&1; do
  if grep -q "Locked" "$TMP/inst.log"; then echo "   Unlock the iPhone..."; sleep 5; else cat "$TMP/inst.log"; exit 1; fi
done
if xcrun devicectl device process launch --device "$UDID" dev.balltracker.cam >"$TMP/run.log" 2>&1; then
  echo "Done: BallTracker Cam is open on the iPhone."
else
  echo "Installed. First time only, on the iPhone: Settings > General > VPN & Device Management >"
  echo "tap the developer (your Apple ID) > Trust. Then open BallTracker Cam."
fi
