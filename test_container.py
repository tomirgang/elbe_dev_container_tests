import subprocess
from subprocess import PIPE
import shlex
import os

def run_in_container(command):
    """
    Run a command in the container.
    """
    home = os.path.expanduser('~')
    work = os.path.abspath('..')
    cmd = shlex.split("docker run --rm --privileged")
    cmd += shlex.split(f"-v {home}/.ssh:/home/dev/.ssh:ro")
    cmd += shlex.split(f"-v {work}/identity:/build/identity:ro")
    cmd += shlex.split(f"-v {work}/buildenv:/build/init:rw")
    cmd += shlex.split(f"-v {work}/results:/build/results:rw")
    cmd += shlex.split(f"-v {work}/../images:/images:ro")
    cmd += shlex.split(f'elbe_bookworm:latest bash -c "{command}"')
    
    result = subprocess.Popen(
        cmd,
        cwd="..",
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE)

    result.wait()

    return result


def test_build_container():
    """
    Test ./.devcontainer/build_container.sh script.

    The build_container.sh script is used to build the Docker container if
    needed for VS Code. Before it checks if the container already exists.

    This test runs the script twice, assures that both times the execution was
    successful, and that in the second run the container already existed.
    """
    result = subprocess.run(
        ["./.devcontainer/build_container.sh"],
        cwd="..",
        shell=True,
        capture_output=True)
    assert result.returncode == 0

    result = subprocess.run(
        ["./.devcontainer/build_container.sh"],
        cwd="..",
        shell=True,
        capture_output=True)
    assert result.returncode == 0

    out = result.stdout.decode('utf-8')
    assert "elbe_bookworm" in out
    assert "latest" in out


def test_docker_images():
    """
    Assert that elbe_bookworm:latest image is available.
    """
    result = subprocess.Popen(
        shlex.split("docker image ls"),
        cwd="..",
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE)

    result.wait(500)

    assert result.returncode == 0
    assert len(result.stderr.read()) == 0

    out = result.stdout.read().decode('utf-8')
    assert "elbe_bookworm" in out
    assert "latest" in out


def test_run_in_container():
    """
    Run a command in the container.
    """
    result = run_in_container("ls -lah")

    print(result.stdout.read().decode('utf-8'))
    print(result.stderr.read().decode('utf-8'))

    assert result.returncode == 0
