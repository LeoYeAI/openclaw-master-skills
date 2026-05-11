---
name: agent-avengers
description: |
  올인원 멀티에이전트 오케스트레이션. 복잡한 태스크를 자동으로 분해하고, 전문 에이전트들을 즉석에서 생성/스폰하여 병렬 처리 후 결과를 통합합니다.
  
  TRIGGERS: avengers assemble, 어벤저스, agent-avengers, 멀티에이전트 자동화, 에이전트 팀 구성, 자동 에이전트
version: 1.0.0
author: 카라얀
---

# 🦸 Agent Avengers

> "어벤저스, 어셈블!" — 복잡한 태스크를 자동으로 에이전트 팀이 처리

## 핵심 기능

1. **자동 태스크 분해** — 큰 작업을 독립적 서브태스크로 분할
2. **동적 에이전트 생성** — 각 태스크에 맞는 전문 에이전트 즉석 생성
3. **병렬 실행** — 독립 태스크는 동시 처리
4. **자동 통합** — 결과 수집, 검증, 병합
5. **완료 후 정리** — 임시 에이전트 자동 해제

## 사용법

### 기본 사용
```
사용자: "어벤저스 어셈블! [복잡한 태스크 설명]"
```

### 예시
```
"어벤저스 어셈블! 경쟁사 A, B, C 분석해서 비교 리포트 만들어줘"

→ 자동으로:
  1. 태스크 분해 (3개 리서치 + 1개 통합)
  2. 에이전트 3개 스폰 (각 회사 담당)
  3. 병렬 리서치 실행
  4. 결과 통합 에이전트가 최종 리포트 생성
  5. 완료 보고
```

---

## 워크플로우

```
┌─────────────────────────────────────────────────────────────────┐
│                    🦸 AVENGERS ASSEMBLE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1️⃣  ANALYZE — 태스크 분석 및 분해                              │
│      └─ 목표 파악 → 서브태스크 도출 → 의존성 매핑                 │
│                                                                 │
│  2️⃣  RECRUIT — 에이전트 팀 구성                                 │
│      └─ 각 서브태스크에 최적 에이전트 프로필 생성                 │
│      └─ 에이전트 역할: 🔬연구 🖊️작성 🔍분석 ✅검토 🔧통합        │
│                                                                 │
│  3️⃣  DEPLOY — 에이전트 스폰 및 태스크 할당                      │
│      └─ sessions_spawn으로 병렬 실행                            │
│      └─ 각 에이전트에 명확한 입력/출력 지정                      │
│                                                                 │
│  4️⃣  MONITOR — 진행 상황 추적                                   │
│      └─ 완료 대기, 실패 시 재시도 또는 대체                      │
│                                                                 │
│  5️⃣  ASSEMBLE — 결과 통합                                       │
│      └─ 모든 산출물 수집 → 검증 → 병합                          │
│                                                                 │
│  6️⃣  REPORT — 최종 보고 및 정리                                 │
│      └─ 사용자에게 결과 전달, 임시 리소스 정리                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 에이전트 모드

### 🔷 Mode 1: 기존 에이전트 활용
Gateway에 등록된 에이전트들을 조합하여 사용

```javascript
// 기존 에이전트에게 태스크 전달
sessions_send({
  label: "watson",      // 기존 에이전트 ID
  message: "X 리서치해줘",
  timeoutSeconds: 300
})
```

**장점:** 
- 에이전트별 전문성/기억 유지
- Discord 채널 바인딩 활용 가능
- 지속적인 컨텍스트

### 🔶 Mode 2: 임시 에이전트 스폰
태스크별로 일회성 에이전트 생성

```javascript
// 임시 서브에이전트 스폰
sessions_spawn({
  task: "X 분석해줘",
  model: "sonnet",
  runTimeoutSeconds: 1800,
  cleanup: "delete"
})
```

**장점:**
- 격리된 실행
- 완료 후 자동 정리
- 유연한 모델 선택

### 🟣 Mode 3: 멀티 프로필 (봇 인스턴스)
다른 OpenClaw 프로필/봇을 팀에 참여시킴

```yaml
# 프로필 목록 예시
profiles:
  - name: "main"           # 메인 봇 (카라얀)
    specialty: ["조율", "통합"]
    
  - name: "research-bot"   # 리서치 전용 봇
    specialty: ["심층조사", "데이터수집"]
    model: opus
    
  - name: "code-bot"       # 코딩 전용 봇
    specialty: ["개발", "테스트"]
    model: opus
    
  - name: "creative-bot"   # 크리에이티브 봇
    specialty: ["디자인", "콘텐츠"]
    model: gemini
```

**봇 간 통신:**
```javascript
// 다른 프로필의 봇에게 태스크 전달
sessions_send({
  sessionKey: "research-bot:main",  // 프로필:세션
  message: "심층 리서치 요청: X",
  timeoutSeconds: 600
})
```

**장점:**
- 봇별 전용 모델/설정
- 병렬 처리 능력 극대화
- 각 봇의 전문 스킬 활용
- 부하 분산

### 🔷🔶🟣 Mode 4: 풀 하이브리드 (권장)
기존 에이전트 + 임시 스폰 + 멀티 프로필 통합

```
예시: "대규모 경쟁 분석 프로젝트"

┌─────────────────────────────────────────┐
│  🟣 research-bot (별도 봇)              │
│     └── 🔬 watson (에이전트) → A사 조사  │
│     └── 🔶 temp-1 (스폰) → B사 조사      │
├─────────────────────────────────────────┤
│  🟣 code-bot (별도 봇)                  │
│     └── 💻 분석 스크립트 작성            │
├─────────────────────────────────────────┤
│  🔷 main (카라얀)                       │
│     └── 🔧 결과 통합 + 리포트 생성       │
└─────────────────────────────────────────┘
```

---

## 프로필 설정

### `avengers.yaml` 프로필 섹션

```yaml
profiles:
  # 메인 봇 (오케스트레이터 역할)
  main:
    role: orchestrator
    canSpawn: true
    canDelegate: true
    
  # 리서치 전용 봇
  research-bot:
    role: specialist
    specialty: ["research", "analysis", "data"]
    model: "anthropic/claude-opus-4-5"
    gateway: "localhost:3001"  # 별도 포트
    
  # 코딩 전용 봇  
  code-bot:
    role: specialist
    specialty: ["coding", "testing", "debugging"]
    model: "anthropic/claude-opus-4-5"
    gateway: "localhost:3002"
    
  # 크리에이티브 봇
  creative-bot:
    role: specialist
    specialty: ["design", "image", "content"]
    model: "google/gemini-2.5-pro"
    gateway: "localhost:3003"
```

### 프로필 간 통신 프로토콜

```javascript
// 1. 프로필 상태 확인
const profiles = await checkProfileStatus([
  "research-bot",
  "code-bot", 
  "creative-bot"
])

// 2. 사용 가능한 프로필에 태스크 분배
for (const task of tasks) {
  const bestProfile = matchProfileToTask(task, profiles)
  
  if (bestProfile.type === "external") {
    // 다른 봇에게 전달
    await sendToProfile(bestProfile.name, task)
  } else if (bestProfile.type === "agent") {
    // 현재 봇의 에이전트에게
    await sessions_send({ label: bestProfile.agentId, message: task })
  } else {
    // 임시 스폰
    await sessions_spawn({ task: task.description })
  }
}

// 3. 모든 프로필 완료 대기
await waitForAllProfiles(assignedTasks)

// 4. 결과 수집 및 통합
const results = await collectFromProfiles(assignedTasks)
```

---

## 에이전트 타입

| 타입 | 이모지 | 역할 | 모델 추천 |
|------|--------|------|-----------|
| **Researcher** | 🔬 | 웹 검색, 데이터 수집 | sonnet |
| **Analyst** | 🔍 | 데이터 분석, 패턴 발견 | opus |
| **Writer** | 🖊️ | 콘텐츠 작성, 문서화 | sonnet |
| **Coder** | 💻 | 코드 구현, 테스트 | opus |
| **Reviewer** | ✅ | 품질 검토, 피드백 | opus |
| **Integrator** | 🔧 | 결과 병합, 최종 산출물 | sonnet |

---

## 기존 에이전트 연동

### 에이전트 목록 확인
```javascript
// 활성 에이전트 조회
sessions_list({ kinds: ["agent"], limit: 10 })

// 또는 agents_list()로 등록된 에이전트 ID 확인
agents_list()
```

### 에이전트별 전문 분야 매핑
`avengers.yaml`에 정의:

```yaml
agents:
  watson:
    type: researcher
    specialty: "심층 리서치, 경쟁 분석"
    priority: high
  
  picasso:
    type: creator
    specialty: "이미지 생성, 디자인"
    priority: medium
  
  coder-bot:
    type: coder
    specialty: "코드 구현, 디버깅"
    priority: high
```

### 자동 에이전트 선택

태스크 분석 시 적합한 기존 에이전트 자동 매칭:

```
태스크: "A사 경쟁 분석"
  → watson (researcher, 심층 리서치) ✅ 매칭

태스크: "인포그래픽 만들기"  
  → picasso (creator, 디자인) ✅ 매칭

태스크: "API 연동 코드 작성"
  → coder-bot (coder) ✅ 매칭
  
태스크: "B사 조사" (전문 에이전트 없음)
  → temp-researcher 스폰 🔶
```

---

## 실행 방법

### Phase 1: 태스크 분석

사용자의 요청을 받으면:

```markdown
## 태스크 분석

**원본 요청:** [사용자 요청 전문]

**목표:** [최종 산출물]

**서브태스크:**
1. [태스크1] - 담당: [에이전트타입] - 의존성: 없음
2. [태스크2] - 담당: [에이전트타입] - 의존성: 없음
3. [태스크3] - 담당: [에이전트타입] - 의존성: 1,2

**병렬 실행 가능:** 1, 2
**순차 실행 필요:** 3 (1,2 완료 후)
```

### Phase 2: 에이전트 구성

#### Step 2a: 기존 에이전트 확인
```javascript
// 사용 가능한 에이전트 목록
const availableAgents = agents_list()
const activeAgents = sessions_list({ kinds: ["agent"] })
```

#### Step 2b: 태스크-에이전트 매칭
```markdown
## 에이전트 배정

| 서브태스크 | 배정 | 모드 | 이유 |
|------------|------|------|------|
| A사 리서치 | watson | 기존 | 리서치 전문가 |
| B사 리서치 | temp-1 | 스폰 | 추가 리소스 필요 |
| C사 리서치 | temp-2 | 스폰 | 추가 리소스 필요 |
| 통합 리포트 | temp-integ | 스폰 | 일회성 작업 |
```

#### Step 2c: 실행 계획
```markdown
## 실행 순서

**Phase A (병렬):**
- watson → A사 리서치
- temp-1 → B사 리서치  
- temp-2 → C사 리서치

**Phase B (순차, Phase A 완료 후):**
- temp-integrator → 결과 통합
```

### Phase 3: 에이전트 디스패치

#### 기존 에이전트 활용
```javascript
// 기존 에이전트에게 태스크 전달
sessions_send({
  label: "watson",
  message: `
## 태스크: A사 경쟁 분석

### 요청
- 회사 개요
- 주요 제품/서비스
- 시장 포지션
- 강점/약점

### 출력 형식
마크다운 리포트

### 완료 후
"A사 분석 완료" 라고 알려줘
  `,
  timeoutSeconds: 600
})
```

#### 임시 에이전트 스폰

```javascript
sessions_spawn({
  task: `
    [에이전트 역할 설명]
    
    ## 태스크
    ${subtask.description}
    
    ## 입력
    ${subtask.inputs}
    
    ## 기대 출력
    ${subtask.expectedOutput}
    
    ## 완료 조건
    ${subtask.successCriteria}
  `,
  model: subtask.recommendedModel,
  runTimeoutSeconds: 1800,
  cleanup: "delete"
})
```

### Phase 3: 결과 통합

모든 에이전트 완료 후:

1. 각 에이전트의 산출물 수집
2. 품질 검증 (성공 기준 충족 여부)
3. 충돌 해결 (겹치는 내용)
4. 최종 산출물 생성
5. 사용자에게 전달

---

## 예시 시나리오

### 시나리오 1: 경쟁사 분석 (하이브리드 모드)

```
입력: "어벤저스 어셈블! A사, B사, C사 경쟁 분석 리포트"

에이전트 구성:
├── 🔬 watson (기존) → A사 조사 (전문성 활용)
├── 🔬 temp-researcher-1 (스폰) → B사 조사
├── 🔬 temp-researcher-2 (스폰) → C사 조사
└── 🔧 temp-integrator (스폰) → 비교 리포트 작성

실행:
1. watson에게 sessions_send로 A사 태스크 전달
2. temp-1, temp-2 병렬 스폰
3. 3개 모두 완료 대기
4. temp-integrator 스폰, 결과 통합
5. 최종 리포트 전달
```

### 시나리오 2: 앱 개발 (전체 스폰)

```
입력: "어벤저스 어셈블! 날씨 앱 만들어줘"

에이전트 구성:
├── 🔍 temp-analyst → 요구사항 정의
├── 💻 temp-frontend → UI 구현
├── 💻 temp-backend → API 연동
├── ✅ temp-reviewer → 코드 리뷰
└── 🔧 temp-integrator → 통합 및 테스트

실행:
1. Analyst 먼저 (요구사항 도출)
2. Frontend/Backend 2명 병렬
3. Reviewer가 검토
4. Integrator가 통합 테스트
5. 완성된 앱 전달
```

### 시나리오 3: 기존 에이전트 팀 활용

```
입력: "어벤저스 어셈블! watson이랑 picasso 써서 리서치 + 인포그래픽"

에이전트 구성:
├── 🔬 watson (기존) → 심층 리서치
└── 🎨 picasso (기존) → 인포그래픽 제작 (watson 완료 후)

실행:
1. sessions_send(watson, "리서치 태스크")
2. watson 완료 대기
3. sessions_send(picasso, "인포그래픽 태스크 + watson 결과")
4. 최종 전달
```

### 시나리오 4: 멀티 프로필 대규모 프로젝트

```
입력: "어벤저스 어셈블! 전체 봇 동원해서 신규 서비스 기획부터 개발까지"

프로필 구성:
┌─────────────────────────────────────────┐
│  🟣 research-bot                        │
│     └── 시장 조사 + 경쟁사 분석          │
├─────────────────────────────────────────┤
│  🟣 creative-bot                        │
│     └── UI/UX 디자인 + 브랜딩            │
├─────────────────────────────────────────┤
│  🟣 code-bot                            │
│     └── 프론트엔드 + 백엔드 개발         │
├─────────────────────────────────────────┤
│  🔷 main (카라얀)                       │
│     └── 오케스트레이션 + 최종 통합        │
└─────────────────────────────────────────┘

실행:
1. research-bot에 시장 조사 요청
2. 조사 완료 → creative-bot에 디자인 요청
3. 디자인 완료 → code-bot에 개발 요청
4. main이 전체 통합 및 QA
5. 최종 산출물 전달
```

---

## 가드레일

### 자동 중단 조건
- 에이전트 실패 3회 연속
- 전체 타임아웃 초과 (기본 2시간)
- 사용자 취소 요청

### 안전 장치
- 각 에이전트는 격리된 세션에서 실행
- 파일 수정은 지정된 출력 경로만 허용
- 외부 API 호출은 승인된 것만

---

## 설정

### 기본값
```yaml
avengers:
  maxAgents: 5              # 동시 에이전트 수 (기존+스폰 합산)
  maxProfiles: 4            # 동시 사용 프로필 수
  timeoutMinutes: 120       # 전체 타임아웃
  retryCount: 2             # 실패 시 재시도
  defaultModel: "sonnet"    # 스폰 에이전트 기본 모델
  cleanupOnComplete: true   # 완료 후 임시 에이전트 정리
  preferExisting: true      # 기존 에이전트 우선 사용
  useMultiProfile: true     # 멀티 프로필 모드 활성화
```

### 프로필 설정
```yaml
profiles:
  main:
    role: orchestrator
    gateway: "localhost:3000"
    
  research-bot:
    role: specialist
    specialty: ["research", "analysis"]
    model: opus
    gateway: "localhost:3001"
    
  code-bot:
    role: specialist
    specialty: ["coding", "testing"]
    model: opus
    gateway: "localhost:3002"
    
  creative-bot:
    role: specialist
    specialty: ["design", "content"]
    model: gemini
    gateway: "localhost:3003"
```

### 에이전트 매핑
```yaml
agents:
  # 기존 에이전트 정의
  watson:
    type: researcher
    specialty: ["리서치", "경쟁분석", "시장조사"]
    model: opus
    
  picasso:
    type: creator  
    specialty: ["이미지", "디자인", "인포그래픽"]
    model: gemini-flash
    
  coder-bot:
    type: coder
    specialty: ["코딩", "API", "백엔드", "프론트엔드"]
    model: opus

  # 스폰 에이전트 템플릿
  templates:
    researcher:
      model: sonnet
      timeout: 1800
    analyst:
      model: opus
      timeout: 1200
    writer:
      model: sonnet
      timeout: 900
    coder:
      model: opus
      timeout: 2400
```

---

## 🌟 창발적 협업 패턴

### 1. 🗳️ 경쟁 드래프트 (Competitive Draft)
동일 태스크를 여러 에이전트가 독립적으로 수행 → 결과 비교 → 최고안 선택

```
태스크: "마케팅 전략 수립"

├── 🔷 watson → 전략 A (데이터 기반)
├── 🔶 temp-strategist-1 → 전략 B (창의적)
├── 🟣 creative-bot → 전략 C (감성적)
└── 🗳️ 투표/평가 → 최고안 선택 또는 하이브리드

장점: 다양한 관점, 최적해 도출
```

### 2. 🎭 역할 순환 (Role Rotation)
진행 중 역할을 바꿔서 신선한 시각 확보

```
Round 1:
├── Agent A: 아이디어 제안
├── Agent B: 비평
└── Agent C: 개선

Round 2 (순환):
├── Agent B: 아이디어 제안
├── Agent C: 비평
└── Agent A: 개선

→ 고착화 방지, 다각적 검토
```

### 3. ⚔️ 적대적 협력 (Adversarial Collaboration)
한 에이전트가 만들면 다른 에이전트가 공격적으로 비판 → 반복

```
Creator ──→ 초안 작성
    ↓
Critic ──→ "이건 왜 틀렸는가" 공격
    ↓
Creator ──→ 방어 및 개선
    ↓
Critic ──→ 재공격
    ↓
(3라운드 반복)
    ↓
Arbiter ──→ 최종 판정

결과: 훨씬 견고한 산출물
```

### 4. 🧬 진화적 선택 (Evolutionary Selection)
여러 솔루션 생성 → 평가 → 상위권 교배 → 반복

```
Generation 1:
├── Solution A (점수: 7)
├── Solution B (점수: 8) ✓
├── Solution C (점수: 5)
└── Solution D (점수: 9) ✓

Generation 2:
├── B + D 하이브리드 → E
├── D 변형 → F
└── B 변형 → G

... 3세대 반복 → 최적해
```

### 5. 🐝 스웜 인텔리전스 (Swarm Intelligence)
많은 마이크로 에이전트가 작은 조각 처리 → 창발적 결과

```
태스크: "100개 기업 분석"

Swarm:
├── micro-1 → 기업 1-10
├── micro-2 → 기업 11-20
├── micro-3 → 기업 21-30
...
└── micro-10 → 기업 91-100

Aggregator → 패턴 발견, 통합 인사이트
```

### 6. 🔗 체인 릴레이 (Chain Relay)
한 에이전트의 출력이 다음 에이전트의 입력 (변형 전달)

```
Agent A: 원시 데이터 수집
    ↓ (데이터)
Agent B: 패턴 추출
    ↓ (패턴)
Agent C: 인사이트 도출
    ↓ (인사이트)
Agent D: 액션 아이템 생성
    ↓ (계획)
Agent E: 실행

각 단계에서 가치 증폭
```

### 7. 💭 합의 프로토콜 (Consensus Protocol)
모든 에이전트가 동의해야 진행

```
Proposal: "이 방향으로 가자"

├── Agent A: 동의 ✓
├── Agent B: 반대 ✗ (이유: X)
├── Agent C: 동의 ✓
└── Agent D: 조건부 동의

→ 반대 의견 해소 후 재투표
→ 만장일치 → 진행

위험한 결정에 안전장치
```

### 8. 🎪 크로스 도메인 잼 (Cross-Domain Jam)
완전히 다른 분야의 에이전트가 협업

```
태스크: "혁신적인 앱 아이디어"

├── 🎨 Art-Agent: 예술적 관점
├── 🔬 Science-Agent: 기술적 관점
├── 📚 History-Agent: 역사적 패턴
├── 🎮 Game-Agent: 게이미피케이션
└── 🧘 Philosophy-Agent: 윤리적 고려

→ 예상치 못한 조합에서 혁신 탄생
```

### 9. 🪞 메타 관찰자 (Meta Observer)
다른 에이전트들을 관찰하고 코칭하는 에이전트

```
Working Agents:
├── Agent A (작업 중)
├── Agent B (작업 중)
└── Agent C (작업 중)

Meta-Observer:
├── 패턴 감지: "A와 B가 중복 작업 중"
├── 개입: "B는 다른 방향 시도해봐"
├── 조언: "C의 접근법을 A도 참고해"
└── 학습: 성공 패턴 기록

팀 전체 효율성 향상
```

### 10. ⏰ 시간 분리 협업 (Time-Horizon Split)
같은 문제를 다른 시간 관점으로 접근

```
태스크: "비즈니스 전략"

├── 🏃 Sprint-Agent: 다음 주 할 일
├── 🚶 Quarter-Agent: 분기 계획
├── 🧘 Year-Agent: 연간 비전
└── 🔮 Decade-Agent: 장기 트렌드

→ 단기-장기 균형 잡힌 전략
```

### 11. 🎰 태스크 경매 (Task Auction)
에이전트가 자신감 기반으로 태스크에 입찰

```
Task: "복잡한 API 설계"

Bids:
├── code-bot: 신뢰도 92%, 예상 시간 2h
├── watson: 신뢰도 65%, 예상 시간 4h
└── temp-agent: 신뢰도 78%, 예상 시간 3h

→ code-bot 낙찰 (최고 신뢰도)
→ 실패 시 차순위 시도
```

### 12. 🧠 공유 메모리 실시간 동기화

```
Shared Memory Pool:
┌────────────────────────────────────────┐
│  discoveries/                          │
│  ├── agent-a-finding-1.md             │
│  ├── agent-b-insight-2.md             │
│  └── agent-c-connection-3.md          │
│                                        │
│  모든 에이전트가 실시간 읽기/쓰기        │
│  → 발견 즉시 공유 → 시너지              │
└────────────────────────────────────────┘
```

---

## 통합

이 스킬은 다음 스킬들의 기능을 통합:
- **agent-council** — 에이전트 생성 패턴
- **agent-orchestrator** — 태스크 분해 및 조율 패턴

기존 스킬들과 함께 사용 가능.

---

## 트리거 키워드

- `어벤저스 어셈블`
- `avengers assemble`
- `agent-avengers`
- `멀티에이전트 자동화`
- `에이전트 팀 구성`

---

## 예시 프롬프트

```
"어벤저스 어셈블! 다음 작업을 팀으로 처리해줘: [작업 설명]"

"avengers assemble - 이 프로젝트를 병렬로 진행해줘"

"멀티에이전트로 자동 처리해줘: [복잡한 요청]"
```
