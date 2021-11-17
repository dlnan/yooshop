![alt text](https://github.com/thedmdim/yoo_shop/blob/master/static/pics/logo.svg)
> Online store CMS written with Flask.

## Front end
- Fully adaptive design for desktops and mobiles powered only by CSS grid.
- Every page weights less than 100kb.
- Messengers notifications on users actions
- No more requirements except of Flask and acquiring sdk.

_The point was to build very fast and effective online store in opposite to modern overweighted sites with scripts_

## Back end
- Flask
- sqlite3 > 3.36
[How to update sqlite on hosting](https://eeinte.ch/stream/install-latest-sqlite-version-shared-hosting/)


## Acqirirng
By default [YooKassa acqiring](https://github.com/yoomoney/yookassa-sdk-python) is integrated.

## Local running
1. `pip install Flask`
2. `pip install yookassa`
3. 
```bash
# for linux
export FLASK_APP=main.py
# for Windows
set FLASK_APP=main.py
flask run
```





