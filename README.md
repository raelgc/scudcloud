# ScudCloud - Linux Client for Slack

![ScudCloud Logo](/scudcloud/resources/scudcloud.png?raw=true "Scud clouds are low, ragged and wind-torn cloud fragments, usually not attached to the thunderstorm base. With the 'mother' cloud, the form of them together is like a chat balloon")

ScudCloud is a **non official** open-source Linux (Debian, Ubuntu, Kubuntu, Mint, Arch, Fedora) desktop client for [Slack](http://slack.com).

ScudCloud improves the Slack integration with Linux desktops featuring:

* multiple teams support,
* native system notifications,
* count of unread direct mentions at launcher/sytray icon,
* alert/wobbling on new messages,
* channels quicklist (Unity only),
* optional "Close to Tray".

# Install

## Ubuntu/Kubuntu and Mint

Please, first update your system with:

```term
sudo apt-get update && sudo apt-get upgrade
```

If not, ScudCloud will crash with some old components or will not be installed.

Then, to install it under **Ubuntu/Kubuntu** (14.04, 14.10, 15.04, 15.10), **Mint** and **Debian**, open a Terminal (Ctrl+Alt+T) and run:

```term
sudo apt-add-repository -y ppa:rael-gc/scudcloud
sudo apt-get update
sudo apt-get install scudcloud
```

If you want **spell checking**, add the `hunspell` dictionary for your language. For `en-us`:

    sudo apt-get install hunspell-en-us

If you want to use a Slack icon instead of ScudCloud (which is not possible to include in this package due to copyright), download [any 128px Slack icon](https://www.google.com.br/search?q=slack+icon&tbm=isch&source=lnt&tbs=isz:ex,iszw:128,iszh:128) to your home folder saving as `scudcloud.png` and run:

```term
sudo dpkg-divert --add --rename --divert /usr/share/pixmaps/scudcloud.png.real /usr/share/pixmaps/scudcloud.png
sudo cp ~/scudcloud.png /usr/share/pixmaps/
sudo chmod +r /usr/share/pixmaps/scudcloud.png
```

## Ubuntu 12.04

For Ubuntu 12.04 (Precise Pangolin), **additionally** you'll need to update `qtwebkit`: Slack is not compatible with `libqtwebkit4` package shipped with 12.04, hanging in the `Loading` screen. Please add the following PPAs (for updated `qtwebkit`):

```term
sudo add-apt-repository -y ppa:immerrr-k/qtwebkit4-backport
sudo apt-get update
```

## Debian

Make sure `software-properties-common` is installed, then run:

```
sudo apt-add-repository -y ppa:rael-gc/scudcloud
sudo sed -i 's/jessie/trusty/g' /etc/apt/sources.list.d/rael-gc-scudcloud-jessie.list
sudo apt-get update
sudo apt-get install scudcloud
```

If you want spell checking and a Slack icon, follow related instructions on [Ubuntu Install section](#ubuntukubuntu-and-mint).

## Arch Linux

There is a [PKGBUILD available][pkgbuild] on the Arch User Repository. You can install it
using whichever AUR method you use. For instance, if you use cower:

```term
cower -d scudcloud
cd scudcloud
makepkg -si
```

[pkgbuild]: https://aur.archlinux.org/packages/scudcloud/

## Fedora and openSUSE

There are repositories available for these distributions. All you need to do is follow [these instructions][build_suse].

[build_suse]: http://software.opensuse.org/download.html?project=home%3Amoonwolf%3Ascudcloud&package=scudcloud

## Manual Install

The manual install is intended for not supported distros (if you want to contribute with a package for your distro, you're welcome!).

First, you'll need to install at least packages for `python3`, `python-qt4` (`qt4` for `python3`) and `python-dbus` (`dbus` library for `python3`).

Then run the following steps:

1. Download the [latest release](https://github.com/raelgc/scudcloud/releases/latest)
2. Unpack/unzip it
3. Change into the newly created directory
4. Run `sudo python3 setup.py install`

## Running From Dev Tree

ScudCloud can be run from the development tree. Simply run the following from the root of the project tree:

```bash
python3 -m scudcloud
```

# Troubleshooting

#### 1. Default domain

You can change the default domain editing or just deleting the config file:

    ~/.config/scudcloud/scudcloud.cfg

#### 2. Where is the package for my distro?

If not listed above, you're welcome [to contribute](/CONTRIBUTING.md). In this meanwhile, try the [Manual Install](#manual-install) instructions.

#### 3. Spell checking is not working

Make sure you have the following packages installed:

* `libqtwebkit-qupzillaplugins`
* `python3-hunspell`
* `hunspell-en-us`

#### 4. `Keep me signed in` is not working

For some reason, ScudCloud was not able to create the configuration folder. Please, manually create this folder:

    ~/.config/scudcloud/

#### 5. How to start ScudCloud minimized?

You can start ScudCloud minized to tray with:

    scudcloud --minimized=True

#### 6. High DPI Support

ScudCloud offers zoom support. The zoom level will be persisted between sessions.

- Increase zoom pressing <kbd>Ctrl +</kbd>, usually fired with <kbd>Ctrl Shift =</kbd>
- Decrease with <kbd>Ctrl -</kbd>
- Reset it with <kbd>Ctrl 0</kbd>

# Screenshots

![Some screenshots](/share/screenshot.png?raw=true)

# License

ScudCloud is is released under the [MIT License](/LICENSE).
