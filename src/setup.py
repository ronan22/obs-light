#!/usr/bin/env python

from distutils.core import setup
import distutils.command.build


class build_obslight(distutils.command.build.build, object):
    """
    Custom build command which generates man page.
    """


    def run(self):
        super(build_obslight, self).run()
        

addparams = {}

data_files = []
#if sys.platform[:3] != 'win':
#    data_files.append((os.path.join('share'), [os.path.join('build', 'obslight.0.1.gz')]))


setup(name='obslight',
      version = "0.3",
      description = 'OBS Light',
      long_description = 'Command-line client and UI for the OBS.',
      author = 'Ronan Le Martret',
      author_email = 'ronan@fridu.net',
      license = 'GPLv2',
      platforms = ['Linux'],
      keywords = ['MeeGo','OBS', 'chroot', 'RPM', 'build', 'buildservice'],
      url = 'http://wiki.meego.com/OBS_Light',
      download_url = 'https://meego.gitorious.org/meego-developer-tools/obs-light',

      packages = ['ObsLight', 'ObsLight.util', 'ObsLightGui'],
      package_data = {'ObsLightGui' : ['ui/*.ui']},
      scripts = ['obslight-wrapper.py', 'obslightgui-wrapper.py',
                 'script/obstag', 'script/obs2obscopy', 'script/obsextractgroups'],
      provides = ['ObsLight', 'ObsLightGui'],
      requires = ['osc (>=0.132.5)', 'xml.etree.ElementTree'],
      data_files = data_files,
      
      
      cmdclass = {
        'build': build_obslight,
        },
      **addparams
     )
