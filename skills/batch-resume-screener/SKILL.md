---
name: batch-resume-screener
description: Batch screens multiple resumes against multiple job positions using strict evaluation rules from java-resume-screener skill. Invoke when user asks to batch screen resumes or evaluate multiple candidates against multiple job requirements.
---

# Batch Resume Screener

This skill helps you batch screen multiple resumes against multiple job positions with strict evaluation rules integrated from java-resume-screener skill.

## Usage

When a user asks to batch screen resumes, evaluate multiple candidates, process resume ZIP packages, or screen against multiple job positions, this skill should be invoked.

## Role

You are a professional technical recruiter/interviewer. Strictly follow the rules to complete batch resume initial screening evaluation. All evaluations are based solely on resume text content. No unfounded assumptions are allowed.

## Input Requirements

Provide the following two parts:

1. **Job Requirements**: Multiple job requirements documents (one for each position)
2. **Resumes**: Multiple resume files (PDF/DOC/DOCX) or a ZIP package containing multiple resumes

## Core Execution Rules

### 1. Four-Step Process Overview

**重要说明：只有步骤1使用脚本，步骤1.5、步骤2和步骤3由AI直接完成，不使用脚本，也不要创建python脚本！**

#### Step 1: Extract Resume Content (Using Script)
1. If input is a ZIP package, first extract all resume files (use step1_extract_resumes.py)
2. For each resume file (PDF/DOC/DOCX), extract text content
3. Save each resume's text as a separate .txt file in a designated directory
4. Provide the list of extracted resume .txt files

#### Step 1.5: Pre-filtering (AI Direct - Quick Scan)
1. Load all job requirements and identify key requirements for each position
2. For each resume, perform quick keyword matching:
   - Check if core technology keywords exist (e.g., "Java" for Java position)
   - Check if work experience meets minimum requirement
   - Check if education meets minimum requirement
3. Mark resumes as "high_match", "medium_match", or "low_match"
4. Save pre-filter results as a JSON file for reference in Step 2
5. Note: Pre-filtering does NOT reject candidates, only marks match level for reference

#### Step 2: Evaluate Resumes (AI Direct - Batch Evaluation)
1. Retrieve the list of all resume .txt files from Step 1
2. Load pre-filter results from Step 1.5 (if available)
3. Create a Todo List with tasks for each resume
4. Evaluate resumes in small batches (3-5 resumes at a time):
   a. Load resume .txt file contents for the batch
   b. For each resume in the batch:
      - Identify job level (junior/mid/senior) based on job requirements
      - Apply corresponding weight coefficients
      - Evaluate against all job positions using scoring rules
      - Complete full evaluation (hard requirements check + 7-dimension scoring)
      - Add confidence score
      - Save evaluation results as a JSON file
   c. Update Todo List to mark completed resumes
   d. Proceed to next batch

#### Step 3: Aggregate and Generate Reports (AI Direct Aggregation)
1. Load all evaluation result JSON files from Step 2
2. For each candidate, determine the best matching position with the highest score
3. Sort all candidates by total score descending
4. Generate multiple output formats:
   - **Markdown Report**: Comprehensive batch screening report
   - **Excel-ready Data**: Tabular format for HR filtering
   - **Comparison Table**: Side-by-side candidate comparison
   - **Highlights Summary**: Key highlights for interviewers

### 2. Pre-screening Hard Requirement Check

First check the hard requirements for each job position. **If any hard requirement is not met, directly output a rejection conclusion for that position without subsequent scoring.**

### 3. Hard Requirements (One-Vote Veto)

- **Education Threshold**: Whether meeting the minimum education requirement clearly stated in the job (e.g., bachelor's degree or above, full-time regular education)
- **Work Experience Threshold**: Whether meeting the minimum Java backend development work experience requirement clearly stated in the job
- **Other Hard Requirements**: "Must have/indispensable" other hard requirements clearly stated in the job (e.g., must have distributed project experience, must have financial industry experience, etc.)

### 4. Scoring System: Percentage + Weight Coefficients

#### 4.1 Core Design

**Design Principles**:
- Each dimension is scored on a 100-point scale (0-100)
- Weight coefficients control each dimension's contribution to total score
- Weight coefficients are dynamically adjusted based on job level

**Calculation Formula**:
```
Total Score = Academic Background × Weight1 + Career Stability × Weight2 + Tech Stack × Weight3 
            + Project Match × Weight4 + Problem Solving × Weight5 + Learning Ability × Weight6 + Bonus × Weight7
```

#### 4.2 Dynamic Weight Allocation

| Dimension | Junior | Mid | Senior |
|-----------|--------|-----|--------|
| Academic Background | 15% | 10% | 5% |
| Career Stability | 5% | 10% | 10% |
| Tech Stack Capability | 15% | 15% | 15% |
| Project Match | 20% | 25% | 25% |
| Problem Solving | 10% | 15% | 20% |
| Learning Ability | 20% | 15% | 10% |
| Bonus | 15% | 10% | 15% |

**Job Level Identification Rules**:
- **Junior**: Job requirements contain "初级" (junior), "1-3年", "应届" (fresh graduate) keywords
- **Mid**: Job requirements contain "中级" (mid-level), "3-5年" keywords
- **Senior**: Job requirements contain "高级" (senior), "资深", "5年以上", "架构" (architect) keywords

### 5. Dimension Scoring Standards (100-Point Scale)

#### 5.1 Academic Background (0-100 points)

```
Scoring Rules:
1. Institution Level (40 points):
   - 985/top institutions: 40 points
   - 211/double first-class: 30 points
   - Provincial key undergraduate: 20 points
   - Ordinary full-time undergraduate: 10 points
   - Associate degree: 5 points

2. Major Match (40 points):
   - Computer Science/Software Engineering: 40 points
   - Mathematics/Automation: 20 points
   - Cross-major with relevant certificates: 10 points
   - Completely cross-major: 0 points

3. Academic Performance (20 points):
   - Scholarships/ranking proof: 20 points
   - No relevant description: 0 points

Score = Institution Level + Major Match + Academic Performance
```

#### 5.2 Career Stability (0-100 points)

```
Scoring Rules (based only on clearly calculable time data from resume):

1. Average Tenure (60 points):
   - Average tenure ≥3 years: 60 points
   - Average tenure 2-3 years: 40 points
   - Average tenure 1-2 years: 20 points
   - Average tenure <1 year: 0 points

2. Job-hopping Frequency (40 points):
   - <1 job change per year: 40 points
   - ~1 job change per year: 20 points
   - ≥2 job changes per year: 0 points

Score = Average Tenure + Job-hopping Frequency
```

#### 5.3 Tech Stack Capability (0-100 points)

```
Scoring Rules:

1. Tech Stack Match (35 points):
   - 100% coverage of core technologies: 35 points
   - ≥80% coverage: 25 points
   - ≥60% coverage: 15 points
   - <60% coverage: 0 points

2. Tech Stack Breadth (20 points):
   - Covers backend frameworks, databases, caches, message queues, DevOps, etc.: 20 points
   - Covers basic backend technologies: 10 points
   - Narrow technology range: 0 points

3. Tech Stack Depth (25 points):
   - Source code understanding, tuning experience: 25 points
   - Proficient usage: 15 points
   - Surface-level understanding only: 0 points

4. Practical Experience (20 points):
   - Clear multi-project practice descriptions: 20 points
   - Basic practice descriptions: 10 points
   - Lack of practice descriptions: 0 points

Score = Match + Breadth + Depth + Practical
```

#### 5.4 Project Match (0-100 points)

```
Scoring Rules (5 aspects, 20 points each):

1. Business Domain & Industry Match:
   - Complete match with job business: 20 points
   - Partial match: 10 points
   - No match: 0 points

2. Project Scale & Complexity:
   - Equal to or higher than job requirements: 20 points
   - Slightly below job requirements: 10 points
   - Significantly below job requirements: 0 points

3. Personal Responsibility & Involvement:
   - Core developer/lead: 20 points
   - Core feature development: 15 points
   - Non-core module development: 8 points
   - Low involvement: 0 points

4. Technical Difficulty & Highlights:
   - Technical highlights/breakthroughs: 20 points
   - Some technical challenges: 10 points
   - Routine CRUD: 0 points

5. Project Results & Value:
   - Quantified results: 20 points
   - Qualitative result descriptions: 10 points
   - No result descriptions: 0 points

Score = Business + Scale + Responsibility + Difficulty + Results
```

#### 5.5 Problem Solving Ability (0-100 points)

```
Scoring Rules (quantifiable indicators can stack, max 100 points):

Quantifiable Indicators:
- Clear performance improvement data (e.g., "improved 50%"): +20 points
- Clear cost reduction data (e.g., "saved 30% server cost"): +20 points
- Clear user growth data: +15 points
- Complete technical solution description: +15 points
- Online issue troubleshooting cases: +15 points
- Architecture optimization/refactoring cases: +15 points

Score = min(sum of all indicators, 100)
```

#### 5.6 Learning Ability (0-100 points)

```
Scoring Rules (indicators can stack, max 100 points):

Assessment Indicators:
- Self-learned new technology and completed full project: +25 points
- High-quality open source projects/technical blogs: +20 points
- Technical competition awards: +20 points
- Relevant technical certificates: +15 points
- Quickly took over unfamiliar business and produced results: +15 points
- Clear technical growth trajectory: +10 points

Score = min(sum of all indicators, 100)
```

#### 5.7 Bonus (0-100 points)

```
Scoring Rules:

1. Job Priority Items Satisfaction (40 points):
   - Satisfies all or most priority items: 40 points
   - Satisfies some priority items: 20 points
   - Does not satisfy any priority items: 0 points

2. Technical Certifications (20 points):
   - Relevant advanced certifications: 20 points
   - Relevant basic certifications: 10 points
   - No relevant certifications: 0 points

3. Technical Influence (20 points):
   - Open source contributions/technical blogs/technical sharing: 20 points
   - Some technical sharing records: 10 points
   - No technical influence proof: 0 points

4. Other Highlights (20 points):
   - Award records/special achievements: 20 points
   - General highlights: 10 points
   - No other highlights: 0 points

Score = Priority Items + Certifications + Influence + Other
```

### 6. Confidence Score

Each evaluation result includes a confidence score:

```json
{
  "confidence": {
    "score": 0.85,
    "level": "high",
    "factors": {
      "resume_completeness": 0.9,
      "information_clarity": 0.8,
      "verifiable_data": 0.85
    },
    "suggestions": [
      "Resume project descriptions are detailed, scoring basis sufficient",
      "Recommend verifying work experience during interview"
    ]
  }
}
```

**Confidence Levels**:
- **High (0.8-1.0)**: Resume information complete, scoring basis sufficient
- **Medium (0.6-0.8)**: Resume information basically complete, some content unclear
- **Low (<0.6)**: Resume information incomplete, recommend manual review

### 7. Total Score Rating Reference

- **90-100 points**: Far exceeds job requirements, outstanding core dimension performance, high-quality candidate
- **75-89 points**: Completely meets job requirements, high core dimension match, recommend for interview
- **60-74 points**: Just meets basic job requirements, has obvious shortcomings, can be alternative evaluation
- **Below 60 points**: Meets hard thresholds, but large gap between core ability and job requirements, not recommended

### 8. Individual Evaluation JSON Output Format

For each resume, save the evaluation result as a JSON file with the following structure:

```json
{
  "candidate_name": "候选人姓名",
  "resume_file": "简历文件名.txt",
  "evaluation_time": "YYYY-MM-DD HH:MM:SS",
  "job_level": "junior/mid/senior",
  "weight_coefficients": {
    "academic_background": 0.15,
    "career_stability": 0.05,
    "tech_stack": 0.15,
    "project_match": 0.20,
    "problem_solving": 0.10,
    "learning_ability": 0.20,
    "bonus": 0.15
  },
  "pre_filter": {
    "match_level": "high_match/medium_match/low_match",
    "key_findings": ["关键发现1", "关键发现2"]
  },
  "positions": [
    {
      "position_name": "岗位名称",
      "hard_requirements_check": {
        "passed": true/false,
        "rejection_reason": "如果未通过，说明原因"
      },
      "dimension_scores": {
        "academic_background": {
          "score": 85,
          "breakdown": {
            "institution_level": 30,
            "major_match": 40,
            "academic_performance": 15
          },
          "reason": "评分理由"
        },
        "career_stability": {
          "score": 70,
          "breakdown": {
            "average_tenure": 40,
            "job_hopping_frequency": 30
          },
          "reason": "评分理由"
        },
        "tech_stack": {
          "score": 75,
          "breakdown": {
            "match": 25,
            "breadth": 15,
            "depth": 20,
            "practical": 15
          },
          "reason": "评分理由"
        },
        "project_match": {
          "score": 80,
          "breakdown": {
            "business_match": 15,
            "project_scale": 18,
            "responsibility": 17,
            "technical_difficulty": 15,
            "achievement": 15
          },
          "reason": "评分理由"
        },
        "problem_solving": {
          "score": 65,
          "reason": "评分理由"
        },
        "learning_ability": {
          "score": 70,
          "reason": "评分理由"
        },
        "bonus": {
          "score": 60,
          "breakdown": {
            "job_priority": 20,
            "certifications": 10,
            "influence": 20,
            "other": 10
          },
          "reason": "评分理由"
        }
      },
      "weighted_score": 72.5,
      "rating": "推荐面试",
      "recommended": true
    }
  ],
  "best_position": {
    "position_name": "推荐岗位名称",
    "weighted_score": 72.5,
    "rating": "推荐面试"
  },
  "confidence": {
    "score": 0.85,
    "level": "high",
    "factors": {
      "resume_completeness": 0.9,
      "information_clarity": 0.8,
      "verifiable_data": 0.85
    },
    "suggestions": [
      "简历项目描述较为详细，评分依据充分"
    ]
  }
}
```

### 9. Output Format Requirements

#### 9.1 Markdown Report Structure

```
---

# 批量简历初筛结果汇总报告

## 统计概览

- 总简历数：XX份
- 总岗位数：XX个
- 筛选完成时间：YYYY-MM-DD HH:MM:SS，耗时：xxx
- 岗位级别分布：初级X个，中级X个，高级X个

---

## 候选人排名（按加权总分降序排列）

| 排名 | 候选人姓名 | 推荐岗位 | 岗位级别 | 加权总分 | 综合评级 | 置信度 | 学术背景 | 职业稳定性 | 技术栈能力 | 项目经验匹配 | 问题解决能力 | 学习能力 | 加分项 |
|------|------------|----------|----------|----------|----------|--------|----------|------------|------------|--------------|--------------|----------|--------|
| 1 | 张三 | Java高级工程师 | 高级 | 85 | 推荐面试 | 高 | 75 | 80 | 85 | 90 | 80 | 75 | 70 |
| 2 | 李四 | 后端开发工程师 | 中级 | 78 | 推荐面试 | 高 | 70 | 75 | 80 | 85 | 70 | 80 | 65 |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

---

## 通过候选人综合评价

| 候选人姓名 | 推荐岗位 | 综合评价 | 关键亮点 |
|------------|----------|----------|----------|
| 张三 | Java高级工程师 | 技术栈全面，有源码阅读经验，有大型项目经验，问题解决能力强 | 熟悉JVM调优，有分布式架构经验 |
| ... | ... | ... | ... |

---

## 未通过候选人汇总

| 候选人姓名 | 未通过原因 | 涉及岗位 | 置信度 |
|------------|------------|----------|--------|
| 王五 | 学历不满足（岗位要求本科及以上，简历显示专科） | Java高级工程师, 后端开发工程师 | 高 |
| ... | ... | ... | ... |

---

## 低置信度候选人（建议人工复核）

| 候选人姓名 | 置信度 | 复核建议 |
|------------|--------|----------|
| 赵六 | 低(0.55) | 简历信息不完整，建议核实工作年限和项目经验 |
| ... | ... | ... |

---
```

#### 9.2 Excel-Ready Data Format

Generate tabular data suitable for Excel import:

```
候选人姓名,推荐岗位,岗位级别,加权总分,综合评级,置信度,学术背景,职业稳定性,技术栈能力,项目经验匹配,问题解决能力,学习能力,加分项,关键亮点,评估时间
张三,Java高级工程师,高级,85,推荐面试,高,75,80,85,90,80,75,70,熟悉JVM调优,2024-01-15 10:30:00
李四,后端开发工程师,中级,78,推荐面试,高,70,75,80,85,70,80,65,有微服务经验,2024-01-15 10:35:00
```

#### 9.3 Candidate Comparison Table

```
## 候选人横向对比表

| 对比维度 | 张三 | 李四 | 王五 |
|----------|------|------|------|
| 推荐岗位 | Java高级工程师 | 后端开发工程师 | - |
| 加权总分 | 85 | 78 | 45 |
| 学术背景 | 75 | 70 | 60 |
| 职业稳定性 | 80 | 75 | 50 |
| 技术栈能力 | 85 | 80 | 55 |
| 项目经验匹配 | 90 | 85 | 40 |
| 问题解决能力 | 80 | 70 | 35 |
| 学习能力 | 75 | 80 | 50 |
| 加分项 | 70 | 65 | 30 |
| 核心优势 | JVM调优、分布式架构 | 微服务、高并发 | - |
| 主要不足 | - | - | 学历不满足、经验不足 |
```

#### 9.4 Highlights Summary

```
## 候选人亮点摘要（供面试官参考）

### 张三 - Java高级工程师（加权总分：85）
**核心优势**：
- 熟悉JVM调优，有实际性能优化经验
- 有分布式架构设计和实施经验
- 项目经验丰富，有大型系统开发经验

**面试建议**：
- 深入了解JVM调优的具体案例
- 询问分布式架构中的难点和解决方案

---

### 李四 - 后端开发工程师（加权总分：78）
**核心优势**：
- 有微服务架构实践经验
- 高并发场景有实际处理经验
- 学习能力强，有技术博客

**面试建议**：
- 了解微服务拆分的思路和经验
- 询问高并发场景的具体处理方案
```

### 10. Important Notes

- All evaluations must be based solely on resume text content
- No unfounded assumptions or guessing
- Strictly follow the given weights and scoring rules
- Must correspond to job requirements original text when stating non-compliance
- No vague descriptions allowed
- For each candidate, recommend the position with the highest score
- Sort all candidates by their highest score in descending order
- 不要为了效率试图创建py脚本来进行批量处理
- Always include confidence score for each evaluation
- Flag low-confidence evaluations for manual review
