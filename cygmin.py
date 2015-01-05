#!/usr/bin/env python
# vim:set fileencoding=utf8: #

__VERSION__ = "0.5.1"

README = """

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

__PACKAGES__

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

"""


def getReadmeText(extraPackages):
    if extraPackages:
        packageText = "- " + "\n- ".join(extraPackages)
    else:
        packageText = "*none*"
    return README.lstrip().replace("__PACKAGES__", packageText)


DEFAULT_EXTRA_PACKAGES = """
    bash-completion
    crypt
    ctags
    curl
    dos2unix
    gcc-core
    gcc-g++
    gdb
    git
    keychain
    libncurses-devel
    libncursesw-devel
    libxml2
    make
    makedepend
    mercurial
    ncurses
    netcat
    openssh
    p7zip
    patchutils
    perl
    python
    rsync
    ruby
    socat
    subversion
    termcap
    unzip
    vim
    wget
    w32api
    w32api-headers
    w32api-runtime
    w3m
    xterm
    xxd
    zip
    """.split()

import urllib2
import datetime
import os
import sys
import re
import subprocess
from os.path import join as pjoin
import zipfile
import glob


SETUP_NAME = "setup-x86.exe"

'''
Starting cygwin install, version 2.844
User has NO backup/restore rights

Command Line Options:
 -D --download                     Download from internet
 -L --local-install                Install from local directory
 -s --site                         Download site
 -O --only-site                    Ignore all sites except for -s
 -R --root                         Root installation directory
 -x --remove-packages              Specify packages to uninstall
 -c --remove-categories            Specify categories to uninstall
 -P --packages                     Specify packages to install
 -C --categories                   Specify entire categories to install
 -p --proxy                        HTTP/FTP proxy (host:port)
 -a --arch                         architecture to install (x86_64 or x86)
 -q --quiet-mode                   Unattended setup mode
 -M --package-manager              Semi-attended chooser-only mode
 -B --no-admin                     Do not check for and enforce running as
                                   Administrator
 -h --help                         print help
 -l --local-package-dir            Local package directory
 -r --no-replaceonreboot           Disable replacing in-use files on next
                                   reboot.
 -X --no-verify                    Don't verify setup.ini signatures
 -n --no-shortcuts                 Disable creation of desktop and start menu
                                   shortcuts
 -N --no-startmenu                 Disable creation of start menu shortcut
 -d --no-desktop                   Disable creation of desktop shortcut
 -K --pubkey                       URL of extra public key file (gpg format)
 -S --sexpr-pubkey                 Extra public key in s-expr format
 -u --untrusted-keys               Use untrusted keys from last-extrakeys
 -U --keep-untrusted-keys          Use untrusted keys and retain all
 -g --upgrade-also                 also upgrade installed packages
 -o --delete-orphans               remove orphaned packages
 -A --disable-buggy-antivirus      Disable known or suspected buggy anti virus
                                   software packages during execution.
Ending cygwin install
'''


class DownloadError(Exception):
    pass


def notify(msg):
    print(msg)


def downloadSetup(setupUrl, setupPath):
    if os.path.isfile(setupPath):
        notify("Using existing %s" % setupPath)
    else:
        notify("Downloading %s..." % setupUrl)
        inFile = urllib2.urlopen(setupUrl)
        outFile = open(setupPath, "wb")
        outFile.write(inFile.read())
        inFile.close()
        outFile.close()


def makeDirWithParents(path):
    if not os.path.exists(path):
        os.makedirs(path)


def prepareWorkDir(workDir):
    makeDirWithParents(workDir)


def escWinPath(s):
    return '"' + s + '"'


def runSetup(workDir, setupPath, mirrorUrl, extraPackages=[],
        interactive=False):
    notify("Running setup utility")

    # Need --no-admin to prevent re-spawning to elevate privileges (since
    # re-spawning has the side-effect of causing setup.exe to return early).
    args = [escWinPath(os.path.abspath(setupPath)),
            "--download",
            "--site=" + mirrorUrl,
            "--local-package-dir=" + escWinPath(os.path.abspath(workDir)),
            "--root=" + escWinPath(os.path.abspath(workDir)),
            "--no-admin",
            "--no-verify",
            "--no-desktop",
            "--no-shortcuts",
            "--no-startmenu"]
    if not interactive:
        args.append("--quiet-mode")

    extraPackages = [p for p in extraPackages if not p.startswith("-")]
    if extraPackages:
        args.extend(["--packages", ",".join(extraPackages)])

    batPath = pjoin(workDir, "setup-helper.bat")
    with open(batPath, "w") as batFile:
        batFile.write("@echo off\n")
        batFile.write(" ^\n ".join(args) + "\n")

    retCode = subprocess.call([batPath])
    return retCode


def addToZip(zipFile, fileName, baseDir):
    #notify("addToZip(..., %s, %s)" % (repr(fileName), repr(baseDir)))
    if os.path.isdir(fileName):
        baseDir = pjoin(baseDir, os.path.basename(fileName))
        for path in os.listdir(fileName):
            addToZip(zipFile, pjoin(fileName, path), baseDir)
    else:
        zipFile.write(fileName, pjoin(baseDir, os.path.basename(fileName)))


def makeZipFile(zipPath, workDir, setupPath, readmePath, scriptDestPath):
    baseDir = os.path.splitext(os.path.basename(zipPath))[0]
    downloadDirs = glob.glob(pjoin(workDir, "*%*"))
    if not downloadDirs:
        raise DownloadError("No download directories found in %s" % workDir)
    elif len(downloadDirs) > 1:
        raise DownloadError("Multiple download directories found; "
                "delete all but one of these:\n  " +
                "\n  ".join(downloadDirs))

    with zipfile.ZipFile(zipPath, "w") as zipFile:
        addToZip(zipFile, setupPath, baseDir)
        addToZip(zipFile, readmePath, baseDir)
        addToZip(zipFile, scriptDestPath, baseDir)
        for path in glob.glob(pjoin(downloadDirs[0], "*")):
            addToZip(zipFile, path, baseDir)


def parseArgs():
    from optparse import OptionParser
    usage = r"""
%prog [ OPTIONS ]
"""
    parser = OptionParser(usage, version="%prog " + __VERSION__)

    parser.add_option("--readme", dest="readme",
            action="store",
            help="""generate file README""")

    parser.add_option("--mirror", dest="mirror",
            action="store",
            default="http://mirror.cs.vt.edu/pub/cygwin/cygwin/",
            help="""URL of mirror site to use""")

    parser.add_option("--package", dest="packages",
            action="append",
            metavar="PACKAGE | -PACKAGE",
            default=[],
            help="""add or subtract a package """
                """(leading '-' to remove, bare '-' to remove all).  """
                """Multiple packages may be separated by spaces or commas, """
                """as in --package 'package1 package2'""")

    parser.add_option("--package-file", dest="packageFile",
            action="store",
            help="""use PACKAGEFILE to adjust list of extra packages """
                """(one package per line, leading '-' to remove, """
                """bare '-' to remove all)""")

    parser.add_option("--interactive", dest="interactive",
            action="store_true", default=False,
            help="""allow interaction with setup GUI (disables setup-x86.exe's
                    ``--quiet-mode``)""")
    '''
    parser.add_option("-f", "--flag", dest="flag",
            action="store_true", default=False,
            help="""set FLAG to TRUE""")
    parser.add_option("-s", "--string", dest="string",
            action="store",
            help="""set STRING to string value""")
    parser.add_option("-i", "--integer", dest="integer",
            action="store", type="int", default=42,
            help="""set INTEGER to integral value""")
    '''

    (options, args) = parser.parse_args()
    return parser, options, args


def writeReadme(readme, extraPackages):
    with open(readme, "w") as f:
        f.write(getReadmeText(extraPackages))


def addPackage(extraPackages, package):
    if package.startswith("-"):
        # Removing one or all.
        package = package[1:]
        if not package:
            # Lone "-" on a line; remove all packages.
            notify("Removing all extra packages")
            del extraPackages[:]
        else:
            try:
                extraPackages.remove(package)
                notify("Removing package %s" % package)
            except ValueError:
                # OK if package to remove is not present.
                pass
    else:
        if package not in extraPackages:
            extraPackages.append(package)
            notify("Adding package %s" % package)


def main():
    today = datetime.date.today().isoformat()
    extraPackages = DEFAULT_EXTRA_PACKAGES[:]
    parser, options, args = parseArgs()

    if options.packageFile:
        notify("Using package-file %s" % options.packageFile)
        with open(options.packageFile) as packFile:
            for line in packFile:
                package = line.strip()
                addPackage(extraPackages, package)
    for packageSpec in options.packages:
        for package in re.split(r"(?:\s+|,)", packageSpec):
            addPackage(extraPackages, package)

    if options.readme:
        writeReadme(options.readme, extraPackages)
        sys.exit()

    workDir = "cygmin-tmp"
    distName = "cygmin-" + today
    zipPath = distName + ".zip"
    readmePath = distName + "-README.txt"

    setupUrl = "http://cygwin.com/" + SETUP_NAME
    setupPath = pjoin(workDir, SETUP_NAME)
    mirrorUrl = options.mirror

    scriptSrcPath = sys.argv[0]
    scriptName = os.path.basename(scriptSrcPath)
    scriptDestPath = pjoin(workDir, scriptName)

    prepareWorkDir(workDir)
    downloadSetup(setupUrl, setupPath)
    retCode = runSetup(workDir, setupPath, mirrorUrl, extraPackages,
            options.interactive)
    notify("\n\nSetup complete.\n")

    if retCode == 0:
        writeReadme(readmePath, extraPackages)
        with open(scriptSrcPath) as srcFile:
            with open(scriptDestPath, "w") as destFile:
                destFile.write("\n".join(srcFile.readlines()) + "\n")
        makeZipFile(zipPath, workDir, setupPath, readmePath, scriptDestPath)

    notify("Created archive: %s" % zipPath)

if __name__ == '__main__':
    try:
        main()
    except DownloadError, e:
        notify("\n** Error: " + str(e))
        sys.exit(1)

