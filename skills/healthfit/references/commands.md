# Quick Commands Instructions

> **Version:** v3.0.1  
> **Last Updated:** 2026-03-17  
> **Purpose:** Detailed instructions for all quick commands

---

## 📋 Command List

### Logging Commands

| Command | Alias | Function | Example | Responding Role |
|---------|-------|----------|---------|-----------------|
| `/log` | — | Quick workout log | `/log running 5km 32min` | Coach Alex |
| `/eat` | — | Quick diet log | `/eat lunch chicken breast salad` | Dr. Mei |
| `/weight` | — | Log today's weight | `/weight 70.2` | Analyst Ray |
| `/pr` | — | Log personal record | `/pr squat 80kg` | Coach Alex |

### Query Commands

| Command | Alias | Function | Example | Responding Role |
|---------|-------|----------|---------|-----------------|
| `/plan` | — | View today's training plan | `/plan` | Coach Alex |
| `/week` | — | View weekly summary | `/week` | Analyst Ray |
| `/month` | — | View monthly summary | `/month` | Analyst Ray |
| `/tcm` | — | View TCM constitution | `/tcm` | Dr. Chen |
| `/solar` | — | View solar term wellness | `/solar` | Dr. Chen |

### Settings Commands

| Command | Alias | Function | Example |
|---------|-------|----------|---------|---------|
| `/goal` | — | Modify fitness goal | `/goal muscle building` |
| `/menu` | — | Display full menu | `/menu` |
| `/healthfit-help` | `/hf-help` | Display help information | `/healthfit-help` |

---

## 🔧 Command Implementation Logic

### Command Parsing Flow

```
1. Detect if message starts with "/"
2. Extract command name (part before space)
3. Extract command parameters (part after space)
4. Route to corresponding role based on command name
5. Role processes command and returns result
```

### Command Routing Rules

| Command Prefix | Routes to Role | Processing Logic |
|---------------|---------------|-----------------|
| `/log`, `/pr` | Coach Alex | Parse exercise type, duration, intensity, record to workout_log.txt |
| `/eat` | Dr. Mei | Parse food name, estimate calories, record to nutrition_log.txt |
| `/weight` | Analyst Ray | Record weight to metrics_daily, update trends |
| `/plan`, `/week`, `/month` | Analyst Ray | Query database/log files, generate reports |
| `/tcm`, `/solar` | Dr. Chen | Read constitution profile/solar term data, provide advice |
| `/goal` | Multiple Roles | Update profile.json, notify related roles to adjust plans |
| `/menu`, `/help` | System | Display static menu/help information |

---

## 📝 Command Usage Examples

### 1. Log Workout

**Input:**
```
/log running 5km 32 minutes
```

**Parsed:**
- Command: `/log`
- Exercise type: Running
- Distance: 5km
- Duration: 32 minutes

**Response (Coach Alex):**
```
[Coach Alex] ✅ Today's workout logged!

🏃 Running 5km | 32 minutes
📊 Pace: 6'24"/km
🔥 Estimated calories: about 320 kcal
💪 Intensity: Moderate (RPE 6/10)

This is your 3rd cardio session this week, keep it up!
```

### 2. Log Diet

**Input:**
```
/eat lunch chicken breast 200g broccoli 150g brown rice 1 bowl
```

**Parsed:**
- Command: `/eat`
- Meal: Lunch
- Foods: Chicken breast 200g, broccoli 150g, brown rice 1 bowl

**Response (Dr. Mei):**
```
[Dr. Mei] ✅ Lunch logged!

🍗 Chicken breast 200g → about 330 kcal, protein 62g
🥦 Broccoli 150g → about 50 kcal, fiber 5g
🍚 Brown rice 1 bowl → about 215 kcal, carbs 45g

Total: about 595 kcal
Protein: 62g ✅ | Carbs: 45g | Fat: 5g

Well balanced, keep it up!
```

### 3. Log Weight

**Input:**
```
/weight 70.2
```

**Parsed:**
- Command: `/weight`
- Weight: 70.2 kg

**Response (Analyst Ray):**
```
[Analyst Ray] ✅ Weight logged!

⚖️ Today's weight: 70.2 kg
📈 vs Yesterday: -0.3 kg ⬇️
📊 This week's average: 70.5 kg
🎯 Distance to goal: -5.8 kg (12 weeks remaining)

Good trend, keep it up!
```

---

## ⚠️ Notes

1. **Command format:** Space separates command and parameters
2. **Parameters optional:** Some commands can be without parameters (e.g., `/plan`)
3. **Natural language compatible:** Even without using commands, natural language will be recognized (e.g., "log today's 5km run")
4. **Command conflicts:** `/help` changed to `/healthfit-help` to avoid conflicts with system commands

---

## 🔮 Future Plans (v3.1)

- [ ] `/photo` - Upload body comparison photos
- [ ] `/period` - Log menstrual cycle (female users)
- [ ] `/share` - Share achievements to social media
- [ ] `/compare` - Compare body composition changes

---

*HealthFit v3.0.1 | Quick Commands Instructions | 2026-03-17*
