import os

import pytest

from conans.client.tools import vswhere, which
from conans.errors import ConanException

tool_locations = {
    'msys2': os.getenv("CONAN_MSYS2_PATH", "C:/msys64/usr/bin"),
    'cygwin': os.getenv("CONAN_CYGWIN_PATH", "C:/cygwin64/bin")
}

tools_available = [
    'cmake',
    'gcc', 'clang', 'visual_studio', 'mingw', 'xcode',
    'msys2', 'cygwin',
    'autotools', 'pkg_config', 'premake', 'meson',
    'file',
    'git', 'svn',
    'compiler',
    'conan',  # Search the tool_conan test that needs conan itself
]

if not which("cmake"):
    tools_available.remove("cmake")

if not which("gcc"):
    tools_available.remove("gcc")
if not which("clang"):
    tools_available.remove("clang")
try:
    if not vswhere():
        tools_available.remove("visual_studio")
except ConanException:
    tools_available.remove("visual_studio")

if not any([x for x in ("gcc", "clang", "visual_sudio") if x in tools_available]):
    tools_available.remove("compiler")

if not which("mingw32-make"):
    tools_available.remove("mingw")

if not which("xcodebuild"):
    tools_available.remove("xcode")

if not which("file"):
    tools_available.remove("file")

if not which("git"):
    tools_available.remove("git")
if not which("svn"):
    tools_available.remove("svn")

if not which("autoconf") or not which("automake"):
    tools_available.remove("autotools")
if not which("meson"):
    tools_available.remove("meson")
if not which("pkg-config"):
    tools_available.remove("pkg_config")
if not which("premake"):
    tools_available.remove("premake")
if not which("conan"):
    tools_available.remove("conan")


@pytest.fixture(autouse=True)
def add_tool(request):
    add_tools = []
    for mark in request.node.iter_markers():
        if mark.name.startswith("tool_"):
            tool_name = mark.name[5:]
            if tool_name in tool_locations:
                add_tools.append(tool_locations[tool_name])
    if add_tools:
        add_tools.append(os.environ["PATH"])
        temp_env = {'PATH': os.pathsep.join(add_tools)}
        old_environ = dict(os.environ)
        os.environ.update(temp_env)
        yield
        os.environ.clear()
        os.environ.update(old_environ)
    else:
        yield


def tool_check(mark):
    tool_name = mark.name[5:]
    if tool_name not in tools_available:
        pytest.skip("required {} not satisfied".format(tool_name))


def pytest_runtest_setup(item):
    # Every mark is a required tool, some specify a version
    for mark in item.iter_markers():
        if mark.name.startswith("tool_"):
            tool_check(mark)
