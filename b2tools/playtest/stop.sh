#!/bin/zsh
# stop my own emulator runs (python -u tools/<my script>.py, started from work/agents/playthrough)
for pid in $(pgrep -f -- "-u tools/(phase|tz|tour|poke|do|run|chap|ruby|s[0-9]+|t[0-9]+)\.py"); do
  cwd=$(lsof -a -p $pid -d cwd -Fn 2>/dev/null | grep '^n' | cut -c2-)
  if [[ "$cwd" == *agents/playthrough* ]]; then kill $pid; sleep 1; kill -9 $pid 2>/dev/null; echo "stopped $pid"; fi
done
