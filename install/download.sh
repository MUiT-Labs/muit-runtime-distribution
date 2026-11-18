#!/bin/sh
# Downloads/verification only. No root, service changes, shell-piped downloads.
set -eu
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec python3 "$script_dir/download.py" "$@"
