import heapq
from datetime import datetime, timedelta, timezone
from typing import Callable, Literal, Optional

from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

from pythongo.infini import write_log

try:
    from zoneinfo import ZoneInfo
    SHANGHAI_TZ = ZoneInfo("Asia/Shanghai")
except ImportError:
    SHANGHAI_TZ = timezone(timedelta(hours=8), name="Asia/Shanghai")


class BacktestJob(object):
    """
    回测专用的 `Job` 对象
    模拟 `apscheduler.job.Job` 的行为，但更加轻量
    """
    def __init__(
        self,
        scheduler: "BacktestScheduler",
        id: str,
        func: Callable,
        trigger: CronTrigger | IntervalTrigger | DateTrigger,
        args: list,
        kwargs: dict
    ):
        self._scheduler = scheduler
        self.id = id
        self.func = func
        self.trigger = trigger
        self.args = args
        self.kwargs = kwargs
        self.next_run_time: Optional[datetime] = None

    def remove(self):
        """支持 job.remove() 操作"""
        self._scheduler.remove_job(self.id)

    def modify(self, **changes):
        """简单的修改支持"""
        for key, value in changes.items():
            setattr(self, key, value)

    def __lt__(self, other: "BacktestJob"):
        """
        用于 heapq 的比较逻辑：
        按 next_run_time 从小到大排序 (Min-Heap)
        """

        if self.next_run_time is None:
            """None 视为无穷大，排在后面（或者不应该出现在堆里）"""
            return False

        if other.next_run_time is None:
            return True

        return self.next_run_time < other.next_run_time

    def __repr__(self):
        return f"<BacktestJob (id={self.id}, next_run_time={self.next_run_time})>"


class BacktestScheduler(object):
    """回测专用虚拟调度器，实现 `BackgroundScheduler` 的功能"""
    _instances: list["BacktestScheduler"] = []

    def __init__(self, scheduler_name: str = None) -> None:
        self.scheduler_name: str = scheduler_name

        self.pending_jobs: list[BacktestJob] = []
        """刚添加、未初始化的任务"""

        self.scheduled_jobs: list[BacktestJob] = []
        """已排程的任务 (最小堆)"""

        self._job_map: dict[str, BacktestJob] = {}
        """ID 索引，用于 `O(1)` 查找和有效性验证"""

        self.running: bool = False
        """是否正在运行"""

        BacktestScheduler._instances.append(self)

    def add_job(
        self,
        func: Callable,
        trigger: Literal["date", "interval", "cron"],
        id: str = None,
        **kwargs
    )-> BacktestJob:
        """
        添加任务
        """

        trigger_obj = None

        job_args = kwargs.pop("args", [])
        job_kwargs = kwargs.pop("kwargs", {})

        # 移除系统自动传入但不需要的参数
        kwargs.pop("next_run_time", None) 
        timezone = kwargs.pop("timezone", None)

        if trigger == "date":
            run_date = kwargs.get("run_date")
            trigger_obj = DateTrigger(run_date=run_date, timezone=timezone)
        elif trigger == "interval":
            trigger_obj = IntervalTrigger(timezone=timezone, **kwargs)
        elif trigger == "cron":
            trigger_obj = CronTrigger(timezone=timezone, **kwargs)

        job_id = id or func.__name__

        if job_id in self._job_map:
            # 防止 ID 重复覆盖，如果ID重复，移除旧的，添加新的
            self.remove_job(job_id)

        job = BacktestJob(
            scheduler=self,
            id=job_id,
            func=func,
            trigger=trigger_obj,
            args=job_args,
            kwargs=job_kwargs
        )

        job.next_run_time = None

        self.pending_jobs.append(job)

        self._job_map[job_id] = job

        return job

    def get_job(self, job_id: str, jobstore=None) -> Optional[BacktestJob]:
        """获取单个 `Job`"""
        return self._job_map.get(job_id)

    def get_jobs(self) -> list[BacktestJob]:
        """
        获取 `pending_jobs` 和 `scheduled_jobs` 中所有 Job 的总和，过滤掉已失效的
        
        Note:
            因为 `scheduled_jobs` 里可能包含已删除但未 pop 的脏数据，所以以 `_job_map` 为准
        """

        return list(self._job_map.values())

    def remove_job(self, job_id: str, jobstore=None) -> None:
        """
        删除 `Job`（惰性）

        Note:
            只从 _job_map 中移除
            堆中对应的 `Job` 依然存在，但下次 pop 出来的时候，
            因为不在 _job_map 中，会被直接丢弃
        """

        if job_id in self._job_map:
            del self._job_map[job_id]

    def start(self) -> None:
        """启动调度器"""
        self.running = True

    def stop(self) -> None:
        """停止调度器"""
        self.running = False

    @classmethod
    def run_pending_jobs(cls, current_dt: datetime) -> None:
        """
        全局驱动函数

        Args:
            current_dt: 回测时间
        """

        for scheduler in cls._instances:
            if scheduler.running:
                scheduler._check_and_run(current_dt.replace(tzinfo=SHANGHAI_TZ))

    def _check_and_run(self, current_dt: datetime) -> None:
        """
        检查并运行到期任务

        Args:
            current_dt: 回测时间
        """

        if self.pending_jobs:
            # 处理待初始化的任务，计算 `next_run_time`
            for job in self.pending_jobs:
                if job.id not in self._job_map:
                    # 检查任务是否已被删除
                    continue

                trigger = job.trigger

                if hasattr(trigger, "start_date") and trigger.start_date:
                    # 设置首次运行时间
                    try:
                        if trigger.start_date > current_dt:
                            # trigger 的开始时间大于当前回测流时间
                            trigger.start_date = current_dt
                    except TypeError:
                         trigger.start_date = current_dt

                # 计算首次运行时间
                job.next_run_time = trigger.get_next_fire_time(None, current_dt)

                if job.next_run_time:
                    # 有效任务，推入堆中
                    heapq.heappush(self.scheduled_jobs, job)
                else:
                    # 任务已过期或无效，从 map 中移除
                    self.remove_job(job.id)

            # 清空待处理列表
            self.pending_jobs.clear()

        # 处理堆中的任务
        # 只需要查看堆顶元素 (最小的 next_run_time)
        while self.scheduled_jobs:
            # 获取堆顶任务
            job = self.scheduled_jobs[0]

            # 如果堆顶的任务 ID 不在 map 里，说明它已经被删除了
            # 直接将其弹出并丢弃，查看下一个
            if job.id not in self._job_map or self._job_map[job.id] is not job:
                heapq.heappop(self.scheduled_jobs)
                continue

            # 如果堆顶任务的时间还没到，说明后面所有的任务都没到
            # 直接退出循环，O(1) 退出
            if job.next_run_time > current_dt:
                break

            # 此时任务时间已到，弹出任务
            heapq.heappop(self.scheduled_jobs)

            # 追赶机制
            while job.next_run_time and current_dt >= job.next_run_time:
                try:
                    job.func(*job.args, **job.kwargs)
                except Exception as e:
                    name_tag = f"[{self.scheduler_name}] " if self.scheduler_name else ""
                    write_log(f"{name_tag}定时任务 <{job.id}> 执行出错: {e}")

                previous_run_time = job.next_run_time
                next_time = job.trigger.get_next_fire_time(previous_run_time, previous_run_time)

                if next_time:
                    job.next_run_time = next_time
                else:
                    # 任务结束（如下一次时间为 None），从 map 中彻底移除
                    self.remove_job(job.id)
                    job.next_run_time = None
                    break

            # 如果任务还有下一次运行时间，且任务仍然有效，重新放回堆中
            if job.next_run_time and job.id in self._job_map:
                heapq.heappush(self.scheduled_jobs, job)
