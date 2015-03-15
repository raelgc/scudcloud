# ScudCloud - Ubuntu Client for Linux

![ScudCloud Logo](/scudcloud-1.0/resources/scudcloud.png?raw=true "Scud clouds are low, ragged and wind-torn cloud fragments, usually not attached to the thunderstorm base. With the 'mother' cloud, the form of them together is like a chat balloon")

ScudCloud is a **non official** open-source Linux (Debian, Ubuntu, Kubuntu, Mint) desktop client for [Slack&copy;](http://slack.com).

[Slack&copy;](http://slack.com) is a platform for team communication.

ScudCloud uses the [QT](http://qt-project.org) library + [Webkit](http://www.webkit.org/) to render the web version of Slack, but using the [QWebkit-Native bridge](http://qt-project.org/doc/qt-4.8/qtwebkit-bridge.html) to improve desktop integration with:

* multiple teams support,
* native system notifications,
* count of unread direct mentions at launcher/sytray icon,
* alert/wobbling on new messages,
* channels quicklist (Unity only),
* optional "Close to Tray".

# Install

To install it under Ubuntu/Kubuntu 14.04, 14.10, Mint and Debian, open a Terminal (Ctrl+Alt+T) and run:

```term
sudo apt-add-repository -y ppa:rael-gc/scudcloud
sudo apt-get update
sudo apt-get install scudcloud
```

If you want **spell checking**, add the `hunspell` dictionary for your language. For `en-us`:

    sudo apt-get install hunspell-en-us

## Ubuntu 12.04

For Ubuntu 12.04 (Precise Pangolin), you'll need to update `qtwebkit` (if not, ScudCloud will hang in the `Loading` screen. Please add the following PPAs (for updated `gstreamer` and `qtwebkit`):

```term
sudo add-apt-repository -y ppa:gstreamer-developers/ppa
sudo add-apt-repository -y ppa:immerrr-k/qtwebkit4-backport
sudo apt-get update
```

# Screenshots

![Some screenshots](/screenshot.png?raw=true)

# License

ScudCloud is is released under the [MIT License](/LICENSE).
