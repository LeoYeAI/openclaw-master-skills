# CV Data Reference

Complete field documentation for the `cv_data` object in `POST /api/agent/cv`.

---

## Profile Fields

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `firstName` | string | **yes** | |
| `lastName` | string | **yes** | |
| `title` | string | **yes** | Headline or tagline (e.g. "Software Engineer", "Digital Creator") |
| `email` | string | **yes** | For contact, not publicly displayed |
| `phone` | string | no | |
| `city` | string | no | |
| `country` | string | no | |
| `summary` | string | no | 2-3 sentence career summary |
| `website` | string | no | URL |

## Social Links

```json
{ "platform": "LINKEDIN", "url": "https://..." }
```

Supported platforms: `LINKEDIN`, `GITHUB`, `TWITTER`, `DRIBBBLE`, `BEHANCE`, `STACKOVERFLOW`, `MEDIUM`, `YOUTUBE`, `INSTAGRAM`, `FACEBOOK`, `TIKTOK`, `XING`, `OTHER`

## Experience

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `jobTitle` | string | **yes** | NOT "position" or "role" |
| `company` | string | **yes** | |
| `location` | string | no | |
| `startDate` | string | no | Format: `YYYY` or `YYYY-MM` |
| `endDate` | string | no | Omit if current |
| `isCurrent` | boolean | no | |
| `description` | string | no | |
| `achievements` | string[] | no | Bullet points |

## Education

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `institution` | string | **yes** | |
| `degree` | string | no | e.g. "M.Sc.", "B.A." |
| `fieldOfStudy` | string | no | |
| `startDate` | string | no | |
| `endDate` | string | no | |
| `isCurrent` | boolean | no | |
| `description` | string | no | |
| `location` | string | no | |
| `grade` | string | no | |

## Skills (4 separate types)

**hardSkills** — Technical skills with proficiency level
```json
{ "name": "React", "level": 5 }
```
Level: 1 (Beginner) to 5 (Expert). Optional.

**softSkills** — Interpersonal skills
```json
{ "name": "Team Leadership" }
```

**toolSkills** — Tools and platforms
```json
{ "name": "Docker" }
```

**languages** — Spoken languages
```json
{ "name": "English", "level": "NATIVE" }
```
Level values: `NATIVE`, `C2`, `C1`, `B2`, `B1`, `A2`, `A1`

Do NOT use a generic `skills` array. It will be rejected.

## Projects

| Field | Type | Notes |
|-------|------|-------|
| `name` | string | Project name |
| `description` | string | What it does |
| `url` | string | Live URL or repo |
| `startDate` | string | |
| `endDate` | string | |
| `isCurrent` | boolean | |
| `technologies` | string[] | Tech stack |

## Certificates

| Field | Type | Notes |
|-------|------|-------|
| `name` | string | Certificate name |
| `issuer` | string | Issuing organization |
| `issueDate` | string | |
| `expiryDate` | string | |
| `credentialId` | string | |
| `url` | string | Verification link |

## Hobbies

```json
{ "name": "Rock Climbing", "description": "Bouldering 3x/week" }
```

## Full Example

```http
POST https://www.talent.de/api/agent/cv-simple
Content-Type: application/json

{
  "slug": "dev",
  "template_id": "003",
  "cv_data": {
    "firstName": "Alex",
    "lastName": "Johnson",
    "title": "Senior Full-Stack Developer",
    "email": "alex@example.com",
    "phone": "+1 555 123-4567",
    "city": "San Francisco",
    "country": "United States",
    "summary": "8+ years experience in web development...",
    "website": "https://alexjohnson.dev",
    "socialLinks": [
      { "platform": "LINKEDIN", "url": "https://linkedin.com/in/alexjohnson" },
      { "platform": "GITHUB", "url": "https://github.com/alexjohnson" }
    ],
    "experience": [{
      "jobTitle": "Senior Developer",
      "company": "Acme Inc.",
      "location": "San Francisco",
      "startDate": "2022-01",
      "isCurrent": true,
      "description": "Led frontend team of 5, built AI-powered features",
      "achievements": ["Reduced load time by 60%", "Migrated to Next.js"]
    }],
    "education": [{
      "institution": "Stanford University",
      "degree": "M.Sc.",
      "fieldOfStudy": "Computer Science",
      "startDate": "2016",
      "endDate": "2018",
      "grade": "3.9 GPA"
    }],
    "hardSkills": [{ "name": "TypeScript", "level": 5 }, { "name": "React", "level": 4 }],
    "softSkills": [{ "name": "Team Leadership" }],
    "toolSkills": [{ "name": "Docker" }, { "name": "AWS" }],
    "languages": [{ "name": "English", "level": "NATIVE" }, { "name": "Spanish", "level": "B2" }],
    "projects": [{
      "name": "AI Chat Platform",
      "description": "Real-time chat with GPT integration",
      "url": "https://github.com/alexjohnson/ai-chat",
      "technologies": ["React", "Node.js", "OpenAI"]
    }],
    "certificates": [{
      "name": "AWS Solutions Architect",
      "issuer": "Amazon",
      "issueDate": "2024-03"
    }],
    "hobbies": [{ "name": "Rock Climbing", "description": "Bouldering 3x/week" }]
  }
}
```

All fields beyond `firstName`, `lastName`, `title`, `email` are optional. Omit what you don't have — don't send empty arrays.
