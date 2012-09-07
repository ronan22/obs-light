#!/usr/bin/env python

from distutils.core import setup

setup(name='obslight-fakeobs',
      version="1.0.0",
      description='OBS Light Fake OBS',
      long_description='Python script that partially implement an OBS API.\
 It is based on Mer Delivery System',
      author='Florent Vennetier',
      license='GPLv2',
      platforms=['Linux'],
      keywords=['MeeGo', 'OBS', 'RPM', 'build', 'buildservice', 'fakeobs'],
      url='http://en.opensuse.org/openSUSE:OBS_Light_Fakeobs',
      download_url='https://meego.gitorious.org/meego-developer-tools/obs-light',
      packages=['ObsLightFakeObs'],
      package_data={'ObsLightFakeObs' : ['obslight-fakeobs.conf']},
      requires=['osc (>=0.132.5)', 'cmdln', 'xml.etree.ElementTree'],
      data_files=[('/etc', ['config/obslight-fakeobs.conf']),
                  ('/srv/obslight-fakeobs/theme', ['theme/fakeobs.png',
                                                   'theme/favicon.ico']),
                  ('/srv/obslight-fakeobs/tools', ['tools/expanddeps',
                                                   'tools/create_rpm_list_from_spec',
                                                   'tools/emptyrepositorycache.cpio']),
                  ('/srv/obslight-fakeobs/config', ['config/fakeobs-repos.apache2conf',
                                                    'config/fakeobs-repos.lighttpdconf',
                                                    'config/fakeobs.service',
                                                    'config/fakeobswebui.service',
                                                    'config/init_fakeobs',
                                                    'config/init_fakeobswebui',
                                                    'config/logrotate_fakeobs',
                                                    'config/obslight-fakeobs.conf',
                                                    'config/upstart_fakeobs',
                                                    'config/upstart_fakeobswebui'])]
     )
