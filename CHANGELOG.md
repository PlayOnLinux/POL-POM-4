# 4.3.4
* Fixed some bugs in the wineversion process
* Begining of code cleaning and refactoring
* Begining of using wx box sizers instead of absolute positioning.
  Most of the windows are now resizable
  This should solve display issues on many cases: HDPI and alternative windows manager: (see https://www.playonlinux.com/en/topic-16188-Visual_error_with_KDE.html)
* macOS: Remove XQuartz installation
* macOS: Bundle an up-to-date wine version
* macOS: Use native terminal instead of xterm

# 4.3.3
* Linux: Fix HDPI support
* Compatibility with OSX < Mojave

# 4.3
* Various fix on OSX
* Phoenicis (POL 5) winebuild compatibility. POL 4 winebuilds will be deprecated. (See https://github.com/PhoenicisOrg/phoenicis-winebuild)

# 4.2.11
* Fix POL_SetupWindow_download clobbering $FILENAME
* Fix small typo in first use "send report" message

# 4.2.10
* Silence POL_Notice_IsAck when ack_notices file doesn't exist
* Allow Set_SoundDriver '' to disable sound
* Add in the wineprefix configuration tab for Wine: Control panel
* Remove in the wineprefix configuration tab for Wine: Wine Uninstaller
* Add support for Wine-staging DLL redirects (POL_Wine_RedirectDLL,
  POL_Wine_DelRedirectDLL, POL_Wine_RedirectDLL_App,
  POL_Wine_DelRedirectDLL_App) (#5163)
* Fix POL_System_cpmv log message
* Reimplement deprecated functions POL_SetupWindow_make_shortcut and
  POL_SetupWindow_auto_shortcut using POL_Shortcut for consistency

# 4.2.9
* Fixed a bug in the user agent used in urllib that would make it look like an attack to paranoid eyes (and filters) (#5072)
* Try to improve general installation instructions
* Update About's copyright years span (let's make it look like we're still working on the project ;) ) Many more could be updated though
* POL_Download_Resource: don't test hash of missing file (one less spurious warning message)
* Adding some visual clue while virtual drives are being removed
* Fix "debbuger" typo
* POL_System_find_file: really pick the shallowest file
* fix "debbuger" typo
* POL_SetupWindow_VMS: mention that the expected answer units are megabytes
* Try to make instructions to rerun a program in debug mode more obvious (#5104)
* Some GetRegValue fixing/hardening
* Remove spurious .lnk files from user desktop for all architectures during POL_Shortcut calls (#4200)
* Add waiting messages to POL_System_unzip & friends
* Deprecate Set_WineWindowTitle that no longer works with Wine 1.5.16+, and breaks Set_Desktop (#5118)
* Fix playonlinux-pkg -b (broken since PlayOnLinux 4.0)
* MacOS 10.11 support

# 4.2.8

* Feature freeze has been declared for POL 4.x, so this changelog should
  contain only bug fixes
* checkVersionUse(): don't assume cfg files have any order
* manual installation: component installation bugfix ($IFS not restored correctly)
* POL_OpenShell: call POL_Wine_AutoSetVersionEnv in all cases, to set $PATH (#5062)
* Fix consecutive shortcut creations
* POL_Wine_SetVideoDriver bugfix, device IDs were not inserted as DWORDs

# 4.2.7

* Detect and abort scripts when trying to run 64bit programs with 32bit Wine
* POL_DetectVideoCards: list VGA compatible controllers and 3D controllers (#5012)
* Add support for several other value types than REG_SZ to registry
  updating statements (#5013)
* POL_Wine_SelectPrefix: abort if no prefix name is provided
* Sort install scripts lists case insensitively (iTunes)
* Fix "hash-bang" line in shortcuts so they're actually executable
* Deprecate the usage of $REPERTOIRE in PlayOnLinux own code
* Translate remaining french comments and identifiers in Bash code
* Improve POL_Wine_PrefixDelete to remove ancillary resources (shortcuts, icons,...)
* Wine versions manager: attributes tell apart used versions instead of
  unused versions; Add an extra warning when about to remove a version in use
* Avoid Python detection loops
* Display wx version found
* Fix Settings > Internet menu (#4989, thanks to rupert)
* Workaround for Wine bug #37575 (#5023)
* Improve find_binary function and make it public as POL_System_find_file
* Add support for .lnk, .bat and .cmd files to POL_Shortcut and POL_SetupWindow_shortcut_creator
* Added an icon to open the debugger from the installation wizard when
  POL_Debug_Init has been called (#4948)
* Implement POL_SetupWindow_notice to display important messages, but
  allow the user to acknowledge them once and for all ("Don't remind me") (#2036)
* POL_OpenShell (Configure > Misc > Open a shell) bug fixes
* Add a warning when OpenGL autotests are missing (user support)
* Make sure "Install non-listed application" link is always visible in
  install window
* POL_SetupWindow_cdrom: don't suggest "*" when no CDROM has been found
* Remove use of remaining os.system() calls (less overhead, less quoting nightmare)
* Use os.kill() instead of shell command
* Use of "exec" to avoid some useless extra Bash processes
* polconfigurator interface cleanup (no risk of translation breakage)

# 4.2.6

* Use $POL_TERM more consistently, allow POL_TERM global configuration
  override. Beware, the terminal must support -T and -e options, so
  gnome-terminal doesn't qualify (gnome-terminal.wrapper does though)
* Add a POL_Wine_VersionSignature function to compute a hash of a Wine
  package
* Python version string extraction hardening (#4895)
* POL_System_PartInfo identifies filesystems thru mount point instead of device
  (Btrfs subvolumes compatibility)
* Modify bash/document_reader to pass extra arguments unchanged (http://www.playonlinux.com/en/topic-12519-Pass_arguments_to_PDFXChange_Viewer.html)
* Remove "skipped lines" messages when the debugger gets the focus back
* POL_Shortcut: do not overwrite $Binaire to improve logging
* mainwindow: make alert boxen child of the main window so they cannot get
  lost behind other windows
* Prevent POL_Download_Resource clobbering $APP_ANSWER
* Wine versions management: grey out versions that are not currently in use by any virtual drive and can be safely removed (Tutul)

# 4.2.5

* Fix reading/writing values containing '=' symbol in configuration files (#4834)
* Make POL_Wine_InstallFonts preserve current directory (regression since 4.2.3)
* Disable "Install" component button until a component is selected
* Compatibility with wxpython 3.0
* Compatibility with Debian 8
* Compatibility with Mac OS 10.10
* Mention URL in POL_Download and POL_Download_Resource error messages
  (should help with user support)
* Add POL_Config_Win16 to check if the host can run win16 programs, see
  http://linux-kernel.2935.n7.nabble.com/tip-x86-urgent-x86-64-modify-ldt-Ban-16-bit-segments-on-64-bit-kernels-td838675i120.html

# 4.2.4

* New support and feedback system, easier to use
* Links to social networks
* 4.2.3 regresion fixed in run_exe module

# 4.2.3

* Fix for Python version "2.7" (#3749)
* POL_SetupWindow_shortcut_creator: always suggest unused shortcut names;
  If user chooses an already used name, warn before overwrite (#3770)
* Fix for "Error 427" http://www.playonlinux.com/en/topic-11490-Error_427.html
  regression in 4.2.2 (functions override)
* Fix IE3 icon extraction (#3885)
* Debugger: if behind by too many lines, skip displaying some
  (...skipped n lines...) to keep up
* wineserver not in path problem fixed again (debian bug, but they won't fix it)
* Fix "Open a shell" to enable the wine version of the prefix
* New attempt at fixing download gauge overflow (#2123)
* Do not totally silence gpg import errors
* Allow POL_SetupWindow_textbox to accept an extra max length parameter
* Limit bug reports title to 80 characters
* virtual drive removal: use os.lstat() instead of os.stat() to check for broken rights (reported by Xenos5)
* change of Wine version used in a virtual drive: kill running wineserver after asking for permission
* Experimental: FreeBSD support
* Removing PlayOnLinux_Online
* Corefonts are now managed as any other POL_Call package. (Debian.lib is consequently no longer needed)
* Removing installation process of missing gecko and mono at startup. It should not happen anymore
* Cleaner way to save panel position
* Fix a bug in GetSettings() where the value contain the equal ('=') character
* PlayOnMac does no longer need a reboot after installing XQuartz
* PlayOnMac does no longer popup a warning before xterm is installed
* Removing IRC
* Icones install can now be bigger than 22x22

# 4.2.2

* Changelog move from plaintext to Markdown syntax.
* read script lists in utf8 when looking up script to install (#2076)
* (experimental) new algorithm to find installed Python version,
  implements fallback which is probably overkill (#2122)
* New version of PlayOnLinux Vault 4.0.4:
  - Adding lzop compression if available (fast compression with medium
    compression rate).
  - Add a "Save" shortcut in PlayOnLinux side panel
* Fix double utf-8 decoding of shortcuts (#2125, #2289)
* Add POL_Shortcut_Configurator
* Modified POL_System_wget to keep error messages from wget
* Updated PNG icons with broken profiles, thanks to calvertyl
  (http://www.playonlinux.com/en/topic-10442-New_Warning_Message_on_startup.html)
* wine-mono download support
* Fix POL_SetupWindow_message typo (not enough video memory message) (#2790)
* POL_LoadVar_Device: refacto POL_DetectVideoCards;
  Let user choose when there's more than one known videocard present
* Add link to download page in side panel when version is not up-to-date (#2677)
  Not sure it's visible enough, could be improved.
* Added logging to archivers wrappers (POL_System_unzip etc.)
* Update mono download URLs
* Updated IRC server address, freenode.com domain is gone
* Harden applications list parsing
* force LANG=C when spawning wineconsole (Wine bug #10063)
* fix typo in bash/manual_install
* Developer feature: allow to override function scripts
  When global configuration ALLOW_FUNCTION_OVERRIDES is set to TRUE, function
  scripts in $POL_USER_ROOT/configurations/function_overrides/ override function
  scripts by the same name. This feature disables bug reporting.
* Fix website login when username contains spaces (#3573)
* "Run an .exe in this virtual disk" sets current directory to program's
  directory (#1855)
* fix "wineserver not found" in interactive use of POL_Wine_Direct3D /
  POL_Wine_X11Drv / POL_Wine_DirectSound / POL_Wine_DirectInput
* Remove use of os.system() from mainwindow.py and configure.py
  (less overhead, less quoting nightmare)
* Add missing POL_Wine_AutoSetVersionEnv before wineserver calls

# 4.2.1

* When removing shortcuts or virtual drives from the Configure window,
  make sure desktop icons, menu entries, etc. are also removed.
* fix Python's VersionLower (infinite source of bugs)
* Update © in about box LP: #1160801
* Fix a huge problem in bug reporting I introduced in 4.2... I thought
  it tested it well, this is depressing. Without testers, without
  users testing beta versions, it seems there's no way to get bugfree
  releases.
* (experimental) enable display of beta scripts by default,
  differenciate them in lists using a reddish background

# 4.2

* Huge icons download speedup by reusing a single HTTP connection
* Make sure debug mode is disabled when using playonlinux --run; Debug may still be used in playonlinux-bash though
* Make sure entered prefix name contains no space or slash during manual installations
* POL_System_wget: make sure the pipelined wget exitcode is not masked by grep's one
* POL_System_wget: interpret wget exitcodes
* genere_icone(): pick the right icon instead of Wine generic one (reported by Simon/excalibr on IRC) (#1815)
* (experimental) WINEDEBUG prefix setting, modify the amount of   logging when debugging is enabled. I'm not sure of the right scope,
  should it be per-shortcut, like the old "enable debugging" flag, or even global?
* POL_SetupWindow_shortcut_creator: use executable name as default shortcut name
* sort shortcuts case insensitively in main window so that lowercase doesn't end up at the bottom
* bug report: insert basic questions to answer in the bug report
* add "Report a problem" in shortcut-related actions in the side panel
* do not ask for confirmation to close PlayOnLinux if there's no program started
* do not suggest bug reporting if a script has been canceled by the user because a prefix already existed
* virtual drive removal should now overpass bad directory rights (caused by WMP9 for example) (#1732)
* POL_System_HomeSpaceLeft fix for df multiline output (#1890)
* added POL_System_UserRootSpaceLeft, in case ~/.PlayOnLinux is a symlink or a mount
* use POL_System_UserRootSpaceLeft in POL_System_EnoughSpace
* if exists, look for mounted devices in /media/$USER/ directory (Ubuntu Quantal, #1893)
* manual_install: don't call POL_Wine_PrefixCreate on patch installation
* irc: only warn about closing window when connected
* Debug log all user inputs (POL_SetupWindow_textbox, etc.)
* mainwindow.py: try to handle EINTR while reading from pol_update_list pipe (#1687)
* DeletePrefix: if root is actually a symlink, just delete the symlink
* gui_server.py: try to handle EINTR while accepting socket connections (#1687)
* Fix typo (#1932)
* POL_SetupWindow_download: accept a directory or a filename as 4th parameter
* POL_Download: accept URLs with "query strings", that get included in local filename
* (experimental) if missing, look for resources in winetricks cache before attempting download (#1963)
* Add POL_Wine_DelOverrideDLL, POL_Wine_DelAppOverrideDLL (#1989)
* POL_Wine_OverrideDLL and POL_Wine_AppOverrideDLL cleanups
* Support creation of desktop menu entries (#1943). POL_Shortcut needs
  an extra parameter, categories, for the entry to be created. And
  similarly to NO_DESKTOP_ICON setting, a NO_MENU_ICON can be set to
  TRUE to prevent desktop menu entries from being created.

# 4.1.9

* POL_System_is32bit
* Improved package menu
* Added : POL_Download_GetSize, POL_System_HomeSpaceLeft
* Fixed bug : #1446
* POL_Wine_PrefixCreate(): wait for wineserver to finish instead of hardcoded 3s wait (#1486)
* Fix bug in POL_Download_GetSize when redirected
* Fix options parsing bug in POL_System_CheckFS
* Log when NO_FSCHECK TRUE has been used
* Tried to make it clearer that no-cd patches may be needed to get legal programs to work
* Handle prefix overwrite in POL_Wine_PrefixCreate (Overwrite/Erase/Abort)
* POL_Download_Resource(): fix for $3 and $4 mixed up (#1651)
* VersionLower: fix cases when 3rd component in version strings is missing ("1.4") or dot in development string ("1.4-dos_support_0.6")
* Fixes to lib.playonlinux.VersionLower()
* Set_Desktop: support Wine 1.5.16+ (#1710)
* Try to make the purpose of install filters more obvious (#1652)

# 4.1.8

* Wine issue fixed on OSX 10.8.2 and 10.7.5
* Make "missing package" messages a bit more explicit
* Fix typo in POL_Wine_OverrideDLL
* Don't log regedit parameter if not a file
* irc client: changed reg.sub() to not depend on flag parameter (Python 2.7+)

# 4.1.7

* Search bar
* Bug fix
* DONT_KILL_ON_EXIT setting
* additional debug messages in POL_Download and POL_Download_Resource
* additional debug messages in POL_Call
* Many stability and UI improvements

# 4.1.6

* Critical fixes

# 4.1.5

* POL_Debug_* cookie forgotten
* Bug in update process

# 4.1.4

* Timer: read modification date instead of listing directories (CPU usage)
* CheckGL command
* Bug 1076, quote disappear after configure menu fixed
* Clickable links on install window
* Better (and clearer) debug windows
* Small fix for OSX 10.8
* NEW: PlayOnLinux --run supports extensions!
* POL_Shortcut_Document : Researches
* New POL_SetupWindow_browse GUI
* POL_SetupWindow_browse supports filters
* Ask to redownload when failed
* Minor: bug 1053
* Hypertext link in IRC
* Some improvement in IRC
* PlayOnLinux user agent
* A new method to manage setup window (cleaner code)
* Added POL_SimpleAlert
* Exiting POL will kill all opened bash scripts
* Updating the GIT is possible from the GUI
* Several UIs improvements
* Added POL_Die(), POL_Restart(), POL_System_RegisterPID()
* Harden POL_Download, POL_Download_Resource, POL_System_wget, POL_System_CopyDirectory against errors (disk full?)
* Create hardened commands POL_System_unzip, POL_System_7z, POL_System_tar, POL_System_cabextract, POL_System_unrar

# 4.1.3

* Real time refreshing
* New install window
* 64x64 icons support
* 24bits icon support
* regedit alone does not log anything
* POL vault updated
* Grep : line buffered
* IRC client : make URLs clickable

# 4.1.2

* Debian package unified
* Bug #953 fixed
* Usage stats
* Speed up POL_LoadVar_device by twice on OSX
* Video card detections
* POL needs to be updated for bug reports
* Icon change
* wineserver not in path problem fixed (debian bug, but they won't fix it)
* Improved irc
* UTF-8 pb fixed
* Starting a new GUI
* Beta: Look native feature for OSX

# 4.1.1

Fixes to critial problem
* Removing optirun support which makes wine hang
* UTF8 problem with files association

# 4.1.0

* Proxy problems fixed
* Lot of improvements in configure window
* Wineversion autorefresh in configure menu
* PlayOnLinux checks dependances
* Optirun support
* Debug scripts are sent on the good bug tracker
* More clever debugging
* A (very nice) debugger
* POL_SW_Check_cdrom supports multiple setup files
* Extension manager window
* WGETRC problem fixed
* PlayOnLinux can manage extensions

# 4.0.19

* Refresh button forces POL's update
* Fix utf8 problem in playonlinux path
* Debug error and fatal does no longer block bash when GUI is not initialized
* Local var problems
* POL_Lnk_Read to read .lnk files
* New screenshot system
* Bugfix
* Arch problem
* Pre run command should not be shown for prefixes
* Fix TRANSLATORS files, some names did not appear.
* Bugfix if wx is to lower

# 4.0.18

* Bug fix in AMD64 check_dd opengl
* Starting dosbox api
* POL_DosBox_InstallCDROM added
* POL_Debug_Init is quicker
* POL_Wine_InstallCDROM
* Progress bar for directory copy
* Support for Windows CD-ROM mounting on OSX
* Bug report disabled for unsigned scripts
* Ability to add commands before running a program
* Language issue problem fixed on OSX
* Bug 72 fixed
* POL_SetupWindow_licence does no longer crash when file is not found
* Bug 651 fixed
* Bugfix with wineprefixcreate
* Winemenubuilder only once
* Center text on linux
* Added PRE_WINE config
* Line return is now automatic
* 64bits prefix creation support
* Always create 32bits prefix with system's wine
* POL_Config_DosPrefix
* Updated sed binary for OSX
* Override user's ~/.wgetrc with $POL_USER_ROOT/configurations/wgetrc
* Fix "wineprefix" appearing in prefixes when scratching ~/.PlayOnLinux but not "virtual drives" symlink in home directory.
* Correctly log selected prefixes

# 4.0.17

* Manual install fix for existing 64bits prefixes
* Killing all processes
* Remove some /
* base64
* POL_SetupWindow_login adapted
* POL_System_wget
* Stderr wine changelog
* Useful aliases
* Bug 707 fixed
* First use is compulsory
* Bugfix
* Filesystem checks
* Bug 732 : text color
* Writting POL_WGET everywhere
* unset WINEARCH
* When installing a patched Wine, deploy Gecko for the non-patched version
* Report "patched Wine version" in prefix logs only when it's true
* POL_ExtractIcon, POL_ExtractBiggestIcon: can also extract icons from .ico files
* Removed dependency upon curl by posting to pastebin with wget (bug #670)
* New function POL_Shortcut_QuietDebug to suppress "crash" dialog for
  programs when not in debug mode; Useful for programs that are known
  not to exit cleanly with an exitcode = 0
* Scans for .exe only look for files
* Execute some of bash/startup synchronously (tmp cleanup among others)

# 4.0.16

* Removing Messenger from menu bar
* POL_Internal_KillAll
* Wine crashes does not wait for POL gui when
  running an app
* Wine does not complains about winemenubuilder
* Fixed slow wine ! At last
* DESURA and ORIGIN support
* Gecko support by POL
* Reading error fixe
* Error when running a program if prefix does no longer exists
* WaitExit --allow-kill is an argument
* Internet connexion problem should not empty POL_functions
* PlayOnLinux slow down wine (bug appearead since
  using tee to log wine. Does not exist in 4.0.15)
* A logfile is generated for each wineprefix
  (If ever one day, wine developers want to read
  them)
* Really, echo -e is better than printf
* POL/POM cleans tmp directory on startup
* Launchpad bug 947883 should be fixed
* Quote added in shortcuts
* run_exe is able to detect if we are in a POL
  wineprefix
* Create a symbolic link in $HOME (Will not be
  recreated if user choose to delete it)
* Title in IRC close confirm box
* wineprefixcreate should no longer exist!
  POL needs to run it on OLD POL versions,
  but should NOT run in on recent ones.
* Bugfix in requiredversion
* SelectPrefix make the directory
* Cleaning in wine.lib
* Wait_Next_Signal supports button
* Added debug messages
* Bug fix in lspci for some distro
* Debug lib in colors
* Send OpenGL states to logs
* XQuartz problems should be fixed on OSX
* Log when required version not satisfied
* Bug 676 fixed
* Bugfix in manual
* Bugfix in POL_Wine_WaitBefore

# 4.0.15

* sudo -k
* Run local script's script v4
* Translation problem
* GPG warning is now in gettext
* Confirmation needed to change a shortcut prefix
* Preferences menu fixed on OSX
* POL_Config_Read adapted to be usable in variable bash file (bugfix)
* POL_LoadVar_ScreenResolution
* Bug 225 fixed
* POL_Wine_WaitBefore
* Arch on prefix's icon
* POL_RequiredVersion, POL_AdvisedVersion
* Version comparison fixed
* Service pack bug fixed
* Title on dialog boxes
* OpenGL detection
* Removing Offline POL (no longer supported)
* rm "*" message removed (Don't worry, it was controled)
* POL_Shortcut(): Possibly to use path instead of executable
* POL_Shortcut_InsertBeforeWine: made sure the commands are not interpreted
  before insertion. Even \n is no longer interpreted, to insert several lines,
  call POL_Shortcut_InsertBeforeWine once per line.
* PlayOnMac is now compatible with Mac OS 10.8 : Mountain Lion (not tested, but it should work)
* PlayOnMac ask for a reboot after XQuartz is installed
* Accept to find into symlinks (Attempt to fix bug #609)
* Possibility to add arguments to a program
* POL will no longer run as root
* POL_Shortcut_Document to support manual
* Console prefix improved
* First part of bug #665 fixed
* Force playonlinux.cfg creation

# 4.0.14

* Slow DNS on IPV6 issue should be solved
* Higher timeout for slow DNS
* Register link send to the good website
* Wineversion windows remade
* Old wineversion support
* Change default size for main window
* POL Website detection, small fix
* Windows size and position saved
* ICON_SIZE setting added
* Python Detection
* Fixed AMD64 detection problem
* Fixed POL_Wine_OverrideDLL
* Fixed POL_Wine_wineboot
* Fixed POL_LoadVar_PROGRAMFILES
* Fixed bug 429 - Login to PlayOnLinux doesn't work
* Added POL_Wine_X11Drv (bug 543)
* Fixed IRC client
* Translation: Update of template & strings...
* Removing message.mo.
* Updating changelog. Victory \o/.
* Fixing bug report.
* Translation add a translator file.
* Added Plugin Vault (from Congelli501)

# 4.0.13

* Rebuild translation template and updating translation strings from Launchpad.
* Fixing bug #437.
* too_many_arguments_line fixed.
* Fixing bug #449.
* Fixing POL_GetSetupImages
* Cleaning.
* Fixing some bugs.

# 4.0.12

* Rebuilding translation template.
* Fixing problem with desktop icon.
* Adding screencapture plugin.
* Updating translation from launchpad.
* Cleaning.
* Disabling "sending a bug while running".

# from 4.0.9 to 4.0.11

* Rebuild of translation template.
* Fixing some bugs with translations strings.
* Cleaning.
* POL_Debug improved.
* Fixing POL_Wine_WaitExit function.
* Fix msfonts install.

# 4.0.8

* Support of pre and post-running scripts.

# from 4.0.4 to 4.0.7

* Various changes fixing the merge of PlayOnLinux and PlayOnMac into one program.

# 4.0.4

4.0.3 was skipped...
* Wineversion fix.
* POL_Functions fixed.
* Update of Capture.
* Variouses fixes.

# 4.0.2

* External shortcuts fixed.

# 4.0.1

* Bug fixed that preventing POL from running when a playonlinux 3 wineversion setting was remaining.

# 4.0

* Start V4 developement.
* Removing old files.
* Removing pol_cmd support.

# 3.8.13

* Fix POL_SetupWindow_check_cdrom

# 3.8.12

* Fixed bug #59 : No menu in Ubuntu
* Timeout changed to 2 seconds for update checking
* playonlinux-daemon removed
* ! removed in new_guiv3.py

# 3.8.11

* Rebuild translation template.
* Sync translation.
* Fix error message in WineVersion.
* Added url handler support

# 3.8.10

* Fix broken packages

# 3.8.9

* FIX: bug #93.
* Script authentification support
* Winetricks support in Manual Installation

# 3.8.8

* ADD: POL_Winetricks
* UPDATE: Template for translation, no sync with launchpad.

# 3.8.7

* UPDATE: Translation, sync with launchpad.
* UPDATE: Offline PlayOnLinux to 0.4
* FIX: bug #54. Change icon doesn't work properly.
* FIX: bug #61. Launcher didn't work on Ubuntu 10.04+.
* FIX: bug #85.
* FIX: bug #81.
* ADD: POL_Debug.
* ADD: GUI for help bug report creation.
* FIX: bug #88.
* UPDATE: Title variable defined automaticaly

# 3.8.6

* SYNC: Translation from launchpad
* FIX: A bug in bash/polconfigurator
* REBUILD: Template language.
* FIX: Update translation of script responsibility
* UPDATE: Detour to 0.5.
* UPDATE: AdvancedWineConfiguration to 3.6.1

# 3.8.5

* Change how the current version POL is send to the server.
* Fix bug #58. PlayOnLinux unable to start when an update is available.

# 3.8.4

* Fix a bug in auto_shortcut, arguments was inverted.
* Send version of POL when fetching a script.

# 3.8.3

* ADD: Plugin Detour
* UPDATE: Translation was updated, forgotten in 3.8.2.

# 3.8.2

* FIX: PlayOnLinux bug: #17. An error message was displayed during manual installation
* FIX: know bug in pol-cmd, pol-cmd was unable to create .PlayOnLinux repository
* FIX: Translation problems. Launchpad bugs: #629421, #629422, #629423, #629425. PlayOnLinux bugs: #36
* FIX: PlayOnLinux bug: #26, function POL_LoadVar_ProgramFiles didn't remove line char.
* UPDATE: Using convertVersionToInt to see if new version of POL is available, so the developement version does not say that a newer is available.
* UPDATE: Change all echo to $POL_SW_id by a cat / EOF. In other word write write all text message in one pass instead of line by line.
* UPDATE: Capture to 2.2.
* UPDATE: AdvancedWineConfiguration to 3.6.
* UPDATE/ADD: mainwindow show a message when: using a development version, no network, plugin offline pol used.
* ADD: Missing string in tranlation. String used by plugins.
* ADD: Set_WineWindowTitle. See POL bug: #23.
* ADD: New function for convert the string version to integer.
* ADD: playonlinux-cmd support search.
* ADD: playonlinux-cmd can list installed software.
* ADD: playonlinux-cmd can remove an already installed application.
* ADD: playonlinux-cmd now support all function POL_SW_* (guiv3) in shell mode.
* Full rebuild of translation template using xgettext. Python and Shell.
* Better use of the gettext function and string corrections for:
	* python/wine_versions.py
	* python/guiv3.py
	* python/telecharger.py
	* python/options.py
	* python/mainwindow.py
	* python/message_one.py
	* bash/LiveInstall
	* bash/autorun
	* bash/daemon/autorun
	* bash/uninstall
	* bash/expert/Executer
	* bash/expert/kill_wineserver
	* bash/install_wver
	* bash/killall
	* bash/polconfigurator (always used?)
	* bash/system_info
	* bash/check_maj
	* bash/check_maj_
	* lib/applications
	* lib/check_depend
	* lib/interface_v3
	* lib/main
	* lib/wine
	* lib/interface (+ cleaning)
	* playonlinux-cmd
	* playonlinux-pkg
	* Plugins: Capture
* Removing some unused files plus cleaning some files.
* Update copyright header.

# 3.8.1

* UPDATE: Capture to 2.1.1.
* UPDATE: Translation update with launchpad on 2010-08-31 and 2010-09-02.
* UPDATE/FIX: function install_plugin rewrited to a more sure system.
* FIX: function POL_SW_auto_shortcut doesn't work properly with icons.
* FIX: bug #31.
* FIX: bug #30. Adding a sleep 0.2 for some functions.
* NEW: include template for translation.
* NEW: add playonlinux-cmd for manage POL by command line.
* NEW: playonlinux-cmd now support --update
* NEW: playonlinux-cmd now support --start-install

# 3.8

* Bug #22 POL_SetupWindow_Init checks if a windows is already opened. --force option can be used to force windows opening in that case
* Ukranian name is .uk, not .ua
* New variable : $POL_USER_ROOT ( = $REPERTOIRE )
* Defaults plugins : Offline PlayOnLinux, Advanced wine configuration, Transgaming Cedega, Wine Import, Wine Look, Capture
* New functions : POL_GetImages, POL_SetupWindow_InitWithImages
* PlayOnLinux detects if you are alreay on a PlayOnLinux terminal, and if yes, it refuses to run
* A bug corrected in sources loading
* Wine Import and Offline PlayOnLinux plugin corrected
* playonlinux-shell command added to run PlayOnLinux shell in your terminal !
* PlayOnLinux uses a git repository for the developement
* Some cleaning
* The program does not show acceleration 3D message error when mesa-utils is not installed

# 3.7.7

* Bug #4 corrected (wine version manager does not start)
* Bug #14 corrected (conflict with gtkrgba module)
* Bug #27 fully corrected (a more natural sort)
* Added POL_SetupWindow_auto_shortcut which will replace POL_SetupWindow_make_shortcut
* Added POL_SetupError function
* install.py is fully compatible with offline mode plugin
* Some bugs corrected in wine version management

# 3.7.6

* Multiple wineversion bug fixed
* Lucid Lynx Compatiblity

# 3.7.5

* Improvement on icon managing
* Manual installation now supports .msi files
* Highest rank category added in install menu
* Most downloaded category added in install menu
* Stars behavior improved in install menu
* Added a patch category in install menu
* Added a testing zone in install menu

# 3.7.3

* A function added to correct Program Files problem
* Icon are automaticaly extracted from exe files
* Other bugs corrected

# 3.7.2

* Few bugs corrected

# 3.7.1

* Added POL_Call to replace tricks lib
* New polish and german translation

# 3.7

* Right Click Menu
* Kill All Apps
* Possibility to change icon
* Possibility to open user directory
* playonlinux --debug option


# 3.6

* Various bug fixed
* Winetricks integration

# 3.5

* Icon changed
* pol.mulx.net becomes mulx.playonlinux.com
* English translation improved

# 3.4

* Changelog removed when a new version is installed
* Possibility to configure the prefix before manual install
* Repository is automaticaly updated when needed
* POL_SetupWindow_prefixcreate use POL_SetupWindow_normalprefixcreate to avoid bugs
* POL_SetupWindow_specificprefixcreate and POL_SetupWindow_oldprefixcreate are made
* Autorun is moved on tools menu
* Refresh the repository should no more be needed. Therefor, it has been removed from the toolbar

# 3.3.1

* An important bug corrected in wine version manager
* lzma is no more asked by check_depend

# 3.3

* Wine version manager changed
* lzma is no more requiered

# 3.2.2

* An important bug corrected. The configuration button was hidden
# 3.2.1

* A bug corrected in the game list

# 3.2

* PlayOnLinux's game configurator is remade.
* The scriptor has the possibility to make a configurator for each script in ~/.PlayOnLinux/configurations/configurators/script_name
* The irc chat is removed
* GLSL bug corrected

# 3.1.3

* Added the possibility to disable PlayOnLinux messenger (also called IRC chat)
* An important bug fixed in the install menu with the latest version of Ubuntu Intrepid (The window freezed)
* The miniatures of the applications are no more downloaded during the repository refreshing process but directly in the install menu.
* A bug corrected in PlayOnLinux Setup Window : the top image position is now calculated according to its width

# 3.1.2

* PlayOnLinux install menu is faster
* Low connection can read the descriptions

# 3.1.1

* Description box in install menu has become an html box. Now, it's possible to underline or bold words in the description of a game.
* Descriptions are downloaded when the user clic on the name of the game, and no more when PlayOnLinux repositories are refreshed.
* Users can edit the description of a game on the website when they send a script.
* PlayOnLinux repositories refreshing has become faster
* A bug corrected in folders like "Applications Data". Now, it has the same name for every languages do avoid problems.

# 3.1

* Added playonlinux-daemon which run automatically you cd-rom setup's when it finds an autorun file.
* Proxy support corrected
* Changelog shown after upgrading
* Program Files different name corrected, the folder is automatically called "Program Files" instead of "Programmi" for example
* An important bug corrected in wine version.
* Added stars in install menu

# 3.0.8

* Added POL_SetupWindow_checkbox_list
* Translations improved
* IRC client improved (Multi channel support with a combobox)

# 3.0.2 to 3.0.6

* A lot of improvements in the IRC client
* Bug fixed in microsoft fonts
* Added POL_SetupWindow_pulsebar, pulse and settext

# 3.0.1

* A bug corrected in 3.0
* 4 New functions : Set_SoundSampleRate, Set_SoundBitsPerSample, Set_SoundHardwareAcceleration, Set_SoundEmulDriver

# 3.0

* POL_SetupWindow support (a setup box for scriptors)
* New GUIs
* POL is is .po files
* New wine version support GUI
* Minor corrections in IRC
* A lot of new fonction
* Use_WineVersion function

# 2.7.2

* message_one function added (Scriptors can add a box "No more alert me")
* Tools menu improved : wine tools are no more accessible for non-wine shortcuts
* wineversion fixed
* irc improved
* manque() function added after check_depend
* new dependance : lzma for wineversion

# 2.7.1

* Bug fixed in Ubuntu deb packages

# 2.7

* Color in IRC chat
* Plugin manager made
* Dosbox becomes a plugin
* PlayOnLinux show a warning if it is lanched at root
* Icons added for wait, download and upgrade available
* Lot of bugs in translation fixed
* Changelog updated

# 2.6.1

* A security problem corrected
* A bug fixed

# 2.6

* A lot of improvement in IRC chat
* An Option GUI
* A lot of settings added

# 2.5

* IRC Chat integrated
* Lynx dependances does exists any more
* Install menu bug fixed

# 2.3

* New install menu
* Lot of bugs fixed

# 2.2.1

* French sentance translated
* Languages files corrected
* New dependance : cabextract
* Fonts installation problem corrected

# 2.2

* New menu more user friendly
* Autorun automated installer
* Community and workonlinux doesn't exists anymore
* Ask_For_cdrom improved
* Fixed bugs in package manager
* Lot of translations
* Lot of commands translated in english

# 2.1

* Dialog are pretty more comprehensible
* Langage panels corrected
* All the file in the same languages
* About window translated
* Hungarian translation
* .pol package manager
* A new logo
* LiveInstall is called "Manual installation"
* Bug corrected in icons installation
* Wine GIT in wineversion menu

# 2.0.10

* Wineversion bug fix
* WinGit bug fix

# 2.0.9

* creer_prefixe runs fonts-to-prefix
* Microsoft fonts problem solved
* Some french message are translated

# 2.0.7

* Russian translation
* Polish translation
* Italian correction
* --run refixed

# 2.0.6

* Italian translation
* --run problem solved
* English corrected

# 2.0.5

* Wine Look added
* Expert menu is "Tools"
* New function : browser and OpenWineLookBox
* Functions translation (erreur > error, etc...)

# 2.0.4

* Fix LiveInstall
* German translation
* Improvements in french languages files
* Two more function : Set_Desktop and Set_Iexplore

# 2.0.3

* Added dosbox support
* Check_cdrom ask for a new mount point  instead of canceling the installation when the cdrom is not in the drive

# 2.0.2

* Wine GIT added
* Wine Booster 2 Added

# 2.0.1

* Downloading plugin improved (Start automatically to download is possible)
* Python 2.4 and by the way, debian compatibility
* Check if PlayOnLinux is running at startup

# 2.0

* All the GUI is remade with wx-python
* Scripts are more configurable (Cf PlayOnLinux doc)
* Improved prefix support
* Prefix are detected
* PlayOnLinux is more user-friendly
* Kill wineserver process in expert menu
* DirectX in one downloading
* tahoma fonts support
* All the window remade with wx python
* Zenity, kdialog, xdialog and dialog are no more used
* winemaster and winebooster are temporarely unavailable
* Possibility to run several programs in the same time
* Added Set_WineVersion_Assign and Set_WineVersion_Session
* New download plugin
* Possibility to delete shortcut without deleting the prefix
* "About" window
* Licence : GPL-v3
* One menu for all the games (Valable pour le menu expert)
* Different script repository from 1.8
* attendre_multiple does work any more


# 1.8

* PlayOnLinux menu in gnome
* WorkOnLinux support
* Big differences in scripts downloading : playonlinux do not download all thescripts available.
* Add check_pol_update and check_network
* Polshell added
* Old version are not more supported

# 1.7.4

* Third website adress. Moving to playonlinux.com
* Some bug fixed

# 1.7.2

* Lot of bugs fixed
* PolScriptCreator added
* LiveInstall added
* GLX tests remade
* Some commands for translators
* creer_lanceur and creer_lanceur_expansion are the same

# 1.7.1

* Add directx in the expert menu
* Add information menu in options
* WineMaster added

# 1.7

* Options menu added
* Tests added
* New adress for the website
* French and english are available
* Official and community repository
* Microsoft fonts support
* Update question is not at running but a installation
* Kdialog (QT) or zenity (GTK) choice is available
* Lot of bug fixed

# 1.6.3

* Added wineversion tools. It permits you to run differents wine version in
PlayOnLinux
* Bug corrected in add-on menu

# 1.6.2

* The script can make a shortcut in your desktop for you
* Menus are reorganized
* Expert menu added
* "BaseDeRegistre", "WineConfig", "WineBooster", "UpdatePrefixe"
and "Executer" tools are added
* Possibilites to run non-official scripts

# 1.6

* Added KDE support with Kdialog

# 1.5

* Add-On support

# 1.4

* More commands like "simuler_reboot" in libraries
* wine lib added

# 1.2

* PlayOnLinux lib are made for scriptors.
* PlayOnLinux is ready to work on KDE with kdialog

# 1.1

* "Play" menu added
* The shortcut are not more in ~/bin

# 1.0

* Zenity integration

# 0.8

* The script is working since first execution
* No more need to exec it twice
* Lot of bug fixed

# 0.7

* .deb and .tar.gz available
* PlayOnLinux ask at startup if the user want to upgrade

# 0.6

* Lot of bugs in install menu and update fixed

# 0.5

* Added patch support
* PlayOnLinux check that dialog is installed before executing

# 0.4

* Add uninstall menu
* Bug fixed in install menu

# 0.3

* Using dialog GUI
* Lot of bugs fixed

# 0.2

* Dependances detection at execution
* Fix a bug on script execution

# 0.1

* First version of PlayOnLinux.
* Upgrades available from the website.
* No GUI, all in a shell
