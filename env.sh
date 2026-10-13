# Source this before working:  source env.sh
# Puts the project's tools on PATH (nothing is installed system-wide).
export JAVA_HOME="$(/usr/libexec/java_home -v 21)"
export PATH="$JAVA_HOME/bin:/opt/homebrew/opt/gnu-sed/libexec/gnubin:/opt/homebrew/opt/llvm/bin:$HOME/Applications/Wine Devel.app/Contents/Resources/wine/bin:$PATH"
export WINEPREFIX="$HOME/.wine-hoennb2"
export WINEDEBUG=-all
export HOENN="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
alias ctrmap='java -jar "$HOENN/tools/CTRMap.jar"'
alias melonds='open -a "$HOME/Applications/melonDS.app"'
alias blender='$HOME/Applications/Blender.app/Contents/MacOS/Blender'
export SDL_AUDIODRIVER=dummy   # emulator tests are silent
