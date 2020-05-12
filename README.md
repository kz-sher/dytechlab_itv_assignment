# SGX Historical Data For Trading - Task Automation

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
-d      Choose datetime in format of yyyy-mm-dd e.g. 2020-05-08. By default it would be set as latest date
-out    Specify download directory. By default, it would be 'downloads/'
```

# Other Concerns

### How to download files for another date

By using command with `-d` option and proper format of date specified, this can be achieved. For example:

```
python3 downloadSGXFiles.py -d 2020-05-08
```

This will download files on 08 May 2020 if they are available. Otherwise, you will be notified with error message in console.

### How to change my downloads directory

By using command with `-out` option and proper format of folder name specified, this can be achieved. For example:

```
python3 downloadSGXFiles.py -out sgx -d 2020-05-08
```

The downloaded files will then be at `./sgx/2020-05-08`.

### Logging
All the messages will be logged to the console. Only error message will additionally be logged to `errors.log` file, which is located in the project root directory. 

### Download Failure
Currently, if download failure is encountered, you have to issue the command again to perform redownload. For older files, it is relatively difficult to download as it is not available on the website.

# Got Question?
> kzsherdev@gmail.com
