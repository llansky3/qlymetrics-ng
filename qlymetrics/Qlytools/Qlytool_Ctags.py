import re

from .Qlytool import Qlytool
from .Qlytool_Cppcheck import Qlymetric_OrderOfTen, Qlymetric_Zero

from ..Qlymetrics import Qlymetric, Risk

class Ctags(Qlytool):
    # From: http://ctags.sourceforge.net
    def __init__(self, toolpath=None):
        super().__init__("Ctags", "Static code analysis by Ctags")
        if toolpath is not None:
            self.toolpath = toolpath
        # Check if ctags is available and can be executed correctly
        self.available = self.check_if_installed('ctags --version')

    def get_metrics_dict(self):
        # Dictionary of provided metrics
        metrics = {
            "Ctags - functions"  : "Number of functions",
            "Ctags - files"      : "Number of files"
        }
        
        metrics_dict = {}
        for metric in metrics:
            metrics_dict[metric] = Qlymetric(metric,metrics[metric])
        return metrics_dict   

    def get_metric(self, fpath):
        # Get static code analysis from Ctags
        metrics = self.get_metrics_dict()

        out_ctags = Qlytool.execute_shell_command(f"""
            {self.toolpath}/ctags -x --c-types=f {fpath} 2>&1
            """)
        ptrn = re.compile(r"""		    
            (?P<fcnname>.+)\s+function\s+
            (?P<line>\d+)\s+
            (?P<details>.+)
            """, re.VERBOSE)
        # TODO: Parse the details for number of arguments

        for metric in metrics:
            metrics[metric].value = 0

        for i,out in enumerate(out_ctags):
            match = ptrn.match(out)
            if i == 0:
                metrics["Ctags - files"].value = 1
                metrics["Ctags - files"].msgs.append(fpath)
            if match is not None:
                metrics["Ctags - functions"].value += 1
                metrics["Ctags - functions"].msgs.append(out)

        return metrics
