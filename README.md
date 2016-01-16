# Alup

Alup is a python script that provide to keep you logged on University Of Pisa captive portal.
After configuration of Alup with your credential, the login session will be managed automatically  in order to avoid the logout due to timeout or connection issues.

### Installation
Run alup:

```sh
$ python alup.py -cp /path/to/config/file

```

Create an user configuration:

```sh
$ python alup.py -cp /path/to/config/file --user-config

```

**Note:** python is an alias for python3, therefore verify your configuration.
