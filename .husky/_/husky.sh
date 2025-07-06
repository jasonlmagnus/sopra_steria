#!/bin/sh
if [ -f "$(git rev-parse --git-dir)/hooks/husky.sh" ]; then
  . "$(git rev-parse --git-dir)/hooks/husky.sh"
fi
