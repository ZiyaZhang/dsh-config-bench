"""隐藏测试判分：把一套不在工作区里的测试拷进交付的代码旁边跑。

测试目录由 task.yaml 的 scorers[].suite 指定。跑测试要隔离环境，
所以这个 scorer 需要 runner 提供一个一次性容器（trial.run_in_sandbox）。
测试超时用 task.yaml 的 max_test_timeout_sec，超时算这一项判不了，不算 0 分。
"""
from __future__ import annotations


from harness.pyenv import python as test_python

from . import Score, scorer


@scorer("hidden_tests")
def score_hidden_tests(trial, task, spec) -> Score:
    suite = task.dir / spec["suite"]
    if spec.get("assets") == "pending" or not suite.exists():
        return Score(value=None, passed=None, reason=f"测试还没放进来（{spec[suite]}）")
    layout = spec.get("layout", "flat")
    if layout == "per_exercise":
        exercises = [d.name for d in sorted(suite.iterdir()) if d.is_dir()]
        copy_in = [(suite / name, f"exercises/{name}") for name in exercises]
        per = max(60, task.max_test_timeout_sec // max(1, len(exercises)))
        results = trial.run_each([f"exercises/{n}" for n in exercises],
                                 [test_python(), "-m", "pytest", "-q"], per, copy_in)
        detail, ok = {}, 0
        for name in exercises:
            r = results[f"exercises/{name}"]
            p_, f_ = r.pytest_counts()
            full = (not r.timed_out) and f_ == 0 and p_ > 0
            ok += 1 if full else 0
            detail[name] = {"passed": p_, "failed": f_, "timed_out": r.timed_out, "all_passed": full}
        return Score(value=ok / len(exercises), passed=(ok == len(exercises)),
                     reason=f"{ok}/{len(exercises)} 道全过", detail=detail)

    res = trial.run_in_sandbox(
        command=[test_python(), "-m", "pytest", "-q", "tests"],
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
