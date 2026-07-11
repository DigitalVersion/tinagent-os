#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"

PATTERN='tail7f125e|100\.(93\.112\.94|103\.234\.123|117\.243\.60)|/home/tin/Central_Command|\.important|DISCORD_.*WEBHOOK|CF_PAGES_API_TOKEN|OPENROUTER_API_KEY=[^F]'
FILES=$(find . -type f -not -path './.git/*' -not -path './docs/assets/*' -not -path './scripts/check-no-private-data.sh' -not -name '*.pyc')
if grep -InE "$PATTERN" $FILES; then
  echo "FAIL: private fleet data or secret-shaped content found"
  exit 1
fi

if find . -type f -not -path './.git/*' \( -name '*.pem' -o -name 'id_rsa*' -o -name '*.key' \) | grep -q .; then
  echo "FAIL: private key-shaped file found"
  exit 1
fi

echo "PASS: no private fleet domains, known private node IPs, secret files, or private workspace paths"
