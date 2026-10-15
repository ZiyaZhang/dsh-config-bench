"""隐藏测试判分：把一套不在工作区里的测试拷进交付的代码旁边跑。

测试目录由 task.yaml 的 scorers[].suite 指定。跑测试要隔离环境，
所以这个 scorer 需要 runner 提供一个一次性容器（trial.run_in_sandbox）。
测试超时用 task.yaml 的 max_test_timeout_sec，超时算这一项判不了，不算 0 分。
"""
from __future__ import annotations

from . import Score, scorer


@scorer("hidden_tests")
def score_hidden_tests(trial, task, spec) -> Score:
    suite = task.dir / spec["suite"]
    if spec.get("assets") == "pending" or not suite.exists():
        return Score(value=None, passed=None, reason=f"测试还没放进来（{spec[suite]}）")
    res = trial.run_in_sandbox(
        command=["python", "-m", "pytest", "-q", str(suite)],
        timeout_sec=task.max_test_timeout_sec,
        copy_in=[(suite, "tests")],
    )
    if res.timed_out:
        return Score(value=None, passed=None, reason="测试超时，这一项判不了",
                     detail={"timeout_sec": task.max_test_timeout_sec})
    passed, failed = res.pytest_counts()
    if passed + failed == 0:
        return Score(value=None, passed=None, reason="测试没跑起来",
                     detail={"exit_code": res.exit_code, "stdout_tail": res.stdout[-2000:]})
    return Score(
        value=passed / (passed + failed),
        passed=(failed == 0),
        reason=f"{passed} 过 / {failed} 不过",
        detail={"passed": passed, "failed": failed, "exit_code": res.exit_code},
    )
