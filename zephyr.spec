Name:		zephyr
Version:	3.0.2
Release:	1%{?dist}
Summary:	Project Athena's notification service

License:	MIT
URL:		http://zephyr.1ts.org/
Source0:	http://zephyr.1ts.org/files/zephyr-%{version}.tar.gz
Source1:	zhm.service

BuildRequires:	krb5-devel
BuildRequires:	readline-devel
BuildRequires:	libss-devel
BuildRequires:	hesiod-devel
BuildRequires:	libcom_err-devel
BuildRequires:	bison
BuildRequires:	libX11-devel
BuildRequires:	libXt-devel
BuildRequires:	xorg-x11-proto-devel
BuildRequires:	ncurses-devel
BuildRequires:	c-ares-devel
BuildRequires:	systemd-units
Requires:	zephyr-lib%{?_isa} = %{version}-%{release}

# Enable a hardened build, a bunch of processes are long-lived
# services (zhm, zephyrd, zwgc)
%global _hardened_build 1

%description
Zephyr is derived from the original Project Athena 'Instant Message'
system and allows users to send messages to other users or to groups
of users.  Users can view incoming Zephyr messages as windowgrams
(transient X windows) or as text on a terminal.


%package -n libzephyr4-krb5
Summary:	Zephyr libraries with Kerberos 5 support
Provides:	zephyr-lib%{?_isa} = %{version}-%{release}
Requires(post): %{_sbindir}/update-alternatives
Requires(postun): %{_sbindir}/update-alternatives


%description -n libzephyr4-krb5
TODO


%package -n libzephyr4-krb5-devel
Summary:	Zephyr libraries with Kerberos 5 support (development)
Requires:	libzephyr4-krb5%{?_isa} = %{version}-%{release}
Provides:	libzephyr4-krb5-static = %{version}-%{release}


%description -n libzephyr4-krb5-devel
TODO


%package server-krb5
Summary:	Zephyr server with Kerberos 5 support
Requires:	libzephyr4-krb5%{?_isa} = %{version}-%{release}
Requires(post): %{_sbindir}/update-alternatives
Requires(postun): %{_sbindir}/update-alternatives


%description server-krb5
TODO

%package -n libzephyr4
Summary:	Zephyr libraries
Provides:	zephyr-lib%{?_isa} = %{version}-%{release}
Requires(post): %{_sbindir}/update-alternatives
Requires(postun): %{_sbindir}/update-alternatives


%description -n libzephyr4
TODO


%package -n libzephyr4-devel
Summary:	Zephyr libraries (development)
Requires:	libzephyr4%{?_isa} = %{version}-%{release}
Provides:	libzephyr4-static = %{version}-%{release}


%description -n libzephyr4-devel
TODO


%package server
Summary:	Zephyr server
Requires:	libzephyr4%{?_isa} = %{version}-%{release}
Requires(post): %{_sbindir}/update-alternatives
Requires(postun): %{_sbindir}/update-alternatives


%description server
TODO


%prep
%setup -q
cp -p %{SOURCE1} .


%build
%define _configure ../configure

for type in base krb5; do
	if [ "$type" = "base" ]; then
		libname=zephyr
		extra_configure=""
	else
		libname=zephyr-${type}
		extra_configure="--with-${type}"
	fi
	mkdir -p %{_arch}_${type}

	pushd %{_arch}_${type}

	# Set datadir to sysconfdir so configuration files end up in
	# the right place.
	%configure --datadir=%{_sysconfdir} \
		   --libdir=%{_libdir}/$libname \
		   --with-hesiod --with-ss --with-cares \
		   --enable-cmu-zwgcplus $extra_configure
	# Make sure libtool doesn't do rpath
	sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
	sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

	make %{?_smp_mflags}
	popd
done

%install
rm -rf %{buildroot}
for type in krb5 base; do
	pushd %{_arch}_${type}
	%make_install
	mkdir -p %{buildroot}/%{_datadir}/zephyr/
	if [ "$type" = "base" ]; then
		binname=zephyr
		echo "%{_libdir}/$binname" \
		> %{buildroot}/%{_datadir}/zephyr/zephyr-%{_arch}.conf
	else
		binname=zephyr-$type
		echo "%{_libdir}/$binname" \
		> %{buildroot}/%{_datadir}/zephyr/zephyr-%{_arch}-${type}.conf
	fi
	mv %{buildroot}/%{_sbindir}/zephyrd %{buildroot}/%{_sbindir}/zephyrd.${binname}
	popd
done
touch %{buildroot}/%{_sbindir}/zephyrd

install -Dpm 644 zhm.service %{buildroot}/%{_unitdir}/zhm.service

# Remove the .la files that somehow got installed
find %{buildroot} -name '*.la' -delete

# Make RPM's Provide: searcher actually search the .so files! A recent
# change in how RPM detects Provides automatically means that only
# files that are executable get searched. Without this hack, all of
# the zephyr client tools are Requires: libzephyr.so.4 which is never
# Provides:, leading to uninstallable RPMS. This can be removed when
# zephyr starts installing the libraries with mode 755 rather than
# 644. (Zephyr #79)
find %{buildroot}%{_libdir} -name 'libzephyr.so.*' -exec chmod a+x {} ';'


%files
%doc README USING
%{_bindir}/zaway
%{_bindir}/zctl
%{_bindir}/zleave
%{_bindir}/zlocate
%{_bindir}/znol
%{_bindir}/zstat
%{_bindir}/zwgc
%{_bindir}/zwrite
%{_sbindir}/zhm
%{_sbindir}/zshutdown_notify
%{_mandir}/man1/zaway.1.gz
%{_mandir}/man1/zctl.1.gz
%{_mandir}/man1/zephyr.1.gz
%{_mandir}/man1/zleave.1.gz
%{_mandir}/man1/zlocate.1.gz
%{_mandir}/man1/znol.1.gz
%{_mandir}/man1/zwgc.1.gz
%{_mandir}/man1/zwrite.1.gz
%{_mandir}/man8/zhm.8.gz
%{_mandir}/man8/zstat.8.gz
%{_mandir}/man8/zshutdown_notify.8.gz
%{_unitdir}/zhm.service
%dir %{_sysconfdir}/zephyr
%dir %{_sysconfdir}/zephyr/acl
%config(noreplace) %{_sysconfdir}/zephyr/default.subscriptions
%config(noreplace) %{_sysconfdir}/zephyr/zwgc.desc
%config(noreplace) %{_sysconfdir}/zephyr/zwgc_resources


%files -n libzephyr4-krb5
%doc
%{_libdir}/zephyr-krb5/libzephyr.so.4
%{_libdir}/zephyr-krb5/libzephyr.so.4.0.0
%{_datadir}/zephyr/zephyr-%{_arch}-krb5.conf
%attr(0644, root, root) %ghost /etc/ld.so.conf.d/zephyr-%{_arch}.conf


%files -n libzephyr4-krb5-devel
%doc
%{_libdir}/zephyr-krb5/libzephyr.so
%{_libdir}/zephyr-krb5/libzephyr.a
%{_includedir}/zephyr


%files server-krb5
%doc OPERATING
%{_sbindir}/zephyrd.zephyr-krb5
%{_mandir}/man8/zephyrd.8.gz
%attr(0755, root, root) %ghost %{_sbindir}/zephyrd

%files -n libzephyr4
%doc
%{_libdir}/zephyr/libzephyr.so.4
%{_libdir}/zephyr/libzephyr.so.4.0.0
%{_datadir}/zephyr/zephyr-%{_arch}.conf
%attr(0644, root, root) %ghost /etc/ld.so.conf.d/zephyr-%{_arch}.conf


%files -n libzephyr4-devel
%doc
%{_libdir}/zephyr/libzephyr.so
%{_libdir}/zephyr/libzephyr.a
%{_includedir}/zephyr


%files server
%doc OPERATING
%{_sbindir}/zephyrd.zephyr
%{_mandir}/man8/zephyrd.8.gz
%attr(0755, root, root) %ghost %{_sbindir}/zephyrd


%post -n libzephyr4-krb5
%{_sbindir}/update-alternatives --install /etc/ld.so.conf.d/zephyr-%{_arch}.conf \
				libzephyr-%{_arch} \
				%{_datadir}/zephyr/zephyr-%{_arch}-krb5.conf 50
/sbin/ldconfig


%postun -n libzephyr4-krb5
if [ $1 -eq 0 ] ; then
	%{_sbindir}/update-alternatives --remove libzephyr-%{_arch} \
	%{_datadir}/zephyr/zephyr-%{_arch}-krb5.conf
fi
/sbin/ldconfig


%post -n libzephyr4
%{_sbindir}/update-alternatives --install /etc/ld.so.conf.d/zephyr-%{_arch}.conf \
				libzephyr-%{_arch} \
				%{_datadir}/zephyr/zephyr-%{_arch}.conf 10
/sbin/ldconfig


%postun -n libzephyr4
if [ $1 -eq 0 ] ; then
	%{_sbindir}/update-alternatives --remove libzephyr-%{_arch} \
	%{_datadir}/zephyr/zephyr-%{_arch}.conf
fi
/sbin/ldconfig


%post server-krb5
%{_sbindir}/update-alternatives --install %{_sbindir}/zephyrd \
				zephyrd %{_sbindir}/zephyrd.zephyr-krb5 50


%postun server-krb5
if [ $1 -eq 0 ] ; then
	%{_sbindir}/update-alternatives --remove zephyrd %{_sbindir}/zephyrd.zephyr-krb5
fi


%post server
%{_sbindir}/update-alternatives --install %{_sbindir}/zephyrd \
				zephyrd %{_sbindir}/zephyrd.zephyr 10


%postun server
if [ $1 -eq 0 ] ; then
	%{_sbindir}/update-alternatives --remove zephyrd %{_sbindir}/zephyrd.zephyr
fi


%changelog
* Wed Mar 13 2013 Alexander Chernyakhovsky <achernya@mit.edu> - 3.0.2-1
- Initial packaging for zephyr

