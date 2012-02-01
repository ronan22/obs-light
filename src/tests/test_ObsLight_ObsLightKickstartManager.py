import unittest
import os.path

from ObsLight.ObsLightKickstartManager import ObsLightKickstartManager

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "ObsLightKickstartManager_fixtures")

class TestObsLightKickstartManager(unittest.TestCase):

    validKs = os.path.join(FIXTURE_DIR, "Tablet-armv7hl-tegra2-v02.ks")
    origPkgList = ['evtest', 'xorg-x11-drv-evdev', 'xorg-x11-utils-xinput',
                   'xorg-x11-drv-mtev', 'xorg-x11-utils-xev', 'qt-demos',
                   'mesa-libGL', 'xinput_calibrator']
    origExcludedPkgList = ['dsme', 'libdsme']
    origGroupList = ['@MeeGo Core', '@MeeGo X Window System',
                     '@MeeGo Tablet', '@MeeGo Tablet Applications',
                     '@X for Netbooks', '@MeeGo Base Development',
                     '@Development Tools']
    origRepoList = ['1.2-oss', '1.2-non-oss']

    def test___init__(self):
        self.assertIsInstance(ObsLightKickstartManager(), ObsLightKickstartManager)

    def test_getPackageGroupList(self):
        obs_light_kickstart_manager = ObsLightKickstartManager(self.validKs)
        self.assertItemsEqual(self.origGroupList, obs_light_kickstart_manager.getPackageGroupList())

    def test_getPackageList(self):
        obs_light_kickstart_manager = ObsLightKickstartManager(self.validKs)
        self.assertItemsEqual(self.origPkgList, obs_light_kickstart_manager.getPackageList())

    def test_getExcludedPackageList(self):
        obs_light_kickstart_manager = ObsLightKickstartManager(self.validKs)
        self.assertItemsEqual(self.origExcludedPkgList,
                         obs_light_kickstart_manager.getExcludedPackageList())

    def test_getRepositoryList(self):
        obs_light_kickstart_manager = ObsLightKickstartManager(self.validKs)
        self.assertItemsEqual(self.origRepoList, obs_light_kickstart_manager.getRepositoryList())

    def test_kickstartPath(self):
        obs_light_kickstart_manager = ObsLightKickstartManager(self.validKs)
        self.assertEqual(self.validKs, obs_light_kickstart_manager.kickstartPath)
        obs_light_kickstart_manager.kickstartPath = None
        self.assertEqual(None, obs_light_kickstart_manager.kickstartPath)

    def test_kickstartPath_case_2(self):
        # Auto-generated but useless
        pass

    def test_parseKickstart(self):
        obs_light_kickstart_manager = ObsLightKickstartManager()
        obs_light_kickstart_manager.kickstartPath = self.validKs
        self.assertEqual(None, obs_light_kickstart_manager.parseKickstart())

    def test_addRepositoryByConfigLine(self):
        obs_light_kickstart_manager = ObsLightKickstartManager(self.validKs)
        cfgLine = "repo --name=adobe --baseurl=http://linuxdownload.adobe.com/linux/i386/ --save"
        expectedList = ["adobe"] + self.origRepoList
        self.assertEqual(None, obs_light_kickstart_manager.addRepositoryByConfigLine(cfgLine))
        self.assertItemsEqual(expectedList, obs_light_kickstart_manager.getRepositoryList())

    def test_addPackage(self):
        obs_light_kickstart_manager = ObsLightKickstartManager(self.validKs)
        expectedList = list(self.origPkgList)
        expectedList.append('vim')
        self.assertEqual(None, obs_light_kickstart_manager.addPackage('vim'))
        self.assertItemsEqual(expectedList, obs_light_kickstart_manager.getPackageList())
        self.assertItemsEqual(self.origExcludedPkgList,
                              obs_light_kickstart_manager.getExcludedPackageList())

    def test_addExcludedPackage(self):
        obs_light_kickstart_manager = ObsLightKickstartManager(self.validKs)
        expectedList = ['vim'] + self.origExcludedPkgList
        self.assertEqual(None, obs_light_kickstart_manager.addExcludedPackage('vim'))
        self.assertItemsEqual(expectedList, obs_light_kickstart_manager.getExcludedPackageList())
        self.assertItemsEqual(self.origPkgList, obs_light_kickstart_manager.getPackageList())


if __name__ == '__main__':
    unittest.main()
