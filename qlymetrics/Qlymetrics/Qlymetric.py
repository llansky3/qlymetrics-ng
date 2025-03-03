import re
import statistics

from enum import Enum

class Risk(Enum):
    # Available risk levels
    UNKNOWN = 0
    GREEN = 1
    YELLOW = 2
    RED = 3

class Qlymetric:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.value = None
        self.msgs = []

    def get_risk(self):
        # This needs to be implemented in derived classes
        # If not - assume unknown
        return Risk.UNKNOWN

    def get_value(self):
        # This needs to be implemented in derived classes
        # If not - assume statistic median
        if isinstance(self.value, list):
            v = statistics.median(self.value)
        else:
            v = self.value
        return v

    def get_html_table_header(self):
        return "\n".join([
            f'<th colspan="1">',
            f'<span class="info">{self.name}',
            f'<span class="infotext">{self.description}</span>',
            '</span>',
            '</th>'
        ])

    def get_html_table_metric(self):
        riskclass = Risk(self.get_risk()).name
        return "\n".join([
            f'<td colspan="1" class="{riskclass}">{self.get_value()}</td>'
        ])    
        # TODO: Generate report for messages if available
        # Must pass file SHA for this
   
    def get_html_metric_info(self):
        if self.msgs:
            strmsgs = "\n".join(self.msgs)
            strmsgs = Qlymetric.escchar_to_html(strmsgs)
            return "\n".join([
                f'<h2><span class="info">{self.name}'
                f'<span class="infotext">{self.description}',
                '</span></span></h2>',
                f'<table id="qlyreport_table" class="terminal"><tr><td><pre>{strmsgs}'
                '</pre></tr></td></table>'
            ])
        else:
            return '' 
     
    @staticmethod
    def escchar_to_html(str):
        # Replaces terminal special characters with html equivalents
        str = str.replace('\n', '<br>') 
        str = str.replace('\r', '')
        str = str.replace('\t', '&nbsp&nbsp&nbsp&nbsp')
        return str