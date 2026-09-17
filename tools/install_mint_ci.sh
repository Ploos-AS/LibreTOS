#!/usr/bin/env bash
set -euo pipefail

# Launchpad PPAs occasionally return transient 5xx errors. Keep Atari
# qualification deterministic while tolerating temporary mirror outages.
retry() {
    local attempt=1
    local max=5
    local delay=5
    while ! "$@"; do
        if [ "$attempt" -ge "$max" ]; then
            echo "command failed after ${max} attempts: $*" >&2
            return 1
        fi
        echo "attempt ${attempt}/${max} failed; retrying in ${delay}s: $*" >&2
        sleep "$delay"
        attempt=$((attempt + 1))
        delay=$((delay * 2))
    done
}

retry sudo add-apt-repository -y ppa:vriviere/ppa
retry sudo apt-get -o Acquire::Retries=5 update
retry sudo apt-get -o Acquire::Retries=5 install -y cross-mint-essential hatari xvfb git make

# Verify the installed tools independently of their informational version
# command exit conventions. Hatari 2.4.1 prints a valid version banner but
# exits with status 1 for --version on the Ubuntu runner.
command -v m68k-atari-mint-gcc >/dev/null
command -v hatari >/dev/null
m68k-atari-mint-gcc --version
hatari --version || true
