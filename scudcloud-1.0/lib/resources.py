import os, re

class Resources:

    APP_NAME = "ScudCloud Slack_SSB"
    SIGNIN_URL = "https://slack.com/signin"
    MAINPAGE_URL_RE = re.compile(r'^http[s]://[a-zA-Z0-9_\-]+.slack.com/?$')
    MESSAGES_URL_RE = re.compile(r'^http[s]://[a-zA-Z0-9_\-]+.slack.com/messages/.*')
    SSO_URL_RE = re.compile(r'^http[s]://[a-zA-Z0-9_\-]+.slack.com/sso/saml/start$')

    # It's initialized in /scudcloud script
    INSTALL_DIR = None

    def get_path(filename):
        return os.path.join(Resources.INSTALL_DIR, 'resources', filename)
