#!/usr/bin/env python
# vim:set fileencoding=utf8: #

__VERSION__ = "0.1.2"

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

- Run cygmin-yyyy-mm-dd\setup.exe.

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
  the need for user input.

  Note that a default mirror is chosen for you.  It's permissible to change to
  another mirror, but it is then your responsibility to use the same mirror
  each time, or to remove the cgymin-tmp directory between runs.

- Upon completion, cygmin will create cygmin-yyyy-mm-dd.zip containing
  the downloaded packages and setup.exe.

For more options, run "cygmin.py --help".

On future runs of cygmin.py, additional packages may be selected for download.
If the cygmin-tmp directory has not been deleted, only the newly selected
packages will be downloaded, but all downloaded packages will be included in
the archive.

If the --package-file option de-selects a previously downloaded package, the
generated archive will still contain that package until it is manually pruned
from cygmin-tmp.

The following extra packages were selected when this README was generated:

"""


def getReadmeText(extraPackages):
    if extraPackages:
        packageText = "- " + "\n- ".join(extraPackages)
    else:
        packageText = "*none*"
    return README.lstrip() + packageText + "\n"


DEFAULT_EXTRA_PACKAGES = """
    bash-completion
    crypt
    ctags
    curl
    gcc4
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
    w3m
    xterm
    xxd
    zip
    """.split()

import urllib2
import datetime
import os
import sys
import subprocess
from os.path import join as pjoin
import zipfile
import glob


SETUP_NAME = "setup.exe"


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


def runSetup(workDir, setupPath, mirrorUrl, extraPackages=[]):
    notify("Running setup utility")
    args = [os.path.abspath(setupPath),
            "--download",
            "--site=" + mirrorUrl,
            "--local-package-dir=" + os.path.abspath(workDir),
            "--root=" + os.path.abspath(workDir),
            "--quiet-mode",
            "--no-verify",
            "--no-desktop",
            "--no-shortcuts",
            "--no-startmenu"]

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

    parser.add_option("--package-file", dest="packageFile",
            action="store",
            help="""use PACKAGEFILE to adjust list of extra packages """
                """(one package per line, leading '-' to remove, """
                """bare '-' to remove all)""")

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


def main():
    today = datetime.date.today().isoformat()
    extraPackages = DEFAULT_EXTRA_PACKAGES[:]
    parser, options, args = parseArgs()

    if options.packageFile:
        notify("Using package-file %s" % options.packageFile)
        with open(options.packageFile) as packFile:
            for line in packFile:
                package = line.strip()
                if package.startswith("-"):
                    # Removing one or all.
                    package = package[1:]
                    if not package:
                        # Lone "-" on a line; remove all packages.
                        notify("Removing all extra packages")
                        extraPackages = []
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
    retCode = runSetup(workDir, setupPath, mirrorUrl, extraPackages)
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

