# iGOT Portal — UI Selectors Reference

Last verified: March 2026. iGOT uses Angular-based SunBird platform.
Update selectors here if the portal redesigns.

---

## Login Page (igotkarmayogi.gov.in)

```
Login button (homepage)     : button.btn-login, [data-name="login"], text="Login"
Email input                 : input[type="email"], input[placeholder*="Email"]
Password input              : input[type="password"]
OTP login toggle            : text="Login using OTP", a.otp-login
OTP input                   : input[placeholder*="OTP"], input[maxlength="6"]
Sign In submit              : button[type="submit"], button.sign-in-btn
Parichay login              : text="Login with Parichay", .parichay-btn
```

---

## Learn Hub (portal.igotkarmayogi.gov.in/app/learn)

```
Search bar                  : input.search-input, input[placeholder*="Search"]
Course cards                : .course-card, .sb-card, [class*="course-item"]
Course title in card        : .course-title, .sb-card-title, h3.title
Course provider             : .course-provider, .sb-card-desc
Course duration             : .course-duration, [class*="duration"]
Enroll / Start btn on card  : button.enroll-btn, button[contains(text(),"Enroll")]
```

---

## Course TOC Page (app/toc/<id>/overview)

```
Course title                : h1.course-title, .toc-header h1
Enroll button               : button.enroll-action, button[text*="Enroll"]
Continue Learning button    : button[text*="Continue"], .resume-btn
Start Learning button       : button[text*="Start Learning"]
Progress bar                : .course-progress-bar, progress[value]
Certificate tab             : a[text*="Certificate"], .certificate-tab
Download certificate btn    : button[text*="Download"], .certificate-download
```

---

## My Dashboard (app/my-dashboard)

```
Enrolled courses section    : .enrolled-courses, [data-section="enrolled"]
Course progress             : .progress-value, span[class*="percent"]
Completed tab               : button[text*="Completed"], .tab-completed
Course status badge         : .status-badge, [class*="completion-status"]
```

---

## Profile Page (app/profile)

```
Karma Points display        : .karma-points, [data-id="karma"], span.points-value
Badges section              : .badges-container, .achievement-badges
Completed course count      : .completed-count, [text*="Completed"]
Username/name               : .user-name, .profile-name, header .username
```

---

## Notes for Selector Failures

1. iGOT runs on the **SunBird** platform (open source). Check SunBird docs if selectors break.
2. Many elements have dynamic Angular classes — prefer `text=` or `aria-label=` selectors
   over class-based ones when possible.
3. The portal is a SPA (Single Page App) — always wait for `networkidle` or specific
   elements to appear before scraping, not just page load.
4. Login state persists via localStorage JWT token — check `localStorage.getItem('userDetails')`
   to verify session without navigating to profile.
