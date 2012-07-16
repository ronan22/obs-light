#!/usr/bin/env python

from distutils.core import setup
import distutils.command.build


class build_obslight(distutils.command.build.build, object):
    """
    Custom build command which generates man page.
    """


    def run(self):
        super(build_obslight, self).run()



setup(name='obslight',
      version="0.5.1",
      description='OBS Light',
      long_description='Command-line client , UI and tools for the OBS.',
      author='Ronan Le Martret',
      author_email='ronan@fridu.net',
      license='GPLv2',
      platforms=['Linux'],
      keywords=['MeeGo', 'OBS', 'chroot', 'RPM', 'build', 'buildservice'],
      url='http://en.opensuse.org/openSUSE:OBS_Light',
      download_url='https://meego.gitorious.org/meego-developer-tools/obs-light',

      packages=['ObsLight', 'ObsLight.util', 'ObsLightGui', 'ObsLightGui.Wizard'],
      package_data={'ObsLightGui' : ['ui/*.ui', 'ui/*.png'],
                    'ObsLight' : ['emptySpec/empty*',
                                  'config/ObslightConfig']},
      scripts=['obslight-wrapper.py',
               'obslightgui-wrapper.py',
               'script/obstag',
               'script/obs2obscopy',
               'script/obsextractgroups',
	            'script/obsdodupdate',
                'script/obsprojectsdiff'],
      provides=['ObsLight', 'ObsLightGui'],
      requires=['osc (>=0.132.5)', 'xml.etree.ElementTree'],
      data_files=[('/etc', ['sudoers.obslight']),
                  ('/etc/bash_completion.d/', ['obslight.sh']),
                  ('/usr/share/applications/', ['obslightgui.desktop']),
                  ('/usr/share/pixmaps/', ['ObsLightGui/ui/obslight.png']),
                  ('/etc/xinetd.d/', ['ObsLightServer/tftp']),
                  ('/srv/obslight-image-server/config', ['ObsLightServer/obslight-image.apache2conf']),
                  ('/srv/obslight-repo-server/config', ['ObsLightServer/obslight-repos.apache2conf'])],

      cmdclass={
        'build': build_obslight,
        }
     )
