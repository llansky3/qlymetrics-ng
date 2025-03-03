# qlymetrics-ng
2nd generation of Qlymetrics framework for software quality metrics

## List of implemented tools 
[Please look here for details!](docs/tools-table.md)

## Example
This fetches jemalloc package from [openSUSE:Factory OBS project](https://api.opensuse.org/package/show/openSUSE:Factory/jemalloc) and generate software quality metrics reports

```shell
python3 qlymetrics.py --project openSUSE:Factory --packages jemalloc
```
and generates overview report page
<img src="docs/example screenshot - jemalloc - Main.png" alt="">
from where you can navigate to get more details about invidiual source files
<img src="docs/example screenshot - jemalloc - Package.png" alt="output_ibs_Qlyreport_jemalloc.html">

