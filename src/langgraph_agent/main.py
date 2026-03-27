from __future__ import annotations

import json

from .graph import build_graph


def run_sample() -> None:
    app = build_graph()
    input_state = {
        "request_id": "r-1",
        "user_id": "u-1",
        "session_id": "s-1",
        "user_goal": "고객 문의 요약, CRM 티켓 생성",
    }
    result = app.invoke(input_state)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    run_sample()
