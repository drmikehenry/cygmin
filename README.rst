Introduction
============

Cygmin is a tool for downloading and packaging a reduced subset of the Cygwin
Unix-like toolset for Windows (http://cygwin.com), suitable for software
development.  The default set of packages requires approximately 500 MB to
install (compared to Gigabytes for installing all of Cygwin).


Installing Cygwin from cygmin-yyyy-mm-dd.zip
============================================

To install Cygwin from the cgymin archive:

- Unpack the file cygmin-yyyy-mm-dd.zip to a temporary location (somewhere on
  your local hard drive is recommended for speed).  All archive contents live
  below the directory cygmin-yyyy-mm-dd.

- Run cygmin-yyyy-mm-dd\setup-x86.exe.

- Choose "Next" on the introduction screen.

- Choose "Install from Local Directory" for the installation type, then choose
  "Next".

- The defaults are recommended on the "Choose Installation Directory" screen;
  choose "Next".

- Choose the "cygmin-yyyy-mm-dd" directory extracted from the zip archive for
  the "Local Package Directory", then choose "Next".

- If a "Setup Alert" indicates this is the first time for installing
  Cygwin 1.7.x, choose "OK" to dismiss it.

- Click *once* on the word "Default" next to "All" in the package tree on the
  "Select Packages" screen; it should now say "All - Install".  Choose "Next".
  (This will install everything in the cygmin archive, not all of Cygwin.)

- If you see a "Resolving Dependencies" dialog that mentions packages selected
  to meet dependencies, install them as well.  They should be present in the
  Cygmin archive, and though they've already been marked for installation, for
  some reason the installer wants extra confirmation.

- When Cygwin Setup completes, the miniature distribution of Cygwin has been
  installed.


Downloading Cygwin using cygmin.py
==================================

To download the desired subset of Cygwin and create cygmin-yyyy-mm-dd.zip:

- Install python 2.x (http://python.org/) as a prerequisite.

- Change to a suitable download directory.

- Run "python cygmin.py" from a normal Windows command prompt, or via
  Windows explorer, but *not* from within a pre-existing Cygwin installation.

- The Cygwin setup program will launch in "quiet mode", running without
  the need for user input.  ("Quiet mode" may be disabled via the
  ``--interactive`` switch.)

  Note that a default mirror is chosen for you.  It's permissible to change to
  another mirror, but it is then your responsibility to use the same mirror
  each time, or to remove the cgymin-tmp directory between runs.

- Upon completion, cygmin will create cygmin-yyyy-mm-dd.zip containing
  the downloaded packages and setup-x86.exe.

For more options, run "cygmin.py --help".

On future runs of cygmin.py, additional packages may be selected for download.
If the cygmin-tmp directory has not been deleted, only the newly selected
packages will be downloaded, but all downloaded packages will be included in
the archive.

If the --package-file option de-selects a previously downloaded package, the
generated archive will still contain that package until it is manually pruned
from cygmin-tmp.

The following extra packages were selected when this README was generated:

- bash-completion
- crypt
- ctags
- curl
- dos2unix
- gcc-core
- gcc-g++
- gdb
- git
- keychain
- libncurses-devel
- libncursesw-devel
- libxml2
- make
- makedepend
- mercurial
- mingw64-i686-gcc
- mingw64-x86_64
- nasm
- ncurses
- netcat
- openssh
- p7zip
- patchutils
- perl
- python
- rsync
- ruby
- socat
- subversion
- termcap
- unzip
- vim
- wget
- w32api
- w32api-headers
- w32api-runtime
- w3m
- xterm
- xxd
- zip

History
=======

Version 0.5.0 (2014-03-12)
--------------------------

- Add dos2unix.

- Change gcc4 to gcc-core and gcc-g++ (due to package rename).

- Prevent re-launching as administrator, as that causes setup-x86.exe to exit
  prematurely.

Version 0.3.0 (2012-05-16)
--------------------------

- Added "p7zip" package.

- Added "--interactive" switch for running "setup-x86.exe" interactively during
  download phase.

- Added "--package" switch to allow specification of packages without a
  separate package file.

- Embedded documentation for "setup-x86.exe" for reference.

Version 0.2.0 (2012-05-05)
--------------------------

- Added "patchutils" package.

Version 0.1.2 (2012-04-22)
--------------------------

- Initial release.

