#!/bin/bash
# B02 추가 verify 2회 — '판카지' 회귀 결정론 catch
RESULTS_DIR="$HOME/GuruNote/verify_results"
cd /Users/gesicht/GuruNote || exit 1
{
  echo "=== B02 추가 verify 시작: $(date) ==="
  echo "HEAD: $(git rev-parse HEAD)"
  echo ""
  for i in 2 3; do
    echo "=== B02 extra run $i 시작: $(date) ==="
    /Users/gesicht/GuruNote/.venv/bin/python3 docs/wip/checkpoint4_realvideo_verify.py \
      > "${RESULTS_DIR}/phase2_b02_run${i}.md" 2>&1
    rc=$?
    echo "=== B02 extra run $i 종료 (rc=$rc): $(date) ==="
    if [ $i -lt 3 ]; then
      sleep 30
    fi
  done
  echo "=== B02 추가 verify 완료: $(date) ==="
} > "${RESULTS_DIR}/b02_extra_master.log" 2>&1
