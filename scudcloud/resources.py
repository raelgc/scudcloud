import os, re

class Resources:

    APP_NAME = 'ScudCloud'
    SIGNIN_URL = 'https://slack.com/signin'
    MAINPAGE_URL_RE = re.compile(r'^http[s]://[a-zA-Z0-9_\-]+.slack.com/?$')
    MESSAGES_URL_RE = re.compile(r'^http[s]://[a-zA-Z0-9_\-]+.slack.com/messages/.*')
    SSO_URL_RE = re.compile(r'^http[s]://[a-zA-Z0-9_\-]+.slack.com/sso/saml/start$')
    SERVICES_URL_RE = re.compile(r'^http[s]://[a-zA-Z0-9_\-]+.slack.com/services/.*')
    GOOGLE_OAUTH2_URL_RE = re.compile(r'^https://accounts.google.com/o/oauth')

    SPELL_LIMIT = 6
    SPELL_DICT_PATH  = '/usr/share/hunspell'
    DEFAULT_CONFDIR  = '~/.config/scudcloud'
    DEFAULT_CACHEDIR = '~/.cache/scudcloud'

    # It's initialized in /scudcloud script
    INSTALL_DIR = os.path.dirname(os.path.realpath(__file__))

    def get_path(filename):
        return os.path.join(Resources.INSTALL_DIR, 'resources', filename)
