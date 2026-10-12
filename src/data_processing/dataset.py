from datasets import load_dataset


class DataHandler:

    def __init__(self, config, mode):
        self.config = config["datasets"]
        self.ds = self.load_datasets(config)
        self.mode = mode # "train" or "test"
        
    def load_datasets(self):
        data = {}
        for ds in self.config:
            data[ds.replace("/", "_")] = load_dataset(ds)
        return data
