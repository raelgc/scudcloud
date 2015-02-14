# ScudCloud - Ubuntu Client for Slack

![ScudCloud Logo](/scudcloud-0.9/resources/scudcloud.png?raw=true "Scud clouds are low, ragged and wind-torn cloud fragments, usually not attached to the thunderstorm base. With the 'mother' cloud, the form of them together is like a chat balloon")

ScudCloud is a **non official** open-source Ubuntu/Linux desktop client for [Slack&copy;](http://slack.com).

[Slack&copy;](http://slack.com) is a platform for team communication.

ScudCloud uses the [QT](http://qt-project.org) library + [Webkit](http://www.webkit.org/) to render the web version of Slack, but using the [QWebkit-Native bridge](http://qt-project.org/doc/qt-4.8/qtwebkit-bridge.html) to improve desktop integration with:

* native system notifications,
* count of unread notifications at launcher icon,
* launcher icon wobbling on new messages,
* and channels quicklist at launcher icon.

# Install

To install it, open a Terminal (Ctrl+Alt+T) and run:

```term
sudo apt-add-repository -y ppa:rael-gc/scudcloud
sudo apt-get update
sudo apt-get install scudcloud
```

# First Run

In the first run, you'll see a dialog asking for your Identifier.

Identifier is your Slack subdomain without the `.slack.com` part.

By example: my test domain is `raelcunha.slack.com`. So, my identifier is `raelcunha`.

Enter this value in the Identifier input dialog.

# Screenshots

![Some screenshots](/screenshot.png?raw=true)

# License

ScudCloud is is released under the [MIT License](/LICENSE).
