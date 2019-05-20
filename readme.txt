virtualenv env
env\Scripts\activate.py

pip freeze >requirements.txt
pip install -r requirements.txt


set FLASK_APP=main.py
flask run


flask shell
>>>app.url_map
