# -*- coding: utf-8 -*-

#DATABASE='/tmp/kanripo.db'
DEBUG=True
SECRET_KEY='~[ \xab\xff\xf2\x08\xc8\x9aG\x1d\xd2\xd7a\xde9\xac;\xa1\xb4A\xaf\xbe\x15'
USERNAME='admin'
PASSWORD='default'

#mandoku
MDBASE="/Users/Shared/md-remote"
TXTDIR="/Users/Shared/md-remote/text"
IDXDIR="/Users/Shared/md-remote/index"
## not needed anymore, we handle this locally
# DICURL="http://localhost:5000/dic/"
##babel
LANGUAGES = {
    'ja': '日本語',
    'en': 'English',
}
BABEL_DEFAULT_LOCALE='ja'
