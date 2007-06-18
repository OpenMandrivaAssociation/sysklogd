Name:		sysklogd
Version:	1.4.1
Release: 	%mkrel 13
Summary:	System logging and kernel message trapping daemons
License:	GPL
Group:		System/Kernel and hardware 
URL:		http://www.infodrom.org/projects/sysklogd/
Source0		ftp://sunsite.unc.edu/pub/Linux/system/daemons/%{name}-%{version}rh.tar.bz2
Source1:	sysklogd.conf
Source2:	sysklogd.logrotate
Patch1: 	sysklogd-1.4rh-do_not_use_initlog_when_restarting.patch
Patch2:		sysklogd-1.4.1-owl-syslogd-crunch_list.diff
Patch3:		sysklogd-1.4.1rh-pinit.patch
Patch4:		sysklogd-1.4.1-siginterrupt.patch
Patch5:		sysklogd-1.4.1-noforward_local_address.patch
Patch6:		sysklogd-1.4.1-preserve_percents.patch
Patch7:		sysklogd-1.4.1-no_io_in_sighandlers.patch
Patch8:		sysklogd-1.4.1-fix_mark.patch
Patch9:		sysklogd-1.4.1-reload.patch
Patch10:	sysklogd-1.4.1-umask.diff
Patch11:	sysklogd-1.4.1-disable__syslog_chk.patch
Patch12:	sysklogd-1.4.1-fix_race.patch
Requires:	logrotate >= 3.3-8mdk
Requires:	bash >= 2.0
Requires(pre):	fileutils
Requires(pre):	/sbin/chkconfig
Requires(pre):	initscripts >= 5.60
Requires(post):	    rpm-helper
Requires(preun):	rpm-helper
Provides:	syslog-daemon
Conflicts:  logrotate <= 3.7.5-2mdv
BuildRoot:	%{_tmppath}/%{name}-%{version}

%description
The sysklogd package contains two system utilities (syslogd and klogd)
which provide support for system logging.  Syslogd and klogd run as
daemons (background processes) and log system messages to different
places, like sendmail logs, security logs, error logs, etc.

%prep
%setup -q -n %{name}-%{version}rh
%patch1 -p1 -b .initlog
%patch2 -p1 -b .sec
%patch3 -p1 -b .pinit
%patch4 -p1 -b .siginterrupt
%patch5 -p1 -b .noforward_local_address
%patch6 -p1 -b .preserve_percents
%patch7 -p1 -b .no_io_in_sighandlers
%patch8 -p1 -b .fix_mark
%patch9 -p1 -b .reload
%patch10 -p1 -b .umask
%patch11 -p1 -b .disable__syslog_chk
%patch12 -p1 -b .race

%build
%serverbuild
%make

%install
rm -rf %{buildroot}

install -d -m 755 %{buildroot}{/sbin,%{_bindir},%{_mandir}/man{5,8}}

make install TOPDIR=%{buildroot} MANDIR=%{buildroot}%{_mandir} \
	MAN_OWNER=`id -nu`

install -d -m 755 %{buildroot}%{_sysconfdir}
install -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/syslog.conf

install -d -m 755 %{buildroot}%{_initrddir}
install -m 755 redhat/syslog.init %{buildroot}%{_initrddir}/syslog
install -d -m 755 %{buildroot}%{_sysconfdir}/sysconfig
install -m 644 redhat/syslog %{buildroot}%{_sysconfdir}/sysconfig/syslog

install -d -m 755 %{buildroot}%{_sbindir}
chmod 755 %{buildroot}/sbin/syslogd
chmod 755 %{buildroot}/sbin/klogd

install -d -m 755 %{buildroot}%{_sysconfdir}/logrotate.d
install -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/syslog

%pre
# Because RPM do not know the difference about a file or a directory,
# We need to verify if there is no file with the same name as the directory
# we want to create for the new logdir architecture.
# If the name is the same and it is a file, rename it to name.old
for file in mail cron kernel lpr news daemons; do
	if [ -f /var/log/$file ]; then 
		mv -f /var/log/$file /var/log/$file.old \
		&& mkdir /var/log/$file && mv /var/log/$file.old /var/log/$file/$file.old  
	fi
done

%post
# Create each log directory with logfiles : info, warnings, errors :
for dir in /var/log/{mail,cron,kernel,lpr,news,daemons}; do
    [ -d $dir ] || mkdir ${dir}
    for file in $dir/{info,warnings,errors}; do
        [ -f $file ] || touch $file && chmod 600 $file
    done
done

# Create standard logfiles if they do not exist:
for file in \
 /var/log/{auth.log,syslog,user.log,messages,secure,spooler,boot.log,explanations};
do
    [ -f $file ] || touch $file && chmod 600 $file
done

%_post_service syslog

%preun
%_preun_service syslog

%postun
if [ "$1" -ge "1" ]; then
	service syslog condrestart > /dev/null 2>&1
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
/sbin/*
%{_mandir}/*/*


