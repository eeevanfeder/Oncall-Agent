#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
project_src="$root/config/project.template.json"
user_src="$root/config/user.project.template.json"
project_dst="$root/config/project.json"
user_dst="$root/config/user.project.json"

if [[ ! -f "$project_dst" ]]; then
  cp "$project_src" "$project_dst"
fi

if [[ ! -f "$user_dst" ]]; then
  cp "$user_src" "$user_dst"
fi

echo "已准备被忽略的本机配置（如已存在则未覆盖）。请勿 git add 这些文件。"
