import os
from setuptools import setup, find_packages
from distutils.extension import Extension
import numpy as np

# build knn extension for pointconvs (knn directory copied from https://github.com/aboulch/ConvPoint)
ext_modules = [Extension(
    "nearest_neighbors",
    sources=["elektronn3/models/knn/knn.pyx", "elektronn3/models/knn/knn_.cxx", ],  # source file(s)
    include_dirs=["./", np.get_include()],
    language="c++",
    extra_compile_args=["-std=c++11", "-fopenmp", ],
    extra_link_args=["-std=c++11", '-fopenmp'],
)]

on_rtd = os.environ.get('READTHEDOCS') == 'True'
if on_rtd:
    install_requires = []
else:
    install_requires = [
        'torch==1.1.0',
        'numpy',
        'scipy',
        'h5py',
        'matplotlib',
        'numba',
        'ipython',
        'imageio',
        'pillow',
        'colorlog',
        'tqdm',
        'scikit-learn',
        'scikit-image',
        'tensorboard',
        'tensorboardX',
        'torchvision'
    ]

setup(
    name='elektronn3',
    version='0.0.0',
    description='Utilities for 3D CNNs in PyTorch',
    url='https://github.com/ELEKTRONN/elektronn3',
    author='ELEKTRONN team',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    ext_modules=ext_modules,
    packages=find_packages(exclude=['scripts']),
    install_requires=install_requires,
)
