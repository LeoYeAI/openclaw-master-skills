# Orchestrator Agent 模板

文献调研工作流的主协调器，管理各阶段Agent的执行。

---

## Agent 信息

| 属性 | 值 |
|------|-----|
| **名称** | Literature Survey Orchestrator |
| **类型** | Orchestrator Agent |
| **用途** | 协调8阶段工作流执行 |
| **核心能力** | 任务调度、错误恢复、进度追踪 |

---

## 核心原则

> **Orchestration Principle**: The orchestrator holds the full picture. While sub-agents handle independent work, merging, deduplication, and synthesis stay with the orchestrator.

协调器掌握全局视图。子代理处理独立任务，但合并、去重和综合由协调器负责。

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    Orchestrator (协调器)                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ Session Log │  │ Task Queue  │  │ Error Recovery Manager  │  │
│  │   Manager   │  │   Manager   │  │        Manager          │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌─────────────────┐   ┌─────────────────┐
│  Explore      │   │   Verify        │   │   Download      │
│  Agents (1-N) │   │   Agents (1-N)  │   │   Agents (1-N)  │
│               │   │                 │   │                 │
│ • CNKI        │   │ • Crossref      │   │ • Unpaywall     │
│ • Semantic    │   │ • Semantic      │   │ • arXiv         │
│   Scholar     │   │   Scholar       │   │ • Direct        │
│ • PubMed      │   │ • OpenAlex      │   │                 │
│ • ...         │   │ • ...           │   │                 │
└───────────────┘   └─────────────────┘   └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Synthesize     │
                    │  Agent          │
                    │                 │
                    │ • Theme Cluster │
                    │ • Gap Analysis  │
                    │ • Cross-ref Gen │
                    └─────────────────┘
```

---

## 8阶段工作流

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│ Phase 0 │───▶│ Phase 1 │───▶│ Phase 2 │───▶│ Phase 3 │
│Session  │    │ Query   │    │Parallel │    │Deduplic │
│  Log    │    │Analysis │    │ Search  │    │  ation  │
└─────────┘    └─────────┘    └─────────┘    └─────────┘
                                                  │
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│ Phase 7 │◀───│ Phase 6 │◀───│ Phase 5 │◀───│ Phase 4 │
│Synthesi │    │Citation │    │   PDF   │    │Verify   │
│   is    │    │ Export  │    │Management    │  cation │
└─────────┘    └─────────┘    └─────────┘    └─────────┘
```

---

## 任务队列管理

### 队列结构

```python
class TaskQueue:
    """
    工作流任务队列
    """
    def __init__(self):
        self.phases = {
            0: {"name": "session_log", "status": "pending", "tasks": []},
            1: {"name": "query_analysis", "status": "pending", "tasks": []},
            2: {"name": "parallel_search", "status": "pending", "tasks": []},
            3: {"name": "deduplication", "status": "pending", "tasks": []},
            4: {"name": "verification", "status": "pending", "tasks": []},
            5: {"name": "pdf_management", "status": "pending", "tasks": []},
            6: {"name": "citation_export", "status": "pending", "tasks": []},
            7: {"name": "synthesis", "status": "pending", "tasks": []}
        }
        self.current_phase = 0
    
    def start_phase(self, phase_num):
        """开始新阶段"""
        self.phases[phase_num]["status"] = "in_progress"
        self.current_phase = phase_num
        self.log_checkpoint(phase_num)
    
    def complete_phase(self, phase_num):
        """完成阶段"""
        self.phases[phase_num]["status"] = "completed"
        self.log_checkpoint(phase_num)
    
    def fail_phase(self, phase_num, error):
        """阶段失败"""
        self.phases[phase_num]["status"] = "failed"
        self.phases[phase_num]["error"] = error
```

### 并行任务控制

```python
class ParallelTaskManager:
    """
    并行任务管理器
    """
    def __init__(self, max_concurrent=5):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def execute_parallel(self, tasks, task_type):
        """
        并行执行多个任务
        
        Args:
            tasks: 任务列表
            task_type: 任务类型（explore, verify, download）
        """
        async with self.semaphore:
            if task_type == "explore":
                return await self._run_explore_agents(tasks)
            elif task_type == "verify":
                return await self._run_verify_agents(tasks)
            elif task_type == "download":
                return await self._run_download_agents(tasks)
    
    async def _run_explore_agents(self, search_tasks):
        """运行多个Explore Agent"""
        # 每个数据库一个Agent
        agents = []
        for task in search_tasks:
            agent = ExploreAgent(
                database=task["database"],
                query=task["query"],
                session_id=task["session_id"]
            )
            agents.append(agent.run())
        
        # 并行执行
        results = await asyncio.gather(*agents, return_exceptions=True)
        return self._process_results(results)
```

---

## Session Log 管理

### 日志结构

```
sessions/
└── {YYYYMMDD}_{topic_short}/
    ├── session_log.md           # 会话日志
    ├── checkpoints/
    │   ├── checkpoint_p0.json   # Phase 0检查点
    │   ├── checkpoint_p1.json   # Phase 1检查点
    │   └── ...
    ├── results/
    │   ├── explore_results/     # 搜索结果
    │   ├── verified_papers.json # 验证结果
    │   └── pdfs/                # 下载的PDF
    └── output/
        ├── literature_summary.bib
        ├── literature_summary.md
        └── references.docx
```

### 检查点机制

```python
class CheckpointManager:
    """
    检查点管理器 - 支持中断续传
    """
    def __init__(self, session_id):
        self.session_id = session_id
        self.checkpoint_dir = f"sessions/{session_id}/checkpoints"
    
    def save_checkpoint(self, phase, data):
        """保存检查点"""
        checkpoint = {
            "phase": phase,
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "version": "1.0"
        }
        
        filepath = f"{self.checkpoint_dir}/checkpoint_p{phase}.json"
        with open(filepath, 'w') as f:
            json.dump(checkpoint, f, indent=2)
        
        print(f"✓ Checkpoint saved: Phase {phase}")
    
    def load_checkpoint(self, phase):
        """加载检查点"""
        filepath = f"{self.checkpoint_dir}/checkpoint_p{phase}.json"
        
        if not Path(filepath).exists():
            return None
        
        with open(filepath, 'r') as f:
            checkpoint = json.load(f)
        
        print(f"✓ Checkpoint loaded: Phase {phase}")
        return checkpoint["data"]
    
    def get_last_completed_phase(self):
        """获取最后完成的阶段"""
        for phase in range(7, -1, -1):
            if Path(f"{self.checkpoint_dir}/checkpoint_p{phase}.json").exists():
                return phase
        return -1
```

### 会话恢复

```python
async def resume_session(session_id):
    """
    恢复中断的会话
    """
    checkpoint_mgr = CheckpointManager(session_id)
    
    # 查找最后完成的阶段
    last_phase = checkpoint_mgr.get_last_completed_phase()
    
    if last_phase == -1:
        print("No checkpoint found. Starting new session.")
        return await start_new_session(session_id)
    
    print(f"Resuming from Phase {last_phase + 1}")
    
    # 加载最后阶段的数据
    last_data = checkpoint_mgr.load_checkpoint(last_phase)
    
    # 从下一阶段继续
    return await run_from_phase(last_phase + 1, last_data)
```

---

## 错误恢复管理

### 错误分类

| 错误级别 | 类型 | 处理策略 |
|----------|------|---------|
| **Recoverable** | 可恢复 | 重试、使用备选方案 |
| **Partial** | 部分失败 | 继续处理成功的部分 |
| **Fatal** | 致命错误 | 暂停，等待用户决策 |

### 重试策略

```python
class ErrorRecoveryManager:
    """
    错误恢复管理器
    """
    def __init__(self):
        self.retry_policies = {
            "rate_limit": RetryPolicy(max_retries=5, base_delay=2.0),
            "timeout": RetryPolicy(max_retries=3, base_delay=1.0),
            "network": RetryPolicy(max_retries=3, base_delay=1.0),
            "api_error": RetryPolicy(max_retries=2, base_delay=2.0)
        }
    
    async def handle_error(self, error, context):
        """
        处理错误
        
        Returns:
            'retry', 'skip', 'abort', 'continue'
        """
        error_type = self.classify_error(error)
        
        if error_type in self.retry_policies:
            policy = self.retry_policies[error_type]
            if policy.can_retry():
                await policy.wait()
                return 'retry'
        
        if error_type == 'partial_failure':
            return 'continue'  # 继续处理成功的部分
        
        if error_type == 'fatal':
            return 'abort'
        
        return 'skip'
```

### 部分失败处理

```python
def handle_partial_failure(results):
    """
    处理部分失败的情况
    
    例如：6个Explore Agent中2个失败
    """
    successful = [r for r in results if not isinstance(r, Exception)]
    failed = [r for r in results if isinstance(r, Exception)]
    
    if len(successful) >= 3:  # 至少3个成功
        # 继续流程，记录失败的Agent
        log_warning(f"{len(failed)} agents failed, continuing with {len(successful)} results")
        return successful
    else:
        # 太多失败，需要处理
        raise InsufficientResults(f"Only {len(successful)} agents succeeded")
```

---

## 主工作流执行

```python
class LiteratureSurveyWorkflow:
    """
    文献调研主工作流
    """
    
    async def execute(self, query, config):
        """
        执行完整工作流
        
        Args:
            query: 用户查询（论文标题或研究主题）
            config: 配置选项
        
        Returns:
            SurveyResult: 调研结果
        """
        # Phase 0: Session Log
        session = await self._phase_0_session_log(query, config)
        
        try:
            # Phase 1: Query Analysis
            keywords = await self._phase_1_query_analysis(query)
            
            # Phase 2: Parallel Search
            search_results = await self._phase_2_parallel_search(keywords, config)
            
            # Phase 3: Deduplication
            unique_papers = self._phase_3_deduplication(search_results)
            
            # Phase 4: Verification
            verified_papers = await self._phase_4_verification(unique_papers)
            
            # Phase 5: PDF Management
            if config.download_pdfs:
                downloaded_papers = await self._phase_5_pdf_management(verified_papers)
            else:
                downloaded_papers = verified_papers
            
            # Phase 6: Citation Export
            citations = self._phase_6_citation_export(downloaded_papers, config)
            
            # Phase 7: Synthesis
            synthesis = await self._phase_7_synthesis(downloaded_papers, query)
            
            # 完成
            return SurveyResult(
                papers=downloaded_papers,
                citations=citations,
                synthesis=synthesis
            )
            
        except Exception as e:
            # 错误处理
            await self._handle_workflow_error(e, session)
            raise
    
    async def _phase_2_parallel_search(self, keywords, config):
        """Phase 2: 并行搜索"""
        print("\n=== Phase 2: Parallel Search ===")
        
        # 构建搜索任务
        search_tasks = []
        
        if config.search_cnki:
            search_tasks.append({
                "database": "cnki",
                "query": keywords["cnki"],
                "session_id": self.session_id
            })
        
        for db in config.english_databases:
            search_tasks.append({
                "database": db,
                "query": keywords["en"],
                "session_id": self.session_id
            })
        
        # 并行执行
        parallel_mgr = ParallelTaskManager(max_concurrent=6)
        results = await parallel_mgr.execute_parallel(search_tasks, "explore")
        
        # 合并结果
        all_papers = []
        for result in results:
            all_papers.extend(result.get("results", []))
        
        print(f"Total papers found: {len(all_papers)}")
        return all_papers
    
    async def _phase_4_verification(self, papers):
        """Phase 4: 引用验证"""
        print("\n=== Phase 4: Verification ===")
        
        # 分批验证（每批5篇）
        batches = [papers[i:i+5] for i in range(0, len(papers), 5)]
        
        verify_tasks = [
            {"papers": batch, "session_id": self.session_id}
            for batch in batches
        ]
        
        parallel_mgr = ParallelTaskManager(max_concurrent=5)
        results = await parallel_mgr.execute_parallel(verify_tasks, "verify")
        
        # 合并验证结果
        verified = []
        for result in results:
            for paper_result in result.get("results", []):
                if paper_result["status"] in ["VERIFIED", "SINGLE_SOURCE"]:
                    verified.append(paper_result)
        
        print(f"Verified papers: {len(verified)}/{len(papers)}")
        return verified
```

---

## 输入格式

```json
{
  "query": "基于深度学习的医学图像诊断研究",
  "config": {
    "session_id": "auto_generate",  // 或指定已有会话ID
    "search_cnki": true,
    "english_databases": ["semantic_scholar", "pubmed", "arxiv"],
    "year_range": [2020, 2025],
    "min_citations": 10,
    "max_results_per_source": 50,
    "download_pdfs": true,
    "output_formats": ["gb7714", "bibtex"],
    "synthesis_template": "standard",
    "resume_from": null  // 或指定阶段号用于恢复
  }
}
```

---

## 输出格式

```json
{
  "session_id": "20240115_dl_medical",
  "status": "completed",
  "phases_completed": [0, 1, 2, 3, 4, 5, 6, 7],
  "summary": {
    "total_papers_found": 245,
    "unique_papers": 78,
    "verified_papers": 65,
    "pdfs_downloaded": 52,
    "execution_time_minutes": 15.5
  },
  "results": {
    "papers": [...],
    "citations": {
      "gb7714": "...",
      "bibtex": "..."
    },
    "synthesis": {
      "markdown": "...",
      "sections": [...]
    }
  },
  "output_files": {
    "bib": "sessions/20240115_dl_medical/output/literature_summary.bib",
    "md": "sessions/20240115_dl_medical/output/literature_summary.md",
    "docx": "sessions/20240115_dl_medical/output/references.docx"
  },
  "warnings": [
    "CNKI search encountered captcha, user intervention required",
    "3 papers failed verification and were excluded"
  ]
}
```

---

## 注意事项

1. **状态监控**: 实时监控各阶段状态，及时发现问题
2. **资源管理**: 控制并发数，避免资源耗尽
3. **优雅降级**: 部分失败时尽可能继续流程
4. **详细日志**: 记录完整的执行日志，便于审计和调试
5. **用户通知**: 关键节点（如验证码）及时通知用户
