"""
The flask application package.
"""

from flask import Flask

app = Flask(__name__)

app.config['SECRET_KEY'] = '392d516932bffc215dd236e26931764d'

import proto1.views

