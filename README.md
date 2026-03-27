# LangGraph Architecture Blueprint (Plan + Tool Selector + Parallel Action)

요구사항:
- LangGraph 중심으로 전체 아키텍처 구성
- 먼저 Plan 수립
- Tool Selector에서 각 액션의 실행 가능 여부를 `executable: true | false`로 판정
- 실행 가능한 액션은 병렬 실행
- 여러 업무(Task)를 동시에 처리

---

## 1) 전체 구조 (High-Level)

```text
[Client/API]
   |
   v
[Request Normalizer]
   |
   v
[LangGraph Orchestrator]
   |
   +--> (A) PLAN Graph
   |       - Intent Parse
   |       - Task Decomposition
   |       - Action Plan Generation
   |
   +--> (B) TOOL SELECTOR Graph
   |       - each action -> executable true/false
   |       - dependency check
   |       - safety/policy check
   |
   +--> (C) ACTION Graph
   |       - executable=true actions in parallel
   |       - executable=false actions skip/defer
   |       - collect outputs
   |
   +--> (D) SYNTHESIS Graph
           - merge results
           - retry/fallback decision
           - final response

[Observability]
- LangSmith Trace
- Structured Logs
- Metrics (latency/cost/success)
```

---

## 2) 핵심 개념

### PLAN (paln) 우선
1. 입력을 하나의 요청으로 보지 않고, 복수 Task로 분해
2. Task별로 Action 목록 생성
3. Action 간 의존성(선행/후행) 정의

### Tool Selector의 executable 플래그
각 Action에 대해 아래를 판정:
- 정책 위반 여부
- 권한 보유 여부
- 도구 가용성 여부
- 선행 의존성 충족 여부

결과 예시:
- `executable: true`  -> 즉시 실행 가능
- `executable: false` -> 스킵/보류/사람 승인 대기

### 병렬 실행
- 의존성이 없는 `executable=true` Action은 동시 실행
- 의존성이 있는 Action은 조건 충족 후 실행
- 부분 실패는 전체 실패가 아니라 “부분 완료 + 후속 처리”로 전환

---

## 3) State 설계 (LangGraph Shared State)

```yaml
AgentState:
  request_id: str
  user_id: str
  session_id: str
  user_goal: str

  tasks:                       # 분해된 업무 단위
    - task_id: str
      description: str
      priority: int

  plan_actions:                # PLAN 결과
    - action_id: str
      task_id: str
      tool_name: str
      input: dict
      dependencies: [action_id]
      executable: bool         # Tool Selector에서 확정
      reason: str              # false인 이유 또는 true 근거

  action_results:
    - action_id: str
      status: "success|failed|skipped|deferred"
      output: dict
      error: str

  policy_flags: [str]
  retry_queue: [action_id]
  deferred_queue: [action_id]

  final_answer: str
  summary: dict
```

---

## 4) Graph 설계

## 4.1 PLAN Graph
노드:
1. `parse_intent_node`
2. `decompose_tasks_node`
3. `build_action_plan_node`

출력:
- `tasks`
- `plan_actions (초안, executable 미확정)`

## 4.2 TOOL SELECTOR Graph
노드:
1. `policy_check_node`
2. `capability_check_node`
3. `dependency_check_node`
4. `set_executable_flag_node`

출력:
- 각 Action에 `executable: true/false`
- `reason`

## 4.3 ACTION Graph
노드:
1. `parallel_dispatch_node`
2. `tool_executor_node`
3. `collect_results_node`
4. `retry_or_defer_node`

동작:
- `executable=true` + `dependencies satisfied` => 병렬 실행
- `executable=false` => skipped/deferred 처리
- 실패 Action은 정책에 따라 재시도 또는 보류 큐 이동

## 4.4 SYNTHESIS Graph
노드:
1. `merge_outputs_node`
2. `quality_guard_node`
3. `response_writer_node`

출력:
- 최종 응답
- 작업별 처리 요약(성공/실패/보류)

---

## 5) 다중 업무 동시 수행 전략

### 전략 A: Task-level Fan-out
- Task를 분해한 뒤, Task별 Action DAG를 독립적으로 실행
- 최종 단계에서 Task 결과를 집계

### 전략 B: Action-level Global Scheduler
- 전체 Action을 하나의 큐로 두고,
- 우선순위/의존성/리소스 기반으로 스케줄링

권장:
- 초기에는 **전략 A**(단순/디버깅 용이)
- 규모 확대 시 **전략 B**로 전환

---

## 6) LangGraph 조건 분기(개념)

```python
if action.executable is False:
    goto("defer_or_skip_node")
elif dependencies_satisfied(action):
    goto("parallel_tool_executor")
else:
    goto("wait_dependency_node")
```

---

## 7) Action 스키마 예시

```json
{
  "action_id": "a-102",
  "task_id": "t-3",
  "tool_name": "crm_update_tool",
  "input": {"customer_id": "C123", "tier": "gold"},
  "dependencies": ["a-100"],
  "executable": false,
  "reason": "missing_permission:crm.write"
}
```

---

## 8) 노드 구성안 (ACTION 중심)

필수 노드:
- `plan_entry_node`
- `tool_selector_node`
- `parallel_action_node`
- `action_result_aggregator_node`
- `final_response_node`

선택 노드:
- `human_approval_node`
- `cost_guard_node`
- `fallback_model_node`

---

## 9) 구현 순서 (추천)

1. **v0.1**: PLAN + TOOL SELECTOR + 단일 Task 병렬 Action
2. **v0.2**: 멀티 Task 동시 수행 + retry/defer 큐
3. **v0.3**: human approval + cost guard + fallback model
4. **v1.0**: 운영 메트릭/SLO 자동 알림 + 안정화

---

## 10) 다음 단계
원하면 다음으로 바로 아래를 작성할 수 있습니다:
- `StateGraph` 노드/엣지 정의서
- 각 노드의 I/O 스키마(Pydantic)
- 병렬 실행 제한(동시성 N, rate limit) 정책
- 실패 복구 정책(재시도 횟수, backoff, dead-letter)
