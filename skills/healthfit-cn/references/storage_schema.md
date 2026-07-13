# HealthFit 数据存储 Schema

## 存储架构总览

```
HealthFit 数据存储
│
├── JSON 文件（结构化数据）
│   ├── profile.json — 基础生理数据档案
│   ├── profile_health_history.json — 健康史
│   ├── profile_fitness_baseline.json — 体测基准
│   ├── private_sexual_health.json — 性健康隐私数据（独立存储，二次确认门控）
│   ├── tcm_profile.json — 中医体质档案
│   └── daily/YYYY-MM-DD.json — 每日综合日志
│
├── TXT 文件（文本记录）
│   ├── workout_log.txt — 运动训练日志
│   ├── nutrition_log.txt — 饮食记录日志
│   ├── glossary_western.txt — 西医术语库
│   ├── glossary_tcm.txt — 中医术语库
│   └── achievements.txt — 成就里程碑记录
│
├── SQLite 数据库（查询优化）
│   └── healthfit.db
│       ├── workouts — 运动记录表
│       ├── nutrition_entries — 饮食记录表
│       ├── metrics_daily — 每日身体指标表
│       ├── pr_records — 个人最佳成绩表
│       ├── weekly_summaries — 周统计缓存
│       └── monthly_summaries — 月统计缓存
│
└── assets/ 资源文件（非用户数据）
    └── exercise_images/ — 动作图解资源（公开资源/用户自拍）
        └── [用户自拍照片建议加密存储或存于私有目录]
```

---

## 隐私数据保护说明

### 敏感数据分类

| 数据类别 | 文件 | 保护级别 | 说明 |
|---------|------|---------|------|
| **高度敏感** | `private_sexual_health.json` | 🔴 最高级 | 独立存储，默认排除备份/导出，需二次确认 |
| **中度敏感** | `profile_health_history.json` | 🟡 高级 | 包含用药史、疾病史，建议加密 |
| **低敏感度** | `profile.json`, `workout_log.txt` | 🟢 普通级 | 可正常备份/导出 |
| **用户自拍照片** | `assets/exercise_images/` | 🟡 高级 | 建议加密存储或存于私有目录，不随技能分发 |

### 用户自拍照片存储方案

**如用户选择拍摄动作照片供 AI 纠正：**

1. **存储位置：** 建议存于用户私有目录（如 `data/private_photos/`），而非技能目录
2. **加密方案：** 可使用 base64 编码 + 密码保护，或调用系统加密 API
3. **访问控制：** 仅在用户明确授权时读取，用后及时清理
4. **备份策略：** 默认排除在备份之外，用户可手动选择是否包含
5. **当前状态：** ⚠️ v3.1 计划功能，当前版本需手动上传图片到 `exercise_images` 目录

**实现示例（伪代码）：**
```python
# 用户自拍照片存储建议
photo_path = Path(__file__).parent.parent / "data" / "private_photos" / f"{date}_{exercise}.jpg"
# 建议：使用加密库（如 cryptography）对照片进行加密存储
# 或：仅保存照片的 base64 编码到 JSON，原始照片不落地
```

---

### 性健康数据加密方案（可选）

**当前状态：** ⚠️ 明文存储（依赖文件隔离 + 备份排除）

**加密升级方案（未来迭代）：**

#### 方案 A：简单加密（Base64 + XOR）
```python
# scripts/crypto_utils.py
import base64
import hashlib
import json

def encrypt_data(data: dict, password: str) -> str:
    """简单加密（非军用级，但足够防止随意查看）"""
    json_str = json.dumps(data, ensure_ascii=False)
    key = hashlib.sha256(password.encode()).digest()
    encrypted_bytes = bytes([b ^ key[i % len(key)] for i, b in enumerate(json_str.encode('utf-8'))])
    return base64.b64encode(encrypted_bytes).decode('ascii')

def decrypt_data(encrypted_str: str, password: str) -> dict:
    """解密数据"""
    key = hashlib.sha256(password.encode()).digest()
    encrypted_bytes = base64.b64decode(encrypted_str.encode('ascii'))
    decrypted_bytes = bytes([b ^ key[i % len(key)] for i, b in enumerate(encrypted_bytes)])
    return json.loads(decrypted_bytes.decode('utf-8'))
```

#### 方案 B：AES-256 加密（推荐）
```python
# scripts/secure_storage.py
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

def generate_key(password: str, salt: bytes = None) -> tuple:
    """从密码生成加密密钥"""
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt

def encrypt_file(data: dict, password: str, filepath: Path):
    """加密并保存文件"""
    key, salt = generate_key(password)
    fernet = Fernet(key)
    
    json_bytes = json.dumps(data, ensure_ascii=False).encode('utf-8')
    encrypted = fernet.encrypt(json_bytes)
    
    # 保存 salt + 加密数据
    filepath.write_bytes(salt + encrypted)
```

**实施建议：**
- 当前版本：明文存储 + 文件隔离 + 备份排除（已足够安全）
- 未来版本：可选加密升级（用户设置密码后启用）
- 密码管理：密码仅存于用户记忆中，系统不保存（丢失无法恢复）

---

## JSON Schema 定义

### 1. profile.json（基础生理数据）

```json
{
  "created_at": "2026-03-16",
  "updated_at": "2026-03-16",
  "nickname": "用户昵称",
  "gender": "male",
  "age": 28,
  "height_cm": 175,
  "weight_kg": 70.5,
  "body_fat_pct": 18.5,
  "waist_cm": 82,
  "hip_cm": 96,
  "bmi": 23.0,
  "bmr": 1780,
  "tdee": 2490,
  "activity_level": "moderate",
  "primary_goal": "fat_loss",
  "secondary_goals": ["glute_shape", "cardio"],
  "target_weight_kg": 65,
  "goal_deadline": "2026-09-16",
  "has_gym": true,
  "equipment": ["dumbbells", "resistance_bands"],
  "weekly_workout_days": 4,
  "session_duration_min": 60,
  "preferred_time": "evening",
  "diet_type": "omnivore",
  "food_allergies": [],
  "alcohol_weekly": "occasional",
  "work_type": "sedentary",
  "stress_level": 6,
  "sleep_target_hours": 7.5
}
```

### 2. profile_health_history.json（健康史）

```json
{
  "medications": [
    {
      "name": "X 药",
      "category": "降压药",
      "start_date": "2024-06",
      "status": "ongoing",
      "purpose": "高血压",
      "notes": "影响运动强度上限"
    }
  ],
  "diseases": [
    {
      "name": "轻度腰椎间盘突出",
      "diagnosed_date": "2024-03",
      "status": "managed",
      "impact_on_training": "避免高负荷脊椎压缩动作"
    }
  ],
  "surgeries": [],
  "chronic_conditions": ["hypertension"],
  "allergies": {
    "food": ["坚果"],
    "medication": []
  }
}
```

### 3. profile_fitness_baseline.json（体测基准）

```json
{
  "test_date": "2026-03-16",
  "cardio": {
    "run_1500m_sec": null,
    "run_2km_sec": 720,
    "step_test_recovery_hr": 95
  },
  "upper_body": {
    "pushup_max": 22,
    "pushup_type": "standard",
    "pullup_max": 5,
    "dumbbell_curl_max_kg": 14
  },
  "core": {
    "plank_sec": 85,
    "situp_1min": 28,
    "side_plank_left_sec": 60,
    "side_plank_right_sec": 55
  },
  "lower_body": {
    "squat_bodyweight_max": 30,
    "lunge_max": 20,
    "single_leg_squat_can_do": false
  },
  "flexibility": {
    "seated_reach_cm": -3,
    "shoulder_clasp_can_do": false
  }
}
```

### 4. private_sexual_health.json（性健康隐私数据）

```json
{
  "privacy_confirmed": true,
  "created_at": "2026-03-16",
  "last_updated": "2026-03-16",
  "common_data": {
    "frequency_weekly": "B",
    "post_sex_fatigue_level": "B",
    "affects_next_day_training": "A"
  },
  "male_data": {
    "erectile_function_score": 7,
    "morning_erection_frequency": "B",
    "symptoms": [],
    "prostate_symptoms": false,
    "medications": []
  },
  "female_data": null,
  "goals_related": [],
  "notes": ""
}
```

### 5. tcm_profile.json（中医体质档案）

```json
{
  "created_at": "2026-03-16",
  "last_assessed": "2026-03-16",
  "primary_constitution": "yang_xu",
  "secondary_constitutions": ["qi_xu"],
  "constitution_scores": {
    "ping_he": 45,
    "qi_xu": 62,
    "yang_xu": 78,
    "yin_xu": 30,
    "tan_shi": 40,
    "shi_re": 25,
    "xue_yu": 35,
    "qi_yu": 50,
    "te_bing": 20
  },
  "questionnaire": {
    "q1": "A",
    "q2": "A",
    "q3": "A"
  },
  "tongue_records": [
    {
      "date": "2026-03-16",
      "body_color": "淡白",
      "body_shape": "胖大有齿痕",
      "coating": "白腻苔",
      "moisture": "水滑",
      "notes": "边缘有轻微齿痕",
      "dr_chen_assessment": "典型阳虚 + 气虚舌象"
    }
  ],
  "current_plan": {
    "exercise_restrictions": ["避免大汗", "冬季减少室外"],
    "recommended_exercises": ["八段锦", "太极拳"],
    "food_therapy": {
      "beneficial": ["山药", "红枣", "羊肉"],
      "avoid": ["冷饮", "苦瓜"],
      "daily_tea": "黄芪红枣枸杞茶"
    },
    "acupoints": ["关元穴", "足三里"],
    "seasonal_notes": "冬至前后是调养黄金期"
  }
}
```

### 6. daily/YYYY-MM-DD.json（每日综合日志）

```json
{
  "date": "2026-03-16",
  "metrics": {
    "weight_kg": 70.2,
    "energy_level": 7,
    "sleep_hours": 7.0,
    "sleep_quality": 6,
    "stress_level": 5,
    "sore_muscles": ["quadriceps", "glutes"]
  },
  "workout_ids": ["workout:2026-03-16:1"],
  "nutrition_logged": true,
  "daily_note": "今天状态还不错，但下午有点困",
  "sexual_health_note": null
}
```

---

## TXT 日志格式

### workout_log.txt

```
[2026-03-16 19:30] 上肢力量训练 | 55 分钟
  - 哑铃卧推：4 组 (12/10/8/8) × 20-22kg
  - 单臂划船：3 组 × 12 次/侧 × 14kg
  - 面拉：3 组 × 15 次 × 拉力绳
  RPE: 7/10 | 完成度：100% | 备注：状态不错，卧推 PR 22kg

[2026-03-15 07:00] 晨跑 | 32 分钟
  - 距离：5.0km
  - 配速：6'24''/km
  - 平均心率：145bpm
  RPE: 6/10 | 完成度：100% | 备注：晨跑状态好
```

### nutrition_log.txt

```
[2026-03-16] 训练日 | 目标：2740 kcal
  早餐：燕麦 + 牛奶 + 鸡蛋 + 香蕉 = 550 kcal (P30g/C65g/F12g)
  午餐：鸡胸肉 + 糙米饭 + 西兰花 = 750 kcal (P45g/C85g/F18g)
  晚餐：三文鱼 + 红薯 + 芦笋 = 700 kcal (P35g/C60g/F25g)
  加餐：蛋白粉 + 苹果 + 杏仁 = 400 kcal (P28g/C25g/F15g)
  ────────────────────────────────────────────────────
  合计：2400 kcal (P138g/C235g/F70g)
  达标率：热量 88% | 蛋白质 99% | 碳水 61% | 脂肪 100%
  备注：碳水偏低，明天注意补充
```

### achievements.txt

```
[2026-03-16 19:45] 成就解锁：铁人意志
  描述：连续训练 30 天
  难度：🔴 困难
  数据统计：
    - 开始日期：2026-02-15
    - 结束日期：2026-03-16
    - 总训练次数：26 次
    - 总训练时长：1,480 分钟
    - 总消耗：约 11,200 kcal
  期间进步：
    - 体重：-2.0kg
    - 深蹲：+14%
    - 5km 配速：-25 秒
```

---

## SQLite 数据库 Schema

```sql
-- 运动记录表
CREATE TABLE workouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    type TEXT NOT NULL,
    subtype TEXT,
    duration_min INTEGER,
    calories INTEGER,
    exercises TEXT,
    rpe INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 饮食记录表
CREATE TABLE nutrition_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    meal_type TEXT NOT NULL,
    items TEXT,
    total_calories INTEGER,
    protein_g REAL,
    carbs_g REAL,
    fat_g REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 每日指标表
CREATE TABLE metrics_daily (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL UNIQUE,
    weight_kg REAL,
    sleep_hours REAL,
    sleep_quality INTEGER,
    energy_level INTEGER,
    stress_level INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- PR 记录表
CREATE TABLE pr_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exercise_name TEXT NOT NULL,
    best_value REAL NOT NULL,
    unit TEXT NOT NULL,
    achieved_date TEXT NOT NULL,
    history TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 周统计缓存表
CREATE TABLE weekly_summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    week TEXT NOT NULL UNIQUE,
    period_start TEXT,
    period_end TEXT,
    training_days INTEGER,
    total_duration_min INTEGER,
    total_calories INTEGER,
    avg_weight_kg REAL,
    weight_change_kg REAL,
    achievements TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 月统计缓存表
CREATE TABLE monthly_summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    month TEXT NOT NULL UNIQUE,
    period_start TEXT,
    period_end TEXT,
    training_days INTEGER,
    total_workouts INTEGER,
    avg_weight_kg REAL,
    weight_change_kg REAL,
    pr_count INTEGER,
    achievements TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 索引优化
CREATE INDEX idx_workouts_date ON workouts(date);
CREATE INDEX idx_nutrition_date ON nutrition_entries(date);
CREATE INDEX idx_metrics_date ON metrics_daily(date);
CREATE INDEX idx_weekly_week ON weekly_summaries(week);
CREATE INDEX idx_monthly_month ON monthly_summaries(month);
```

---

## 数据备份策略

### 自动备份
- **频率**：每周日凌晨 2:00
- **内容**：所有 JSON 文件 + SQLite 数据库
- **位置**：`data/db/backup/`
- **保留**：最近 4 次备份

### 手动导出
**用户命令**：`导出我的数据`

**输出**：
- 所有 JSON 文件打包
- SQLite 数据库导出为 CSV
- 生成可读的 Markdown 报告

### 数据清除
**用户命令**：`清除健康数据`

**操作**：
1. 清空所有 JSON 文件内容
2. 删除 SQLite 数据库
3. 保留 TXT 日志（可选）
4. 重置所有计数器

---

*存储 Schema 完成 | 下一步：回复模板（response_templates.md）*
