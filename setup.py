from setuptools import setup, find_packages

setup(
    name='goldenface',
    version='0.1',
    packages=find_packages(), # Automatically find the GoldenFace package 
    package_data={'GoldenFace': ['*.yaml', '*.json', '*.png']}, # Include model and data files
    include_package_data=True,
    install_requires=[
        'opencv-python',
        'opencv-contrib-python',
        'streamlit',
        'numpy',
        'Pillow',
        'setuptools'
    ],
)
