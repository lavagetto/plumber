import os
import tempfile
import jinja2
import shutil
import yaml
import subprocess
from plumber import marathon
from argparse import ArgumentParser
import time


SUPPORTED_PROJECT_TYPES = ['python']
REGISTRY_URL = os.getenv('REGISTRY_URL')
tpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
templateLoader = jinja2.FileSystemLoader( searchpath=tpl_dir )
templateEnv = jinja2.Environment( loader=templateLoader )
mc = marathon.MarathonController(os.getenv('MARATHON_MASTER_URL'), 'admin', os.getenv('MESOS_PASS'))

def parse_manifest(filename):
    with open(filename, 'rb') as fh:
        c = yaml.load(fh)
    return c

def clean_checkout(path):
    """
    Clean up the current checkout
    """
    shutil.rmtree(path)

def marathon_deploy(name, tag):
    """
    Deploy to marathon
    """
    r = mc.deploy(name,  REGISTRY_URL, tag)
    print r

def clone_repo(path):
    tmpdir = tempfile.mkdtemp(prefix='git_clone_' + os.path.basename(path))
    try:
        res = subprocess.check_output(['git', 'clone', path, tmpdir])
        return tmpdir
    except CalledProcessError, e:
        clean_checkout(tmpdir)
        raise

def get_dockerfile(c, path):
    """
    Creates the docker file from a template that's language-specific.
    """
    dockerfile = os.path.join(path, 'Dockerfile')
    template = templateEnv.get_template("Dockerfile.{}.tpl".format(c['type']))
    dockerdata = template.render(c)
    with open(dockerfile, 'w') as fh:
        fh.write(dockerdata)

def docker_build_and_push(c,dir):
    os.chdir(dir)
    # Todo: validate this, and everything else
    name = c['name']
    tag = name + ':' + str(int(time.time()))
    # Build the docker container from the Dockerfile
    res = subprocess.check_output(['sudo', 'docker', 'build', '-t', tag, '.'])
    res = subprocess.check_output(['sudo', 'docker', 'tag', '-f', tag, REGISTRY_URL + '/' + tag])
    res = subprocess.check_output(['sudo', 'docker', 'push', REGISTRY_URL + '/' + tag])
    return tag

def run():
    parser = ArgumentParser(description="Processing pipeline for building and deploying containers")
    parser.add_argument('repository_path', default=os.getcwd())
    args = parser.parse_args()
    clone_dir = clone_repo(args.repository_path)
    config_file = os.path.join(clone_dir, 'manifest.yaml')
    c = parse_manifest(config_file)
    c['REGISTRY_URL'] = REGISTRY_URL
    # Dockerfile template rendering here
    get_dockerfile(c, clone_dir)
    tag = docker_build_and_push(c, clone_dir)
    # TODO: we will have a central db with the max number of instances of a project we're gonna run.
    marathon_deploy(c['name'], tag)
    #clean_checkout(clone_dir)

if __name__ == '__main__':
    run()
