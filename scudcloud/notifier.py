from dbus.exceptions import DBusException
try:
    from gi.repository import Notify
except ImportError:
    from scudcloud import notify2
    Notify = None

class Notifier(object):

    def __init__(self, app_name, icon):
        self.icon = icon
        try:
            if Notify is not None:
                Notify.init(app_name)
                self.notifier = Notify
            else:
                notify2.init(app_name)
                self.notifier = notify2
            self.enabled = True
        except DBusException:
            print("WARNING: No notification daemon found! "
                  "Notifications will be ignored.")
            self.enabled = False

    def notify(self, title, message, icon=None):
        if not self.enabled:
            return
        if icon is None:
            icon = self.icon
        if Notify is not None:
            notice = self.notifier.Notification.new(title, message, icon)
        else:
            notice = notify2.Notification(title, message, icon)
        notice.set_hint_string('x-canonical-append', '')
        notice.show()
