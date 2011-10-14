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

<<<<<<< HEAD
setup(name='obslight',
      version = "0.1",
=======

setup(name='obslight',
      version = "0.3",
>>>>>>> 0f14dab9ce584c8b24463b4d79e1cbba05d90668
      description = 'OBS Light',
      long_description = 'Command-line client and UI for the OBS.',
      author = 'Ronan Le Martret',
      author_email = 'ronan@fridu.net',
<<<<<<< HEAD
      license = 'GPL',
=======
      license = 'GPLv2',
>>>>>>> 0f14dab9ce584c8b24463b4d79e1cbba05d90668
      platforms = ['Linux'],
      keywords = ['MeeGo','OBS', 'chroot', 'RPM', 'build', 'buildservice'],
      url = 'http://wiki.meego.com/OBS_Light',
      download_url = 'https://meego.gitorious.org/meego-developer-tools/obs-light',

<<<<<<< HEAD
      packages = ['OBSLight', 'OBSLight.util'],
      scripts = ['obslight-wrapper.py'],
=======
      packages = ['OBSLight', 'OBSLight.util', 'OBSLightGui'],
      package_data = {'OBSLightGui' : ['ui/*.ui']},
      scripts = ['obslight-wrapper.py', 'obslightgui-wrapper.py',
                 'script/obstag', 'script/obs2obscopy', 'script/obsextractgroups'],
      provides = ['OBSLight', 'OBSLightGui'],
      requires = ['osc (>=0.132.5)', 'xml.etree.ElementTree'],
>>>>>>> 0f14dab9ce584c8b24463b4d79e1cbba05d90668
      data_files = data_files,
      
      
      cmdclass = {
        'build': build_obslight,
        },
      **addparams
     )














