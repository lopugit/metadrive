import os
import imp
from pathlib import Path
import configparser
import requests
import gpgrecord
config = configparser.ConfigParser()

INSTALLED = imp.find_module('metadrive')[1]

HOME = str(Path.home())
DEFAULT_LOCATION = os.path.join(HOME,'.metadrive')
CONFIG_LOCATION = os.path.join(DEFAULT_LOCATION, 'config')
CREDENTIALS_DIR = os.path.join(DEFAULT_LOCATION, '-/+')
SESSIONS_DIR = os.path.join(DEFAULT_LOCATION, 'sessions')

if not os.path.exists(SESSIONS_DIR):
    os.makedirs(SESSIONS_DIR)

if not os.path.exists(CONFIG_LOCATION):
    username = input("Type your GitHub username: ")

    config['GITHUB'] = {'USERNAME': username}

    with open(CONFIG_LOCATION, 'w') as configfile:
        config.write(configfile)


config.read(CONFIG_LOCATION)

GITHUB_USER = config['GITHUB']['USERNAME']
REPO_PATH = os.path.join(DEFAULT_LOCATION, '-')
DRIVERS_PATH = os.path.join(DEFAULT_LOCATION, 'drivers')


def ENSURE_REPO():

    while not requests.get('https://github.com/{}/-'.format(GITHUB_USER)).ok:
        input("Please, create repository named `-` on your GitHub. Type [ENTER] to continue... ")


    if os.path.exists(REPO_PATH):
        # git pull #
        os.system('cd {}; git pull'.format(REPO_PATH))
    else:
        # git clone #
        os.system('cd {}; git clone {}'.format(
            DEFAULT_LOCATION,
            'git@github.com:{}/-.git'.format(GITHUB_USER)))

    if not os.path.exists(CREDENTIALS_DIR):
        os.makedirs(CREDENTIALS_DIR)
        os.system("cd {}; git add .; git commit -m 'credentials (+)'; git push origin master".format(
            REPO_PATH
        ))

def ENSURE_GPG():
    config.read(CONFIG_LOCATION)
    if 'GPG' in config.keys():
        return config['GPG']['KEY']

    print('Choose your GPG key for encrypting credentials:')
    KEY_LIST = gpgrecord.list_recipients()

    for i, key in enumerate(KEY_LIST):
        print('{id}. {uid} {fingerprint}'.format(
            id=i+1,
            uid=key['uids'],
            fingerprint=key['fingerprint']
        ))

    i = int(input('Type key order in the list: ')) - 1

    GPG_KEY = KEY_LIST[i]['fingerprint']

    config['GPG'] = {'KEY': GPG_KEY}

    with open(CONFIG_LOCATION, 'w') as configfile:
        config.write(configfile)

    return GPG_KEY
