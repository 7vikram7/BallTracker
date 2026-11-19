# Source before building:  source mobile/scripts/env.sh
# Java 17 and the Android SDK as installed on this Mac (no system-wide changes).
export JAVA_HOME="$HOME/.local/toolchains/jdk-17.0.21+9/Contents/Home"
export ANDROID_HOME="$HOME/Library/Android/sdk"
export ANDROID_SDK_ROOT="$ANDROID_HOME"
export PATH="$JAVA_HOME/bin:$ANDROID_HOME/platform-tools:$ANDROID_HOME/cmdline-tools/latest/bin:$PATH"
export PATH="/usr/local/opt/node/bin:$PATH"   # Node 26 from Homebrew (Expo 58 needs Node >= 22.13)
# CocoaPods (iOS builds): installed with Homebrew's bundled Ruby into ~/.local/gems (no system changes).
# If a Homebrew update breaks it: $RUBY_BIN/gem install --no-document cocoapods
export RUBY_BIN="/usr/local/Homebrew/Library/Homebrew/vendor/portable-ruby/current/bin"
export GEM_HOME="$HOME/.local/gems"
export PATH="$GEM_HOME/bin:$RUBY_BIN:$PATH"
export LANG="${LANG:-en_US.UTF-8}"
