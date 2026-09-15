#!/bin/bash
# Wrapper — canonical script: .github/actions/new-ai-project/new-ai-project.sh
# Kept here for manual runs on the EC2 and existing runbook paths.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
exec bash "${ROOT}/.github/actions/new-ai-project/new-ai-project.sh" "$@"
