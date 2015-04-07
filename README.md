# ScudCloud - Linux Client for Slack

![ScudCloud Logo](/scudcloud-1.0/resources/scudcloud.png?raw=true "Scud clouds are low, ragged and wind-torn cloud fragments, usually not attached to the thunderstorm base. With the 'mother' cloud, the form of them together is like a chat balloon")

ScudCloud is a **non official** open-source Linux (Debian, Ubuntu, Kubuntu, Mint, Arch) desktop client for [Slack&copy;](http://slack.com).

[Slack&copy;](http://slack.com) is a platform for team communication.

ScudCloud uses the [QT](http://qt-project.org) library + [Webkit](http://www.webkit.org/) to render the web version of Slack, but using the [QWebkit-Native bridge](http://qt-project.org/doc/qt-4.8/qtwebkit-bridge.html) to improve desktop integration with:

* multiple teams support,
* native system notifications,
* count of unread direct mentions at launcher/sytray icon,
* alert/wobbling on new messages,
* channels quicklist (Unity only),
* optional "Close to Tray".

# Install

Please, first update your system with a `sudo apt-get update && sudo apt-get upgrade`. If not, ScudCloud will crash with some old components.

Then, to install it under Ubuntu/Kubuntu 14.04, 14.10, Mint and Debian, open a Terminal (Ctrl+Alt+T) and run:

```term
sudo apt-add-repository -y ppa:rael-gc/scudcloud
sudo apt-get update
sudo apt-get install scudcloud
```

If you want **spell checking**, add the `hunspell` dictionary for your language. For `en-us`:

    sudo apt-get install hunspell-en-us

## Ubuntu 12.04

For Ubuntu 12.04 (Precise Pangolin), **additionally** you'll need to update `qtwebkit`: Slack is not compatible with `libqtwebkit4` package shipped with 12.04, hanging in the `Loading` screen. Please add the following PPAs (for updated `gstreamer` and `qtwebkit`):

```term
sudo add-apt-repository -y ppa:gstreamer-developers/ppa
sudo add-apt-repository -y ppa:immerrr-k/qtwebkit4-backport
sudo apt-get update
```

## Arch Linux

There is a [PKGBUILD available][pkgbuild] on the Arch User Repository. You can install it
using whichever AUR method you use. For instance, if you use cower:

```term
cower -d scudcloud
cd scudcloud
makepkg -si
```

[pkgbuild]: https://aur.archlinux.org/packages/scudcloud/

## Manual Install

The manual install is intended for not supported distros (if you want to contribute with a package for your distro, you're welcome!).

First, you'll need to install at least packages for `python3`, `python-qt4` (`qt4` for `python3`) and `python-dbus` (`dbus` library for `python3`).

Then run the below script: it'll download the code and install it:

```bash
wget https://github.com/raelgc/scudcloud/archive/v1.0.26.tar.gz
tar -xvf v1.0.26.tar.gz
cd scudcloud-1.0.26
SOURCE="scudcloud-1.0"
INSTALL="/opt/scudcloud"
sudo mkdir -p $INSTALL/lib
sudo mkdir -p $INSTALL/resources
sudo cp $SOURCE/lib/*.py $INSTALL/lib
sudo cp $SOURCE/resources/* $INSTALL/resources
sudo cp $SOURCE/scudcloud $INSTALL
sudo cp $SOURCE/LICENSE $INSTALL
sudo cp $SOURCE/scudcloud.desktop /usr/share/applications
sudo cp $SOURCE/systray/hicolor/* /usr/share/icons/hicolor/scalable/apps
sudo ln -sf $INSTALL/scudcloud /usr/bin/scudcloud
```

# Screenshots

![Some screenshots](/screenshot.png?raw=true)

# License

ScudCloud is is released under the [MIT License](/LICENSE).
