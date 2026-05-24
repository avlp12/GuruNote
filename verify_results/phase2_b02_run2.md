=== 체크포인트 4 real video E2E verify ===
  reconstructed segments: 288
  MAX_SEGMENTS_PER_CHUNK: 15
  DEFAULT_CHUNK_CHAR_LIMIT: 12000
  예상 chunk 수: 20

=== translate_transcript 실행 (288 segments) ===
  [17:29:31] 🌐 LLM 번역 시작 — 20 청크 (openai_compatible/qwen3.6-35b-q5)
  [17:29:31] 📖 영상 컨텍스트(게시일/챕터/자막)를 LLM 에 주입합니다.
  [17:29:32]    📚 entity cache bootstrap — 4건 사전 추출
  [17:29:32]    ↳ 청크 1/20 번역 중…
  [17:29:38]    ⚠ 길이 미스매치: 11 != 15 (retry 1/3, finish_reason=stop)
  [17:30:13]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:30:13]    📚 entity cache 갱신: +1건 (누적 5건)
  [17:30:14]    ↳ 청크 2/20 번역 중…
  [17:30:19]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:30:20]    ↳ 청크 3/20 번역 중…
  [17:30:26]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:30:27]    ↳ 청크 4/20 번역 중…
  [17:30:34]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:30:35]    ↳ 청크 5/20 번역 중…
  [17:30:41]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:30:42]    ↳ 청크 6/20 번역 중…
  [17:30:50]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:30:51]    ↳ 청크 7/20 번역 중…
  [17:30:57]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:30:58]    ↳ 청크 8/20 번역 중…
  [17:31:12]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:31:13]    ↳ 청크 9/20 번역 중…
  [17:31:19]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:31:20]    ↳ 청크 10/20 번역 중…
  [17:31:26]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:31:27]    ↳ 청크 11/20 번역 중…
  [17:31:33]    ✅ Index Mapping 정합 — 15 outputs (finish_reason=stop)
  [17:31:34]    ↳ 청크 12/20 번역 중…
Traceback (most recent call last):
  File "/Users/gesicht/GuruNote/gurunote/llm.py", line 1346, in _call_with_wall_clock_timeout
    return future.result(timeout=timeout_sec)
           ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/concurrent/futures/_base.py", line 458, in result
    raise TimeoutError()
TimeoutError

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/Users/gesicht/GuruNote/docs/wip/checkpoint4_realvideo_verify.py", line 63, in <module>
    result = translate_transcript(
        transcript,
    ...<3 lines>...
        stop_event=None,
    )
  File "/Users/gesicht/GuruNote/gurunote/llm.py", line 1010, in translate_transcript
    translated = translate_chunk_index_mapping_v2(chunk, extended_context, config, log)
  File "/Users/gesicht/GuruNote/gurunote/llm.py", line 1624, in translate_chunk_index_mapping_v2
    outputs = _call_llm_with_index_mapping(
        config, prompt, expected_count=len(inputs), max_retries=3, log=log,
    )
  File "/Users/gesicht/GuruNote/gurunote/llm.py", line 1553, in _call_llm_with_index_mapping
    content, finish_reason = _call_llm_with_continuation(
                             ~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        config, messages, max_tokens, response_format=active_response_format
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/Users/gesicht/GuruNote/gurunote/llm.py", line 1466, in _call_llm_with_continuation
    content, finish_reason = _call_llm_once_with_reason(
                             ~~~~~~~~~~~~~~~~~~~~~~~~~~^
        config, current_messages, max_tokens, response_format, timeout=timeout
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/Users/gesicht/GuruNote/gurunote/llm.py", line 1401, in _call_llm_once_with_reason
    resp = _call_with_wall_clock_timeout(
        client.chat.completions.create,
        DEFAULT_LLM_CHUNK_TIMEOUT_SEC,
        **kwargs,
    )
  File "/Users/gesicht/GuruNote/gurunote/llm.py", line 1348, in _call_with_wall_clock_timeout
    raise TimeoutError(
        f"LLM 호출 wall-clock timeout — {timeout_sec}초 초과 (B02)"
    )
TimeoutError: LLM 호출 wall-clock timeout — 60.0초 초과 (B02)
