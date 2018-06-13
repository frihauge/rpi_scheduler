#!flask/bin/python
from app import app
import time


# HOST='192.168.1.170'
HOST='0.0.0.0'

# Starting on my server, your ip address may be different.
app.run(host=HOST, debug=False)