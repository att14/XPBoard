XPBoard
=======

https://trac.yelpcorp.com/login/rpc

Create a `config.py` within the `xp_board` dircectory. This config should contain your trac `username`, `password` and the base `trac_url` (e.g. trac.mycompany.com), along with the base ReviewBoard `url`. Additonally you will need `users` and a `team_name`.

An example config would be as follows.

```python
username = 'username'
password = 'password'

trac_url = 'trac.mycompany.com'
url = 'reviewboard.mycompany.com/'

team_name = 'XPBoard'
users = ["att14", "IvanMalison", "nigelchanyk"]
```
