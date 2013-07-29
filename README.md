XPBoard
=======

Create a `config.py` within the `xp_board` dircectory. This config should contain your trac `username`, `password` and the base `trac_url` (e.g. trac.mycompany.com), along with the base `rb_url`. Additonally you will need `users` and a `team_name`. An example config would be as follows.

```python
# Trac Information
trac_url = 'trac.mycompany.com'
username = 'username'
password = 'password'

# Reviewboard Information
rb_url = 'reviewboard.mycompany.com'

# Team Information
team_name = 'XPBoard'
users = ["att14", "IvanMalison", "nigelchanyk"]
```

To start a development environment. First, activate a virtual environment
```
virtualenv ENV
source ENV/bin/activate
```

Install the dependencies.
```
pip install -r requirements.txt
python setup.py install
```

Populate the database.
```
python db_init.py
python refresh.py
```

Run the application.
```
python xp_board/main.py
```
