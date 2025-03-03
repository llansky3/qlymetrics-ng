#!/usr/bin/python3

import requests
import hashlib
import os
import xml.etree.ElementTree as Eltree
import pickle
import functools
import multiprocessing
import argparse
import sys

from qlymetrics import *
from utils import retry

@retry
def get_package_list(apiurl, project):
    resp = requests.get(
            f"{apiurl}/public/source/{project}?view=info")
    xml_pkgs = Eltree.fromstring(resp.text)
    xml_pkgs = xml_pkgs.findall("sourceinfo")
    pkgs_names = [x.attrib["package"] for x in xml_pkgs]

    pkgs = []
    for xml_pkg in xml_pkgs:
        pkg_name = xml_pkg.attrib["package"]
        
        # Do not include bootstrap
        if pkg_name == 'AGGR-bootstrap':
            continue

        # Do not include linked package    
        linked = xml_pkg.findall("linked")
        originpackage = xml_pkg.findall("originpackage")
        if linked:
            if linked[0].attrib["package"] in pkgs_names:
                continue
        if originpackage:
            if originpackage[0].text in pkgs_names:
                continue

        pkgs.append(pkg_name)
    return pkgs

def get_package_list_from_file(fpath):
    with open(fpath) as f:
        pkgs = f.read().splitlines()
    return pkgs   

@retry
def download_file(url, dest, dont_redownload=False):
    # Download a file to given destination
    sha1 = hashlib.sha1()
    if not os.path.exists(dest):
        os.makedirs(dest)

    local_filename = f"{dest}/{url.split('/')[-1]}"
    if os.path.exists(local_filename) and dont_redownload:
        # Do not re-download if the file exists
        return local_filename, None     

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        f = open(local_filename, 'wb')
        with f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)
                sha1.update(chunk)
    
    return local_filename, sha1 

@retry
def get_srcrpm(apiurl, project, package):
    resp = requests.get(
        f"{apiurl}/public/build/{project}/standard/x86_64/{package}")
    xml_binarylist = Eltree.fromstring(resp.text)

    # Get the source RPMs out of binary list
    xml_srcrpm = [e for e in xml_binarylist.findall(".//binary[@filename]") if "src.rpm" in e.attrib["filename"]]
    
    if xml_srcrpm:   
        return xml_srcrpm[0].attrib["filename"]
    else:    
        return None

def get_srccode(apiurl, project, package):
    fn_srcrpm = get_srcrpm(apiurl, project, package)
    # patch_srcs = []
    if fn_srcrpm is not None:
        destdir = f'./download/{package}'
        destdir = os.path.abspath(destdir)
        path_srcrpm, sha1 = download_file(f"{apiurl}/public/build/{project}/standard/x86_64/{package}/{fn_srcrpm}", destdir, True)

        # Unpack the source RPM to a SOURCES folder
        srcdir = f"{destdir}/SOURCES"
        if not os.path.exists(srcdir):
            os.makedirs(srcdir)

        out_cpio = Qlytool.execute_shell_command(f"rpm2cpio {path_srcrpm} | cpio -idmv --directory={srcdir}")

        out_rpmbuild = Qlytool.execute_shell_command(f'rpmbuild -bp {srcdir}/{package}.spec --define "_topdir {destdir}" --nodeps')

        # Gather source code files
        patch_srcs = gather_srcs(f"{destdir}/BUILD")
    else:
        patch_srcs = []
        print(f"Skipping {package} - no source RPM available!")
    return patch_srcs

def gather_srcs(dir):
    patch_srcs = []
    for subdir, dirs, files in os.walk(dir):
        for file in files:
            for ext in ['.c', '.cpp']:
                # Only C/C++
                if file.lower().endswith(ext):
                    if subdir.find('test') == -1 and file.find('test') == -1:
                        patch_srcs.append(os.path.join(subdir, file))
                    else:
                        print(f'Skipping test file {os.path.join(subdir, file)} !')
    return patch_srcs

def process_package(pkg, tools, srcfiles, apiurl, project, folder, report):
    print(f"Processing {pkg}")
    report_package = Qlyreport_Package(pkg)
    all_metrics = {}
    for tool in tools:
        metrics = tool.get_metrics_dict()
        for metric in metrics:
            metrics[metric].value = []    
            report_package.add_header(metrics[metric].get_html_table_header())
        all_metrics.update(metrics)
    if folder is None:
        patch_srcs = get_srccode(apiurl, project, pkg)
    else:
        patch_srcs = gather_srcs(folder)
    if not patch_srcs:
        # Do nothing - no source files available
        report[0].add_row_message(pkg, 'No C/C++ files available! This package is likely written in other language!', len(all_metrics))
        return {
            "srcfiles" : {},
        }

    # Getting the metrics and worst case information
    new_srcfiles = {}
    for path_src in patch_srcs:
        srcfile = Qlyfile(path_src)
        if srcfile.hash in srcfiles:
            srcfile = srcfiles[srcfile.hash]
        else:
            new_srcfiles[srcfile.hash] = srcfile
            print(f"Getting all metrics for {path_src}")
            for tool in tools:
                if isinstance(tool, Buildlogs):
                    metrics = tool.get_metric(path_src, pkg)  
                else:
                    metrics = tool.get_metric(path_src)   
                for metric in metrics:
                    srcfile.metrics.append(metrics[metric])
                    all_metrics[metric].value.append(metrics[metric].value)
            
        # Package reporting - add files rows
        report_package.add_row_file(srcfile.hash, srcfile.name)
        for metric in srcfile.metrics:
            print(f"{metric.name}: {metric.value}") 
            report_package.add_row(metric.get_html_table_metric())
        report_package.add_row('</tr>')

        # File reporting
        srcfile.create_html_file_report(report[0].path)
                                    
    # Package reporting
    fn_report = report_package.write(report[0].path)

    # For overview reporting - return package row
    report[0].add_row(f'<tr><td><a href="{fn_report}">{pkg}</a></td>')
    for metric in all_metrics:
        report[0].add_row(all_metrics[metric].get_html_table_metric())
    report[0].add_row('</tr>')
    return {
        "srcfiles" : new_srcfiles,
    }

def main(args):
    apiurl = args.url
    project = args.project
    if args.packages:
        pkgs = args.packages
    else:
        pkgs = get_package_list(apiurl, project)
    
    if args.packages_exclude is not None:
        for pkg_excluded in args.packages_exclude:
            try:
                pkgs.remove(pkg_excluded)
            except ValueError:    
                pass

    if args.folder is not None:
        if os.path.exists(args.folder):
            pkgs = [os.path.basename(args.folder)]
        else:
            sys.stderr.write(f"The provided path {args.folder} doesn't exist! Please check and try again!\n")
            sys.exit(1)

    # TODO: detect available tools and use just them
    tools = [
        Filesize(),
        Pmccabe('/usr/bin'),
        Cppcheck('/usr/bin'),
        Splint('/usr/bin'),
        Cpplint('/usr/bin'),
        Buildlogs(apiurl, project),
        Ctags('/usr/bin')
    ]

    datafile = './Qlymetrics_data.saved'
    if not os.path.exists(datafile) or not args.loading:
        srcfiles = {}
    else:   
        with open(datafile, 'rb') as f:
            srcfiles = pickle.load(f)

    reportdir = './report'
    if not os.path.exists(reportdir):
        os.makedirs(reportdir)

    report_main = Qlyreport_Main(reportdir)
    for tool in tools:
        metrics = tool.get_metrics_dict()
        for metric in metrics:
            report_main.add_header(metrics[metric].get_html_table_header())

    fcn_process_package = functools.partial(
        process_package, 
        tools = tools, 
        srcfiles = srcfiles,
        apiurl = apiurl,
        project = project,
        folder = args.folder,
        report = [report_main]
    )

    if args.multiprocessing:
        cpu_count = multiprocessing.cpu_count()
        print(f"Multiprocessing using {cpu_count} workers")
        with multiprocessing.Pool(cpu_count) as p:
            outmap = p.map(fcn_process_package, pkgs)
    else:
        outmap = []
        for pkg in pkgs:
            outmap.append(fcn_process_package(pkg))

    for subdict in outmap:
        if subdict:
            if not subdict["srcfiles"] == None:
                srcfiles.update(subdict["srcfiles"])
    # Save it for next time
    # TODO: Maybe we want to save it as we go in case something goes wrong
    with open(datafile, 'wb') as f:
        pickle.dump(srcfiles, f)

    # Overview reporting
    report_main.write()

def parse_args():
    parser = argparse.ArgumentParser(
        __file__, description="Python script for evaluating various quality metrics!"
    )
    parser.add_argument(
        "--url", "-u",
        help="URL address to OBS API",
        action="store",
        default="https://api.opensuse.org"
    )

    parser.add_argument(
        "--project", "-p",
        help="OBS project",
        action="store",
        default="openSUSE:Factory"
    )

    parser.add_argument(
        "--folder", "-f",
        help="Target path on local machine",
        action="store"
    )

    parser.add_argument(
        "--debug", "-d",
        help="Debug mode",
        dest="loglevel",
        choices=["INFO", "WARNING", "ERROR", "DEBUG"],
        action="store",
        default="ERROR"
    )

    parser.add_argument(
        "--multiprocessing", "-m",
        help="Multiprocessing enabled",
        action="store_true",
        default=False
    )

    parser.add_argument(
        "--loading", "-l", 
        help="Loading of old results enabled to speed up",
        action="store_true",
        default=False
    )

    parser.add_argument(
        '--packages',
        nargs='+',
        help='List of packages',
        required=True
    )

    parser.add_argument(
        '--packages-exclude',
        nargs='+',
        help='List of excluded packages',
        required=False
    )

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    main(args)
    print("--- done ---")