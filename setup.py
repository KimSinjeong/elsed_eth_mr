import os
import re
import sys
import platform
import subprocess

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from distutils.version import LooseVersion

import sysconfig

class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    def run(self):
        try:
            out = subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError("CMake must be installed to build the following extensions: " +
                               ", ".join(e.name for e in self.extensions))

        if platform.system() == "Windows":
            cmake_version = LooseVersion(re.search(r'version\s*([\d.]+)', out.decode()).group(1))
            if cmake_version < '3.1.0':
                raise RuntimeError("CMake >= 3.1.0 is required on Windows")

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        cmake_args = ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir,
                      '-DPYTHON_EXECUTABLE=' + sys.executable]

        cfg = 'Debug' if self.debug else 'Release'
        build_args = ['--config', cfg]

        if platform.system() == "Windows":
            cmake_args += ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}'.format(cfg.upper(), extdir)]
            if sys.maxsize > 2 ** 32:
                cmake_args += ['-A', 'x64']
            build_args += ['--', '/m']
        else:
            cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
            build_args += ['--', '-j2']

        env = os.environ.copy()
        env['CXXFLAGS'] = '{} -DVERSION_INFO=\\"{}\\"'.format(
            env.get('CXXFLAGS', ''),
            self.distribution.get_version()
        )
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)

        cmake_args += ['-DPYTHON_INCLUDE_DIR=' + sysconfig.get_path('include')]
        cmake_args += ['-DPYTHON_LIBRARY=' + sysconfig.get_config_var('LIBDIR')]

        #cmake_args += ['-DOpenCV_INCLUDE_DIRS=' + '/home/sjkim/Documents/MR/mr-library-demo/.buildozer/android/platform/build-arm64-v8a/build/other_builds/opencv/arm64-v8a__ndk_target_21/opencv/include']
        cmake_args += ['-DOpenCV_INCLUDE_DIRS=' + '/usr/local/include/opencv4']
        cmake_args += ['-DOpenCV_DIR=' + '/home/sjkim/Documents/MR/mr-library-demo/.buildozer/android/platform/build-arm64-v8a/build/libs_collections/mr-demo/arm64-v8a']
        cmake_args += ['-DOpenCV_LIBS=' + "['opencv_calib3d' 'opencv_core' 'opencv_dnn' 'opencv_features2d' 'opencv_flann' 'opencv_gapi' 'opencv_highgui' 'opencv_imgcodecs' 'opencv_imgproc' 'opencv_ml' 'opencv_objdetect' 'opencv_photo' 'opencv_stitching' 'opencv_video' 'opencv_videoio']"]
        # cmake_args += ['-DOpenCV_LIBS=' + '/home/sjkim/Documents/MR/mr-library-demo/.buildozer/android/platform/build-arm64-v8a/build/libs_collections/mr-demo/arm64-v8a']
        cmake_args += ['-DOpenCV_FOUND=' + '1']
        # cmake_args += ['-llibopencv_calib3d', '-llibopencv_core', '-llibopencv_dnn', '-llibopencv_features2d', '-llibopencv_flann', '-llibopencv_gapi', '-llibopencv_highgui', '-llibopencv_imgcodecs', '-llibopencv_imgproc', '-llibopencv_ml', '-llibopencv_objdetect', '-llibopencv_photo', '-llibopencv_stitching', '-llibopencv_video', '-llibopencv_videoio']
        
        print(['cmake', ext.sourcedir] + cmake_args)
        subprocess.check_call(['cmake', ext.sourcedir] + cmake_args, cwd=self.build_temp, env=env)
        subprocess.check_call(['cmake', '--build', '.'] + build_args, cwd=self.build_temp)


setup(
    name='pyelsed',
    version='0.0.0',
    author='Iago Suarez',
    description='ELSED (Enhanced Line SEgment Detector) bindings',
    long_description='',
    ext_modules=[CMakeExtension('pyelsed')],
    cmdclass=dict(build_ext=CMakeBuild),
    zip_safe=False,
)
