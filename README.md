# AI Agent Architecture (LangChain + LangGraph)

좋습니다. 이번에는 **LangChain + LangGraph 기반 전체 아키텍처의 큰 그림**부터 맞추고,
세부 구현은 대화로 천천히 확정하는 방식으로 진행합니다.

## 1) 우리가 먼저 합의할 것 (Big Picture)
- 어떤 문제를 해결하는 에이전트인지 (업무 자동화 / 고객지원 / 사내지식 검색 등)
- 단일 에이전트인지, 멀티 에이전트인지
- 사람 승인(Human-in-the-loop)이 필요한 구간
- 품질/속도/비용 중 우선순위

---

## 2) 전체 아키텍처 개요

```text
[Client/UI]
   |
   v
[API Server (FastAPI)]
   |
   +---------------------------+
   |                           |
   v                           v
[LangGraph Runtime]        [Observability]
(StateGraph)               (LangSmith, Logs, Metrics)
   |
   +--> [Planner Node] -------------------------------+
   |                                                  |
   +--> [Retriever Node (RAG)] --> [Vector DB]        |
   |                                                  |
   +--> [Tool Node] -----------> [Internal/External APIs]
   |                                                  |
   +--> [Policy/Guard Node] ----> [Safety Rules]      |
   |                                                  |
   +--> [Human Approval Node] (optional)              |
   |                                                  |
   +--> [Responder Node] -----------------------------+
   |
   v
[Short-term Memory (checkpoint)]
[Long-term Memory (profile / history / summary)]
```

### 역할 분리
- **LangChain**: 모델, 프롬프트, 툴, 리트리버 같은 빌딩 블록 계층
- **LangGraph**: 상태 기반 실행 플로우(분기/반복/재시도/승인) 오케스트레이션 계층

---

## 3) LangGraph 기준 노드 설계(초안)

### A. Planner Node
- 사용자 의도를 구조화
- 실행 계획 생성(툴 필요 여부, RAG 필요 여부)

### B. Retriever Node (RAG)
- 질의 재작성
- 벡터 검색 + rerank
- 근거 문서 컨텍스트 구성

### C. Tool Node
- 사내 API / 외부 API 호출
- 실패 시 재시도, 타임아웃, 폴백 처리

### D. Policy/Guard Node
- PII/보안/권한 정책 검사
- 금지 요청 차단 또는 마스킹

### E. Human Approval Node (선택)
- 결제/삭제/배포 같은 고위험 작업에서 승인 요청

### F. Responder Node
- 최종 답변 생성(근거 포함)
- 응답 포맷(JSON/Markdown/stream) 변환

---

## 4) 상태(State) 모델 초안

```yaml
AgentState:
  user_id: str
  session_id: str
  user_query: str
  intent: str
  plan: list
  retrieved_docs: list
  tool_results: list
  safety_flags: list
  approval_required: bool
  approval_status: str
  final_answer: str
  traces: list
```

이 상태를 LangGraph 노드들이 순차/분기적으로 업데이트합니다.

---

## 5) 실행 흐름(초기 버전)
1. `Planner`가 요청 분석 및 경로 결정
2. 필요 시 `Retriever` 실행(RAG)
3. 필요 시 `Tool` 실행(API/DB)
4. `Policy/Guard`로 안전성 재검증
5. 고위험 작업이면 `Human Approval` 대기
6. `Responder`가 최종 응답 생성
7. 전 구간 trace를 LangSmith/로그로 기록

---

## 6) 기술 스택 제안
- **Framework**: LangChain, LangGraph
- **Model**: OpenAI/Anthropic/로컬 모델(어댑터 패턴)
- **RAG**: PGVector / Weaviate / Pinecone 중 택1
- **API**: FastAPI
- **Observability**: LangSmith + OpenTelemetry + Prometheus/Grafana
- **Storage**: Postgres(메타/히스토리), Redis(캐시/세션)

---

## 7) 지금은 “큰 그림” 단계: 대화 안건
다음 질문에 답해주면, 그걸 기반으로 바로 **아키텍처 v0.1** 고정하겠습니다.

1. 주 사용 시나리오 1순위는 무엇인가요?
2. 도구 호출이 필수인가요, 아니면 우선 RAG 중심인가요?
3. Human approval이 반드시 필요한 작업이 있나요?
4. 응답 속도 vs 정확도 vs 비용 중 우선순위는?
5. 온프레미스/클라우드 제약이 있나요?

---

원하면 다음 단계에서 바로 **LangGraph 다이어그램(v0.1) + 노드별 I/O 스키마**까지 이어서 작성하겠습니다.
