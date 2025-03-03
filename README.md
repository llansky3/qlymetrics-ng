# qlymetrics-ng
2nd generation of Qlymetrics framework for software quality metrics

## Example
This fetch jemalloc package from [openSUSE:Factory OBS project](https://api.opensuse.org/package/show/openSUSE:Factory/jemalloc) and generate software quality metrics reports.

```shell
python3 qlymetrics.py --project openSUSE:Factory --packages jemalloc
```
This generates overview page
<img src="docs/example screenshot - jemalloc - Main.png" alt="">
from where you can get more details about invidiual source files
<img src="docs/example screenshot - jemalloc - Package.png" alt="output_ibs_Qlyreport_jemalloc.html">

