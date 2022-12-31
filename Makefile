# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Authors:		Jiri Konecny <dragonlichcz@gmail.com>


# Arguments:
#
# PREFIX  -- Set prefix for the installation (/usr is default)
# DESTDIR -- Where you want to install
#

ifeq ($(shell uname -s),Darwin)
    CFLAGS ?= -O2 -I/opt/X11/include
    LFLAGS ?= -L/opt/X11/lib -lGL -lX11
    PYTHON = python2.7 -m py_compile
    SED = sed -i '' -e
else
    CFLAGS ?= -O2 
    LFLAGS ?= -lGL -lX11
    PYTHON = python2 -m py_compile
    SED = sed -i
endif
CC = gcc $(CFLAGS)
GZIP = gzip
SHELL := /bin/bash

PREFIX ?= /usr
DESTDIR ?= # root dir

sharedir := $(DESTDIR)$(PREFIX)/share
bindir := $(DESTDIR)$(PREFIX)/bin
execdir := $(DESTDIR)$(PREFIX)/libexec


all: build

clean:
	$(RM) ./python/*.pyc
	$(RM) ./python/lib/*.pyc
	$(RM) ./bin/check_dd
	$(RM) ./bin/playonlinux
	$(RM) ./bin/playonlinux-pkg
	$(RM) ./ChangeLog

build:
	$(CC) ./src/check_direct_rendering.c -o ./bin/playonlinux-check_dd $(LFLAGS)
	$(PYTHON) ./python/*.py
	$(PYTHON) ./python/lib/*.py
	echo -e '#!/bin/bash\nGDK_BACKEND=x11 ${sharedir}/playonlinux/playonlinux "$$@"\nexit 0' > ./bin/playonlinux
	echo -e '#!/bin/bash\n${sharedir}/playonlinux/playonlinux-pkg "$$@"\nexit 0' > ./bin/playonlinux-pkg
	chmod +x ./bin/playonlinux
	chmod +x ./bin/playonlinux-pkg
	$(SED) 's/\(\["DEBIAN_PACKAGE"\]\s*=\s*\)"FALSE"/\1"TRUE"/' \
		./python/lib/Variables.py

install:
	install -d $(bindir)
	install -d $(execdir)
	install -d $(sharedir)/pixmaps
	install -d $(sharedir)/applications
	install -d $(sharedir)/appdata
	install -d $(sharedir)/playonlinux/bin
	install -d $(sharedir)/man/man1
	install -d $(sharedir)/locale
	$(GZIP) -c ./doc/playonlinux-pkg.1 > $(sharedir)/man/man1/playonlinux-pkg.1.gz
	$(GZIP) -c ./doc/playonlinux.1 > $(sharedir)/man/man1/playonlinux.1.gz
	cp ./etc/PlayOnLinux.desktop $(sharedir)/applications/PlayOnLinux.desktop
	cp ./etc/PlayOnLinux.appdata.xml $(sharedir)/appdata/PlayOnLinux.appdata.xml
	cp ./etc/playonlinux.png $(sharedir)/pixmaps/playonlinux.png
	cp ./etc/playonlinux16.png $(sharedir)/pixmaps/playonlinux16.png
	cp ./etc/playonlinux32.png $(sharedir)/pixmaps/playonlinux32.png
	cp ./bin/{playonlinux,playonlinux-pkg} $(bindir)/
	cp ./bin/playonlinux-check_dd $(execdir)/
	cp ./{playonlinux*,README.md,TRANSLATORS,CHANGELOG.md,LICENCE} $(sharedir)/playonlinux/
	cp -R ./{bash,etc,lib,plugins,python,resources,tests} $(sharedir)/playonlinux/
	cp -R ./lang/locale/* $(sharedir)/locale/

changelog:
	(GIT_DIR=.git git log > .changelog.tmp && mv .changelog.tmp ChangeLog; rm -f .changelog.tmp) || (touch ChangeLog; echo 'git directory not found: installing possibly empty changelog.' >&2)

.PHONY: all clean build install changelog

