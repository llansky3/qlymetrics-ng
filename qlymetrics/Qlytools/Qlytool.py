import subprocess
import re
import os

from ..Qlymetrics import Qlymetric, Risk

class Qlytool:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.id = re.sub('[^A-Za-z0-9_]+', '', self.name).lower()
        self.toolpath = '/usr/bin'
        self.available = None
        self.version = None

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

    def check_if_installed(self, get_version_cmd):
        # A command to get version shall be used for testing
        cmd = f'{self.toolpath}/{get_version_cmd} 2>&1'
        try:
            r = subprocess.check_output(cmd, shell=True)
            self.version = r.decode('UTF-8','ignore')
            return True
            # returncode = 0
        except subprocess.CalledProcessError as e:
            return False 
            # returncode = e.returncode

    def get_html_table_row(self):
        return f"""
            <tr>
                <td rowspan="1">{self.name}</td>
                <td rowspan="1">{self.description}</td>
                <td rowspan="1">{self.available}</td>
                <td rowspan="1">{self.version}</td>
                <td rowspan="1">{self.toolpath}</td>
            </tr>
            """    

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



