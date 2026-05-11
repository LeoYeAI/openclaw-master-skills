---
name: bizcard
description: |
  Business card scanner + Google Contacts manager. Auto-detects business card images,
  extracts contact info via OCR (imageModel),
  confirms with user, saves to Google Contacts with configurable name format and card photo.
  Trigger: image that looks like a business card, or keywords "명함", "bizcard", "연락처 저장".
  Settings: /bizcard config
metadata:
  clawdbot:
    emoji: 📇
    requires:
      env: [MATON_API_KEY, NANO_BANANA_API_KEY]
---

# Bizcard — 명함 스캐너 + 연락처 관리

명함 이미지를 받으면 자동 감지 → 전처리 → OCR → 사용자 확인 → Google Contacts 저장까지 처리한다.

## Pipeline Overview

```
이미지 수신 → 명함 자동 감지
→ Gemini Flash OCR → 필드 파싱 → Name 포맷 적용
→ 사용자 확인 → 중복 감지 → Nano Banana Pro 보정 → Google Contacts 저장 + 사진 첨부
```

---

## 1. 자동 감지 (Trigger Detection)

### 키워드 매칭 (API 호출 없음)
메시지에 다음 키워드가 포함되면 즉시 명함 처리 모드 진입:
- 한국어: "명함", "연락처 저장", "연락처 추가"
- 영어: "bizcard", "business card", "save contact"

### 이미지 분석 (키워드 없이 이미지만 올라왔을 때)
imageModel에 다음을 요청:

```
이 이미지가 명함(business card)인지 판단해.
명함이면 YES, 아니면 NO만 답해.
명함 = 사람의 이름, 회사명, 연락처 정보가 인쇄된 카드 형태.
음식, 풍경, 스크린샷, 메모, 영수증 등은 NO.
```

- YES → 명함 처리 진행
- NO → 무시 (다른 스킬에 넘기거나 일반 응답)

---

## 2. 이미지 전처리 (ImageMagick)

### 2-1. 품질 평가

imageModel에 요청:

```
이 명함 이미지의 품질을 평가해:
- 텍스트가 선명하게 읽히는가? (CLEAR / BLURRY)
- 기울어져 있는가? (STRAIGHT / TILTED)
- 전체적으로 전처리가 필요한가? (NEEDS_PROCESSING / SKIP)
JSON으로 답해: {"clarity": "...", "tilt": "...", "preprocessing": "..."}
```

### 2-2. 전처리 실행 (NEEDS_PROCESSING일 때만)

```bash
# 요청별 고유 디렉터리 생성
BIZCARD_TMP=$(mktemp -d /tmp/bizcard-XXXXXXXX)

# 1. Deskew (기울기 보정)
magick "$BIZCARD_TMP/raw.jpg" -deskew 40% "$BIZCARD_TMP/deskew.jpg"

# 2. 콘트라스트 개선 + 선명화
magick "$BIZCARD_TMP/deskew.jpg" -normalize -sharpen 0x1 "$BIZCARD_TMP/enhanced.jpg"
```

전처리된 이미지로 OCR 진행.

### 2-3. SKIP일 때

원본 그대로 OCR 진행. 전처리 건너뜀.

---

## 3. OCR 필드 추출

imageModel(Gemini Flash)에 다음 JSON 구조로 추출 요청:

```
이 명함 이미지에서 연락처 정보를 추출해. 다음 JSON 형식으로 답해.
읽을 수 없는 필드는 null로 남겨.

{
  "name_ko": "한글 이름",
  "name_en": "English name",
  "company_ko": "한글 회사명",
  "company_en": "English company name",
  "title_ko": "한글 직함",
  "title_en": "English title",
  "department": "부서",
  "mobile": ["개인 휴대폰 배열"],
  "email": ["이메일 배열"],
  "locations": [
    {
      "label": "본사",
      "phone": ["063-000-0000"],
      "fax": ["063-000-0001"],
      "address_ko": "서울특별시 강남구 테헤란로 123",
      "address_en": null
    },
    {
      "label": "영업부",
      "phone": ["02-000-0000"],
      "fax": ["02-000-0001"],
      "address_ko": "경기도 성남시 분당구 판교로 456",
      "address_en": null
    }
  ],
  "website": ["웹사이트 배열"],
  "notes": "기타 (SNS, 자격증 등)",
  "language": "명함의 주 언어 (ko / en / ja / zh / other)"
}
```

---

## 4. 전화번호 정규화

한국 번호를 국제 형식으로 변환:

| 원본 | 변환 |
|------|------|
| `010-1234-5678` | `+82-10-1234-5678` |
| `02-1234-5678` | `+82-2-1234-5678` |
| `031-123-4567` | `+82-31-123-4567` |

규칙:
- `0`으로 시작하는 한국 번호 → 앞의 `0`을 `+82-`로 교체
- `+`로 시작하는 해외 번호 → 원본 유지
- 숫자 사이 `-` 또는 공백은 `-`로 통일

---

## 5. 이름 처리 규칙

### 5-1. 한국식 명함 (config: `koreanStyleName=true`, 기본값)

**한국에서는 성과 이름을 분리하지 않는다.** 비즈니스에서 "홍길동 대표", "김갑돌 과장"처럼 풀네임이 하나의 단위다.

People API 저장 시:
- `familyName` → **비움** (빈 문자열)
- `givenName` → **풀네임** (예: `홍길동`)
- `unstructuredName` → config 포맷 적용된 이름 (예: `#홍길동 과장`)

### 5-2. 외국 명함 (config: `koreanStyleName=false`이거나, OCR language가 ko가 아닌 경우)

외국인은 first name / last name 분리가 기본:
- `givenName` → first name (예: `John`)
- `familyName` → last name (예: `Smith`)
- `unstructuredName` → config 포맷 적용

### 5-3. Korean Reading (config: `koreanReading=true`)

외국어 명함일 때, 이름과 회사명을 한국어로 독음(transliteration)하여 기록:

| 원본 | 독음 |
|------|------|
| John Smith | 존 스미스 |
| Google LLC | 구글 |
| Toyota Motor | 토요타 모터 |
| François Dupont | 프랑수아 뒤퐁 |

**적용 방법:**
- imageModel에 "이 이름/회사명을 한국어 외래어 표기법으로 독음해줘" 요청
- **이름 독음 → People API `phoneticName` 필드에 저장** (검색 가능!)
- 회사명 독음 → `biographies`에 기록

**People API 저장:**
```
names[].phoneticGivenName = "퀘 훙 웨인"   ← 풀네임 독음을 하나로
names[].phoneticFamilyName = ""             ← 비움
```

**규칙:** 독음은 성/이름 분리하지 않는다. 풀네임 독음을 `phoneticGivenName`에 통째로 넣는다.

예시: `Kweh Hoong Wayne` → phoneticGivenName=`퀘 훙 웨인`
예시: `François Dupont` → phoneticGivenName=`프랑수아 뒤퐁`

**효과:** Google Contacts에서 "퀘 훙 웨인"으로 검색해도 해당 연락처를 찾을 수 있다.

`koreanReading=false`이면 독음 생략.

---

## 6. Name 포맷 적용

config 설정을 읽어 `unstructuredName` (displayName)을 생성한다.

### 적용 순서

```
1. 기본 이름: "홍길동"
2. hashtag=true     → "#홍길동"
3. appendTitle=true → "#홍길동 과장"
4. appendCompany=true → "#홍길동 과장 (ABC주식회사)"
```

### 조합 예시

| hashtag | appendTitle | appendCompany | 결과 |
|:---:|:---:|:---:|------|
| off | off | off | `홍길동` |
| on | off | off | `#홍길동` |
| off | on | off | `홍길동 과장` |
| off | off | on | `홍길동 (ABC주식회사)` |
| on | on | on | `#홍길동 과장 (ABC주식회사)` |

### People API 저장 시 (한국식)

- `names[].unstructuredName` → 포맷된 displayName (예: `#홍길동 과장`)
- `names[].givenName` → 풀네임 (예: `홍길동`)
- `names[].familyName` → 비움

### People API 저장 시 (외국식)

- `names[].unstructuredName` → 포맷된 displayName (예: `#John Smith, VP`)
- `names[].givenName` → first name (예: `John`)
- `names[].familyName` → last name (예: `Smith`)

---

## 7. 사용자 확인 플로우

OCR + 포맷 결과를 **아래 템플릿 그대로** 출력한다. 포맷 변경 금지.

**한국 명함 템플릿 (이 포맷 그대로 사용):**
```
📇 명함 인식 결과

👤 #홍길동 과장 (ABC주식회사)
🏢 ABC주식회사 / 영업부
💼 과장
📱 +82-10-1234-5678
📧 gdhong@example.co.kr
🌐 www.example.co.kr

📍 본사:
  📞 +82-63-450-3500 / 📠 +82-63-450-3517
  서울특별시 강남구 테헤란로 123

📍 영업부:
  📞 +82-2-597-8071~3 / 📠 +82-2-586-4388
  경기도 성남시 분당구 판교로 456

🖼️ 명함 사진 → 연락처 프로필 사진으로 저장

1. 저장
2. 수정
3. 취소
```

**거점이 1개뿐이면** 📍 label 없이 한 줄로:
```
📞 +82-2-9876-5432
📠 +82-2-9876-5433
📍 서울시 강남구 테헤란로 123
```

**외국 명함 템플릿 (koreanReading=true, 이 포맷 그대로 사용):**
```
📇 명함 인식 결과

👤 John Smith (존 스미스)
🏢 Google LLC (구글)
💼 VP of Engineering
📱 +1-555-123-4567
📧 jsmith@example.com
🖼️ 명함 사진 → 연락처 프로필 사진으로 저장

1. 저장
2. 수정
3. 취소
```

**규칙:**
- 이모지 순서 고정: 👤🏢💼📱📞📠📧🌐📍🖼️
- 없는 필드는 해당 줄 자체를 생략 (빈 줄 금지)
- 부가 설명이나 "20년차 전문가" 같은 OCR 잡데이터를 이름에 넣지 마라. 타이틀 필드에만 표시.
- 이름 라인(👤)에는 config 포맷만 적용: `#이름 직함 (회사명)`
- **직함은 💼 줄에 별도 표시.** 👤 줄의 직함은 config appendTitle 적용 시에만, 짧게. ALL CAPS 금지.
  - ✅ `👤 #Kweh Hoong Wayne` + `💼 Technical Service Manager`
  - ❌ `👤 #Kweh Hoong Wayne TECHNICAL SERVICE MANAGER`
- 하단은 반드시 `1. 저장 / 2. 수정 / 3. 취소` 번호 선택. "저장할까?" 같은 서술형 금지.
- **복수 거점:** 명함에 주소가 2개 이상이면 **거점(location) 단위로 그룹핑**하여 출력.
  각 거점은 📍 label + 해당 거점의 📞/📠/주소를 묶어서 표시.
  명함에서 전화/팩스/주소가 시각적으로 분리되어 있으면 반드시 별도 거점으로 분리. 절대 병합하지 마라.
- 거점 label(본사/공장/영업부 등)은 명함에서 추출. 없으면 "거점1", "거점2"로 표시.

### 응답 처리

| 입력 | 동작 |
|------|------|
| `1` | 저장 진행 |
| `2` | "뭘 수정할까?" 물은 뒤, 수정 후 다시 1/2/3 선택 |
| `3` | 취소 |

**번호 외 텍스트 입력도 허용:** "ㅇㅇ", "ok" → 1번 처리, "취소" → 3번 처리.
하지만 **번호 입력을 우선 유도**한다.

---

## 8. 명함 이미지 보정 + 사진 업로드 (항상 실행)

`cardAsPhoto=true`이면 **무조건 실행**한다. 모든 명함을 일관되게 보정한다.
말로만 "적용했어" 하지 말고 **실제로 exec 도구로 명령어를 실행**해라.

### 8-1. 원본 이미지를 /tmp에 복사

```bash
BIZCARD_TMP=$(mktemp -d /tmp/bizcard-XXXXXXXX)
cp /path/to/원본명함이미지.jpg "$BIZCARD_TMP/raw.jpg"
```

### 8-2. Nano Banana Pro로 이미지 보정 (핵심!)

원본 이미지를 Nano Banana Pro에 보내서 **배경 제거 + 정면 보정 + 1:1 정사각형**으로 변환.

```bash
python3 <<'PYEOF'
import urllib.request, json, base64, os

with open(os.environ["BIZCARD_TMP"] + "/raw.jpg", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

api_key = os.environ.get("NANO_BANANA_API_KEY", "")
if not api_key:
    print("ERROR: NANO_BANANA_API_KEY not set")
    exit(1)
url = f"https://generativelanguage.googleapis.com/v1beta/models/nano-banana-pro-preview:generateContent?key={api_key}"

payload = {
    "contents": [{
        "parts": [
            {"inlineData": {"mimeType": "image/jpeg", "data": img_b64}},
            {"text": "이 사진에서 명함 카드만 잘라내서 정면으로 보정한 이미지를 생성해줘. 배경 완전 제거, 명함만 남기고, 흰색 여백을 추가해서 1:1 정사각형 비율로 만들어줘. 명함 내용은 전부 보존해."}
        ]
    }],
    "generationConfig": {
        "responseModalities": ["TEXT", "IMAGE"]
    }
}

data = json.dumps(payload).encode()
req = urllib.request.Request(url, data=data, method="POST")
req.add_header("Content-Type", "application/json")
resp = urllib.request.urlopen(req, timeout=60)
result = json.loads(resp.read())

for part in result["candidates"][0]["content"]["parts"]:
    if "inlineData" in part:
        img_data = base64.b64decode(part["inlineData"]["data"])
        with open(os.environ["BIZCARD_TMP"] + "/clean.jpg", "wb") as f:
            f.write(img_data)
        print(f"OK: clean.jpg ({len(img_data)} bytes)")
    elif "text" in part:
        print(f"Text: {part['text'][:100]}")
PYEOF
```

**결과:** `$BIZCARD_TMP/clean.jpg` — 1024x1024, 배경 제거, 정면 보정, 1:1 정사각형.

### 8-3. 보정된 이미지를 Google Contacts에 업로드

**clean.jpg를 업로드한다. raw.jpg가 아니다.**

```bash
python3 <<'PYEOF'
import urllib.request, os, json, base64

with open(os.environ["BIZCARD_TMP"] + "/clean.jpg", "rb") as f:
    photo_bytes = base64.b64encode(f.read()).decode()

data = json.dumps({"photoBytes": photo_bytes}).encode()
resource_name = os.environ["RESOURCE_NAME"]
req = urllib.request.Request(
    f"https://gateway.maton.ai/google-contacts/v1/{resource_name}:updateContactPhoto",
    data=data, method="PATCH"
)
req.add_header("Authorization", f"Bearer {os.environ['MATON_API_KEY']}")
req.add_header("Content-Type", "application/json")
result = json.load(urllib.request.urlopen(req))
print("Photo uploaded:", result.get("person", {}).get("resourceName", "unknown"))
PYEOF
```

### 8-4. 임시 파일 삭제

```bash
rm -rf "$BIZCARD_TMP"
```

**절대 금지:**
- 보정을 "실행했다"고 말만 하고 실제 exec를 안 하는 것
- clean.jpg 대신 raw.jpg(원본)를 업로드하는 것
- ImageMagick `-deskew`나 `-distort Perspective` 사용 (Nano Banana Pro가 전부 처리)

**Nano Banana Pro API 실패 시:** 원본(raw.jpg)을 그대로 업로드하고 "이미지 보정 실패: 원본으로 저장" 알림.

---

## 9. 중복 감지 (자동 2필드 매칭)

저장 전 **반드시** 이름 + 휴대폰 번호 2개 필드로 기존 연락처를 자동 검색한다. 사용자가 요청하지 않아도 항상 실행.

### 검색 로직

```bash
# 1단계: 이름으로 검색
GET /google-contacts/v1/people:searchContacts?query=홍길동&readMask=names,phoneNumbers,emailAddresses

# 2단계: 휴대폰 번호로 검색
GET /google-contacts/v1/people:searchContacts?query=%2B82-10-1234-5678&readMask=names,phoneNumbers,emailAddresses
```

번호 검색 시 정규화된 +82 포맷과 원본(010) 포맷 모두로 검색하여 누락을 방지한다.

### 매칭 판정

| 이름 일치 | 번호 일치 | 판정 | 동작 |
|:---------:|:---------:|------|------|
| ✅ | ✅ | **확정 중복** | 사용자에게 옵션 제시 |
| ✅ | ❌ | **동명이인 가능** | 사용자에게 알림 후 진행 |
| ❌ | ✅ | **번호 재사용 가능** | 사용자에게 알림 후 진행 |
| ❌ | ❌ | **신규** | 바로 저장 |

### 확정 중복 시 출력 (이름+번호 모두 일치)

**아래 템플릿을 그대로 출력한다. 포맷 변경 금지.**

```
⚠️ 중복 연락처 발견

기존:
  👤 홍길동
  📱 +82-10-1234-5678
  📧 gdhong@example.co.kr

이번 명함:
  👤 #홍길동 과장 (ABC주식회사)
  📱 +82-10-1234-5678
  📧 gdhong@example.co.kr

1. 새로 저장
2. 기존 업데이트
3. 취소
```

### 부분 일치 시 출력 (이름만 또는 번호만 일치)

**아래 템플릿을 그대로 출력한다. 포맷 변경 금지.**

```
ℹ️ 유사 연락처 발견

기존:
  👤 홍길동
  📱 +82-10-9999-0000

이번 명함:
  👤 #홍길동 과장 (ABC주식회사)
  📱 +82-10-1234-5678

번호가 다름. 그대로 새로 저장할까?
```

### 신규 (중복 없음)

중복 없으면 중복 관련 메시지 자체를 출력하지 않는다. 바로 사용자 확인으로 넘어간다.

---

## 10. Google Contacts 저장

Maton API Gateway (People API)를 사용. 전체 필드 + 커스텀 Name + 사진 지원.

### 연락처 생성

```bash
python <<'EOF'
import urllib.request, os, json

# 한국식 명함 예시 (koreanStyleName=true)
contact = {
    "names": [{
        "unstructuredName": "#홍길동 과장",
        "givenName": "홍길동",
        "familyName": ""
    }],
    "organizations": [{
        "name": "ABC주식회사",
        "title": "과장",
        "department": "영업부",
        "type": "work"
    }],
    "emailAddresses": [
        {"value": "gdhong@example.co.kr", "type": "work"}
    ],
    "phoneNumbers": [
        {"value": "+82-10-1234-5678", "type": "mobile"},
        {"value": "+82-2-9876-5432", "type": "work"}
    ],
    "addresses": [
        {"formattedValue": "서울시 강남구 테헤란로 123", "type": "work"}
    ],
    "urls": [
        {"value": "https://www.example.co.kr", "type": "work"}
    ]
}

data = json.dumps(contact).encode()
req = urllib.request.Request(
    'https://gateway.maton.ai/google-contacts/v1/people:createContact',
    data=data, method='POST'
)
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
result = json.load(urllib.request.urlopen(req))
print(json.dumps(result, indent=2))
EOF
```

### 명함 사진을 연락처 사진으로 저장 (`cardAsPhoto=true`)

**Section 8의 파이프라인을 따른다.** 보정 + 업로드는 Section 8에서 일괄 처리.

파이프라인 종료 시 (성공, 취소, 에러 무관) `$BIZCARD_TMP` 디렉터리 전체 삭제 (`rm -rf "$BIZCARD_TMP"`).
다른 세션의 파일을 건드리지 않는다.

---

## 11. 설정 관리 — `/bizcard config`

### 설정 조회

사용자가 `/bizcard config` 또는 "명함 설정"을 입력하면, **아래 템플릿을 그대로 복사해서 출력한다.** 절대 다른 포맷으로 바꾸지 마라. on/off 값만 config.json 실제 상태에 맞춰 교체.

**출력 템플릿 (이 포맷 그대로 사용):**
```
📇 Bizcard Settings

1. Hashtag           : on 🟢 — #이름 (카카오 자동추가 방지)
2. Append title      : on 🟢 — 이름 뒤에 직함
3. Append company    : off ❌ — 이름 뒤에 (회사명)
4. Card as photo     : on 🟢 — 명함→연락처 사진
5. Korean reading    : on 🟢 — 외국 이름 한국어 독음
6. Korean style name : on 🟢 — 성 비움, 이름에 풀네임

00 = Reset ♺
38 = All on 🟢
49 = All off ❌

번호만 입력하면 on↔off 전환.
```

**이모지 규칙:** `on` → `🟢`, `off` → `❌`. 값 바로 뒤에 이모지 붙인다.

**규칙:**
- 번호, 항목명, 설명은 고정. 변경 금지.
- `on` / `off` 값만 config.json 실제 상태에 맞춰 출력.
- 불릿 리스트(•)나 다른 포맷으로 변환 금지.
- 부가 설명이나 "원하면 바꿔줄게" 같은 멘트 추가 금지.

### 설정 변경 — 번호 토글

**번호만 입력하면 현재 상태의 반대로 자동 전환된다.** config.json 파일을 실제로 수정하고, 아래 응답 포맷 그대로 출력.

**세션 규칙:** `/bizcard config` 실행 후 다음 1회 입력만 설정 변경으로 처리한다. 그 이후의 숫자 입력은 일반 대화로 취급. 설정을 연속 변경하려면 `/bizcard config`를 다시 입력.

**예시 1:** 현재 `3. Append company : off` 상태에서 사용자가 `3` 입력

**응답 (이 포맷 그대로):**
```
3. Append company    : on 🟢

All set now.
```

**예시 2:** 현재 `1. Hashtag : on` 상태에서 사용자가 `1` 입력

**응답 (이 포맷 그대로):**
```
1. Hashtag           : off ❌

All set now.
```

**규칙:** 변경된 항목만 한 줄 출력 + "All set now." 그 외 추가 멘트 금지.

### 특수 명령

| 코드 | 동작 | 설명 |
|:----:|------|------|
| `00` | Reset | 기본값으로 초기화 |
| `38` | All on | 전체 설정 켜기 |
| `49` | All off | 전체 설정 끄기 |

**입력:** `49`
**응답:**
```
📇 Bizcard Settings

1. Hashtag           : off ❌ — #이름 (카카오 자동추가 방지)
2. Append title      : off ❌ — 이름 뒤에 직함
3. Append company    : off ❌ — 이름 뒤에 (회사명)
4. Card as photo     : off ❌ — 명함→연락처 사진
5. Korean reading    : off ❌ — 외국 이름 한국어 독음
6. Korean style name : off ❌ — 성 비움, 이름에 풀네임

00 = Reset ♺
38 = All on 🟢
49 = All off ❌

All off. All set now.
```

**입력:** `00`
**응답:**
```
📇 Bizcard Settings (defaults)

1. Hashtag           : on 🟢 — #이름 (카카오 자동추가 방지)
2. Append title      : on 🟢 — 이름 뒤에 직함
3. Append company    : off ❌ — 이름 뒤에 (회사명)
4. Card as photo     : on 🟢 — 명함→연락처 사진
5. Korean reading    : on 🟢 — 외국 이름 한국어 독음
6. Korean style name : on 🟢 — 성 비움, 이름에 풀네임

00 = Reset ♺
38 = All on 🟢
49 = All off ❌

Reset to defaults. All set now.
```

### 번호-키 매핑 (고정)

| # | config key | 설명 |
|:---:|-----------|------|
| 1 | `hashtag` | 이름 앞에 `#` 추가 (카카오톡 자동추가 방지) |
| 2 | `appendTitle` | 이름 뒤에 직함 추가 |
| 3 | `appendCompany` | 이름 뒤에 `(회사명)` 추가 |
| 4 | `cardAsPhoto` | 명함 이미지를 연락처 사진으로 저장 |
| 5 | `koreanReading` | 외국 명함 이름/회사를 한국어 독음으로 기록 |
| 6 | `koreanStyleName` | 한국 명함: familyName 비우고 givenName에 풀네임 |

### 기본값 (00 Reset 시 적용)

```json
{
  "hashtag": true,
  "appendTitle": true,
  "appendCompany": false,
  "cardAsPhoto": true,
  "koreanReading": true,
  "koreanStyleName": true
}
```

---

## 12. 첫 사용 온보딩

사용자가 처음 명함을 보낼 때 (bizcard-log.jsonl이 없거나 비어있을 때):

```
📇 명함 스캐너 첫 사용!

기본 설정:
1. Hashtag           : on
2. Append title      : on
3. Append company    : off
4. Card as photo     : on
5. Korean reading    : on
6. Korean style name : on

설정 변경: /bizcard config
이 명함 처리할까?
```

이후에는 온보딩 없이 바로 처리.

---

## 13. 메모리 로깅

저장 성공 시 `memory/bizcard-log.jsonl`에 **최소한의 정보만** 기록한다. 이메일, 전화번호 등 민감한 PII는 저장하지 않는다. 상세 정보는 Google Contacts에서 resourceName으로 조회.

```json
{"ts": "2026-02-20T14:30:00Z", "name": "홍길동", "company": "ABC주식회사", "resourceName": "people/c1234567890"}
```

**PII 최소화 원칙:** 로그에는 이름과 회사명(검색용)만 남기고, 전화번호/이메일/주소는 저장하지 않는다.

---

## 14. 검색 & 조회

| 명령 | 동작 |
|------|------|
| "명함 검색 홍길동" / "bizcard search 홍길동" | People API `searchContacts` 실행 |
| "최근 명함" / "recent bizcards" | `bizcard-log.jsonl`에서 최근 10건 표시 |

---

## 15. 에러 처리

| 에러 상황 | 사용자 메시지 |
|-----------|--------------|
| OCR 실패 / 빈 결과 | "텍스트를 인식하지 못했어. 더 선명한 사진으로 다시 보내줘" |
| Maton API 실패 | "Google Contacts 연결을 확인해줘. API 키나 OAuth가 만료됐을 수 있어" |
| 빈 명함 (정보 없음) | "연락처 정보를 못 찾았어. 명함이 맞는지 확인해줘" |
| 네트워크 오류 | "네트워크 연결을 확인해줘" |
| 사진 업로드 실패 (연락처는 저장됨) | "연락처는 저장됐는데 사진 업로드가 실패했어. 다시 시도할까?" |
| config.json 파싱 오류 | 기본값으로 자동 복구 후 "설정 파일이 손상돼서 기본값으로 복구했어" |

---

## Config Reference

설정 파일: `skills/bizcard/config.json`

| # | key | 기본값 | 설명 |
|---|-----|--------|------|
| 1 | `hashtag` | `true` | 이름 앞에 `#` 추가 (카카오톡 자동추가 방지) |
| 2 | `appendTitle` | `true` | 이름 뒤에 직함 추가 |
| 3 | `appendCompany` | `false` | 이름 뒤에 `(회사명)` 추가 |
| 4 | `cardAsPhoto` | `true` | 명함 이미지를 연락처 사진으로 저장 |
| 5 | `koreanReading` | `true` | 외국 명함 이름/회사를 한국어 독음으로 기록 |
| 6 | `koreanStyleName` | `true` | 한국 명함: familyName 비우고 givenName에 풀네임 |

## Dependencies

| Tool | Purpose | Install |
|------|---------|---------|
| `MATON_API_KEY` | Maton API Gateway auth (People API proxy) | [maton.ai/settings](https://maton.ai/settings) |
| `NANO_BANANA_API_KEY` | Google Gemini API key (used by Nano Banana Pro for image correction) | [aistudio.google.com](https://aistudio.google.com/app/apikey) |

## References

- [references/people-api-fields.md](references/people-api-fields.md) — Google People API field reference
- [Google People API docs](https://developers.google.com/people/api/rest)
