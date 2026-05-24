#!/bin/bash
# Phase 4a-1 stochastic 변동성 측정 — 4회 반복 verify
# 영구 경로 저장 (/tmp 손실 위험 차단)
RESULTS_DIR="$HOME/GuruNote/verify_results"
cd /Users/gesicht/GuruNote || exit 1
{
  echo "=== 4회 verify 시작: $(date) ==="
  echo "HEAD: $(git rev-parse HEAD)"
  echo "python: $(/Users/gesicht/GuruNote/.venv/bin/python3 --version)"
  echo ""
} > "${RESULTS_DIR}/run_4x.log"

for i in 1 2 3 4; do
    echo "=== run $i 시작: $(date) ===" >> "${RESULTS_DIR}/run_4x.log"
    /Users/gesicht/GuruNote/.venv/bin/python3 docs/wip/checkpoint4_realvideo_verify.py \
        > "${RESULTS_DIR}/realvideo_run${i}.md" 2>> "${RESULTS_DIR}/run_4x.log"
    rc=$?
    echo "=== run $i 종료 (rc=$rc): $(date) ===" >> "${RESULTS_DIR}/run_4x.log"
    if [ $i -lt 4 ]; then
        sleep 60
    fi
done
echo "=== 4회 verify 완료: $(date) ===" >> "${RESULTS_DIR}/run_4x.log"
