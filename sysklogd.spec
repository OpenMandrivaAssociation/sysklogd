Name:		sysklogd
Version:	1.5
Release: 	%mkrel 3
Summary:	System logging and kernel message trapping daemons
License:	GPLv2
Group:		System/Kernel and hardware
URL:        http://download.fedora.redhat.com/pub/fedora/linux/core/development/source/SRPMS/
Source0:	%{name}-%{version}.tar.gz
Source1:	sysklogd.conf
Source2:	sysklogd.logrotate
Source3:	sysklogd.init
Source4:	sysklogd.sysconfig
Source5:        sbin.klogd.apparmor
Source6:        sbin.syslogd.apparmor
Patch1: sysklogd-1.5-empty-debuginfo.patch
Requires:	logrotate >= 3.3-8mdk
Requires:	bash >= 2.0
Requires(pre):	coreutils
Requires(pre):	chkconfig
Requires(pre):	initscripts >= 5.60
Requires(post):	    rpm-helper
Requires(post): chkconfig >= 1.3.37-3mdv
Requires(preun):	rpm-helper
Provides:	syslog-daemon
Conflicts:  logrotate <= 3.7.5-2mdv
Conflicts:      apparmor-profiles < 2.1-1.961.5mdv2008.0
BuildRoot:	%{_tmppath}/%{name}-%{version}

%description
The sysklogd package contains two system utilities (syslogd and klogd)
which provide support for system logging.  Syslogd and klogd run as
daemons (background processes) and log system messages to different
places, like sendmail logs, security logs, error logs, etc.

%prep
%setup -q -n %{name}-%{version}
%patch1 -p1

%build
%serverbuild
%make

%install
rm -rf %{buildroot}

install -d -m 755 %{buildroot}/sbin
install -d -m 755 %{buildroot}%{_bindir}
install -d -m 755 %{buildroot}%{_sbindir}
install -d -m 755 %{buildroot}%{_mandir}/man{5,8}
install -d -m 755 %{buildroot}%{_includedir}/%{name}

make install prefix=%{buildroot} TOPDIR=%{buildroot} MANDIR=%{buildroot}%{_mandir} \
	BINDIR=%{buildroot}%{_sbindir} MAN_USER=`id -nu` MAN_GROUP=`id -ng`


install -d -m 755 %{buildroot}%{_sysconfdir}
install -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/syslog.conf

# init script
install -d -m 755 %{buildroot}%{_initrddir}
install -m 755 %{SOURCE3} %{buildroot}%{_initrddir}/syslog
install -d -m 755 %{buildroot}%{_sysconfdir}/sysconfig
install -m 644 %{SOURCE4} %{buildroot}%{_sysconfdir}/sysconfig/syslog

install -d -m 755 %{buildroot}%{_sbindir}
chmod 755 %{buildroot}/%{_sbindir}/syslogd
chmod 755 %{buildroot}/%{_sbindir}/klogd

install -d -m 755 %{buildroot}%{_sysconfdir}/logrotate.d
install -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/syslog

# apparmor profiles
mkdir -p %{buildroot}%{_sysconfdir}/apparmor.d
install -m 0644 %{SOURCE5} %{buildroot}%{_sysconfdir}/apparmor.d/sbin.klogd
install -m 0644 %{SOURCE6} %{buildroot}%{_sysconfdir}/apparmor.d/sbin.syslogd

#do symlinks for compatibility
ln -sf /usr/sbin/syslogd %{buildroot}/sbin/syslogd
ln -sf /usr/sbin/klogd %{buildroot}/sbin/klogd

%post
# create all configured file if they don't already exist
for file in /var/log/{{auth,user,boot,drakxtools}.log,syslog,messages}; do
    [ -f $file ] || touch $file
done

for dir in /var/log/{mail,cron,kernel,daemons}; do
    [ -d $dir ] || mkdir $dir
    for file in $dir/{info,warnings,errors}.log; do
        [ -f $file ] || touch $file
    done
done

%_post_service syslog

%preun
%_preun_service syslog

%postun
if [ "$1" -ge "1" ]; then
	service syslog condrestart > /dev/null 2>&1
fi

%posttrans
# if we have apparmor installed, reload if it's being used
if [ -x /sbin/apparmor_parser ]; then
        /sbin/service apparmor condreload
fi

%triggerpostun -- sysklogd < 1.5-3mdv 
/sbin/chkconfig --level 7 syslog reset

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc ANNOUNCE README* NEWS INSTALL
%{_initrddir}/syslog
%config(noreplace) %{_sysconfdir}/syslog.conf
%config(noreplace) %{_sysconfdir}/sysconfig/syslog
%config(noreplace) %{_sysconfdir}/logrotate.d/syslog
%config(noreplace) %{_sysconfdir}/apparmor.d/sbin.klogd
%config(noreplace) %{_sysconfdir}/apparmor.d/sbin.syslogd
%{_sbindir}/*
/sbin/*
%{_mandir}/*/*
%{_includedir}/%{name}
