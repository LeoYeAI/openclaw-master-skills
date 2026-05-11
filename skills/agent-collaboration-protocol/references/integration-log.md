# Integration Log — `shared/build-{YYYYMMDD}/integration.md`

## Format

```markdown
# Build: {Feature Name} — {Date}

## Status
Orchestrator: ⏳ Waiting / 🔍 Reviewing / ✅ Complete
Backend: 🔨 Building / ✅ Done / ❌ Blocked
Frontend: 🔨 Building / ✅ Done / ❌ Blocked

## Backend Progress
- [ ] Router implemented at `backend/router.py`
- [ ] Models defined at `backend/models.py`
- [ ] Endpoints responding correctly
- [ ] README updated

### Blockers
- ...

## Frontend Progress
- [ ] Components built in `frontend/components/`
- [ ] API client wired to endpoints
- [ ] All states handled (loading, empty, error, populated)
- [ ] Designs match spec

### Blockers
- ...

## Integration Notes
- Data format mismatch found: endpoint returns `items`, UI expects `data`
- Auth tokens not flowing through — need session cookie handling
```
