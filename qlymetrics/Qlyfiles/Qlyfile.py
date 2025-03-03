import os
import hashlib

from string import Template

class Qlyfile:
    def __init__(self, path):
        self.path = path
        self.folder, self.name = os.path.split(path)
        self.hash = Qlyfile.get_sha1(path)
        self.metrics = []

    def create_html_file_report(self, reportdir):
        # Create html report for details about findings
        metric_info = []
        for metric in self.metrics:
            metric_info.append(metric.get_html_metric_info())
        module_dir = os.path.dirname(__file__)
        file_template = os.path.join(module_dir, 'Qlyreport_file_template.html')
        with open(file_template, 'r') as tmpl:
            src = Template(tmpl.read())
            html = src.substitute({
                'path': self.path,
                'abspath': os.path.abspath(self.path),
                'name': self.name,
                'hash': self.hash,
                'metrics_information' : "\n".join(metric_info)
            })
            with open(f"{reportdir}/output_ibs_Qlyreport_{self.hash}.html", "w") as out:
                out.write(html)

    @staticmethod
    def get_sha1(path):
        # Calculate SHA1 for a given file
        buffersize = 8192
        sha1 = hashlib.sha1()
        if not os.path.exists(path):
            return None
        with open(path, 'rb') as f:
            while True:
                data = f.read(buffersize)
                if not data:
                    break
                sha1.update(data)
        return sha1.hexdigest()
        