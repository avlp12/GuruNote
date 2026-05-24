#!/bin/bash
# Phase 3 추가 verify 2회 (run 2, run 3)
RESULTS_DIR="$HOME/GuruNote/verify_results"
cd /Users/gesicht/GuruNote || exit 1
{
  echo "=== Phase 3 추가 2회 verify 시작: $(date) ==="
  echo "HEAD: $(git rev-parse HEAD) (Phase 3 unstaged)"
  echo "omlx cache: ON (사용자 대시보드 확인)"
  echo ""
  for i in 2 3; do
    echo "=== Phase 3 run $i 시작: $(date) ==="
    /Users/gesicht/GuruNote/.venv/bin/python3 docs/wip/checkpoint4_realvideo_verify.py \
      > "${RESULTS_DIR}/phase3_run${i}.md" 2>&1
    rc=$?
    echo "=== Phase 3 run $i 종료 (rc=$rc): $(date) ==="
    if [ $i -lt 3 ]; then
      sleep 60
    fi
  done
  echo "=== Phase 3 추가 verify 완료: $(date) ==="
} > "${RESULTS_DIR}/phase3_extra_master.log" 2>&1
