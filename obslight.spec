%define name obslight
%define version 0.3
%define unmangled_version 0.3
%define release 1

Summary: OBS Light
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: GPLv2
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Ronan Le Martret <ronan@fridu.net>
Url: http://wiki.meego.com/OBS_Light
BuildRequires: osc
BuildRequires: python-xml
Requires: meego-packaging-tools
Requires: python-xml
Requires: sudo
Requires: qemu
%{!?python_sitelib: %define python_sitelib %(python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%description
Command-line client and UI for the OBS.

%prep
%setup -n %{name}-%{unmangled_version}

%build
python setup.py build

%install
python setup.py install -O1 --root=%{buildroot} --prefix=%{_prefix}
ln -s obslight-wrapper.py %{buildroot}/%{_bindir}/obslight
ln -s obslightgui-wrapper.py %{buildroot}/%{_bindir}/obslight-gui
echo "%users ALL=(ALL)NOPASSWD:/usr/bin/build" >> /etc/sudoers
echo "%users ALL=(ALL)NOPASSWD:/usr/bin/mic-chroot" >> /etc/sudoers

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc AUTHORS README TODO NEWS
%{_bindir}/obslight*
%{python_sitelib}/*
