# SGX Historical Data For Trading Automation

A simple web automation program that helps admin or equivalent position download daily data using selenium and python.

# Prerequisite

- FireFox (version 76.0.1)
- Python (version 3.7)

# Installation

Make sure you install the webdriver for Firefox browser

```bash
brew install geckodriver
```

Install python library dependencies

```bash
pip3 install -r requirements.txt
```

# Usage

```
usage: python3 downloadSGXFiles.py [options] [datetime|filename]

-a      Download all files [WEBPXTICK_DT.*.zip, TickData_structure.dat, TC_*.txt, TC_structure.dat]
-d      Choose datetime in format of yyyy-mm-dd e.g. 2020-05-08
-out    Specify download directory. By default, it would be 'downloads/'
```

# Got Question?
> kzsherdev@gmail.com
