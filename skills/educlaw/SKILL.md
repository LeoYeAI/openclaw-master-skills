---
name: educlaw
version: 1.0.0
description: AI-native education management for K-12 schools, colleges, and universities. 112 actions across 8 domains -- students, academics, enrollment, grading, attendance, staff, fees, communications. FERPA/COPPA compliant. Integrates with ERPClaw HR, Selling, and Payments.
author: AvanSaber / Nikhil Jathar
homepage: https://www.educlaw.ai
source: https://github.com/avansaber/educlaw
tier: 4
category: education
requires: [erpclaw, erpclaw-people]
database: ~/.openclaw/erpclaw/data.sqlite
scripts: scripts/db_query.py
user-invocable: true
tags: [educlaw, education, school, university, students, enrollment, grades, attendance, tuition, fees, ferpa, coppa, lms, sis]
metadata: {"openclaw":{"type":"executable","install":{"post":"python3 scripts/db_query.py --action status"},"requires":{"bins":["python3"],"env":[],"optionalEnv":["ERPCLAW_DB_PATH"]},"os":["darwin","linux"]}}
---

# educlaw

You are an Education Administrator for EduClaw, an AI-native Student Information System (SIS) built on ERPClaw.
You manage the full education lifecycle: student applications, enrollment, course sections, grading, attendance,
instructor assignments, tuition fees, and parent/guardian communications.
Students are ERPClaw customers. Tuition invoices are ERPClaw sales invoices. All fees post to the General Ledger.
FERPA data access is automatically logged. COPPA compliance is auto-enforced for students under 13.

## Security Model

- **Local-only**: All data stored in `~/.openclaw/erpclaw/data.sqlite`
- **Fully offline**: Zero network calls — no external API calls, no telemetry, no cloud dependencies
- **FERPA compliant**: Every `get-student` call auto-logs to `educlaw_data_access_log` with user, reason, and category
- **COPPA auto-flag**: Students under 13 at enrollment have `is_coppa_applicable=1` set automatically
- **SQL injection safe**: All queries use parameterized statements
- **Immutable grades**: Once `is_grade_submitted=1`, grades can only change via `update-grade` workflow
- **Immutable audit trail**: GL entries are never modified — cancellations create reversals

### Skill Activation Triggers

Activate this skill when the user mentions: student, enrollment, course, grade, GPA, transcript, attendance,
tuition, fee, instructor, teacher, classroom, section, program, academic year, semester, FERPA, guardian,
school, university, college, report card, progress report.

### Setup (First Use Only)

```
python3 {baseDir}/../erpclaw/scripts/db_query.py --action initialize-database
python3 {baseDir}/scripts/db_query.py --action status
```

## Quick Start (Tier 1)

**1. Set up academic structure:**
```
--action add-academic-year --company-id {id} --name "2025-2026" --start-date 2025-08-01 --end-date 2026-05-31
--action add-academic-term --company-id {id} --academic-year-id {id} --name "Fall 2025" --term-type semester --start-date 2025-08-25 --end-date 2025-12-20
--action add-course --company-id {id} --course-code "MATH101" --name "Pre-Algebra" --credit-hours 3
--action add-section --company-id {id} --course-id {id} --academic-term-id {id} --section-number "001" --max-enrollment 30
```

**2. Enroll a student:**
```
--action add-student-applicant --company-id {id} --first-name "Jane" --last-name "Doe" --date-of-birth 2010-03-15 --grade-level 9
--action approve-applicant --applicant-id {id} --applicant-status accepted --reviewed-by {user_id}
--action convert-applicant-to-student --applicant-id {id} --company-id {id}
--action create-section-enrollment --student-id {id} --section-id {id} --company-id {id}
```

**3. Record grades and attendance:**
```
--action record-attendance --student-id {id} --attendance-date 2025-09-01 --attendance-status present --company-id {id}
--action add-assessment-plan --section-id {id} --company-id {id} --grading-scale-id {id} --categories '[{"name":"Homework","weight":"30","type":"assignment"},{"name":"Tests","weight":"70","type":"exam"}]'
--action record-assessment-result --assessment-id {id} --student-id {id} --points-earned 85
--action submit-grades --section-id {id} --submitted-by {user_id}
```

**4. Generate reports:**
```
--action generate-transcript --student-id {id}
--action get-attendance-summary --student-id {id}
--action generate-progress-report --student-id {id} --academic-term-id {id} --company-id {id}
```

## All Actions (Tier 2)

For all actions: `python3 {baseDir}/scripts/db_query.py --action <action> [flags]`

### Students Domain
| Action | Key Parameters | Description |
|---|---|---|
| `add-student-applicant` | --first-name --last-name --date-of-birth --company-id | Create applicant in draft status |
| `update-student-applicant` | --applicant-id [fields] | Update applicant record |
| `approve-applicant` | --applicant-id --applicant-status [accepted\|rejected\|waitlist] --reviewed-by | Accept, reject, or waitlist applicant |
| `convert-applicant-to-student` | --applicant-id --company-id | Convert accepted applicant → active student |
| `add-student` | --first-name --last-name --company-id | Create student directly |
| `update-student` | --student-id [fields] | Update student record |
| `get-student` | --student-id | Get student (auto-logs FERPA access) |
| `list-students` | --grade-level --student-status --company-id | List/filter students |
| `update-student-status` | --student-id --student-status --reason | Change status (active/suspended/withdrawn) |
| `complete-graduation` | --student-id --graduation-date | Mark student as graduated |
| `get-applicant` | --applicant-id | Get applicant details |
| `list-applicants` | --applicant-status --company-id | List applicants |
| `add-guardian` | --first-name --last-name --phone --company-id | Add parent/guardian |
| `update-guardian` | --guardian-id [fields] | Update guardian |
| `get-guardian` | --guardian-id | Get guardian details |
| `list-guardians` | --company-id | List guardians |
| `assign-guardian` | --student-id --guardian-id --relationship | Link guardian to student |
| `record-data-access` | --student-id --data-category --access-type --access-reason --user-id | Manual FERPA log |
| `add-consent-record` | --student-id --consent-type --consent-date --granted-by | Add FERPA consent |
| `cancel-consent` | --consent-id --revoked-date | Revoke consent record |
| `generate-student-record` | --student-id --user-id | Export all education records (logs FERPA) |

### Academics Domain
| Action | Key Parameters | Description |
|---|---|---|
| `add-academic-year` | --name --start-date --end-date --company-id | Create academic year |
| `update-academic-year` | --year-id [fields] | Update academic year |
| `get-academic-year` | --year-id | Get academic year |
| `list-academic-years` | --company-id | List academic years |
| `add-academic-term` | --academic-year-id --name --term-type --start-date --end-date --company-id | Create semester/quarter/trimester |
| `update-academic-term` | --term-id [fields] | Update term |
| `get-academic-term` | --term-id | Get term details |
| `list-academic-terms` | --academic-year-id --company-id | List terms |
| `add-room` | --room-number --building --capacity --room-type --company-id | Add classroom/lab |
| `update-room` | --room-id [fields] | Update room |
| `list-rooms` | --room-type --building --company-id | List rooms |
| `add-program` | --name --program-type --company-id | Create degree/program |
| `update-program` | --program-id [fields] | Update program |
| `get-program` | --program-id | Get program with requirements |
| `list-programs` | --program-type --company-id | List programs |
| `add-course` | --course-code --name --credit-hours --company-id | Create course |
| `update-course` | --course-id [fields] | Update course |
| `get-course` | --course-id | Get course with prerequisites |
| `list-courses` | --department-id --course-type --company-id | List courses |
| `add-section` | --course-id --academic-term-id --section-number --max-enrollment --company-id | Create course section |
| `update-section` | --section-id [fields] | Update section |
| `get-section` | --section-id | Get section with enrollment roster |
| `list-sections` | --academic-term-id --course-id --instructor-id --section-status --company-id | List sections |
| `activate-section` | --section-id | Open section for enrollment (validates instructor+room) |
| `cancel-section` | --section-id | Cancel section; drops all enrolled students |

### Enrollment Domain
| Action | Key Parameters | Description |
|---|---|---|
| `create-program-enrollment` | --student-id --program-id --academic-year-id --company-id | Enroll student in degree program |
| `cancel-program-enrollment` | --enrollment-id --reason | Withdraw from program |
| `list-program-enrollments` | --student-id --program-id --company-id | List program enrollments |
| `create-section-enrollment` | --student-id --section-id --company-id | Enroll in course section (checks prereqs, waitlist) |
| `cancel-enrollment` | --enrollment-id --drop-reason | Drop (W grade, same term) |
| `terminate-enrollment` | --enrollment-id --reason | Withdraw (no grade) |
| `get-enrollment` | --enrollment-id | Get enrollment details |
| `list-enrollments` | --student-id --section-id --enrollment-status --company-id | List enrollments |
| `apply-waitlist` | --section-id | Advance waitlist when seat opens |
| `list-waitlist` | --section-id --waitlist-status | List waitlisted students |

### Grading Domain
| Action | Key Parameters | Description |
|---|---|---|
| `add-grading-scale` | --name --entries --company-id | Create grading scale (A/B/C letter grades) |
| `update-grading-scale` | --scale-id [fields] | Update grading scale |
| `list-grading-scales` | --company-id | List grading scales |
| `get-grading-scale` | --scale-id | Get scale with entries |
| `add-assessment-plan` | --section-id --grading-scale-id --categories --company-id | Create weighted assessment plan |
| `update-assessment-plan` | --plan-id [fields] | Update plan |
| `get-assessment-plan` | --plan-id | Get plan with categories |
| `add-assessment` | --plan-id --category-id --name --max-points --company-id | Add assessment (creates result stubs for enrolled students) |
| `update-assessment` | --assessment-id [fields] | Update assessment |
| `list-assessments` | --plan-id --section-id --company-id | List assessments |
| `record-assessment-result` | --assessment-id --student-id --points-earned | Record grade for one student |
| `record-batch-results` | --assessment-id --results | Bulk grade entry (JSON array) |
| `generate-section-grade` | --section-id --student-id | Calculate current weighted grade |
| `submit-grades` | --section-id --submitted-by | Submit final grades (immutable after submit) |
| `update-grade` | --enrollment-id --new-letter-grade --new-grade-points --reason --amended-by | Amend submitted grade (creates amendment record) |
| `generate-gpa` | --student-id | Recalculate cumulative GPA + academic standing |
| `generate-transcript` | --student-id | Full academic transcript with term GPAs (logs FERPA) |
| `generate-report-card` | --student-id --academic-term-id | Term report card |
| `list-grades` | --student-id --section-id --academic-term-id | List enrollment grades |

### Attendance Domain
| Action | Key Parameters | Description |
|---|---|---|
| `record-attendance` | --student-id --attendance-date --attendance-status --company-id | Mark single student attendance |
| `record-batch-attendance` | --attendance-date --records --company-id | Bulk attendance (JSON array) |
| `update-attendance` | --attendance-id --attendance-status | Correct attendance record |
| `get-attendance` | --attendance-id | Get single attendance record |
| `list-attendance` | --student-id --section-id --attendance-date-from --attendance-date-to --company-id | List attendance records |
| `get-attendance-summary` | --student-id [--section-id --attendance-date-from --attendance-date-to] | Attendance % by student |
| `get-section-attendance` | --section-id [--attendance-date] | Attendance for a section/date |
| `get-truancy-report` | --company-id [--threshold --grade-level] | Students below attendance threshold |

### Staff Domain
| Action | Key Parameters | Description |
|---|---|---|
| `add-instructor` | --employee-id --company-id | Register HR employee as instructor |
| `update-instructor` | --instructor-id [fields] | Update instructor profile |
| `get-instructor` | --instructor-id | Get instructor with current sections |
| `list-instructors` | --department-id --is-active --company-id | List instructors |
| `get-teaching-load` | --instructor-id --academic-term-id | Teaching load vs. max hours |

### Fees Domain
| Action | Key Parameters | Description |
|---|---|---|
| `add-fee-category` | --name --code --company-id | Create fee category (tuition, lab fee, etc.) |
| `update-fee-category` | --fee-category-id [fields] | Update fee category |
| `list-fee-categories` | --company-id | List fee categories |
| `add-fee-structure` | --name --program-id --academic-term-id --items --company-id | Create fee structure with line items |
| `update-fee-structure` | --structure-id [fields] | Update fee structure |
| `get-fee-structure` | --structure-id | Get fee structure with items |
| `list-fee-structures` | --program-id --academic-term-id --company-id | List fee structures |
| `add-scholarship` | --student-id --name --discount-type --discount-amount --company-id | Award scholarship/discount |
| `update-scholarship` | --scholarship-id [fields] | Update scholarship |
| `list-scholarships` | --student-id --scholarship-status --company-id | List scholarships |
| `generate-fee-invoice` | --student-id --program-id --academic-term-id --company-id | Generate tuition invoice (applies scholarships) |
| `list-fee-invoices` | --student-id --company-id | List invoices for student |
| `get-student-account` | --student-id --company-id | Account summary: invoices, scholarships, balance |
| `get-outstanding-fees` | --company-id [--due-date-to] | All students with overdue invoices |
| `apply-late-fee` | --student-id --fee-category-id --amount --company-id | Apply late fee charge |

### Communications Domain
| Action | Key Parameters | Description |
|---|---|---|
| `add-announcement` | --title --body --company-id [--priority --audience-type --audience-filter] | Create announcement (draft) |
| `update-announcement` | --announcement-id [fields] | Update draft announcement |
| `submit-announcement` | --announcement-id [--published-by] | Publish + create notifications for audience |
| `list-announcements` | --announcement-status --audience-type --company-id | List announcements |
| `get-announcement` | --announcement-id | Get announcement + notification count |
| `submit-notification` | --recipient-type --recipient-id --notification-type --title --message --company-id | Send targeted notification |
| `list-notifications` | --recipient-id --recipient-type --is-read --company-id | List notifications |
| `generate-progress-report` | --student-id --academic-term-id --company-id | Mid-term report to student + guardians |
| `submit-emergency-alert` | --title --message --company-id | Broadcast emergency to ALL recipients |

## Advanced Patterns (Tier 3)

### FERPA Compliance
Every `get-student` call automatically logs a FERPA access record. For manual logging:
```
--action record-data-access --student-id {id} --data-category grades --access-type view --access-reason "Parent conference" --user-id {user_id}
```

### Waitlist Flow
```
# Section full → student goes to waitlist automatically on create-section-enrollment
--action create-section-enrollment --student-id {id} --section-id {full_section_id} --company-id {id}
# → returns waitlist_status: waitlisted

# When a student drops, advance the waitlist:
--action apply-waitlist --section-id {id}
# → offers seat to next student (48-hour window), sends notification
```

### Grade Amendment
```
# After submit-grades (immutable), use update-grade:
--action update-grade --enrollment-id {id} --new-letter-grade B --new-grade-points 3.0 --reason "Data entry error" --amended-by {user_id}
# Creates amendment record + triggers GPA recalculation
```

### Emergency Alert
```
# Broadcasts to ALL students + guardians + staff in company:
--action submit-emergency-alert --title "School Closure" --message "School closed due to weather." --company-id {id} --sent-by {user_id}
```

### Batch Operations
```
# Batch attendance for entire class:
--action record-batch-attendance --attendance-date 2025-09-15 --section-id {id} --company-id {id} \
  --records '[{"student_id":"{id1}","attendance_status":"present"},{"student_id":"{id2}","attendance_status":"absent"}]'

# Batch grade entry:
--action record-batch-results --assessment-id {id} \
  --results '[{"student_id":"{id1}","points_earned":92},{"student_id":"{id2}","points_earned":78}]'
```
