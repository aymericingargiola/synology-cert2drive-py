import setuptools

setuptools.setup(name='synology-cert2drive',
                 version='0.1',
                 description='Copy Synology\'s certificates for specified domains names to your drive',
                 url='https://github.com/aymericingargiola/synology-cert2drive-py',
                 author='Aymeric Ingargiola',
                 author_email='aymericfbm@gmail.com',
                 license='MIT',
                 packages=setuptools.find_packages(
                     include=['synology-cert2drive', 'synocert2drive.*', 'synocert2drivegui.*']),
                 package_data={'synology-cert2drive': ['config/config.json']},
                 install_requires=[
                     'paramiko',
                     'scp'
                 ])
