# Alup

Alup (**A**utomatic **L**ogin for **U**niversity of **P**isa) is a python script that provide to keep you logged on **University Of Pisa captive portal (Area SerRA)**.
After configuration of Alup with your credential, the login session will be managed automatically  in order to avoid the logout due to timeout or connection issues.  
  
### Why Alup?
The first reason is my Raspberry Pi. In fact Alup helps me to login without monitor through ssh by managing the captive portal connection.  
During the last year i used Alup also for my laptop and i decide to improve it in order to help someone else.  
I'm lazy, that's all.

### Extra modules
Alup works with these extra python modules:  
* bs4
* requests
Install them simply by using pip.

### Installation
Download alup:
```sh
$ git clone https://github.com/pigna90/alup.git
$ cd alup
```
Install Alup by using the following script:
```sh
$ python3 installer.py install

```
If the installation directory is not specified then Alup will be installed in your home directory.  
Copy the script manually as a super users:
```sh
# cp alup /usr/bin/

```
**Note**: `.alup/` folder will be installed as an hiden directory
### Usage
Run Alup:
```sh
$ alup

```
Create a new profile and run:
```sh
$ alup --new-profile

```
Run with a custom directory:
```sh
$ alup -c /path/to/.alup

```
**Note**: for more commands, run the scripts with -h (--help) command.
### Auto-run (systemd)
A systemd service will be created after installation. Copy it in systemd services directory:
```sh
$ cp alup.service /etc/systemd/system/

```
Start and test the service:
```sh
$ systemctl start alup.service

```
Start automaticaly:
```sh
$ systemctl enable alup.service

```
### Issues and bugs
For any bugs or issues, please contact me via [e-mail] and send me the logs located under `.alup/log/`

### Author
Alessandro Romano

[e-mail]: mailto:alessandro.romano@linux.com
