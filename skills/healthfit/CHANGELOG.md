# HealthFit Changelog

**Version:** v3.0.1  
**Last Updated:** 2026-03-17

---

## v3.0.1 (2026-03-17)

### Added
- ✅ SKILL.md frontmatter triggers (22 triggers) and keywords (10 keywords)
- ✅ config.json version unified to 3.0.1
- ✅ exercise_images directory structure (8 exercise categories)
- ✅ Terminology numbering rules (Western #001-#028, TCM #101-#120)
- ✅ Disaster recovery guide
- ✅ Session state management documentation
- ✅ commands.md quick command detailed instructions
- ✅ Bilingual glossary (glossary_bilingual.md)

### Fixed
- ✅ config.json draft_recovery: false → true
- ✅ analyst_ray.md format errors (deleted template placeholders)
- ✅ evals.json overly strict tests (test cases #3 and #7)
- ✅ Profiling flow added progress prompts
- ✅ draft_manager.py added unified logging format
- ✅ /help command changed to /healthfit-help to avoid conflicts
- ✅ config.json photo_upload field added explanatory note

### Optimized
- ✅ exercise_images/README.md clearly marked "Pending Supplement (v3.1 Plan)"
- ✅ onboarding.md added progress prompt principles
- ✅ Unified script logging format (logging module)
- ✅ storage_schema.md updated photo storage instructions

### Documentation
- ✅ Created CHANGELOG.md
- ✅ Created glossary_bilingual.md
- ✅ Created commands.md
- ✅ Multiple verification reports and checklists

---

## v3.0.0 (2026-03-17)

### Added
- 🎉 Four-in-one architecture (Coach Alex / Dr. Mei / Dr. Chen / Analyst Ray)
- 🎉 Integrated Western & TCM health management system
- 🎉 Three-tier profiling mode (Minimal/Standard/Complete)
- 🎉 Draft recovery mechanism (draft_manager.py)
- 🎉 14 quick commands
- 🎉 48 terminology entries (28 Western + 20 TCM)
- 🎉 Traditional exercise video resource links
- 🎉 Unified configuration file (config.json)

### Core Features
- 📋 Profiling flow (Western + TCM + Sexual Health)
- 🏋️ Training plan creation and logging
- 🥗 Nutrition advice and diet logging
- 📊 Weekly/Monthly report generation
- 🌿 TCM constitution identification (Nine Constitutions)
- 📈 Data anomaly detection and warnings
- 🏆 Achievement system
- 🔒 Privacy protection (secondary confirmation + random verification code)

### Script Tools
- 📦 init_db.py - Database initialization
- 📦 export.py - Data export (JSON/CSV/Markdown)
- 📦 backup.py - Data backup (enhanced error handling)
- 📦 draft_manager.py - Profiling draft management

### Reference Documents
- 📚 17 core reference documents
- 📚 4 Agent role files
- 📚 Exercise library (1300+ lines)
- 📚 Shopping guide (Fat Loss/Bulking/Maintenance)
- 📚 Tongue self-exam guide (standardized form)

---

## v2.x (Historical Versions)

### Known Issues
- Incomplete architecture
- Limited features
- Missing documentation

### Upgrade to v3.0
- ⚠️ v2.x users need to re-create profile (data structure changes)
- ⚠️ Recommend running `python scripts/init_db.py` to initialize database
- ⚠️ Old data can be exported via `python scripts/export.py` for backup

---

## Future Plans (v3.1)

### Feature Enhancements
- [ ] Female menstrual cycle automatic calculation
- [ ] Photo upload comparison feature
- [ ] Social sharing feature
- [ ] Exercise image resource supplement
- [ ] Sexual health data encrypted storage
- [ ] Data visualization (weight curves/training trends)

### Performance Optimization
- [ ] Database query optimization
- [ ] Caching mechanism
- [ ] Batch export optimization

---

*Last Updated: 2026-03-17 | HealthFit v3.0.1*
