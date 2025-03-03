import re

from .Qlytool import Qlytool

from ..Qlymetrics import Qlymetric, Risk

class Splint(Qlytool):
    def __init__(self, toolpath):
        super().__init__("Splint", "Static code analysis by Splint")
        self.toolpath = toolpath
        # TODO: Check if Splint is available there and can be executed correctly

    def get_metrics_dict(self):
        # Dictionary of provided metrics
        metrics = {
            "Splint - all": "Number of findings",
        }
        metrics_dict = {}
        for metric in metrics:
            metrics_dict[metric] = Qlymetric(metric,metrics[metric])
        return metrics_dict        

    def get_metric(self, fpath):
        # Get static code analysis from Cppcheck
        # http://cppcheck.sourceforge.net/manual.pdf\
        metrics = self.get_metrics_dict()

        out_splint = Qlytool.execute_shell_command(f"""
            {self.toolpath}/splint {fpath} 2>&1
            """)
        ptrn = re.compile(r"""		    
            (?P<file>.+):
            (?P<line>\d+):
            (?P<column>\d+):
            """, re.VERBOSE)

        metrics["Splint - all"].value = 0
        p_lastmsg = None
        for out in out_splint:
            match = ptrn.match(out)
            if match is not None:
                metrics["Splint - all"].value += 1
                p_lastmsg = metrics["Splint - all"].msgs
            if p_lastmsg is not None:
                p_lastmsg.append(out)

        # TODO: Different findings could have different severity
        # TODO: The details of findings are spread accross multiple lines
        return metrics
