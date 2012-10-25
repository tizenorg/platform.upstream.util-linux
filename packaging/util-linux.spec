%define time_ver 1.7
%define which_ver 2.20
%define adjtimex_ver 1.29

Name:           util-linux
BuildRequires:  binutils-devel
BuildRequires:  fdupes
BuildRequires:  gettext-devel
BuildRequires:  libtool
BuildRequires:  ncurses-devel
BuildRequires:  pam-devel
BuildRequires:  pkg-config
BuildRequires:  readline-devel
BuildRequires:  zlib-devel
Version:        2.22.1
Release:        0
# util-linux is a base package and uuidd pre-requiring pwdutils pulls
# that into the core build cycle.  pwdutils also pulls in the whole
# ldap stack into it.  Avoid this whole mess which is done only to
# make the rpm install check of uuidd happy which has support to work without
# these tools as well
#!BuildIgnore:  pwdutils
Url:            http://kernel.org/~kzak/util-linux/
Provides:       fsck-with-dev-lock = %{version}
# bnc#651598:
Provides:       util-linux(fake+no-canonicalize)
Summary:        A collection of basic system utilities
License:        GPL-2.0+
Group:          System/Base
Source:         ftp://ftp.kernel.org/pub/linux/utils/util-linux/v2.21/%{name}-%{version}.tar.gz
Source1:        util-linux-rpmlintrc
# XXX: make nologin part of util-linux upstream
Source2:        nologin.c
Source3:        nologin.8
Source6:        etc_filesystems
Source7:        baselibs.conf
Source8:        login.pamd
Source9:        remote.pamd
Source14:       su.pamd
Source15:       su.default
# TODO: split to separate package
Source10:       http://ftp.debian.org/debian/pool/main/a/adjtimex/adjtimex_%{adjtimex_ver}.orig.tar.gz
Source11:       klogconsole.tar.bz2
# TODO: split to separate package
Source12:       which-%{which_ver}.tar.bz2
# TODO: split to separate package
Source13:       time-%{time_ver}.tar.bz2
# XXX: needed?
Source22:       setctsid.c
Source23:       setctsid.8
# XXX: ppc specific, still needed?
Source28:       mkzimage_cmdline.8
Source29:       mkzimage_cmdline.c
Source31:       addnote.c
#
Source30:       README.largedisk
Source50:       uuidd.rc
Source51:       blkid.conf
##
## util-linux patches
##
# 241372 - remove legacy warnings from fdisk
Patch1:         util-linux-2.12r-fdisk_remove_bogus_warnings.patch
Patch2:         util-linux-2.20-libmount-deps.patch
Patch3:         fdisk-tinfo.patch
Patch4:         mount-new-allow-sloppy-for-non-root.patch
Patch5:         libmount-don-t-use-nosuid-noexec-nodev-for-cifs-user.patch

# Patches 6-10: bcn#767208 (taken from upstream
Patch6:         mount-new-improve-error-messages.patch
Patch7:         libmount-add-special-MNT_ERR-codes.patch
Patch8:         mount-new-use-MNT_ERR-for-error-messages.patch
Patch9:         libmount-add-MNT_ERR_LOOPDEV.patch
Patch10:        mount-new-add-loopdev-specific-error-message.patch

# disable encryption
Patch11:        util-linux-2.21.2-noenc.diff
Patch12:        util-linux-2.21.2-noenc-suse.diff

# hack for boot.localfs
Patch20:        util-linux-HACK-boot.localfs.diff
#####

##
## adjtimex
##
##
## klogconsole
##
Patch55:        klogconsole-quiet.patch
Patch56:        klogconsole.diff
##
## time
##
Patch60:        time-1.7.dif

BuildRoot:      %{_tmppath}/%{name}-%{version}-build
Requires(pre):         /usr/bin/sed
#
Provides:       base = %{version}-%{release}
Provides:       login = 4.0-33.7
Provides:       util = %{version}-%{release}
Provides:       uuid-runtime = %{version}-%{release}
Obsoletes:      base < %{version}-%{release}
Obsoletes:      login < 4.0-33.7
Obsoletes:      util < %{version}-%{release}
Obsoletes:      uuid-runtime < %{version}-%{release}

%description
This package contains a large variety of low-level system utilities
that are necessary for a Linux system to function. It contains the
mount program, the fdisk configuration tool, and more.

%package -n libblkid
Summary:        Filesystem detection library
Group:          System/Filesystems

%description -n libblkid
Library for filesystem detection.

%package -n libblkid-devel
Summary:        Development files for the filesystem detection library
Group:          Development/Libraries/C and C++
Requires:       libblkid = %{version}

%description -n libblkid-devel
Files needed to develop applications using the library for filesystem
detection.

%package -n uuidd
Summary:        Helper daemon to guarantee uniqueness of time-based UUIDs
Group:          System/Filesystems

%description -n uuidd
The uuidd package contains a userspace daemon (uuidd) which guarantees
uniqueness of time-based UUID generation even at very high rates on
SMP systems.

%package -n su
Summary:        Library to generate UUIDs
Group:          System/Filesystems

%description -n su
A library to generate universally unique IDs (UUIDs).

%package -n libuuid
Summary:        Library to generate UUIDs
Group:          System/Filesystems

%description -n libuuid
A library to generate universally unique IDs (UUIDs).

%package -n libuuid-devel
Summary:        Development files for libuuid1
Group:          Development/Libraries/C and C++
Requires:       libuuid = %{version}

%description -n libuuid-devel
Files to develop applications using the library to generate universally
unique IDs (UUIDs).

%package -n libmount
Summary:        Device mount library
Group:          System/Filesystems

%description -n libmount
Library designed to be used in low-level utils like
mount(8) and /usr/sbin/mount.<type> helpers.

%package -n libmount-devel
Summary:        Development files for libmount
Group:          Development/Libraries/C and C++
Requires:       libmount = %{version}

%description -n libmount-devel
Files to develop applications using the libmount library.

%prep
%setup -q -n %{name}-%{version} -a 10 -b 11 -b 12 -b 13
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1
%patch11 -p1
%patch12 -p1
#
%patch20 -p1

#
cd adjtimex-*
# adjtimex patches belongs here
cd -
# setctsid
cp %{S:22} %{S:23} .
# nologin
cp %{S:2} %{S:3}  %{S:30} .
cd ../klogconsole
%patch55 -p1
%patch56 -p1
cd ../time-*
%patch60

%build
# adjtimex build
cd adjtimex-%{adjtimex_ver}
%configure
make %{?_smp_mflags}
cd ..
pushd ../
# which build
cd which-%{which_ver}
%configure
make %{?_smp_mflags}
cd ..
# time build
cd time-%{time_ver}
export CFLAGS="%{optflags} -D_GNU_SOURCE "
export INSTALL_PROGRAM='$(INSTALL)'
%configure
make %{?_smp_mflags}
cd ..
# klogconsole build
cd klogconsole
make %{?_smp_mflags} CFLAGS="%{optflags}" CC="%{__cc}"
cd ..
popd
# setctsid build
rm -f setctsid
make %{?_smp_mflags} setctsid CFLAGS="%{optflags}" CC="%{__cc}"
#
# util-linux itself
#
autoreconf -fi
export SUID_CFLAGS="-fpie"
export SUID_LDFLAGS="-pie"
%configure \
  --enable-mesg \
  --enable-partx \
  --disable-kill \
  --enable-write \
  --enable-line \
  --enable-new-mount \
  --enable-ddate \
  --enable-login-utils \
  --disable-mountpoint \
  --disable-use-tty-group \
  --disable-static \
  --disable-silent-rules \
  --disable-rpath
#
make %{?_smp_mflags}
#
%{__cc} -fwhole-program %{optflags} -o nologin nologin.c
%{__cc} -fwhole-program %{optflags} -o mkzimage_cmdline %{S:29}
%{__cc} -fwhole-program %{optflags} -o chrp-addnote %{SOURCE31}

%install
mkdir -p %{buildroot}{/etc/init.d,/etc/pam.d,%{_mandir}/man{1,8},/usr/bin,/usr/sbin,%{_infodir}}
mkdir -p %{buildroot}%{_localstatedir}/lib/libuuid/
mkdir -p %{buildroot}%{_localstatedir}/run/uuidd/
install -m 744 %{SOURCE50} %{buildroot}%{_initddir}/uuidd
install -m 644 %{SOURCE51} %{buildroot}%{_sysconfdir}/blkid.conf
install -m 644 %{SOURCE8} %{buildroot}/etc/pam.d/login
install -m 644 %{SOURCE9} %{buildroot}/etc/pam.d/remote
install -m 644 %{SOURCE14} %{buildroot}/etc/pam.d/su
install -m 644 %{SOURCE14} %{buildroot}/etc/pam.d/su-l
install -d -m 755 %{buildroot}/etc/default
install -m 644 %{S:15} %{buildroot}/etc/default/su
cp adjtimex-*/adjtimex %{buildroot}/%{_sbindir}
cp adjtimex-*/adjtimex.8  %{buildroot}%{_mandir}/man8/
pushd ..
# which install
cd which-%{which_ver}
%make_install
cd ..
# time install
cd time-%{time_ver}
make install DESTDIR=%{buildroot} \
        prefix=%{buildroot}/usr \
        infodir=%{buildroot}%{_infodir} \
        mandir=%{buildroot}%{_mandir} \
        bindir=%{buildroot}%{_bindir}
cd ..
# klogconsole install
cd klogconsole
make install DEST=%{buildroot}
popd
#
# util-linux install
#
%make_install
install -m 644 %{SOURCE6} %{buildroot}%{_sysconfdir}/filesystems
install -m 755 nologin %{buildroot}/%{_sbindir}
rm -f %{buildroot}/%{_libdir}/libblkid.la
rm -f %{buildroot}/%{_libdir}/libuuid.la
rm -f %{buildroot}/%{_libdir}/libmount.la
install -m 755 mkzimage_cmdline %{buildroot}/%{_bindir}
install -m 644 %{S:28} %{buildroot}%{_mandir}/man8
install -m 755 chrp-addnote %{buildroot}/%{_bindir}
install -m 644 nologin.8 %{buildroot}%{_mandir}/man8
# setctsid install
install -m 755 setctsid   %{buildroot}/%{_sbindir}
install -m 444 setctsid.8 %{buildroot}%{_mandir}/man8/
echo -e "#! /bin/bash\n/sbin/blockdev --flushbufs \$1" > %{buildroot}%{_sbindir}/flushb
chmod 755 %{buildroot}%{_sbindir}/flushb
# Stupid hack so we don't have a tcsh dependency
chmod 644 %{buildroot}%{_datadir}/getopt/getopt*.tcsh
# Following files we don't want to package, so remove them
rm -f %{buildroot}%{_bindir}/pg
rm -f %{buildroot}%{_mandir}/man1/pg.1*
# Do not package these files to get rid of the perl dependency
rm -f %{buildroot}%{_bindir}/chkdupexe
rm -f %{buildroot}%{_mandir}/man1/chkdupexe.1
# we use this tools from pwdutils
rm -f %{buildroot}/%{_bindir}/{chfn,chsh,newgrp}
rm -f %{buildroot}/%{_sbindir}/{vigr,vipw}
rm -f %{buildroot}/%{_mandir}/man1/{chfn.1*,chsh.1*,newgrp.1*}
rm -f %{buildroot}/%{_mandir}/man8/{vigr.8*,vipw.8*}



%find_lang %{name} %{name}.lang
# create list of setarch(8) symlinks
find  %{buildroot}%{_bindir}/ -regextype posix-egrep -type l \
  -regex ".*(linux32|linux64|s390|s390x|i386|ppc|ppc64|ppc32|sparc|sparc64|sparc32|sparc32bash|mips|mips64|mips32|ia64|x86_64|parisc|parisc32|parisc64)$" \
  -printf "%{_bindir}/%f\n" >> %{name}.files
find  %{buildroot}%{_mandir}/man8 -regextype posix-egrep  \
  -regex ".*(linux32|linux64|s390|s390x|i386|ppc|ppc64|ppc32|sparc|sparc64|sparc32|sparc32bash|mips|mips64|mips32|ia64|x86_64|parisc|parisc32|parisc64)\.8.*" \
  -printf "%{_mandir}/man8/%f*\n" >> %{name}.files
# clock.txt from uuidd is a ghost file
touch %{buildroot}%{_localstatedir}/lib/libuuid/clock.txt
# rcuuidd helper

rm -rf %{buildroot}/%{_mandir}/ru

# remove duplicate manpages
%fdupes -s %{buildroot}/%{_mandir}


%post -n libblkid -p /sbin/ldconfig

%postun -n libblkid -p /sbin/ldconfig

%post -n libmount -p /sbin/ldconfig

%postun -n libmount -p /sbin/ldconfig

%post -n libuuid -p /sbin/ldconfig

%postun -n libuuid -p /sbin/ldconfig

%lang_package

%docs_package

%files -n su
%{_bindir}/su
%config(noreplace) /etc/pam.d/su
%config(noreplace) /etc/pam.d/su-l
%config(noreplace) /etc/default/su

%files -f %{name}.files 
# Common files for all archs
%defattr(-,root,root)
%config(noreplace) %{_sysconfdir}/filesystems
%config(noreplace) %{_sysconfdir}/blkid.conf
%config(noreplace) /etc/pam.d/login
%config(noreplace) /etc/pam.d/remote
%{_bindir}/cal
%{_bindir}/eject
#%{_bindir}/kill
%{_bindir}/lslocks
%{_bindir}/utmpdump
%{_bindir}/wdctl
%{_sbindir}/resizepart
%{_sbindir}/sulogin
%{_bindir}/login
%{_bindir}/chrt
%{_bindir}/col
%{_bindir}/colcrt
%{_bindir}/colrm
%{_bindir}/column
%{_bindir}/ddate
%{_bindir}/dmesg
%{_bindir}/fallocate
%{_bindir}/findmnt
%{_bindir}/flock
%{_bindir}/getopt
%{_bindir}/hexdump
%{_bindir}/ionice
%{_bindir}/ipcmk
%{_bindir}/ipcrm
%{_bindir}/ipcs
%{_bindir}/isosize
%{_bindir}/line
%{_bindir}/logger
%{_bindir}/look
%{_bindir}/lsblk
%{_bindir}/lscpu
%{_bindir}/mcookie
%{_bindir}/mesg
%{_bindir}/more
%{_bindir}/mount
%{_bindir}/namei
%{_bindir}/prlimit
%{_bindir}/rename
%{_bindir}/renice
%{_bindir}/rev
%{_bindir}/script
%{_bindir}/scriptreplay
%{_bindir}/setarch
%{_bindir}/setsid
%{_bindir}/tailf
%{_bindir}/taskset
%{_bindir}/time
%{_bindir}/ul
%{_bindir}/umount
%{_bindir}/unshare
%{_bindir}/uuidgen
%{_bindir}/which
%{_bindir}/chrp-addnote
%{_bindir}/mkzimage_cmdline
%{_sbindir}/addpart
%{_sbindir}/adjtimex
%{_sbindir}/agetty
%{_sbindir}/blkid
%{_sbindir}/blockdev
%{_sbindir}/chcpu
%{_sbindir}/ctrlaltdel
%{_sbindir}/delpart
%{_sbindir}/findfs
%{_sbindir}/fsck
%{_sbindir}/fsck.minix
%{_sbindir}/fsck.cramfs
%{_sbindir}/fsfreeze
%{_sbindir}/fstrim
%{_sbindir}/ldattach
%{_sbindir}/losetup
%{_sbindir}/mkfs
%{_sbindir}/mkfs.bfs
%{_sbindir}/mkfs.minix
%{_sbindir}/mkfs.cramfs
%{_sbindir}/mkswap
%{_sbindir}/nologin
%{_sbindir}/raw
%{_sbindir}/partx
%{_sbindir}/pivot_root
%{_sbindir}/rtcwake
%{_sbindir}/setctsid
%{_sbindir}/swaplabel
%{_sbindir}/swapoff
%{_sbindir}/swapon
%{_sbindir}/switch_root
%{_sbindir}/wipefs
%verify(not mode) %attr(0755,root,tty) %{_bindir}/wall
%{_bindir}/whereis
%verify(not mode) %attr(0755,root,tty) %{_bindir}/write
%{_sbindir}/flushb
%{_sbindir}/readprofile
%dir %{_datadir}/getopt
%attr (755,root,root) %{_datadir}/getopt/getopt-parse.bash
%attr (755,root,root) %{_datadir}/getopt/getopt-parse.tcsh
#XXX: post our patches upstream
#XXX: call fdupes on /usr/share/man
%{_sbindir}/fdisk
%{_sbindir}/cfdisk
%{_sbindir}/sfdisk
%{_bindir}/cytune
%{_sbindir}/fdformat
%{_sbindir}/hwclock
%{_sbindir}/klogconsole
%{_bindir}/setterm
%{_sbindir}/tunelp

%files -n libblkid
%defattr(-, root, root)
/%{_libdir}/libblkid.so.1
/%{_libdir}/libblkid.so.1.*

%files -n libblkid-devel
%defattr(-, root, root)
%{_libdir}/libblkid.so
%dir %{_includedir}/blkid
%{_includedir}/blkid/blkid.h
%{_libdir}/pkgconfig/blkid.pc

%files -n libmount
%defattr(-, root, root)
/%{_libdir}/libmount.so.1
/%{_libdir}/libmount.so.1.*

%files -n libmount-devel
%defattr(-, root, root)
%{_libdir}/libmount.so
%dir %{_includedir}/libmount
%{_includedir}/libmount/libmount.h
%{_libdir}/pkgconfig/mount.pc

%files -n uuidd
%defattr(-, root, root)
%verify(not mode) %attr(0755,root,root) %{_sbindir}/uuidd
%attr(-,uuidd,uuidd) %dir %{_localstatedir}/lib/libuuid
%ghost %{_localstatedir}/lib/libuuid/clock.txt
%attr(-,uuidd,uuidd) %ghost %dir %{_localstatedir}/run/uuidd
%{_initddir}/uuidd

%files -n libuuid
%defattr(-, root, root)
/%{_libdir}/libuuid.so.1
/%{_libdir}/libuuid.so.1.*

%files -n libuuid-devel
%defattr(-, root, root)
%{_libdir}/libuuid.so
%dir %{_includedir}/uuid
%{_includedir}/uuid/uuid.h
%{_libdir}/pkgconfig/uuid.pc

