import re

from .Qlytool import Qlytool
from .Qlytool_Cppcheck import Qlymetric_OrderOfTen, Qlymetric_Zero

from ..Qlymetrics import Qlymetric, Risk

class Cpplint(Qlymetric):
    # From: https://github.com/cpplint/cpplint
    #       https://google.github.io/styleguide/cppguide.html
    def __init__(self, toolpath):
        super().__init__("Cpplint", "Static code analysis by Cpplint")
        self.toolpath = toolpath
        # TODO: Check if Cpplint is available there and can be executed correctly

    def get_metrics_dict(self):
        # Dictionary of provided metrics
        metrics = {
            "Cpplint - errors"     : "Number of error messages",
            "Cpplint - warnings"   : "Number of warning messages",
            "Cpplint - style"      : "Number of warnings regarding readability and style", 
            "Cpplint - other"      : "Number of other messages",
            "Cpplint - score"      : "Combined score"
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
        # Get static code analysis from Cpplint
        metrics = self.get_metrics_dict()

        out_cpplint = Qlytool.execute_shell_command(f"""
            {self.toolpath}/cpplint {fpath} 2>&1
            """)
        ptrn = re.compile(r"""		    
            (?P<file>.+):
            (?P<line>\d+):\s+
            (?P<details>.+)\[
            (?P<category>.+)/
            (?P<subcategory>.+)\]\s+\[     
            (?P<score>\d+)\]    
            """, re.VERBOSE)

        # All categories can be found here: https://aomedia.googlesource.com/aom/+/master/tools/cpplint.py
        catgrs = {
            "Cpplint - errors": [],
            "Cpplint - warnings": [
                "runtime",
                "legal"
            ],
            "Cpplint - style": [
                "whitespace",
                "readability", 
                "build"
            ]
        }

        for metric in metrics:
            metrics[metric].value = 0

        p_lastmsg = None
        for out in out_cpplint:
            match = ptrn.match(out)
            if match is not None:
                out_catgr = match.group("category")
                found = False
                for ewso in catgrs:
                    for catgr in catgrs[ewso]:
                        if catgr == out_catgr:
                            metrics[ewso].value += 1
                            p_lastmsg = metrics[ewso].msgs
                            found = True
                            break
                    if found:
                        break    
                else:
                    metrics["Cpplint - other"].value += 1
                    p_lastmsg = metrics["Cpplint - other"].msgs  
            if p_lastmsg is not None:
                p_lastmsg.append(out) 

        metrics["Cpplint - score"].value  = metrics["Cpplint - errors"].value   * 100
        metrics["Cpplint - score"].value += metrics["Cpplint - warnings"].value * 10
        metrics["Cpplint - score"].value += metrics["Cpplint - other"].value
        
        # TODO: There could be subcategories that are more severe than other
        # TODO: Maybe we don't want to report findings with low confidence score
        # Every problem is given a confidence score from 1-5, with 5 meaning we are
        # certain of the problem, and 1 meaning it could be a legitimate construct.
        # This will miss some errors, and is not a substitute for a code review.    

        return metrics
