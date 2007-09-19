Name:		sysklogd
Version:	1.4.2
Release: 	%mkrel 4
Summary:	System logging and kernel message trapping daemons
License:	GPL
Group:		System/Kernel and hardware 
URL:        http://download.fedora.redhat.com/pub/fedora/linux/core/development/source/SRPMS/
Source0:	%{name}-%{version}rh.tar.gz
Source1:	sysklogd.conf
Source2:	sysklogd.logrotate
Source3:	sysklogd.init
Source4:	sysklogd.sysconfig
Source5:        sbin.klogd.apparmor
Source6:        sbin.syslogd.apparmor
Patch1: 	sysklogd-1.4rh-do_not_use_initlog_when_restarting.patch
Patch2:     sysklogd-1.4.2rh.timezone.patch
Patch3:     sysklogd-1.4.2rh-includeFacPri.patch
Patch4:     sysklogd-1.4.2rh-dispatcher.patch
Patch5:     sysklogd-1.4.2rh-startFailed.patch
Patch6:     sysklogd-1.4.2rh-reload.patch
Requires:	logrotate >= 3.3-8mdk
Requires:	bash >= 2.0
Requires(pre):	coreutils
Requires(pre):	chkconfig
Requires(pre):	initscripts >= 5.60
Requires(post):	    rpm-helper
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
%setup -q -n %{name}-%{version}rh
%patch1 -p1 -b .initlog
%patch2 -p1 -b .timezone
%patch3 -p1 -b .includeFacPri
%patch4 -p1 -b .dispatcher
%patch5 -p1 -b .startFailed
%patch6 -p1 -b .reload

%build
%serverbuild
%make

%install
rm -rf %{buildroot}

install -d -m 755 %{buildroot}/sbin
install -d -m 755 %{buildroot}%{_bindir}
install -d -m 755 %{buildroot}%{_mandir}/man{5,8}
install -d -m 755 %{buildroot}%{_includedir}/%{name}

make install TOPDIR=%{buildroot} MANDIR=%{buildroot}%{_mandir} \
	MAN_OWNER=`id -nu`

install -d -m 755 %{buildroot}%{_sysconfdir}
install -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/syslog.conf

# init script
install -d -m 755 %{buildroot}%{_initrddir}
install -m 755 %{SOURCE3} %{buildroot}%{_initrddir}/syslog
install -d -m 755 %{buildroot}%{_sysconfdir}/sysconfig
install -m 644 %{SOURCE4} %{buildroot}%{_sysconfdir}/sysconfig/syslog

install -d -m 755 %{buildroot}%{_sbindir}
chmod 755 %{buildroot}/sbin/syslogd
chmod 755 %{buildroot}/sbin/klogd

install -d -m 755 %{buildroot}%{_sysconfdir}/logrotate.d
install -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/syslog

# apparmor profiles
mkdir -p %{buildroot}%{_sysconfdir}/apparmor.d
install -m 0644 %{SOURCE5} %{buildroot}%{_sysconfdir}/apparmor.d/sbin.klogd
install -m 0644 %{SOURCE6} %{buildroot}%{_sysconfdir}/apparmor.d/sbin.syslogd

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
/sbin/*
%{_mandir}/*/*
%{_includedir}/%{name}
