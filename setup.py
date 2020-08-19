from setuptools import setup, find_packages


setup(
   name='DQA_test',
   version='0.6.1',
   author='Patxi Torrealdea',
   author_email='francisco.torrealdea@nhs.net',
   packages=find_packages(),
   url='https://github.com/papomail/Daily_QA_UCLH',
   license='license.md',
   description='Script to process data from DQA-test performed to monitor MR coils at UCLH',
   long_description=open('README.md').read(),
   relies_on_software="dcm2niix version v1.0.20200331",
   install_requires=[
        'cycler==0.10.0',
        'joblib==0.16.0',
        'kiwisolver==1.2.0',
        'matplotlib==3.3.0',
        'nibabel==3.1.1',
        'nilearn==0.6.2',
        'numpy==1.18.4',
        'packaging==20.4',
        'pandas==1.0.3',
        'Pillow==7.2.0',
        'plotly==4.9.0',
        'pyparsing==2.4.7',
        'python-dateutil==2.8.1',
        'pytz==2020.1',
        'retrying==1.3.3',
        'scikit-learn==0.23.2',
        'scipy==1.5.2',
        'six==1.15.0',
        'sklearn==0.0',
        'threadpoolctl==2.1.0'
   ]
)
