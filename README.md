# ScudCloud - Linux Client app for Slack

![ScudCloud Slack app on Ubuntu Unity](/share/screenshot.png?raw=true)

ScudCloud is a **non official** open-source Linux (Debian, Ubuntu, Kubuntu, Mint, Arch, Fedora) desktop client app for [Slack](http://slack.com).

ScudCloud improves the Slack integration with Linux desktops featuring:

* multiple teams support
* native system notifications
* count of unread direct mentions at launcher/sytray icon
* alert/wobbling on new messages
* channels quicklist (Unity only)
* optional tray notifications and "Close to Tray"
* follow your desktop activity and will stay online while you're logged in (if correct packages are installed)

# Install

## Ubuntu/Kubuntu and Mint

Please, first update your system with:

```term
sudo apt-get update && sudo apt-get upgrade
```

If not, ScudCloud will crash with some old components or will not be installed.

Then, to install it under **Ubuntu/Kubuntu** (16.04, 15.10, 14.04), **Mint** and **Debian**, open a Terminal (Ctrl+Alt+T) and run:

```term
sudo apt-add-repository -y ppa:rael-gc/scudcloud
echo ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true | sudo debconf-set-selections
sudo apt-get update
sudo apt-get install scudcloud
```

If you want **spell checking**, add the `hunspell` dictionary for your language and make sure dependencies are installed. For `en-us`:

    sudo apt-get install hunspell-en-us libqtwebkit-qupzillaplugins python3-hunspell

If you want to use a Slack icon instead of ScudCloud (which is not possible to include in this package due to copyright), download [any 128px Slack icon](https://www.google.com.br/search?q=slack+icon+transparent&tbm=isch&source=lnt&tbs=isz:ex,iszw:128,iszh:128) to your home folder saving as `scudcloud.png` and run:

```term
sudo dpkg-divert --add --rename --divert /usr/share/pixmaps/scudcloud.png.real /usr/share/pixmaps/scudcloud.png
sudo cp ~/scudcloud.png /usr/share/pixmaps/
sudo chmod +r /usr/share/pixmaps/scudcloud.png
sudo update-desktop-database
```

## Debian and derivatives like BunsenLabs Linux

Make sure the `software-properties-common` and `lsb-release` packages are installed, then run:

```
sudo apt-add-repository -y ppa:rael-gc/scudcloud
DISTRIB_CODENAME=$(lsb_release -sc)
sudo sed -i "s/${DISTRIB_CODENAME}/trusty/g" /etc/apt/sources.list.d/rael-gc-scudcloud-${DISTRIB_CODENAME}.list
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

## openSUSE

There are repositories available for these distributions. All you need to do is follow [these instructions][build_suse].

[build_suse]: http://software.opensuse.org/download.html?project=home%3Amoonwolf%3Ascudcloud&package=scudcloud

## Fedora

```term
sudo dnf install scudcloud
```

## Manual Install

The manual install is intended for not supported distros (if you want to contribute with a package for your distro, you're welcome!).

First, you'll need to install at least packages for `python3`, `python3-setuptools`, `python3-pyqt5.qtwebkit` (or equivalent `qt5` version of `qtwebkit` for `python3`) and `python-dbus` (`dbus` library for `python3`).

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

#### 1. Default domain and loading order

You can change the default domain (or the domain loading order) editing or just deleting the config file:

    ~/.config/scudcloud/scudcloud.cfg

#### 2. Where is the package for my distro?

If not listed above, you're welcome [to contribute](/CONTRIBUTING.md). In this meanwhile, try the [Manual Install](#manual-install) instructions.

#### 3. Spell checking is not working

Make sure you have the following packages installed:

* `libqtwebkit-qupzillaplugins`
* `python3-hunspell`
* `hunspell-en-us`

#### 4. `Keep me signed in` is not working / My team is not saved

For some reason, ScudCloud was not able to create the configuration folder. Please, manually create this folder:

    mkdir -p ~/.config/scudcloud/

If it exists and `.cfg` file is present, try change permissions in config file:

    chmod -R 0755 ~/.config/scudcloud/scudcloud.cfg

#### 5. How to start ScudCloud minimized?

You can start ScudCloud minized to tray with:

    scudcloud --minimized=True

#### 6. High DPI Support

ScudCloud offers zoom support. The zoom level will be persisted between sessions.

- Increase zoom pressing <kbd>Ctrl +</kbd>, usually fired with <kbd>Ctrl Shift =</kbd>
- Decrease with <kbd>Ctrl -</kbd>
- Reset it with <kbd>Ctrl 0</kbd>

#### 7. No icon in systray/notification area

Make sure that `File` > `Close to Tray` is checked.

#### 8. Code blocks are not using fixed width font

This is the font-family required (i.e., you need of them): `Monaco, Menlo, Consolas, Courier New, monospace`.

#### 9. Viewing snippets consumes too much resources

This is a known behavior of python webkit. But you can disable snippets inline view (they'll be opened in browser).

To achieve this, edit the config file located at `~/.config/scudcloud/scudcloud.cfg` and add the following line:

    Snippets=False

#### 10. How to open webkit console?

Start ScudCloud with:

    scudcloud --debug=True &
    
Then right click in the conversation pane and select `Inspect Element`. Maximize the new window and click in the `Console` tab.    

# License

ScudCloud is is released under the [MIT License](/LICENSE).
