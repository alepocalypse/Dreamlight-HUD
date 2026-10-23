#!/usr/bin/env bash
cd "$(dirname "$0")" && exec python3 -m ddvhud --port "${PORT:-8798}" "$@"
