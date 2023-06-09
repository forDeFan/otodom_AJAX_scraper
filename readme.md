<h1>Web scraper for JS dynamically generated page</h1>

Data feed from AJAX generated data without usage of Selenium, just Requests based - for speed, efficiency and resources saving.

<h2>Technologies used</h2>
* Python 3<br>
* Requests<br>
* Beautiful Soup 4<br>
* Tenacity<br>
* Pydantic<br>
* Poetry<br>
* Pytest


## Table of contents

* [Setup](#setup)
* [Run](#run)
* [Tests](#tests)

## Setup

### Prerequisites

* python 3.X
* linux distro (tested on Ubuntu x86_64 5.4.0-144-generic)


### Install

Advice to set up virtual environment before packages installation.

The project can be installed either by requirements.txt or by poetry.

1. Requirements

```
$ git clone https://github.com/forDeFan/otodom_AJAX_scraper.git
$ cd otodom_AJAX_scraper
$ pip install -r requirements.txt
```

2. Poetry

```
$ git clone https://github.com/forDeFan/otodom_AJAX_scraper.git
$ cd otodom_AJAX_scraper
$ poetry install
```

### Parametrization

Configutation files in /config dir.
<br>
For general setup (search params mainly): parameters.yaml<br>


## Run

Verbose terminal logging is on by default (can be changed in parameters.yaml).<br>
After succesfull run file (example.txt) with scraped data will be created in project root (filename and path can be defined in parameters.yaml)
<br><br>
To start scraper:

If dependencies installed with requirements.txt

```
$ python3 main.py
```
if installed with poetry
```
$ poetry run python3 main.py
```

## Tests

Made with pytest.

```
$ poetry run pytest
```