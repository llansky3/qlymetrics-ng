import subprocess
import re
import os

from ..Qlymetrics import Qlymetric, Risk

class Qlytool:

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.id = re.sub('[^A-Za-z0-9_]+', '', self.name).lower()

    def get_metrics_dict(self):
        # This needs to be implemented in derived classes
        # If not - assume just one default metric
        return {
            self.name: Qlymetric(self.name, self.description)
        }      
    
    def get_metric(self, fpath):
        # This needs to be implemented i derived classes
        # If not - throw error
        raise NotImplementedError()       

    @staticmethod
    def execute_shell_command(cmd):
        # Shell executes given command
        try:
            r = subprocess.check_output(cmd, shell=True)
            # returncode = 0
        except subprocess.CalledProcessError as e:
            r = e.output 
            # returncode = e.returncode    
        r = r.decode('UTF-8','ignore').split("\n")
        # r = r.decode().split("\n")
        # r = r.splitlines()
        return r

