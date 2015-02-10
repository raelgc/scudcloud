# ScudCloud - Slax client for Ubuntu

![ScudCloud Logo](/scudcloud-0.9/resources/scudcloud.png?raw=true "Optional Title") 

ScudCloud is a **non official** open-source Ubuntu desktop client for [Slack&copy;](http://slack.com).

[Slack&copy;](http://slack.com) is a platform for team communication.

ScudCloud uses the [QT](http://qt-project.org) library + [Webkit](http://www.webkit.org/) to render the web version of Slack, but using the [QWebkit-Native bridge](http://qt-project.org/doc/qt-4.8/qtwebkit-bridge.html) to improve desktop integration with:

* native system notifications,
* count of unread notifications at launcher icon,
* and Launcher icon wobbling on new messages.

# Install

To install it, open a Terminal (Ctrl+Alt+T) and run:

```term
sudo apt-add-repository -y ppa:rael-gc/scudcloud
sudo apt-get update
sudo apt-get install scudcloud
```
