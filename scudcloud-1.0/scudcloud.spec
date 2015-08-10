#
# spec file for package scudcloud
#
# Copyright (c) 2015 Marcin Trendota (moonwolf@techsterowniki.pl)
# Copyright (c) 2015 Marcin Bajor (marcin.bajor@gmail.com)
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#


Name:           scudcloud
Version:        1.0
Release:        2%{?dist}
Summary:        Non official desktop client for Slack©
License:        MIT
Group:          Applications/Internet
BuildRequires:  python

%if (0%{?suse_version} || 0%{?fedora_version})
BuildRequires:  fdupes
%endif

%if 0%{?suse_version}
BuildRequires: update-desktop-files
BuildRequires: hicolor-icon-theme
Requires(post): desktop-file-utils
Requires(postun): desktop-file-utils
%else
Requires(post): xdg-utils
Requires(postun): xdg-utils
%endif

Url:            https://github.com/raelgc/scudcloud/
Source:         %{name}-%{version}.tar.gz
Requires:       python3
Requires:       python3-qt4
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildArch:      noarch

%description
ScudCloud uses the QT library + Webkit to render the web version of Slack,
but using the QWebkit-Native bridge to improve desktop integration with:
* multiple teams support,
* native system notifications,
* count of unread direct mentions at launcher/sytray icon,
* alert/wobbling on new messages,
* channels quicklist (Unity only),
* optional "Close to Tray".

%prep
%setup -q

%install
INSTALL="/opt/scudcloud"
cd scudcloud-1.0

mkdir -p %{buildroot}/$INSTALL/lib
mkdir -p %{buildroot}/$INSTALL/resources
mkdir -p %{buildroot}%{_prefix}/bin
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
mkdir -p %{buildroot}%{_datadir}/icons/mono-dark/scalable/apps
mkdir -p %{buildroot}%{_datadir}/icons/mono-light/scalable/apps


install -m0644 lib/*.py %{buildroot}/$INSTALL/lib
install -m0644 resources/* %{buildroot}/$INSTALL/resources
install -m0755 scudcloud %{buildroot}/$INSTALL
install -m0644 LICENSE %{buildroot}/$INSTALL

install -m0644 systray/hicolor/* %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
install -m0644 systray/mono-dark/* %{buildroot}%{_datadir}/icons/mono-dark/scalable/apps
install -m0644 systray/mono-light/* %{buildroot}%{_datadir}/icons/mono-light/scalable/apps

%if 0%{!?suse_version}
install -m0644 scudcloud.desktop %{buildroot}%{_datadir}/applications
%endif

ln -sf $INSTALL/scudcloud %{buildroot}%{_bindir}/scudcloud

%if 0%{?suse_version}
%suse_update_desktop_file -i %{name} Network InstantMessaging
%else
desktop-file-install --dir %{buildroot}%{_datadir}/applications %{name}.desktop
%endif

%if (0%{?suse_version} || 0%{?fedora_version})
%fdupes %{buildroot}/%{_prefix}
%endif

%post
%if 0%{?suse_version}
%desktop_database_post
%icon_theme_cache_post
%else
xdg-icon-resource forceupdate --theme hicolor 2> /dev/null || :
xdg-icon-resource forceupdate --theme mono-dark 2> /dev/null || :
xdg-icon-resource forceupdate --theme mono-light 2> /dev/null || :
xdg-desktop-menu forceupdate 2> /dev/null || :
%endif


%postun
%if 0%{?suse_version}
%desktop_database_postun
%icon_theme_cache_postun
%else
if [ $1 -eq 0 ] ; then
xdg-icon-resource forceupdate --theme hicolor 2> /dev/null || :
xdg-icon-resource forceupdate --theme mono-dark 2> /dev/null || :
xdg-icon-resource forceupdate --theme mono-light 2> /dev/null || :
xdg-desktop-menu forceupdate 2> /dev/null || :
fi
%endif


%files
%defattr(-,root,root)
%dir /opt/scudcloud
%dir %{_datadir}/icons/hicolor
%dir %{_datadir}/icons/hicolor/scalable
%dir %{_datadir}/icons/hicolor/scalable/apps
%dir %{_datadir}/icons/mono-dark
%dir %{_datadir}/icons/mono-dark/scalable
%dir %{_datadir}/icons/mono-dark/scalable/apps
%dir %{_datadir}/icons/mono-light
%dir %{_datadir}/icons/mono-light/scalable
%dir %{_datadir}/icons/mono-light/scalable/apps
/opt/scudcloud/*
%{_datadir}/applications/scudcloud.desktop
%{_datadir}/icons/hicolor/scalable/apps/*
%{_datadir}/icons/mono-dark/scalable/apps/*
%{_datadir}/icons/mono-light/scalable/apps/*
%{_bindir}/scudcloud

%changelog
* Mon Aug 10 2015 Marcin Bajor <marcin.bajor@gmail.com>
- Now build for CentOS, Red Hat Enterprise Linux, openSUSE, SUSE Linux Enterprise Server and others is possible
* Mon May 18 2015 Marcin Trendota <moonwolf@poczta.onet.pl>
- First version