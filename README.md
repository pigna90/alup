# Alup (Automatic Login for University of Pisa)

Alup (**A**utomatic **L**ogin for **U**niversity of **P**isa) is a Python script provides to keep you logged on **University Of Pisa captive portal (Area SerRA)**.
After configuration of Alup with your credentials, the login session will be managed automatically in order to avoid logout due to timeout or connection issues.  
Alup works for **Linux**, **Mac** and **Windows** (excepts for the autorun part).
  
### Why Alup?
The first reason is my Raspberry Pi. Alup helps me to logging in without any monitor through ssh by managing the captive portal connection.  
I've being using Alup also for my laptop so I decided to improve it in order to help someone else.  
I'm lazy, that's all!

## Extra modules
Alup works with these extra python modules:  
* **bs4**
* **requests**

Install them simply by using pip.  
**Note**: be sure you install them for **python3**

## Installation

Download:
```sh
$ git clone https://github.com/pigna90/alup.git
$ cd alup
```
Install:
```sh
$ python3 installer.py install

```
If the installation directory isn't specified then Alup will be installed in your home directory.  
Copy the script manually as a super users:
```sh
# cp alup /usr/local/bin/

```
**Note**: `.alup/` folder will be installed as an hiden directory

## Usage
Run:
```sh
$ alup

```
Create a new profile and run:
```sh
$ alup --new-profile

```
Run from a custom directory:
```sh
$ alup -c /path/to/.alup

```
**Note**: for more commands please use `-h (--help)` command.

## Auto-run (systemd)
Installation script creates a systemd configuration file as well. Copy it in your systemd services directory as super user:
```sh
# cp alup.service /etc/systemd/system/

```
Start and test the service:
```sh
$ systemctl start alup.service

```
Start automaticaly:
```sh
$ systemctl enable alup.service

```
## Issues and bugs
For any bugs or issues use the Issues section or create a new pull request. Please **attach the logs** located under `.alup/log/`.  

## Author
Alessandro Romano
