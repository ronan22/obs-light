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

if __name__ == '__main__':
    unittest.main()
