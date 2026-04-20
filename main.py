from engine import WorkflowEngine

if __name__ == "__main__":
    engine = WorkflowEngine("config.yaml")
    engine.run()