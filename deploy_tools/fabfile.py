import random
from fabric.contrib.files import append, exists
from fabric.api import cd, env, local, run


REPO_URL = 'https://github.com/anyoneElse1/goat.git'
from fabric.api import *

env.hosts = ['staging.talentfit.net']
env.user = 'ubuntu'
env.key_filename = '/users/admin/documents/aws/aws.pem'

def local_uname():
    local('uname -a')

def remote_uname():
    run('uname -a')

def deploy():
    site_folder = f'/home/{env.user}/sites/{env.host}'
    run(f'mkdir -p {site_folder}')
    with cd(site_folder):
        _get_latest_source()
        _update_virtualenv()
        _create_or_update_dotenv()
        _update_static_files()
        _update_database()


def _get_latest_source():
    if exists('.git'):
        run('git fetch')
    else:
        run(f'git clone {REPO_URL} .')
    current_commit = local("git log -n 1 --format=%H", capture=True)
    run('git reset --hard')


def _update_virtualenv():
    if not exists('virtualenv/bin/pip'):
        run(f'python3.6 -m venv myenv')
    run('./myenv/bin/pip install -r requirements.txt')

def _create_or_update_dotenv():
    append('.env', 'DJANGO_DEBUG_FALSE=y')
    append('.env', f'SITENAME={env.host}')
    current_contents = run('cat .env')
    if 'DJANGO_SECRET_KEY' not in current_contents:
        new_secret = ''.join(random.SystemRandom().choices(
            'abcdefghijklmnopqrstuvwxyz0123456789', k=50
        ))
        append('.env', f'DJANGO_SECRET_KEY={new_secret}')


def _update_static_files():
    run('./myenv/bin/python3.6 manage.py collectstatic --noinput')


def _update_database():
    run('./myenv/bin/python3.6 manage.py migrate --noinput')