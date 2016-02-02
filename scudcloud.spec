#
# spec file for package scudcloud
#
# Copyright (c) 2015 Marcin Trendota (moonwolf@poczta.onet.pl)
# Copyright (c) 2016 Marcin Bajor (marcin.bajor@gmail.com)
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
Version:        1.2
Release:        1%{?dist}
Summary:        Non official desktop client for Slack©
License:        MIT
Group:          Applications/Internet
BuildRequires:  python3
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools

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
%if 0%{?suse_version}
Requires:       google-lato-fonts
Requires:       dbus-1-python3
%else
Requires:       lato-fonts
Requires:       python3-dbus
%endif
Suggests:       libqt4-webkit-qupzillaplugins
Suggests:       python3-hunspell
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
%build

%install

/usr/bin/python3 setup.py install --prefix=%{_prefix} --root=%{buildroot}

%if (0%{?suse_version} || 0%{?sles_version})
%suse_update_desktop_file -r -i %{name} Network InstantMessaging
%endif

%if (0%{?suse_version} || 0%{?fedora_version})
%fdupes %{buildroot}/%{_datadir}
%endif

%post

%if (0%{?suse_version} || 0%{?sles_version})
%desktop_database_post
%icon_theme_cache_post
%else
/usr/bin/update-desktop-database &> /dev/null || :
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
%endif


%postun

%if (0%{?suse_version} || 0%{?sles_version})
%desktop_database_postun
%icon_theme_cache_postun
%else
/usr/bin/update-desktop-database &> /dev/null || :
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi
%endif


%posttrans

%if !(0%{?suse_version} || 0%{?sles_version})
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
%endif

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%{python3_sitelib}/*
%{_bindir}/*
%dir %{_datadir}/doc/%{name}
%{_datadir}/doc/%{name}/*
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/*/apps/*
%dir %{_datadir}/icons/ubuntu-mono-dark/
%dir %{_datadir}/icons/ubuntu-mono-dark/scalable
%dir %{_datadir}/icons/ubuntu-mono-dark/scalable/apps
%dir %{_datadir}/icons/ubuntu-mono-light/
%dir %{_datadir}/icons/ubuntu-mono-light/scalable
%dir %{_datadir}/icons/ubuntu-mono-light/scalable/apps
%{_datadir}/icons/ubuntu-mono-dark/*/apps/*
%{_datadir}/icons/ubuntu-mono-light/*/apps/*
%{_datadir}/pixmaps/%{name}.png

%changelog
* Sat Jan 26 2016 Marcin Bajor <marcin.bajor@gmail.com>
- Fixed python3-dbus dependency for Fedora
* Sat Jan 23 2016 Marcin Bajor <marcin.bajor@gmail.com>
- Python package management update
* Mon Dec  7 2015 Marcin Bajor <marcin.bajor@gmail.com>
- Added VERSION file to rpm package
* Sat Sep 26 2015 Marcin Bajor <marcin.bajor@gmail.com>
- Added dependencies: libqt4-webkit-qupzillaplugins and python3-hunspell
* Mon Sep 21 2015 Marcin Trendota <moonwolf@poczta.onet.pl>
- Add lato-fonts dependency
* Mon Aug 10 2015 Marcin Bajor <marcin.bajor@gmail.com>
- Now build for CentOS, Red Hat Enterprise Linux, openSUSE, SUSE Linux Enterprise Server and others is possible
* Mon May 18 2015 Marcin Trendota <moonwolf@poczta.onet.pl>
- First version
