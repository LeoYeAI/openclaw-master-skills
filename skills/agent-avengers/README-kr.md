# Agent Avengers

🦸 **올인원 멀티에이전트 오케스트레이션**

## 설치

이미 설치됨: `~/.openclaw/workspace/skills/agent-avengers/`

## 사용법

```
어벤저스 어셈블! [복잡한 태스크 설명]
```

## 예시

```
어벤저스 어셈블! A사, B사, C사 경쟁 분석해서 비교 리포트 만들어줘
```

## 작동 방식

1. **분해** — 태스크를 서브태스크로 분할
2. **구성** — 각 서브태스크에 전문 에이전트 할당
3. **실행** — 병렬/순차 실행
4. **통합** — 결과 수집 및 병합
5. **보고** — 최종 산출물 전달

## 에이전트 타입

| 타입 | 역할 |
|------|------|
| 🔬 Researcher | 조사, 데이터 수집 |
| 🔍 Analyst | 분석, 패턴 발견 |
| 🖊️ Writer | 문서 작성 |
| 💻 Coder | 코드 구현 |
| ✅ Reviewer | 품질 검토 |
| 🔧 Integrator | 결과 통합 |

## 설정

`avengers.yaml`:
```yaml
maxAgents: 5
timeoutMinutes: 120
retryCount: 2
defaultModel: sonnet
```

## 라이선스

MIT
