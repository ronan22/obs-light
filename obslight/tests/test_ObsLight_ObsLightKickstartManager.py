import unittest
import os.path

from pykickstart.parser import KickstartParser

from ObsLight.ObsLightKickstartManager import ObsLightKickstartManager

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "ObsLightKickstartManager_fixtures")

class TestObsLightKickstartManager(unittest.TestCase):

    validKs = os.path.join(FIXTURE_DIR, "Tablet-armv7hl-tegra2-v02.ks")
    origPkgList = ['evtest', 'xorg-x11-drv-evdev', 'xorg-x11-utils-xinput',
                   'xorg-x11-drv-mtev', 'xorg-x11-utils-xev', 'qt-demos',
                   'mesa-libGL', 'xinput_calibrator']
    origExcludedPkgList = ['dsme', 'libdsme']
    origGroupList = ['MeeGo Core', 'MeeGo X Window System',
                     'MeeGo Tablet', 'MeeGo Tablet Applications',
                     'X for Netbooks', 'MeeGo Base Development',
                     'Development Tools']
    origRepoList = ['1.2-oss', '1.2-non-oss']
    origRepoDict = {'debuginfo': True,
                    'baseurl': 'http://download.meego.com/snapshots/1.2.0.90.8.20110713.4/repos/oss/armv7hl/packages/',
                    'proxy_password': None, 'disable': False,
                    'includepkgs': [], 'ssl_verify': 'yes',
                    'excludepkgs': [], 'name': '1.2-oss',
                    'gpgkey': 'file:///etc/pki/rpm-gpg/RPM-GPG-KEY-meego',
                    'mirrorlist': '', 'priority': None, 'source': True,
                    'cost': None, 'proxy_username': None, 'save': True, 'proxy': None}

    fullCommandList = ['user', 'logvol', 'firewall', 'selinux', 'firstboot',
                       'reboot', 'cdrom', 'poweroff', 'shutdown', 'keyboard',
                       'timezone', 'skipx', 'multipath', 'rescue', 'dmraid',
                       'upgrade', 'group', 'monitor', 'autopart', 'deviceprobe',
                       'ignoredisk', 'iscsi', 'raid', 'clearpart', 'desktop',
                       'iscsiname', 'device', 'text', 'zerombr', 'rootpw',
                       'mediacheck', 'graphical', 'vnc', 'halt', 'auth',
                       'autostep', 'authconfig', 'part', 'updates', 'key',
                       'services', 'sshpw', 'bootloader', 'network', 'lang',
                       'zfcp', 'logging', 'xconfig', 'cmdline', 'url',
                       'partition', 'harddrive', 'volgroup', 'driverdisk',
                       'nfs', 'fcoe', 'install', 'interactive']

    fullCmdDictList = [{'generated_text': '# Installation logging level\nlogging --level=info\n',
                        'aliases': ['logging'], 'name': 'logging', 'in_use': True},
                       {'generated_text': '', 'aliases': ['ignoredisk'],
                        'name': 'ignoredisk', 'in_use': False},
                       {'generated_text': '', 'aliases': ['zerombr'],
                        'name': 'zerombr', 'in_use': False},
                       {'generated_text': '# Root password\nrootpw --plaintext meego\n',
                        'aliases': ['rootpw'], 'name': 'rootpw', 'in_use': True},
                       {'generated_text': '', 'aliases': ['key'], 'name': 'key',
                        'in_use': False},
                       {'generated_text': '', 'aliases': ['mediacheck'],
                        'name': 'mediacheck', 'in_use': False},
                       {'generated_text': '# System authorization information\n' +
                        'auth --useshadow --enablemd5\n',
                        'aliases': ['auth', 'authconfig'], 'name': 'auth', 'in_use': True},
                       {'generated_text': '# System keyboard\nkeyboard us\n',
                        'aliases': ['keyboard'], 'name': 'keyboard', 'in_use': True},
                       {'generated_text': '', 'aliases': ['autostep'],
                        'name': 'autostep', 'in_use': False},
                       {'generated_text': '', 'aliases': ['text', 'graphical', 'cmdline'],
                        'name': 'text', 'in_use': False},
                       {'generated_text': '# Disk partitioning information\n' +
                        'part /boot --active --fstype="ext2" --ondisk=mmcblk0p --size=64\n' +
                        'part / --fstype="ext3" --ondisk=mmcblk0p --size=1600\n',
                        'aliases': ['part', 'partition'], 'name': 'part', 'in_use': True},
                       {'generated_text': '', 'aliases': ['logvol'],
                        'name': 'logvol', 'in_use': False},
                       {'generated_text': '', 'aliases': ['device'],
                        'name': 'device', 'in_use': False},
                       {'generated_text': '', 'aliases': ['updates'],
                        'name': 'updates', 'in_use': False},
                       {'generated_text': '', 'aliases': ['cdrom', 'url', 'harddrive', 'nfs'],
                        'name': 'cdrom', 'in_use': False},
                       {'generated_text': '# X Window System configuration information\n' +
                        'xconfig  --startxonboot\n', 'aliases': ['xconfig'],
                        'name': 'xconfig', 'in_use': True},
                       {'generated_text': '', 'aliases': ['volgroup'],
                        'name': 'volgroup', 'in_use': False},
                       {'generated_text': '', 'aliases': ['selinux'],
                        'name': 'selinux', 'in_use': False},
                       {'generated_text': '', 'aliases': ['interactive'],
                        'name': 'interactive', 'in_use': False},
                       {'generated_text': '', 'aliases': ['firstboot'],
                        'name': 'firstboot', 'in_use': False},
                       {'generated_text': '', 'aliases': ['sshpw'],
                        'name': 'sshpw', 'in_use': False},
                       {'generated_text': '# System timezone\n' +
                        'timezone --isUtc America/Los_Angeles\n', 'aliases': ['timezone'],
                        'name': 'timezone', 'in_use': True},
                       {'generated_text': '', 'aliases': ['firewall'],
                        'name': 'firewall', 'in_use': False},
                       {'generated_text': '', 'aliases': ['zfcp'],
                        'name': 'zfcp', 'in_use': False},
                       {'generated_text': '', 'aliases': ['rescue'],
                        'name': 'rescue', 'in_use': False},
                       {'generated_text': '', 'aliases': ['clearpart'],
                        'name': 'clearpart', 'in_use': False},
                       {'generated_text': '', 'aliases': ['network'],
                        'name': 'network', 'in_use': False},
                       {'generated_text': '', 'aliases': ['iscsi'],
                        'name': 'iscsi', 'in_use': False},
                       {'generated_text': '\n',
                        'aliases': ['reboot', 'poweroff', 'shutdown', 'halt'],
                        'name': 'reboot', 'in_use': False},
                       {'generated_text': '', 'aliases': ['bootloader'],
                        'name': 'bootloader', 'in_use': False},
                       {'generated_text': '', 'aliases': ['fcoe'],
                        'name': 'fcoe', 'in_use': False},
                       {'generated_text': '', 'aliases': ['raid'],
                        'name': 'raid', 'in_use': False},
                       {'generated_text': '', 'aliases': ['skipx'],
                        'name': 'skipx', 'in_use': False},
                       {'generated_text': '', 'aliases': ['vnc'],
                        'name': 'vnc', 'in_use': False},
                       {'generated_text': '', 'aliases': ['driverdisk'],
                        'name': 'driverdisk', 'in_use': False},
                       {'generated_text': '', 'aliases': ['multipath'],
                        'name': 'multipath', 'in_use': False},
                       {'generated_text': '', 'aliases': ['dmraid'],
                        'name': 'dmraid', 'in_use': False},
                       {'generated_text': '', 'aliases': ['services'],
                        'name': 'services', 'in_use': False},
                       {'generated_text':
                            'user --groups=audio,video --name=meego --password=meego\n',
                        'aliases': ['user'], 'name': 'user', 'in_use': True},
                       {'generated_text': '', 'aliases': ['group'],
                        'name': 'group', 'in_use': False},
                       {'generated_text': '# System language\nlang en_US.UTF-8\n',
                        'aliases': ['lang'], 'name': 'lang', 'in_use': True},
                       {'generated_text': '', 'aliases': ['monitor'],
                        'name': 'monitor', 'in_use': False},
                       {'generated_text': '', 'aliases': ['autopart'],
                        'name': 'autopart', 'in_use': False},
                       {'generated_text': '', 'aliases': ['upgrade', 'install'],
                        'name': 'upgrade', 'in_use': False},
                       {'generated_text': '', 'aliases': ['deviceprobe'],
                        'name': 'deviceprobe', 'in_use': False},
                       {'generated_text': '# Default Desktop Settings\n' +
                       'desktop  --autologinuser=meego\n', 'aliases': ['desktop'],
                       'name': 'desktop', 'in_use': True},
                       {'generated_text': '', 'aliases': ['iscsiname'],
                        'name': 'iscsiname', 'in_use': False}]

    fullScriptDictList = [{'name': 'script 0',
                           'script': '# save a little bit of space at least...\n' +
                           'rm -f /boot/initrd*\n\nrm -f /var/lib/rpm/__db*\n' +
                           'rpm --rebuilddb\n\n' +
                           'echo "DISPLAYMANAGER=\\"uxlaunch\\"" >> /etc/sysconfig/desktop\n' +
                           'echo "session=/usr/bin/mcompositor" >> /etc/sysconfig/uxlaunch\n\n' +
                           '#echo "xopts=-nocursor" >> /etc/sysconfig/uxlaunch\n\n' +
                           'gconftool-2 --direct \\\n' +
                           '  --config-source xml:readwrite:/etc/gconf/gconf.xml.mandatory \\\n' +
                           '  -s -t string /meegotouch/target/name tablet\n\n' +
                           'gconftool-2 --direct \\\n' +
                           '  --config-source xml:readwrite:/etc/gconf/gconf.xml.mandatory \\\n' +
                           '  -s -t string /meego/ux/theme 1024-600-10\n\n' +
                           'gconftool-2 --direct \\\n' +
                           '  --config-source xml:readwrite:/etc/gconf/gconf.xml.defaults \\\n' +
                           '  -s -t bool /meego/ux/ShowPanelsAsHome false\n\n' +
                           '# Copy boot and shutdown images\n' +
                           'cp /usr/share/themes/1024-600-10/images/system/boot-screen.png ' +
                           '/usr/share/plymouth/splash.png\n' +
                           'cp /usr/share/themes/1024-600-10/images/system/shutdown-screen.png ' +
                           '/usr/share/plymouth/shutdown-1024x600.png\n\n',
                           'preceededInclude': None, 'interp': '/bin/sh',
                           'errorOnFail': False, 'inChroot': True, 'logfile': None, 'type': 1},
                          {'name': 'script 1',
                           'script': 'if [ -n "$IMG_NAME" ]; then\n' +
                           '    echo "BUILD: $IMG_NAME" >> $INSTALL_ROOT/etc/meego-release\n' +
                           'fi\n' +
                           '#echo \'export M_USE_SOFTWARE_RENDERING=1\' >> $INSTALL_ROOT/home/meego/.bashrc\n\n' +
                           'cat << OMAPFB >> $INSTALL_ROOT/etc/X11/xorg.conf.d/00-input-trimslice.conf\n' +
                           'Section "InputClass"\n        Identifier "evdev pointer catchall"\n' +
                           '        MatchIsPointer "on"\n' +
                           '        MatchDevicePath "/dev/input/event*"\n' +
                           '        Driver "evdev"\nEndSection\n\nSection "InputClass"\n' +
                           '        Identifier "evdev keyboard catchall"\n' +
                           '        MatchIsKeyboard "on"\n' +
                           '        MatchDevicePath "/dev/input/event*"\n' +
                           '        Driver "evdev"\nEndSection\n\nSection "InputClass"\n' +
                           '        Identifier "evdev touchpad catchall"\n' +
                           '        MatchIsTouchpad "on"\n' +
                           '        MatchDevicePath "/dev/input/event*"\n' +
                           '        Driver "evdev"\nEndSection\n\n' +
                           'Section "InputClass"\n' +
                           '        Identifier "evdev tablet catchall"\n' +
                           '        MatchIsTablet "on"\n' +
                           '        MatchDevicePath "/dev/input/event*"\n' +
                           '        Driver "evdev"\nEndSection\n\nSection "InputClass"\n' +
                           '        Identifier "evdev touchscreen catchall"\n' +
                           '        MatchIsTouchscreen "on"\n' +
                           '        MatchDevicePath "/dev/input/event*"\n' +
                           '        Driver "evdev"\nEndSection\nOMAPFB\n\n' +
                           '# Add Meego to sudoers list\n' +
                           'cat << SUDOERS >> $INSTALL_ROOT/etc/sudoers\n' +
                           'meego ALL=(ALL) ALL\nSUDOERS\n',
                           'preceededInclude': None, 'interp': '/bin/sh',
                           'errorOnFail': False, 'inChroot': False, 'logfile': None, 'type': 1}]

    def setUp(self):
        self.ksManager = ObsLightKickstartManager(self.validKs)

    def test___init__(self):
        self.assertIsInstance(ObsLightKickstartManager(), ObsLightKickstartManager)

    def test_getPackageGroupList(self):
        self.assertItemsEqual(self.origGroupList, self.ksManager.getPackageGroupList())

    def test_getPackageList(self):
        self.assertItemsEqual(self.origPkgList, self.ksManager.getPackageList())

    def test_getExcludedPackageList(self):
        self.assertItemsEqual(self.origExcludedPkgList,
                         self.ksManager.getExcludedPackageList())

    def test_getRepositoryList(self):
        self.assertItemsEqual(self.origRepoList, self.ksManager.getRepositoryList())

    def test_kickstartPath(self):
        self.assertEqual(self.validKs, self.ksManager.kickstartPath)
        self.ksManager.kickstartPath = None
        self.assertEqual(None, self.ksManager.kickstartPath)

    def test_kickstartPath_case_2(self):
        # Auto-generated but useless
        pass

    def test_kickstartParser(self):
        ksManager = ObsLightKickstartManager()
        self.assertIsNone(ksManager.kickstartParser)
        ksManager.kickstartPath = self.validKs
        ksManager.parseKickstart()
        self.assertIsInstance(ksManager.kickstartParser, KickstartParser)

    def test_parseKickstart(self):
        ksManager = ObsLightKickstartManager()
        ksManager.kickstartPath = self.validKs
        self.assertIsNone(ksManager.parseKickstart())

    def test_addRepositoryByConfigLine(self):
        cfgLine = "repo --name=adobe --baseurl=http://linuxdownload.adobe.com/linux/i386/ --save"
        expectedList = ["adobe"] + self.origRepoList
        self.assertEqual(None, self.ksManager.addRepositoryByConfigLine(cfgLine))
        self.assertItemsEqual(expectedList, self.ksManager.getRepositoryList())

    def test_addPackage(self):
        expectedList = list(self.origPkgList)
        expectedList.append("vim")
        self.assertIsNone(self.ksManager.addPackage("vim"))
        self.assertItemsEqual(expectedList, self.ksManager.getPackageList())
        expectedList.append("emacs")
        expectedList.append("nano")
        self.assertIsNone(self.ksManager.addPackage(["emacs", "nano"]))
        self.assertItemsEqual(expectedList, self.ksManager.getPackageList())
        self.assertItemsEqual(self.origExcludedPkgList,
                              self.ksManager.getExcludedPackageList())

    def test_addExcludedPackage(self):
        expectedList = ["vim"] + self.origExcludedPkgList
        self.assertEqual(None, self.ksManager.addExcludedPackage("vim"))
        self.assertItemsEqual(expectedList, self.ksManager.getExcludedPackageList())
        self.assertItemsEqual(self.origPkgList, self.ksManager.getPackageList())

    def test_removePackage(self):
        expectedList = list(self.origPkgList)
        expectedList.remove("qt-demos")
        self.assertEqual(None, self.ksManager.removePackage("qt-demos"))
        self.assertItemsEqual(expectedList, self.ksManager.getPackageList())
        self.assertItemsEqual(self.origExcludedPkgList,
                              self.ksManager.getExcludedPackageList())

    def test_removeExcludedPackage(self):
        expectedList = list(self.origExcludedPkgList)
        expectedList.remove("dsme")
        self.assertEqual(None, self.ksManager.removeExcludedPackage("dsme"))
        self.assertItemsEqual(expectedList, self.ksManager.getExcludedPackageList())
        self.assertItemsEqual(self.origPkgList, self.ksManager.getPackageList())

    def test_addRepository(self):
        expectedList = ["adobe"] + self.origRepoList
        self.ksManager.addRepository("http://linuxdownload.adobe.com/linux/i386/",
                                                  "adobe", cost=99, save=True)
        self.assertItemsEqual(expectedList, self.ksManager.getRepositoryList())

    def test_removeRepository(self):
        expectedList = list(self.origRepoList)
        expectedList.remove("1.2-non-oss")
        self.assertIsNone(self.ksManager.removeRepository("1.2-non-oss"))
        self.assertItemsEqual(expectedList, self.ksManager.getRepositoryList())

    def test_getRepositoryDict(self):
        myDict = self.ksManager.getRepositoryDict("1.2-oss")
        self.assertDictEqual(self.origRepoDict, myDict)

    def test_scenario_getRemoveAddRepo(self):
        myDict = self.ksManager.getRepositoryDict("1.2-oss")
        self.assertDictEqual(self.origRepoDict, myDict)
        self.ksManager.removeRepository("1.2-oss")
        expectedList = list(self.origRepoList)
        expectedList.remove("1.2-oss")
        self.assertItemsEqual(expectedList, self.ksManager.getRepositoryList())
        self.ksManager.addRepository(**myDict)
        self.assertItemsEqual(self.origRepoList, self.ksManager.getRepositoryList())

    def test_addPackageGroup(self):
        expectedList = list(self.origGroupList)
        expectedList.append("MyPkgGroup")
        self.assertIsNone(self.ksManager.addPackageGroup("MyPkgGroup"))
        self.assertListEqual(expectedList, self.ksManager.getPackageGroupList())

    def test_removePackageGroup(self):
        expectedList = list(self.origGroupList)
        expectedList.remove('Development Tools')
        self.assertIsNone(self.ksManager.removePackageGroup('Development Tools'))
        self.assertListEqual(expectedList, self.ksManager.getPackageGroupList())

    def test_saveKickstart(self):
        self.assertIsNone(self.ksManager.saveKickstart("/tmp/test.ks"))

    def test_addOrChangeCommand(self):
        assert False

    def test_addOrChangeScript(self):
        # obs_light_kickstart_manager = ObsLightKickstartManager(kickstartPath)
        # self.assertEqual(expected, obs_light_kickstart_manager.addOrChangeScript(name, script, **kwargs))
        assert False # TODO: implement your test here

    def test_addOverlayFile(self):
        # obs_light_kickstart_manager = ObsLightKickstartManager(kickstartPath)
        # self.assertEqual(expected, obs_light_kickstart_manager.addOverlayFile(source, destination))
        assert False # TODO: implement your test here

    def test_getCommandList(self):
        self.assertListEqual(self.fullCommandList, self.ksManager.getCommandList())

    def test_getFilteredCommandDictList(self):
        expected = list(self.fullCmdDictList)
        expected.sort()
        got = self.ksManager.getFilteredCommandDictList()
        got.sort()
        self.assertListEqual(expected, got)

    def test_getOverlayFileDictList(self):
        # obs_light_kickstart_manager = ObsLightKickstartManager(kickstartPath)
        # self.assertEqual(expected, obs_light_kickstart_manager.getOverlayFileDictList())
        assert False # TODO: implement your test here

    def test_getScriptDictList(self):
        expected = list(self.fullScriptDictList)
        expected.sort()
        got = self.ksManager.getScriptDictList()
        got.sort()
        self.assertListEqual(expected, got)

    def test_removeCommand(self):
        expected = [x for x in self.fullCmdDictList if (x["name"] != "keyboard"
                                                        and x["in_use"] is True)]
        expected.sort()
        self.assertIsNone(self.ksManager.removeCommand("keyboard"))
        got = self.ksManager.getFilteredCommandDictList()
        got = [x for x in got if x["in_use"] is True]
        got.sort()
        self.assertListEqual(expected, got)

    def test_removeOverlayFile(self):
        # obs_light_kickstart_manager = ObsLightKickstartManager(kickstartPath)
        # self.assertEqual(expected, obs_light_kickstart_manager.removeOverlayFile(source, destination))
        assert False # TODO: implement your test here

    def test_removeScript(self):
        expected = self.fullScriptDictList[:1]
        expected.sort()
        self.assertIsNone(self.ksManager.removeScript('script 1'))
        got = self.ksManager.getScriptDictList()
        self.assertListEqual(expected, got)

if __name__ == '__main__':
    unittest.main()
