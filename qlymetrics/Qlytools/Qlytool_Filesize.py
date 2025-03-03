import os

from .Qlytool import Qlytool

class Filesize(Qlytool):
    def __init__(self):
        super().__init__("File size", "Calculates size of the file in bytes")
        
    def get_metric(self, fpath):
        # Get size of a given file
        metric = self.get_metrics_dict()
        metric[self.name].value = os.path.getsize(fpath)
        metric[self.name].msgs.append(f"{metric[self.name].value} bytes")
        return metric

