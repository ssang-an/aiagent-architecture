# LangGraph Multi-Task Agent (Plan → Tool Selector → Parallel Action)

요청하신 내용을 코드로 분리해서 구현했습니다.

## 아키텍처 요약
- **Plan-first**: 사용자 요청을 Task/Action으로 분해
- **Tool Selector**: 각 Action에 `executable: true|false` 판정 + `reason` 기록
- **Parallel Action**: 실행 가능한 Action을 병렬 처리
- **Multi-task 동시 수행**: 하나의 요청을 복수 Task로 나눠 처리
- **Synthesis**: 결과 요약/최종 응답 생성

## 디렉터리 구조

```text
src/langgraph_agent/
  state.py            # AgentState, Task, Action 스키마
  planner.py          # parse_intent, decompose_tasks, build_action_plan
  tool_selector.py    # executable true/false 판정
  action_executor.py  # 병렬 실행(의존성 확인 + retry/defer 처리)
  synthesis.py        # 결과 종합 및 final_answer 생성
  graph.py            # LangGraph StateGraph 조립
  main.py             # 샘플 실행 엔트리포인트
  tools/
    base.py           # Tool 추상
    registry.py       # 예시 도구 구현/등록

tests/
  test_workflow_nodes.py
```

## 실행 플로우
1. `parse_intent_node`
2. `decompose_tasks_node`
3. `build_action_plan_node`
4. `set_executable_flag_node`
5. `parallel_action_node`
6. `final_response_node`

## 핵심 동작

### 1) Tool Selector
- 정책 위반, 도구 미가용, 의존성 미충족 여부를 검사
- 결과를 Action별로 기록

```json
{
  "action_id": "a-102",
  "executable": false,
  "reason": "dependency_not_ready"
}
```

### 2) Parallel Action
- `executable=true` 이고 의존성 충족 시 ThreadPool 기반 병렬 실행
- `executable=false`는 deferred 처리
- 실패는 retry_queue로 이동

## 설치

```bash
pip install -r requirements.txt
```

## 샘플 실행

```bash
PYTHONPATH=src python -m langgraph_agent.main
```

## 테스트

```bash
PYTHONPATH=src pytest -q
```

## 다음 확장 포인트
- Human approval node 추가
- 비용/토큰 guard node 추가
- Action-level global scheduler 도입
- 외부 API tool 어댑터 분리
