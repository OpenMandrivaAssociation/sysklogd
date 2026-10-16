Name:		sysklogd
Version:	2.8.0
Release:	1
Summary:	System logging daemon
License:	BSD-3-Clause
Group:		System/Kernel and hardware
URL:		https://github.com/troglobit/sysklogd
Source0:	https://github.com/troglobit/sysklogd/releases/download/v%{version}/%{name}-%{version}.tar.gz
Provides:	syslog-daemon
Recommends:	logrotate
BuildSystem:	autotools
# util-linux owns /usr/bin/logger; upstream's logger is not CLI-compatible.
BuildOption:	--without-logger
BuildRequires:	pkgconfig(systemd)

%description
sysklogd is the syslog daemon. This is the troglobit continuation of the
classic BSD syslogd: one daemon reads kernel messages (no separate klogd),
speaks RFC3164 and RFC5424, and is socket-activated by systemd's
syslog.socket. libsyslog provides the matching syslogp() API.

%install -a
install -D -m 644 syslog.conf %{buildroot}%{_sysconfdir}/syslog.conf

install -d %{buildroot}%{_sysconfdir}/default
cat > %{buildroot}%{_sysconfdir}/default/syslogd <<'EOF'
# Extra options for syslogd. See syslogd(8).
# syslog.conf already sets "secure_mode 1" (do not listen on UDP/514).
SYSLOGD_OPTS=
EOF

install -d %{buildroot}%{_sysconfdir}/logrotate.d
cat > %{buildroot}%{_sysconfdir}/logrotate.d/syslog <<'EOF'
/var/log/auth.log
/var/log/syslog
/var/log/kern.log
/var/log/mail.log
/var/log/mail.err
/var/log/messages
{
	rotate 4
	weekly
	missingok
	notifempty
	compress
	delaycompress
	sharedscripts
	postrotate
		/usr/bin/systemctl reload syslogd.service >/dev/null 2>&1 || true
	endscript
}
EOF

# Static enable. File triggers reload systemd; presets are not applied
# without a scriptlet, and %systemd_post is obsolete here.
install -d %{buildroot}%{_unitdir}/multi-user.target.wants
ln -s ../syslogd.service %{buildroot}%{_unitdir}/multi-user.target.wants/syslogd.service
# syslog.socket activates syslog.service, not syslogd.service.
ln -s syslogd.service %{buildroot}%{_unitdir}/syslog.service

install -d %{buildroot}%{_presetdir}
cat > %{buildroot}%{_presetdir}/86-sysklogd.preset <<'EOF'
enable syslogd.service
EOF

rm -f %{buildroot}%{_libdir}/libsyslog.la

%files
%license %{_docdir}/%{name}/LICENSE
%doc %{_docdir}/%{name}/README.md
%doc %{_docdir}/%{name}/ChangeLog.md
%doc %{_docdir}/%{name}/syslog.conf
%doc %{_docdir}/%{name}/example
%config(noreplace) %{_sysconfdir}/syslog.conf
%config(noreplace) %{_sysconfdir}/default/syslogd
%config(noreplace) %{_sysconfdir}/logrotate.d/syslog
%{_sbindir}/syslogd
%{_unitdir}/syslogd.service
%{_unitdir}/syslog.service
%{_unitdir}/multi-user.target.wants/syslogd.service
%{_presetdir}/86-sysklogd.preset
%{_libdir}/libsyslog.so.*
%{_libdir}/libsyslog.so
%{_libdir}/pkgconfig/libsyslog.pc
%dir %{_includedir}/syslog
%{_includedir}/syslog/syslog.h
%{_mandir}/man3/syslogp.3*
%{_mandir}/man5/syslog.conf.5*
%{_mandir}/man8/syslogd.8*
