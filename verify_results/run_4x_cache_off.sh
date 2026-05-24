#!/bin/bash
# 캐시 OFF 상태 4회 반복 검증
RESULTS_DIR="$HOME/GuruNote/verify_results"
cd /Users/gesicht/GuruNote || exit 1
{
  echo "=== 캐시 OFF 4회 검증 시작: $(date) ==="
  echo "HEAD: $(git rev-parse HEAD)"
  echo "omlx cache.enabled: OFF (대시보드 확인)"
  echo ""
  for i in 1 2 3 4; do
    echo "=== run $i 시작: $(date) ==="
    /Users/gesicht/GuruNote/.venv/bin/python3 docs/wip/checkpoint4_realvideo_verify.py \
      > "${RESULTS_DIR}/cache_off_run${i}.md" 2>&1
    rc=$?
    echo "=== run $i 종료 (rc=$rc): $(date) ==="
    if [ $i -lt 4 ]; then
      sleep 60
    fi
  done
  echo "=== 4회 검증 완료: $(date) ==="
} > "${RESULTS_DIR}/cache_off_master.log" 2>&1
