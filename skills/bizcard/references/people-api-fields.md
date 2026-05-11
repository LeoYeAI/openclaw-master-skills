# Google People API — Person Resource Fields

Reference for fields used by the bizcard skill when creating/updating Google Contacts.

## names[]

| Field | Type | Description |
|-------|------|-------------|
| `displayName` | string | Read-only composite, but settable via `unstructuredName`. Used for config-formatted name (e.g. `#홍길동 과장 (ABC주식회사)`) |
| `familyName` | string | 성 (family/last name). Always stored without formatting |
| `givenName` | string | 이름 (given/first name). Always stored without formatting |
| `unstructuredName` | string | Free-form name. Set this to apply custom displayName format |
| `phoneticGivenName` | string | 이름의 발음 표기 (독음). 검색 가능. |
| `phoneticFamilyName` | string | 성의 발음 표기 (독음). 검색 가능. |

**bizcard usage (한국식, `koreanStyleName=true`):**
- `unstructuredName` → config-formatted display name (예: `#홍길동 과장`)
- `givenName` → 풀네임 (예: `홍길동`)
- `familyName` → 빈 문자열 `""`

**bizcard usage (외국식, `koreanStyleName=false` 또는 비한국어 명함):**
- `unstructuredName` → config-formatted display name (예: `John Smith`)
- `givenName` → first name (예: `John`)
- `familyName` → last name (예: `Smith`)
- `phoneticGivenName` → **풀네임 독음 통째로** (예: `존 스미스`) — `koreanReading=true`일 때. 성/이름 분리 금지.
- `phoneticFamilyName` → 비움 `""`

## organizations[]

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Company name (회사명) |
| `title` | string | Job title (직함) |
| `department` | string | Department (부서) |
| `type` | string | `work` / `school` / `other` |

## emailAddresses[]

| Field | Type | Description |
|-------|------|-------------|
| `value` | string | Email address |
| `type` | string | `work` / `home` / `other` |

## phoneNumbers[]

| Field | Type | Description |
|-------|------|-------------|
| `value` | string | Phone number (E.164 or formatted) |
| `type` | string | `mobile` / `work` / `home` / `workFax` / `homeFax` / `main` / `other` |

**bizcard normalization:**
- `010-1234-5678` → `+82-10-1234-5678`
- `02-1234-5678` → `+82-2-1234-5678`
- International numbers preserved as-is

## addresses[]

| Field | Type | Description |
|-------|------|-------------|
| `formattedValue` | string | Full address string |
| `type` | string | `work` / `home` / `other` |

## urls[]

| Field | Type | Description |
|-------|------|-------------|
| `value` | string | URL |
| `type` | string | `work` / `home` / `blog` / `profile` / `other` |

## biographies[]

| Field | Type | Description |
|-------|------|-------------|
| `value` | string | Free-form text (notes, SNS, qualifications) |
| `contentType` | string | `TEXT_PLAIN` / `TEXT_HTML` |

## photos — updateContactPhoto

Contact photo is set via a separate API call after contact creation.

**Endpoint:**
```
PATCH /google-contacts/v1/people/{resourceName}:updateContactPhoto
```

**Request body:**
```json
{
  "photoBytes": "<base64-encoded-image>"
}
```

**bizcard usage:**
1. Create contact → get `resourceName`
2. Read image file, base64-encode it
3. Call `updateContactPhoto` with encoded bytes
4. If `deskewImage=true`, run ImageMagick deskew before encoding

**Response:** Returns updated `Person` resource with new photo URL.

## personFields Parameter

When reading contacts, specify which fields to return:

```
personFields=names,organizations,emailAddresses,phoneNumbers,addresses,urls,biographies,photos
```

## Full Create Example (한국식)

```json
{
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
  ],
  "biographies": [
    {"value": "명함 스캔으로 추가", "contentType": "TEXT_PLAIN"}
  ]
}
```

## References

- [People API: Person resource](https://developers.google.com/people/api/rest/v1/people)
- [People API: createContact](https://developers.google.com/people/api/rest/v1/people/createContact)
- [People API: updateContactPhoto](https://developers.google.com/people/api/rest/v1/people/updateContactPhoto)
- [People API: searchContacts](https://developers.google.com/people/api/rest/v1/people/searchContacts)
