import re

from .Qlytool import Qlytool

from ..Qlymetrics import Qlymetric, Risk

class Qlymetric_Zero(Qlymetric):
    def get_risk(self):     
        if self.get_value() > 0:
            return Risk.RED
        else:
            return Risk.GREEN
class Qlymetric_OrderOfTen(Qlymetric):
    def get_risk(self):     
        if self.get_value() >= 100:
            return Risk.RED
        elif self.get_value() >= 10:
            return Risk.YELLOW
        else:
            return Risk.GREEN


class Cppcheck(Qlytool):
    def __init__(self, toolpath):
        super().__init__("Cppcheck", "Static code analysis by Cppcheck")
        self.toolpath = toolpath
        # TODO: Check if Cppcheck is available there and can be executed correctly

    def get_metrics_dict(self):
        # Dictionary of provided metrics
        metrics = {
            "Cppcheck - errors"     : "Number of error messages",
            "Cppcheck - warnings"   : "Number of warning messages",
            "Cppcheck - other"      : "Number of other messages",
            "Cppcheck - score"      : "Combined score"
        }
        metrics_dict = {}
        for metric in metrics:
            if "score" in metric:
                metrics_dict[metric] = Qlymetric_OrderOfTen(metric,metrics[metric])
            elif "errors" in metric:
                metrics_dict[metric] = Qlymetric_Zero(metric,metrics[metric])    
            else:
                metrics_dict[metric] = Qlymetric(metric,metrics[metric])
        return metrics_dict         

    def get_metric(self, fpath):
        # Get static code analysis from Cppcheck
        # http://cppcheck.sourceforge.net/manual.pdf
        metrics = self.get_metrics_dict()

        out_cppcheck = Qlytool.execute_shell_command(f"""
            {self.toolpath}/cppcheck --enable=all --inconclusive --std=posix {fpath} 2>&1
            """)
        ptrn = re.compile(r"""		    
            (?P<file>.+):
            (?P<line>\d+):
            (?P<column>\d+):\s+
            (?P<category>\w+):\s+
            (?P<details>.+)
            """, re.VERBOSE)

        for metric in metrics:
            metrics[metric].value = 0

        # TODO: Stop adding message if no text!
        p_lastmsg = None
        for out in out_cppcheck:
            match = ptrn.match(out)
            if match is not None:
                catgr = match.group("category")
                if catgr == "error":
                    metrics["Cppcheck - errors"].value += 1
                    p_lastmsg = metrics["Cppcheck - errors"].msgs
                elif catgr == "warning":
                    metrics["Cppcheck - warnings"].value += 1
                    p_lastmsg = metrics["Cppcheck - warnings"].msgs
                else:
                    metrics["Cppcheck - other"].value += 1
                    p_lastmsg = metrics["Cppcheck - other"].msgs
            if p_lastmsg is not None:
                p_lastmsg.append(out) 
        metrics["Cppcheck - score"].value  = metrics["Cppcheck - errors"].value   * 100
        metrics["Cppcheck - score"].value += metrics["Cppcheck - warnings"].value * 10
        metrics["Cppcheck - score"].value += metrics["Cppcheck - other"].value
  
        return metrics
