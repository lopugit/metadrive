import os
import re
import yaml
import json
import importlib

import requests
import gpgrecord

from metadrive import config

MAIN = 'main'


def get_metaname(namespace):
    return '-:{gituser}/+/{namespace}.md#{main}'.format(
        gituser=config.GITHUB_USER,
        namespace=namespace,
        main=MAIN
    )

def get_credential(namespace):
    '''
    namespace: -- service name, by directory

    Example:
    >>> get_credential('gmail')
    '''

    from typology.utils import get_schema

    try:
        data = get_schema(get_metaname(namespace))

        credential = gpgrecord.decrypt_data(data)

        return credential

    except:
        return None

def set_credential(namespace, credential):
    '''
    namespace: -- service name, by directory

    Example:
    >>> set_credential('gmail', {'username': '', 'password': ''})
    '''
    GPG_KEY = config.ENSURE_GPG()

    if credential:
        encrypted_credential = gpgrecord.encrypt_data(
            credential,
            GPG_KEY
        )

        content = '''## {main}
```yaml
{cont}
```'''.format(
            main=MAIN,
            cont=yaml.dump(encrypted_credential)
        )

        with open(
                os.path.join(
                    config.CREDENTIALS_DIR,
                    namespace+'.md'), 'w') as f:
            f.write(content)

        os.system('cd {}; git add .; git commit -m "update"; git push origin master'.format(
            config.REPO_PATH))

    return

def get_or_ask_credentials(namespace, variables, ask_refresh=False):
    credential = get_credential(namespace)

    refresh = False

    if ask_refresh:
        if credential:
            if input("Found credential, do you want to refresh? [N/y] ") in ['y', 'Y']:
                refresh = True

    if not credential or refresh:
        credential = {}

        print('Type credentials for your {}:'.format(namespace.title()))
        for variable in variables:
            credential[variable] = input('{} = '.format(
                variable
            ))

        if all(credential.values()):
            set_credential(
                namespace,
                credential)
            return credential
        else:
            raise Exception('Some of the credentials were not set.')
    else:
        return credential

def load_session_data(namespace):
    session_path = os.path.join(config.SESSIONS_DIR, namespace)
    if os.path.exists(session_path):
        session_data = json.load(open(session_path, 'r'))
        return session_data
    else:
        return {}

def save_session_data(namespace, session_data):
    session_path = os.path.join(config.SESSIONS_DIR, namespace)
    json.dump(session_data, open(session_path, 'w'))

def ensure_driver_installed(driver_name):
    reader = driver_name

    SUPPORTED_PACKAGE_MANAGERS = ['pypi']

    if reader.lower().split(':',1)[0] not in SUPPORTED_PACKAGE_MANAGERS:
        raise Exception(
            "Unknown package manager. " +
            "Make sure the reader you chose starts with one of these: " +
            "{}. Your chosen reader is: {}".format(
                ', '.join(SUPPORTED_PACKAGE_MANAGERS),
                reader
            )
        )

    # SUPPORTED_PACKAGES = [
    #     'pypi:metadrive',
    #     'pypi:drivers',
    #     'pypi:subtools'
    # ]
    #
    package_name = reader.split('.', 1)[0].lower()
    #
    # if package_name not in SUPPORTED_PACKAGES:
    #     raise Exception(
    #         "Unsupported reader package. " +
    #         "Make sure the reader package is one of these: " +
    #         "{}. Your chosen reader is: {}".format(
    #             ', '.join(SUPPORTED_PACKAGES),
    #             package_name
    #         )
    #
    #     )

    packman, package = package_name.split(':')

    # Make sure we have that package installed.
    spec = importlib.util.find_spec(package)
    if spec is None:
        answer = input(package +" is not installed. Install it? [Y/n] ")
        if answer in ['y', 'Y', '']:
            try:
                #easy_install.main( ["-U", package_name] )
                os.system('pip install --no-input -U {} --no-cache'.format(package))
            except SystemExit as e:
                pass
        else:
            raise Exception(package_name +" is required. Install it and run again.")
    else:
        # Check the version installed.
        import pkg_resources
        importlib.reload(pkg_resources)
        installed_version = pkg_resources.get_distribution(package).version

        # Check the latest version in PyPI
        from yolk.pypi import CheeseShop

        def get_lastest_version_number(package_name):
            pkg, all_versions = CheeseShop().query_versions_pypi(package_name)
            if len(all_versions):
                return all_versions[0]
            return None

        latest_version = get_lastest_version_number(package)

        def cmp_version(version1, version2):
            def norm(v):
                return [int(x) for x in re.sub(r'(\.0+)*$','', v).split(".")]
            a, b = norm(version1), norm(version2)
            return (a > b) - (a < b)

        if latest_version is not None:
            if cmp_version(installed_version, latest_version) < 0:
                print(latest_version, type(latest_version))
                answer = input('You are running {}=={}'.format(package,installed_version)+", but there is newer ({}) version. Upgrade it? [y/N] ".format(latest_version))
                if answer in ['y', 'Y']:
                    try:
                        os.system('pip install --no-input -U {} --no-cache'.format(package))
                    except SystemExit as e:
                        pass

    return package
