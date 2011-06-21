#!/usr/bin/env python

from distutils.core import setup
import distutils.command.build
import distutils.command.install_data
import os.path


import OBSLight.OBSLightManager
from OBSLight import OBSLightManager
from OBSLight import OBSLightTools



class build_osc(distutils.command.build.build, object):
    """
    Custom build command which generates man page.
    """

    def build_man_page(self):
        """
        
        """
        import gzip
        man_path = os.path.join('build', 'obslight.0.1.gz')
        distutils.log.info('generating %s' % man_path)
        outfile = gzip.open(man_path, 'w')
        osccli = commandline.Osc(stdout = outfile)
        # FIXME: we cannot call the main method because osc expects an ~/.oscrc file
        # (this would break builds in environments like the obs)
        #osccli.main(argv = ['osc','man'])
        osccli.optparser = osccli.get_optparser()
        osccli.do_man(None)
        outfile.close()

    def run(self):
        super(build_osc, self).run()
        self.build_man_page()

addparams = {}

data_files = []

data_files.append((os.path.join('share','man','man1'), [os.path.join('build', 'obslight.0.1.gz')]))

setup(name='obslight',
      version = osc.core.__version__,
      description = 'OBS Light',
      long_description = 'Command-line client and UI for the OBS.',
      author = 'Ronan Le Martret',
      author_email = 'ronan@fridu.net',
      license = 'GPL',
      platforms = ['Linux'],
      keywords = ['MeeGo','OBS', 'chroot', 'RPM', 'build', 'buildservice'],
      url = 'http://wiki.meego.com/OBS_Light',
      download_url = 'https://meego.gitorious.org/meego-developer-tools/obs-light',

      packages = ['OBSLight', 'OBSLight.OBSLightManager', 'OBSLight.OBSLightTools'],
      scripts = ['osc_hotshot.py', 'osc-wrapper.py'],
      data_files = data_files,

      # Override certain command classes with our own ones
      cmdclass = {
        'build': build_osc,
        },
      **addparams
     )
