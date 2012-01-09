Name:           emptySpec
Version: 0
Release: 0
License: GPLv2
Summary: empty
Url: empty
Group: empty
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
Source: emptyFile

%description

%prep

%build

%install
echo "emptySpec is used only to create the chroot" > README.emptySpec

%clean
%{?buildroot:%__rm -rf "%{buildroot}"}

%post

%postun

%files
%defattr(-,root,root)
%doc README.emptySpec

%changelog

