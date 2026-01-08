from setuptools import setup, find_packages

setup(
    name='goldenface',
    version='0.1',
    packages=['GoldenFace'],  # Define the package name
    package_dir={'GoldenFace': 'Library Source'},  # Map package to source folder
    package_data={'GoldenFace': ['*.yaml', '*.json', '*.png']}, # Include model and data files
    include_package_data=True,
    install_requires=[
        'opencv-python',
        'opencv-contrib-python',
        'streamlit',
        'numpy',
        'Pillow'
    ],
)
