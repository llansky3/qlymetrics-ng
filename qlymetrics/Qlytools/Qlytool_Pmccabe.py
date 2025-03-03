import re
import numbers

from .Qlytool import Qlytool

from ..Qlymetrics import Qlymetric, Risk

class Qlymetric_Mccabe(Qlymetric):
    def get_risk(self):
        # Risk levels taken from: 
        # https://www.castsoftware.com/glossary/cyclomatic-complexity
        # https://www.aivosto.com/project/help/pm-complexity.html
        if not isinstance(self.value, numbers.Number):
            return Risk.UNKNOWN
        elif self.get_value() <= 20:
            return Risk.GREEN
        elif self.get_value() <= 50:
            return Risk.YELLOW
        else:
            return Risk.RED

class Qlymetric_Lines(Qlymetric):
    def get_risk(self):
        if not isinstance(self.value, numbers.Number):
            return Risk.UNKNOWN
        elif self.get_value() <= 100:
            return Risk.GREEN
        elif self.get_value() <= 500:
            return Risk.YELLOW
        else:
            return Risk.RED
           
class Pmccabe(Qlytool):
    def __init__(self, toolpath=None):
        super().__init__("Pmccabe", "Mccabe's cyclomatic complexity")
        if toolpath is not None:
            self.toolpath = toolpath
        # Check if pmccabe is available there and can be executed correctly
        self.available = self.check_if_installed('pmccabe -V')

    def get_metrics_dict(self):
        # Dictionary of provided metrics
        metrics = {
            "Modified Mccabe": "Modified Mccabe's cyclomatic complexity",
            "Traditional Mccabe": "Traditional Mccabe's cyclomatic complexity",
            "Statements in function": "Maximum number of statemenets in a function",
            "Lines in function": "Maximum number of lines in a function"
        }
        metrics_dict = {}
        for metric in metrics:
            if "Mccabe" in metric:
                metrics_dict[metric] = Qlymetric_Mccabe(metric,metrics[metric])
            elif "Lines" in metric:
                metrics_dict[metric] = Qlymetric_Lines(metric,metrics[metric])     
            else:
                metrics_dict[metric] = Qlymetric(metric,metrics[metric])
        return metrics_dict 

    def get_metric(self, fpath):
        # Get Mccabe's cyclomatic complexity
        metrics = self.get_metrics_dict()

        out_pmccabe = Qlytool.execute_shell_command(f'{self.toolpath}/pmccabe {fpath}')
        ptrn = re.compile(r"""		    
            (?P<modified_Mcccabe>\d+)\s+
            (?P<traditional_Mcccabe>\d+)\s+
            (?P<statements_in_function>\d+)\s+
            (?P<first_line_of_function>\d+)\s+
            (?P<lines_in_function>\d+)\s+
            (?P<file_name>.*)\(\d+\):\s+
            (?P<function_name>[A-Za-z0-9_]+)
            """, re.VERBOSE)

        for metric in metrics:
            metrics[metric].value = [0]
        
        for out in out_pmccabe:
            match = ptrn.match(out)
            if match is not None:
                metrics["Modified Mccabe"].value.append(int(match.group("modified_Mcccabe")))
                metrics["Modified Mccabe"].msgs.append(out)
                metrics["Traditional Mccabe"].value.append(int(match.group("traditional_Mcccabe")))
                metrics["Traditional Mccabe"].msgs.append(out)
                metrics["Statements in function"].value.append(int(match.group("statements_in_function")))
                metrics["Statements in function"].msgs.append(out)
                metrics["Lines in function"].value.append(int(match.group("lines_in_function")))
                metrics["Lines in function"].msgs.append(out)

        # Get the highest value for all the metrics
        for metric in metrics:
            metrics[metric].value = max(metrics[metric].value)        

        return metrics
