import os
from string import Template
from shutil import copyfile

class Qlyreport_Main:
    def __init__(self, path):
        self.module_dir = os.path.dirname(__file__)
        self.template = os.path.join(self.module_dir, 'Qlyreport_Main_template.html')
        self.path = path
        self.table_header = []
        self.table_rows = []

    def add_header(self, header):
        self.table_header.append(header)
        
    def add_row_message(self, package, message, colspan):
        self.table_rows.append(f'<tr><td>{package}</a></td><td colspan="{colspan}">{message}</td>')

    def add_row(self, row):
        self.table_rows.append(row)

    def write(self):
        with open(self.template, 'r') as tmpl:
            src = Template(tmpl.read())
        html = src.substitute({
            'qlymetrics_table_header': "\n".join(self.table_header),
            'qlymetrics_table_rows': "\n".join(self.table_rows)
        })

        with open(f"{self.path}/index.html", "w") as out:
            out.write(html)
        copyfile(os.path.join(self.module_dir, 'Qlyreport_template.css'), f'{self.path}/Qlyreport_template.css')