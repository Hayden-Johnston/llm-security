import json
import threading
from pathlib import Path

from llm_security.worker import Worker


class Pipeline:

    def __init__(self, config, ds):
        self.config = config
        self.datasets = ds
        self.path = Path("data/results") / str(config["run_count"])
        self.workers = []
        self.path.mkdir(parents=True, exist_ok=True)

    def run(self):
        threads = []
        self.write_manifest()
        for k, v in self.config["providers"].items():
            self.workers.append(Worker(k+"/systemone", v[0], v[1]))
        for w in self.workers:
            thread = threading.Thread(
                target=w.run_batch, 
                args=(self.datasets, self.path))
            threads.append(thread)
            thread.start()
        for t in threads:
            t.join()

    def write_manifest(self):
        manifest = {
            "code_version": "0.1",
            "run_id": self.config["run_count"],
            "mode": self.datasets.mode,
            "datasets": self.config["datasets"],
            "providers": self.config["providers"],
            "classification": Worker.build_questions()
        }
        path = Path(self.path) / "manifest.json"
        with path.open("w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=4)
        