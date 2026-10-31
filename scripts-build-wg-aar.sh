#!/usr/bin/env bash
# Build the Relay-derived userspace WireGuard/gVisor engine for Android.
# Requires Go 1.25+, Android SDK and NDK r27+.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
MOD="$ROOT/third_party/relay-wg"
OUT="$ROOT/android/app/libs"
NDK="${ANDROID_NDK_LATEST_HOME:-${ANDROID_NDK_HOME:-}}"
SDK="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-}}"
[[ -n "$NDK" && -d "$NDK" ]] || { echo 'ANDROID_NDK_HOME is required' >&2; exit 2; }
[[ -n "$SDK" && -d "$SDK" ]] || { echo 'ANDROID_HOME is required' >&2; exit 2; }
export ANDROID_NDK_HOME="$NDK" ANDROID_HOME="$SDK" GOTOOLCHAIN=auto
cd "$MOD"
MOBILE_VERSION="$(go list -m -f '{{.Version}}' golang.org/x/mobile)"
go install "golang.org/x/mobile/cmd/gomobile@$MOBILE_VERSION"
go install "golang.org/x/mobile/cmd/gobind@$MOBILE_VERSION"
export PATH="$(go env GOPATH)/bin:$PATH"
gomobile init
mkdir -p "$OUT"
gomobile bind -target=android/arm64,android/arm,android/amd64,android/386 \
  -androidapi 26 -ldflags='-s -w -extldflags=-Wl,-z,max-page-size=16384' \
  -o "$OUT/relaywg.aar" .
# Fail if the artifact is missing or empty; Gradle must never silently ship without it.
test -s "$OUT/relaywg.aar"
echo "Built $OUT/relaywg.aar"
