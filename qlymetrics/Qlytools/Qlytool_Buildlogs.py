import os
import requests
import re

from .Qlytool import Qlytool
from .Qlytool_Cppcheck import Qlymetric_OrderOfTen, Qlymetric_Zero

from ..Qlymetrics import Qlymetric, Risk

class Qlymetric_NonZero(Qlymetric):
    def get_risk(self):     
        if self.get_value() > 0:
            return Risk.GREEN
        else:
            return Risk.RED

class Buildlogs(Qlytool):
    def __init__(self, apiurl, project):
        super().__init__("Build log", "Compiler and linker warnings from IBS")
        self.apiurl = apiurl
        self.project = project
        # To not to repeat requests unnecessarily
        self.requested_data = {}

    def get_metrics_dict(self):
        # Dictionary of provided metrics
        metrics = {
            "Build log - flags" : "Not allowed compiler or linker flags",
            "Build log - warnings" : "Number of warning messages",
            "Build log - notes" : "Number of note messages",
        }
        metrics_dict = {}
        for metric in metrics:
            if "warnings" in metric:
                metrics_dict[metric] = Qlymetric_OrderOfTen(metric,metrics[metric])
            elif "flags" in metric:
                metrics_dict[metric] = Qlymetric_NonZero(metric,metrics[metric])        
            else:
                metrics_dict[metric] = Qlymetric(metric,metrics[metric])
        return metrics_dict

    def get_metric(self, fpath, package):
        # Get build log from IBS and look for compiler and linker warnings and flags
        metrics = self.get_metrics_dict()
        filepath, filename = os.path.split(fpath)

        if package in self.requested_data.keys():
            resp_ibs = self.requested_data[package]
        else:
            resp_ibs = requests.get(
                f"{self.apiurl}/public/build/{self.project}/standard/x86_64/{package}/_log")
            resp_ibs = resp_ibs.text
            resp_ibs = resp_ibs.splitlines()
            self.requested_data[package] = resp_ibs

        ptrn_warning = re.compile(r"""
            (?P<timestamp>\[\s*\d+s\])\s+		    
            (?P<file>.+):
            (?P<line>\d+):
            (?P<column>\d+):\s+
            (?P<category>.+):\s+
            (?P<details>.+)    
            """, re.VERBOSE)

        ptrn_stoplog = re.compile(r".*\^~?.*")

        ptrn_flag = re.compile(r"""
            (?P<timestamp>\[\s*\d+s\]).*\s+(g?cc|g\+\+|G?CC|G\+\+)\s+		    
            (?P<details>.+)    
            """, re.VERBOSE)

        for metric in metrics:
            metrics[metric].value = 0

        p_lastmsg = None
        for out in resp_ibs:
            match_warning = ptrn_warning.match(out)
            if match_warning is not None:
                p_lastmsg = None
                if filename in match_warning.group("file") or ".h" in match_warning.group("file"):
                    catgr = match_warning.group("category")
                    if catgr == "warning":
                        metrics["Build log - warnings"].value += 1
                        p_lastmsg = metrics["Build log - warnings"].msgs
                    elif catgr == "note":
                        metrics["Build log - notes"].value += 1
                        p_lastmsg = metrics["Build log - notes"].msgs    

            match_stoplog = ptrn_stoplog.match(out)
            if match_stoplog is not None:
                p_lastmsg = None  

            match_flag = ptrn_flag.match(out)
            if match_flag is not None:
                p_lastmsg = None
                if filename in match_flag.group("details"):
                    # TODO: if the there is a list of not allowed or obligatory flags then this metrics will be available
                    metrics["Build log - flags"].value += 1
                    metrics["Build log - flags"].msgs.append(out)          

            if p_lastmsg is not None:
                p_lastmsg.append(out) 

        return metrics
