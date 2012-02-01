import unittest
import os.path

from ObsLight.ObsLightKickstartManager import ObsLightKickstartManager

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "ObsLightKickstartManager_fixtures")

class TestObsLightKickstartManager(unittest.TestCase):
    def test___init__(self):
        self.assertIsInstance(ObsLightKickstartManager(), ObsLightKickstartManager)

    def test_getPackageGroupList(self):
        ks = os.path.join(FIXTURE_DIR, "Tablet-armv7hl-tegra2-v02.ks")
        obs_light_kickstart_manager = ObsLightKickstartManager(ks)
        expectedList = ['@MeeGo Core', '@MeeGo X Window System',
                        '@MeeGo Tablet', '@MeeGo Tablet Applications',
                        '@X for Netbooks', '@MeeGo Base Development',
                        '@Development Tools']
        self.assertEqual(expectedList, obs_light_kickstart_manager.getPackageGroupList())

    def test_getPackageList(self):
        ks = os.path.join(FIXTURE_DIR, "Tablet-armv7hl-tegra2-v02.ks")
        obs_light_kickstart_manager = ObsLightKickstartManager(ks)
        expectedList = ['evtest', 'xorg-x11-drv-evdev', 'xorg-x11-utils-xinput',
                        'xorg-x11-drv-mtev', 'xorg-x11-utils-xev', 'qt-demos',
                        'mesa-libGL', 'xinput_calibrator']
        self.assertEqual(expectedList, obs_light_kickstart_manager.getPackageList())

    def test_getRepositoryList(self):
        ks = os.path.join(FIXTURE_DIR, "Tablet-armv7hl-tegra2-v02.ks")
        obs_light_kickstart_manager = ObsLightKickstartManager(ks)
        expectedList = ['1.2-oss', '1.2-non-oss']
        self.assertEqual(expectedList, obs_light_kickstart_manager.getRepositoryList())

    def test_kickstartPath(self):
        ks = os.path.join(FIXTURE_DIR, "Tablet-armv7hl-tegra2-v02.ks")
        obs_light_kickstart_manager = ObsLightKickstartManager(ks)
        self.assertEqual(ks, obs_light_kickstart_manager.kickstartPath)
        obs_light_kickstart_manager.kickstartPath = None
        self.assertEqual(None, obs_light_kickstart_manager.kickstartPath)

    def test_kickstartPath_case_2(self):
        # Auto-generated but useless
        pass

    def test_parseKickstart(self):
        ks = os.path.join(FIXTURE_DIR, "Tablet-armv7hl-tegra2-v02.ks")
        obs_light_kickstart_manager = ObsLightKickstartManager()
        obs_light_kickstart_manager.kickstartPath = ks
        self.assertEqual(None, obs_light_kickstart_manager.parseKickstart())

if __name__ == '__main__':
    unittest.main()
