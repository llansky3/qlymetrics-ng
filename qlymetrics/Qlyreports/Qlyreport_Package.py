import os
from string import Template

class Qlyreport_Package:
    def __init__(self, package):
        module_dir = os.path.dirname(__file__)
        self.template = os.path.join(module_dir, 'Qlyreport_Package_template.html')
        self.package = package
        self.table_header = []
        self.table_rows = []

    def add_header(self, header):
        self.table_header.append(header)
        
    def add_row_message(self, message, colspan):
        self.table_rows.append(f'<tr><td>{self.package}</a></td><td colspan="{colspan}">{message}</td>')

    def add_row_file(self, hash, name):
        self.table_rows.append(f'<tr><td>{self.package}</td><td><a href="output_ibs_Qlyreport_{hash}.html">{name}</a></td>')

    def add_row(self, row):
        self.table_rows.append(row)

    def write(self, path):
        #  Package reporting
        fn_report = f'output_ibs_Qlyreport_{self.package}.html'
        with open(self.template, 'r') as tmpl:
            src = Template(tmpl.read())
            html = src.substitute({
                'package': self.package,
                'qlymetrics_table_header': "\n".join(self.table_header),
                'qlymetrics_table_rows': "\n".join(self.table_rows)
            })

            with open(f"{path}/{fn_report}", "w") as out:
                out.write(html)
        return fn_report