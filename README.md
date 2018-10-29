<img src=https://www.jcr.dow.cam.ac.uk/themes/downingjcr/assets/images/logo_purple.png width=120>

# Downing College JCR Room Balloting System

This system manages the allocation of college rooms during ballot weekend. It comprises a web application, which allows a student to view and select their room, and calculates room pricing automatically according to the Room Pricing Policy 2018.

<img src="https://github.com/cjoc/cjoc.github.io/raw/master/jcr-rbs.png">

## Installation

These instructions are for installation on an Ubuntu machine. The same method will work on any Linux distribution,
but you might have to change some of the paths below as appropriate. Change into the desired installation
directory then clone this repository:

```bash
$ git clone https://github.com/dowjcr/rooms
```

In line with best practice, create yourself a Python 3.5 `virtualenv`. Assuming you don't have `virtualenv` installed:

```bash
$ pip3 install virtualenv
$ mkdir virtualenvs
$ cd virtualenvs
$ virtualenv -p /usr/bin/python3 rooms
$ source rooms/bin/activate
```

Now you've activated the `virtualenv`, you can install the requirements:

```bash
$ cd ../rooms/rooms
$ pip install -r requirements.txt
```

Now configure Django's `settings.py`. An example configuration, `settings_example.py` has been included in the repo.
Simply rename and edit as per the TODOs.

```bash
$ cd rooms
$ mv settings_example.py settings.py
```

Migrate the database, then you're ready to run the test server:

```bash
$ cd ..
$ python manage.py makemigrations
$ python manage.py migrate
$ python manage.py runserver
```

Instructions on how to serve Django in production are widely available; `mod_wsgi` on Apache is to be recommended.

## Built With

- [**Django**](https://www.djangoproject.com/)
- [**django-ucamwebauth**](https://pypi.org/project/django-ucamwebauth/)
- [**jQuery**](https://jquery.com/)
- [**Bootstrap 4.1.1**](https://getbootstrap.com)

## Authors

- **Cameron O'Connor**, JCR Internet Officer 2018-19

## Licence

This project is licensed under the MIT Licence - see LICENSE.md for more details.
