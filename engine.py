import time
import yaml

from vision import Vision
from action import click


class Step:
    def __init__(self, name, timeout=10, retry=1):
        self.name = name
        self.timeout = timeout
        self.retry = retry

        self.start_time = time.time()
        self.retry_count = 0
        self.confirm = 0


class WorkflowEngine:

    def __init__(self, config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)

        self.steps = [
            Step(
                s["name"],
                s.get("timeout", 10),
                s.get("retry", 1)
            )
            for s in cfg["steps"]
        ]

        self.vision = Vision("images")
        self.current = 0

    def run(self):
        print("启动流程引擎")

        while True:
            step = self.steps[self.current]

            pos = self.vision.find(step.name)

            if pos:
                step.confirm += 1
            else:
                step.confirm = 0

            # ✅ 防误识别
            if step.confirm >= 2:
                print(f"执行步骤: {step.name}")
                click(pos)

                self._next_step()
                continue

            # ✅ 超时处理
            if time.time() - step.start_time > step.timeout:
                step.retry_count += 1
                print(f"步骤 {step.name} 超时，重试 {step.retry_count}")

                if step.retry_count > step.retry:
                    print(f"跳过步骤 {step.name}")
                    self._next_step()
                else:
                    step.start_time = time.time()

            time.sleep(0.5)

    def _next_step(self):
        step = self.steps[self.current]

        # 重置状态
        step.start_time = time.time()
        step.retry_count = 0
        step.confirm = 0

        self.current += 1

        if self.current >= len(self.steps):
            print("一轮完成\n")
            self.current = 0