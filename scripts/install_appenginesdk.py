#!/usr/bin/env python
from __future__ import print_function
"""

TODO:
    - TST:
    - check remote version

install_appenginesdk.py
========================
``install_appenginesdk.py`` -- download, unzip, and install Google AppEngine SDK

Requirements
--------------

* Either ``curl`` or ``wget``

Usage
------
Commandline arguments:

.. code:: bash

    install_appenginesdk.py --help
    install_appenginesdk.py --install
    install_appenginesdk.py --clean   # remove APPENGINESDK_PREFIX
    install_appenginesdk.py --clean --install
    install_appenginesdk.py --open-download
    install_appenginesdk.py --open-appengine-docs

.. code:: bash

                                 # default
    CLOUDSDK_PREFIX              "~/google-cloud-sdk/platform"
    APPENGINESDK_PREFIX          "~/google-cloud-sdk/platform/google_appengine"
    APPENGINESDK_VERSION_DEFAULT "1.9.32"
    APPENGINESDK_VERSION         '1.9.32'
    APPENGINESDK_ARCHIVE         'google_appengine_1.9.32.zip'
    APPENGINESDK_ARCHIVE_URL     "https://.../google_appengine_1.9.32.zip"
    _VAR_DATA           "~/data"
    APPENGINESDK_ARCHIVE_PATH
                        "~/data/google_appengine/google_appengine_1.9.32.zip"
    APPENGINESDK_FILEMODE        0x750  # for os.makedirs
    APPENGINESDK_ARCHIVE_DESTDIR "~/google-cloud-sdk/platform/"

Google AppEngine Links:

* https://cloud.google.com/appengine/downloads
* https://cloud.google.com/appengine/docs/
* https://cloud.google.com/appengine/docs/python/
"""
__version__ = version = "0.1.0"
APPENGINESDK_VERSION_DEFAULT = "1.9.33"  # --version='x.y.z'
# APPENGINESDK_FILEMODE_DEFAULT = 0o777
APPENGINESDK_FILEMODE_DEFAULT = 0o751
# APPENGINESDK_FILEMODE_DEFAULT = 0o771

import codecs
import collections
import distutils
# import fnmatch
import functools
import inspect
import json
import logging
import os
import shutil
import subprocess
import sys
import types
import webbrowser

from collections import OrderedDict

BUILDSTEPS = []


def buildstep(f):
    """@buildstep decorator for BuildstepResult-returning callables"""
    BUILDSTEPS.append(f)

    @functools.wraps(f)
    def _buildstep(*args, **kwargs):
        ctxt = OrderedDict__()
        ctxt['name'] = None
        ctxt['step'] = None
        ctxt['args'] = args
        ctxt['kwargs'] = kwargs
        log.debug('## <buildstep> ############')
        log.debug(json_dumps(ctxt))
        ctxt['result'] = result = f(*args, **kwargs)
        if not isinstance(result, BuildstepResult):
            raise ValueError((result, 'is not a BuildstepResult'))
        if result.data.get('step') is None:
            result.data['step'] = f
        ctxt['name'] = f.func_name = result.name = (
            kwargs.get("name",
                       get_obj_name(f,
                                    get_obj_name(result))))
        log.debug(json_dumps(ctxt))
        log.debug('## </buildstep> ###########')
        #name = getattr(result, 'name', None)
        # if name is None:
        #     name = kwargs.get('name', get_obj_name(result))
        #     if name is None:
        #         name = get_obj_name(f)
        del ctxt
        return result
    return _buildstep


def get_buildstep(buildstep, steps=BUILDSTEPS):
    """
    Args:
        buildstep (obj): a callable object or a name string
    Kwargs:
        buildsteps (iterable): iterable of known buildsteps to match
    Returns:
        list: list of matching objects from buildsteps
    """
    _buildsteps = []
    for step in steps:
        if (buildstep == step):
            _buildsteps.append(buildstep)
        name = get_obj_name(step)
        if (buildstep == name):
            _buildsteps.append(step)
    return _buildsteps


# def get_buildstep_fnmatch(pattern, buildsteps=BUILDSTEPS,
#                           matchfunc=fnmatch.fnmatch):
#     """
#     Args:
#         buildstep (obj): a callable object or a name string
#     Kwargs:
#         buildsteps (iterable): iterable of known buildsteps to match
#     Returns:
#         list: list of matching objects from buildsteps
#     """
#     _buildsteps = []
#     for step in buildsteps:
#         name = get_obj_name(step)
#         match_output = matchfunc(name, pattern)
#         if match_output:
#             _buildsteps.append(match_output)
#     return _buildsteps


UNSET = types


def get_obj_name(obj, default=UNSET):
    """
    Args:
        obj (callable): callable to lookup name property from

    .. code:: python

       obj.name, obj.func_name, obj.__class__.__name__ else repr(obj)

    Returns:
        str: description string from the lookup sequence
    """
    return (
        getattr(obj, 'name',
                getattr(obj, '__name__',
                        default if default is not UNSET else repr(obj))))


def get_obj_description(obj, default=UNSET):
    """
    Args:
        obj (callable): callable to lookup description property from
    Returns:
        str: description string from the lookup sequence
    .. code:: python

        obj.description, obj.func_doc, obj.__doc__, obj
    """
    return (
        getattr(obj, 'description',
                getattr(obj, '__doc__',
                        default if default is not UNSET else str(obj))))


def _print_buildsteps(buildsteps=BUILDSTEPS, debug=None):
    for step in buildsteps:
        ctxt = OrderedDict()
        ctxt['name'] = get_obj_name(step) or ''
        ctxt['description'] = get_obj_description(step) or ''
        yield "## {name} ##  {description}".format(**ctxt)
        if debug or log.level <= logging.DEBUG:
            ctxt['step'] = step
            yield "## {name} ## :: {step}".format(**ctxt)


def print_buildsteps(buildsteps=BUILDSTEPS, debug=None):
    for l in _print_buildsteps(buildsteps=buildsteps, debug=debug):
        print(l)


class OrderedDict__(OrderedDict):

    def keys(self):
        """wrap .keys() in a list() so that ``__cmp__`` works w/ Python 3
        (this may imply side effects during sublist traversal)
        """
        return list(self)

    def values(self):
        """wrap .values() in a list() so that ``__cmp__`` works w/ Python 3
        (this may imply side effects during sublist traversal)
        """
        return list(self)


# logging config

DEFAULT_LOGGER = os.path.basename(__file__)
logging.basicConfig(
    level=logging.DEBUG,
    format='## %(levelname)-5s %(filename)s +%(lineno)-4s %(funcName)s()\n## %(message)s/#'
)
log = logging.getLogger(DEFAULT_LOGGER)

########
# JSON

_CALLABLE_TYPES = (types.FunctionType, types.ClassType, types.MethodType)
# _BUILDSTEP_TYPES = (...)


class JSONEncoderDebug(json.JSONEncoder):

    def default(self, obj):
        # log.debug(('jsonencode', obj))
        if isinstance(obj, _CALLABLE_TYPES):
            d = OrderedDict__(obj.__dict__.copy())
            d.setdefault('name', get_obj_name(obj))
            srcpath = inspect.getsourcefile(obj)
            modname = obj.__module__
            if modname == '__main__':
                modname = ''
            else:
                modname = modname + '.'
            x = "{}##{}{}".format(srcpath, modname, obj.__name__)

            # NEW format specification minilanguages!!@#!
            d.setdefault('srcurl', x)
            return d
        elif isinstance(obj, _BUILDSTEP_TYPES):
            return obj.data
        elif isinstance(obj, types.FileType):
            return "<{}>".format(obj.name)
        return json.JSONEncoder.default(self, obj)


def json_dumps(obj, *args, **kwargs):
    """
    Returns:
        str or unicode: json.dumps(cls=JSONEncoderDebug, indent=[2])
    """
    kwargs['cls'] = JSONEncoderDebug
    kwargs.setdefault('indent', 2)
    kwargs.setdefault('skipkeys', True)
    return json.dumps(obj, *args, **kwargs)

##########################################################
# BuildstepResult, BuildstepResultList, BuildstepBuilder


class BuildstepResult(object):

    def __init__(self,
                 name=None,
                 step=None,
                 conf=UNSET,
                 returncode=None,
                 returnvalue=UNSET,
                 msg=UNSET,
                 stdout=UNSET,
                 stderr=UNSET):
        self.data = OrderedDict()
        if name is None:
            if step is not None:
                name = get_obj_name(step)
        self.data['name'] = name
        self.data['step'] = step
        if conf is not UNSET:
            self.data['conf'] = conf
        self.data['returncode'] = returncode
        if msg is not UNSET:
            self.data['msg'] = msg
        if returnvalue is UNSET:
            if stdout is not UNSET or stderr is not UNSET:
                self.data['returnvalue'] = OrderedDict__()
        else:
            if not hasattr(returnvalue, 'keys'):
                raise ValueError((returnvalue, 'is not a dict/OrderedDict__'))
            self.data['returnvalue'] = returnvalue
        if stdout is not UNSET:
            self.data['returnvalue']['stdout'] = stdout
        if stderr is not UNSET:
            self.data['returnvalue']['stderr'] = stderr

    def __repr__(self):
        return "BuildstepResult({%s})" % json_dumps(self.data)

    @property
    def name(self):
        return self.data['name']

    @name.setter
    def name(self, name):
        self.data['name'] = name

    @property
    def success(self):
        returncode = self.data.get('returncode')
        if returncode is not None:
            if returncode == 1:
                return False
            if returncode in [0, True]:
                return True
            else:
                return False
        else:
            return None

    def _repr_checkbox_(self, prefix=None, debug=None):
        msg = self.data.get('msg')
        name = get_obj_name(self)
        if debug is None:
            debug = getattr(self, 'debug', None)
        return "+ [{}] {}{}{}".format(
            'X' if self.success else ' ',
            prefix if prefix is not None else '',
            name,
            ((('\n' + '\n'.join(
                _indent_linestr(str(msg), 1, '        ')))
                if msg is not None else '')))


def _indent_str(str_, depth=0, indentchar=' '):
    return '{}{}'.format(depth * indentchar, str_)


def _indent_lineiter(lines, depth=0, indentchar=' '):
    indentstr = indentchar * depth
    for line in lines:
        yield '{}{}'.format(indentstr, line)


def _indent_linestr(linestr, depth=0, indentchar=' '):
    return _indent_lineiter(
        linestr.splitlines(),
        depth,
        indentchar=indentchar)


class BuildstepStep(object):
    def __init__(self, name=None, func=None, args=UNSET, kwargs=UNSET,
                 result=UNSET):
        if name is None:
            raise ValueError(name, 'is None')
        if func is None:
            if hasattr(self, 'build'):
                func = self.build
            else:
                raise ValueError(func, 'is None')
        self.data = OrderedDict__()
        self.data['name'] = name
        self.data['func'] = func
        if args is not UNSET:
            self.data['args'] = args
        if kwargs is not UNSET:
            self.data['kwargs'] = kwargs
        if result is not UNSET:
            self.data['result'] = result

    @property
    def result(self):
        return self.data.get('result', None)

    @result.setter
    def result(self, value):
        self.data['result'] = value

    @property
    def success(self):
        if 'result' not in self.data:
            return None
        return self.data['result'].success


class BuildstepPlan(list):

    def append(self,
               step=None,
               name=None, func=None, args=UNSET, kwargs=UNSET):
        if step is None:
            if name is None:
                name = get_obj_name(func)
            step = BuildstepStep(
                name=name, func=func, args=args, kwargs=kwargs)
        elif isinstance(step, (tuple, list)):
            if len(step) == 2:
                if isinstance(step[1], BuildstepStep):
                    name, step = step
                    step.name = name
                elif isinstance(step[1], _CALLABLE_TYPES):
                    name, func = step
                    step = BuildstepStep(
                        name=name, func=func, args=args, kwargs=kwargs)
                else:
                    raise ValueError(step)
            else:
                raise ValueError(
                    ('step', step, 'is not a 2-tuple/list'))
        elif isinstance(step, BuildstepResult):
            result = step
            # XXX
            step = BuildstepStep(
                name=result.name,
                func=lambda x: result,
                result=result)
        elif isinstance(step, _CALLABLE_TYPES):
            func = step
            step = BuildstepStep(
                name=get_obj_name(func),
                func=func)

        else:
            raise ValueError(
                ('step', step, 'is not a BuildstepStep or a 2-tuple/list'))
        log.info(('step', (step)))
        return super(BuildstepPlan, self).append(step)

    def extend(self, results):
        for result in results:
            self.append(result)

    @property
    def data(self):
        return self

    def __print_all(self, argv,
                    printheader=True,
                    prefix=None,
                    objs=None,
                    depth=0):
        indentstr = '  ' * depth
        if printheader:
            hdrstr = "##### {!s}results".format(
                (prefix + ' ') if prefix is not None else '')
            yield indentstr + ""
            yield indentstr + hdrstr
            yield indentstr + '#' * len(hdrstr)
        else:
            yield ''
        yield indentstr + '- ### args: {!r}'.format(argv)
        if objs is None:
            objs = self
        for obj in objs:
            try:
                # if isinstance(obj, BuildstepStep):
                if hasattr(obj, 'result'):
                    result = obj.result
                # if isinstance(obj, BuildstepResult):
                elif hasattr(obj, 'data'):
                    result = obj
                elif isinstance(obj, (tuple, list)) and len(obj) == 2:
                    result = obj[1]
                else:
                    raise ValueError((type(obj), obj))
                # TODO step._repr_checkbox_
                if result is None:
                    yield indentstr + '+ [ ] {name}'.format(**obj.data)
                    continue
                yield indentstr + result._repr_checkbox_(prefix=prefix)
                if 'returnvalue' in result.data:
                    subresults = result.data['returnvalue'].get('results')
                    if subresults is not None:
                        for subresult in self.__print_all(
                                argv=argv,
                                objs=subresults,
                                printheader=False,
                                depth=depth+1):
                            yield subresult
                        yield ''
            except Exception as e:
                log.exception(e)
                if isinstance(e, KeyboardInterrupt):
                    raise
                yield indentstr + '- [!] {!r}'.format(e)
        yield ''

    def _print_all(self, argv, prefix=None, depth=0):
        return _indent_lineiter(
            self.__print_all(argv, prefix=prefix),
            depth=depth)

    def print_all(self, argv, prefix=None, depth=0, file=None):
        for obj in self._print_all(argv, prefix=prefix, depth=depth):
            print(obj, file=file)

    @property
    def success(self):
        return all(step.success for step in self)

    def __repr__(self):
        return "BuildstepPlan([%s])" % json_dumps(self)


# class BuildstepResultList(list):

#     def append(self, result):
#         if isinstance(result, BuildstepResult):
#             name_result = (result.name, result)
#         elif (isinstance(result, (tuple, list))
#               and len(result) == 2
#               and isinstance(result[1], BuildstepResult)):
#             name_result = result
#         else:
#             raise ValueError(
#                 ('result', result, 'is not a BuildstepResult'))
#         log.info(('result', (name_result)))
#         return super(BuildstepResultList, self).append(name_result)

#     def extend(self, results):
#         for result in results:
#             self.append(result)

#     def __print_all(self, argv,
#                     printheader=True,
#                     prefix=None,
#                     results=None,
#                     depth=0):
#         indentstr = '  ' * depth
#         if printheader:
#             hdrstr = "##### {!s}results".format(
#                 (prefix + ' ') if prefix is not None else '')
#             yield indentstr + ""
#             yield indentstr + hdrstr
#             yield indentstr + '#' * len(hdrstr)
#         else:
#             yield ''
#         yield indentstr + '- ### args: {!r}'.format(argv)
#         if results is None:
#             results = self
#         for (name, result) in results:
#             yield indentstr + result._repr_checkbox_(prefix=prefix)
#             if 'returnvalue' in result.data:
#                 subresults = result.data['returnvalue'].get('results')
#                 if subresults is not None:
#                     for subresult in self.__print_all(
#                             argv=argv,
#                             results=subresults,
#                             printheader=False,
#                             depth=depth+1):
#                         yield subresult
#                     yield ''
#         yield ''

#     def _print_all(self, argv, prefix=None, depth=0):
#         return _indent_lineiter(
#             self.__print_all(argv, prefix=prefix),
#             depth=depth)

#     def print_all(self, argv, prefix=None, depth=0, file=None):
#         for obj in self._print_all(argv, prefix=prefix, depth=depth):
#             print(obj, file=file)

#     @property
#     def success(self):
#         return all(result.success for (name, result) in self)

#     @property
#     def data(self):
#         return self

#     def __repr__(self):
#         return "BuildstepResultList([%s])" % json_dumps(self)


class BuildstepBuilder(object):

    def __init__(self, steps=None, cfg=None, result_cls=BuildstepResult):
        self.steps = BuildstepPlan() if steps is None else BuildstepPlan(steps)
        self.cfg = OrderedDict() if steps is None else cfg
        self.result_cls = BuildstepResult

    def build_iter(self, cfg=None, steps=None):
        if cfg is None:
            cfg = self.cfg
        if steps is None:
            steps = self.steps
        for step in steps:
            stepresult = step.data['func'](cfg)
            if not isinstance(stepresult, self.result_cls):
                raise ValueError(
                    ('stepresult', stepresult,
                        'is not a {!r}'.format(self.result_cls)))
            stepresult.name = step.data['name']
            stepresult.step = step
            yield stepresult

    def build_plan_iter(self, cfg=None, steps=None): #TODO rename
        cfg = self.cfg if cfg is None else cfg
        steps = self.steps if steps is None else steps
        for step in steps:
            args = [cfg]
            args.extend(step.data.get('args', []))
            kwargs = step.data.get('kwargs', {})
            func = step.data['func']
            step.result = func(*args, **kwargs)
            step.result.name = step.data['name']
            yield step

    def build_plan(self, cfg=None, steps=None):
        return BuildstepPlan(self.build_plan_iter(cfg=cfg, steps=steps))

    def build(self, cfg=None, steps=None):
        return list(self.build_iter(cfg=cfg, steps=steps))

    def data(self):
        return [('cfg', self.cfg), ('steps', self.steps)]

    def append(self, *args, **kwargs):
        return self.steps.append(*args, **kwargs)


_BUILDSTEP_TYPES = (BuildstepBuilder, BuildstepPlan,
                    BuildstepResult, BuildstepStep)


##############################
# portable Python functions

def subprocess_call_expect(cmd, *args, **kwargs):
    """wrap subprocess.call for logging and nonzero returncode checking

    Args:
        cmd (tuple, list): subprocess.call(cmd, *args, **kwargs)
        args (tuple): subprocess.call(cmd, *args, **kwargs)
        kwargs (dict): subprocess.call(cmd, *args, **kwargs)
    Kwargs:
        raiseonerror (bool): raise subprocess.CalledProcessError
            when returncode is not equal to ``expectreturncode``
            (default: ``True``)
        expectreturncode (int): if raiseonerror is True
            and the output returncode is not equal to this value,
            raise a subprocess.CalledProcessError
            (default: ``0``)
    Returns:
        int: nonzero returncode on error
    Raises:
        subprocess.CalledProcessError: if ``raiseonerror``
            and the return code is not equal to ``expectreturncode``;
    """
    log.debug(('cmdcmd', cmd))
    log.debug(('cmdstr', '#' + ' '.join(cmd)))
    log.debug((('args', args), ('kwargs', kwargs)))
    expectreturncode = kwargs.pop('expectreturncode', 0)
    raiseonerror = kwargs.pop('raiseonerror', True)
    _args = [cmd] + list(args)
    retcode = subprocess.call(*_args, **kwargs)
    if raiseonerror:
        if retcode != expectreturncode:
            raise subprocess.CalledProcessError(
                retcode,
                [('cmd', cmd),
                 ('args', args),
                 ('kwargs', kwargs),
                 ('retcode', retcode),
                 ('expectreturncode', expectreturncode)])
    return retcode
    #return BuildstepResult(returncode=retcode)


def _rm_r(path):
    """recursively remove files and directories (``rm -r`` in Python)
    Args:
        path (str): path to recursively delete (like ``rm -r``)
    Returns:
        None
    """
    if os.path.isdir(path) and not os.path.islink(path):
        shutil.rmtree(path)
    elif os.path.exists(path):
        os.remove(path)


def rm_r(path):
    """recursively remove files and directories (``rm -r`` in Python)
    Args:
        path (str): path to recursively delete (like ``rm -r``)
    Returns:
        BuildstepResult
    """
    if path.strip() in ['/', '']:
        raise ValueError(('path', path))
    cmd_equiv = ('rm', '-r', '-f', path)
    success = None
    try:
        _rm_r(path)
        log.debug(('rm_r', path))
        success = True
    except OSError as e:
        success = False
        log.exception(e)
        pass
    returncode = 0 if success is True else 1
    return BuildstepResult(
        returncode=returncode,
        returnvalue=OrderedDict__([
            ('path', path),
            ('cmd', cmd_equiv)]))


def makedirs(path, filemode=None):
    """
    Args:
        path (str):
    Kwargs:
        filemode (int): default filemode (e.g. ``0o771``)
    Returns:
        BuildstepResult
    """
    success = None
    if not os.path.exists(path):
        try:
            os.makedirs(path, filemode=filemode)
        except OSError as e:
            if e.errno == 17:  # 'File exists'
                success = True
                pass
            else:
                success = False
    else:
        success = True
        # XXX os.chmod(path, filemode %^? os.umask.current)
    returncode = 0 if success is True else 1
    return BuildstepResult(
        returncode=returncode,
        returnvalue=OrderedDict__([
            ('path', path)]))


def download_file(url=None,
                  destdir=None,
                  dirmode=0x777,
                  force=False,
                  destfile=None):
    """
    Args:
        url (str): URL string for curl || wget
        destdir (str): path to download url into
    Kwargs:
        dirmode (int): (octal) filemode for os.makedirs
        force (bool): if True, delete any existing file first
        destfile (str): destination path to expect file to be downloaded to
    Returns:
        tuple: (success:bool, cmd:str)
    """
    if url is None:
        raise ValueError((url, 'is None'))
    if destdir is None:
        raise ValueError((destdir, 'is None'))
    # curl -S --continue - -O '$(APPENGINESDK_ARCHIVE_URL)'
    skip_download = None
    result = makedirs(destdir, dirmode)
    if not result.success:
        return result
    if destfile is not None:
        destpath = os.path.join(destdir, destfile)
    if force:
        if destfile is None:
            raise ValueError("specify which file to remove with 'destfile'")
        os.remove(destpath)
    else:
        if destfile is not None:
            if os.path.exists(destfile):
                skip_download = True
    if not skip_download:
        CURL = distutils.spawn.find_executable('curl')
        if not CURL:
            WGET = distutils.spawn.find_executable('wget')
            cmd = (WGET, '-q', url)
            if not WGET:
                raise Exception("neither curl nor wget can be found")
        else:
            cmd = (CURL, '-f', '-S', '-O', url)
        retcode = subprocess_call_expect(
            cmd,
            cwd=destdir,
            expectreturncode=0)
        if destfile is not None:
            if not os.path.exists(destpath):
                raise Exception((
                    ('err', 'The downloaded file does not exit'),
                    ('destpath', destpath)
                ))
        result = [('cmd', cmd), ('destpath', destpath)]
    else:
        retcode = 0
        result = [('destpath', destpath)]
    return BuildstepResult(
        returncode=retcode,
        returnvalue=OrderedDict__(result))


###################################
# AppEngine SDK build functions
#

APPENGINESDK_INSTALL_ENVIRON_KEYS = [  # [default], alternate
    'APPENGINESDK_VERSION',
        # ['1.9.32'] ( APPENGINESDK_VERSION_DEFAULT )
    'APPENGINESDK_ARCHIVE',
        # ['google_appengine_{APPENGINESDK_VERSION}.zip']
    'APPENGINESDK_ARCHIVE_URL_PREFIX',
        # ['https://storage.googleapis.com/appengine-sdks/featured/']
    'APPENGINESDK_ARCHIVE_URL',
        # ['{APPENGINESDK_ARCHIVE_URL_PREFIX}{APPENGINESDK_ARCHIVE}']
    '_VAR_DATA',
        # [~/data/], /var/data
    'APPENGINESDK_ARCHIVE_DESTDIR',
        # [{_VAR_DATA}/google_appengine]
    'APPENGINESDK_ARCHIVE_PATH',
        # [{APPENGINESDK_ARCHIVE_DESTDIR}/{APPENGINESDK_ARCHIVE}]

    'APPENGINESDK_BASEPATH',  # [''], "/usr/local"
    'APPENGINESDK_FILEMODE',  # [0o751], 0o777, 0o771

    'CLOUDSDK_PREFIX',        # ~/google-cloud-sdk
    'APPENGINESDK_PREFIX',    # APPENGINESDK_BASEPATH/google_appengine
    'DEV_APPSERVER'           # APPENGINESDK_PREFIX/dev_appserver.py
]

APPENGINESDK_ENVIRON_KEYS = [
    'CLOUDSDK_PREFIX',
    'APPENGINESDK_PREFIX',
    'DEV_APPSERVER'
]

ENVIRON_ALL = APPENGINESDK_INSTALL_ENVIRON_KEYS
ENVIRON_EXPORT_KEYS = APPENGINESDK_ENVIRON_KEYS


def shell_escape_single(str_):
    # TODO:
    return str_.replace("'", """'"'"'""") # TODO TODO


@buildstep
def print_env_all(cfg, prefix="export ", keys=ENVIRON_ALL):
    for key in keys:
        if key in cfg:
            value = cfg[key]
            if value is None:
                valuestr = ''
            else:
                valuestr = str(value)
            print("{}{}='{}'".format(
                prefix,
                key,
                shell_escape_single(valuestr)))
    return BuildstepResult(returncode=0)


@buildstep
def print_env(cfg, prefix="export ", keys=ENVIRON_EXPORT_KEYS):
    return print_env_all(cfg, prefix=prefix, keys=keys)


@buildstep
def config_from_environ(cfg):
    """Read cfg from os.environ"""

    if 'APPENGINESDK_FILEMODE' in os.environ:
        value = os.environ['APPENGINESDK_FILEMODE']
        if hasattr(value, 'startswith'):
            if value.startswith('0o'):  # octal
                value = int(value, 8)
            else:
                value = int(value)
    for key in APPENGINESDK_INSTALL_ENVIRON_KEYS:
        if key in os.environ:
            envvalue = os.environ[key]
            if key in cfg:
                if cfg[key] != envvalue:
                    log.info(
                        'cfg[{!r}] = os.environ[{!r}] = {!r}'.format(
                            key, key, envvalue))
                    cfg[key] = envvalue
            else:
                cfg[key] = envvalue
    returncode = 0
    return BuildstepResult(
        returncode=returncode,
        conf=cfg)


@buildstep
def config(cfg):
    """Define cfg defaults"""
    # appengine installed in /usr/local/google_appengine:
    #   APPENGINESDK_BASEPATH = "/usr/local"
    # appengine installed in ~/google-cloud-sdk/platform/google_appengine:
    #   APPENGINESDK_BASEPATH = "~/google-cloud-sdk/platform"

    cfg.setdefault(
        "APPENGINESDK_VERSION",
        APPENGINESDK_VERSION_DEFAULT)
    cfg.setdefault(
        "APPENGINESDK_ARCHIVE",
        ("google_appengine_{APPENGINESDK_VERSION}.zip"
         ).format(**cfg))
    cfg.setdefault(
        "APPENGINESDK_ARCHIVE_URL_PREFIX",
        "https://storage.googleapis.com/appengine-sdks/featured/")
    cfg.setdefault(
        "APPENGINESDK_ARCHIVE_URL",
        ("{APPENGINESDK_ARCHIVE_URL_PREFIX}{APPENGINESDK_ARCHIVE}"
         ).format(**cfg))

    cfg.setdefault(
        '_VAR_DATA',
        os.path.join(
            os.path.expanduser('~'),
            'data'))

    cfg.setdefault(
        'APPENGINESDK_ARCHIVE_DESTDIR',
        os.path.join(
            cfg['_VAR_DATA'], 'google_appengine'))
    cfg.setdefault(
        'APPENGINESDK_ARCHIVE_PATH',
        os.path.join(
            cfg['APPENGINESDK_ARCHIVE_DESTDIR'],
            cfg['APPENGINESDK_ARCHIVE']))

    cfg.setdefault(
        'CLOUDSDK_PREFIX',
        os.path.join(
            os.path.expanduser('~'), 'google-cloud-sdk'))
    cfg.setdefault(
        'APPENGINESDK_BASEPATH',
        os.path.join(
            cfg['CLOUDSDK_PREFIX'], 'platform'))

    cfg.setdefault(
        'APPENGINESDK_PREFIX',
        os.path.join(
            cfg['APPENGINESDK_BASEPATH'], 'google_appengine'))
    cfg.setdefault(
        'DEV_APPSERVER',
        os.path.join(
            cfg['APPENGINESDK_PREFIX'], 'dev_appserver.py'))

    returncode = 0
    return BuildstepResult(
        returncode=returncode,
        conf=cfg)


@buildstep
def clean(cfg):
    """rm -r "${APPENGINESDK_PREFIX}" """
    return rm_r(cfg['APPENGINESDK_PREFIX'])


@buildstep
def install(cfg):
    """install AppEngine SDK [clean, download_zip, unzip] """
    steps = [
        # open_download_url,
        clean,
        download_zip,
        unzip
    ]
    bldr = BuildstepBuilder(steps=steps)
    results = BuildstepPlan()
    results.extend(bldr.build())
    returncode = 0 if results.success else 1
    return BuildstepResult(
        returncode=returncode,
        returnvalue=OrderedDict__([
            ('results', results)]))


@buildstep
def setup_var_data(cfg):
    key = '_VAR_DATA'
    path = cfg[key]
    filemode = cfg['APPENGINESDK_FILEMODE']
    return makedirs(path, filemode=filemode)


@buildstep
def setup_APPENGINESDK_ARCHIVE_DESTDIR(cfg):
    key = 'APPENGINESDK_ARCHIVE_DESTDIR'
    path = cfg[key]
    filemode = cfg['APPENGINESDK_FILEMODE']
    return makedirs(path, filemode=filemode)


@buildstep
def download_zip(cfg):
    # curl -fsS -O '$(APPENGINESDK_ARCHIVE_URL)'
    return download_file(
        url=cfg['APPENGINESDK_ARCHIVE_URL'],
        destdir=cfg['APPENGINESDK_ARCHIVE_DESTDIR'],
        dirmode=cfg.get('APPENGINESDK_FILEMODE',
                        APPENGINESDK_FILEMODE_DEFAULT),
        force=cfg.get('FORCE_DOWNLOAD'),
        destfile=cfg['APPENGINESDK_ARCHIVE'])


@buildstep
def unzip(cfg):
    filemode = cfg.get('APPENGINESDK_FILEMODE',
                        APPENGINESDK_FILEMODE_DEFAULT)
    archive_path = cfg['APPENGINESDK_ARCHIVE_PATH']
    basepath = cfg['APPENGINESDK_BASEPATH']
    if not (os.path.exists(archive_path) and os.path.isfile(archive_path)):
        raise AssertionError(
            ('APPENGINESDK_ARCHIVE_PATH not found',
             cfg['APPENGINESDK_ARCHIVE_PATH']))
    if not (os.path.exists(basepath) and os.path.isdir(basepath)):
        os.makedirs(cfg['APPENGINESDK_BASEPATH'], filemode)
    prefix = cfg['APPENGINESDK_PREFIX']
    if os.path.exists(prefix):
        raise AssertionError(('APPENGINESDK_PREFIX already exists',
                         ('APPENGINESDK_PREFIX',
                          cfg['APPENGINESDK_PREFIX'])))
    cmd = ('unzip', '-q',
           cfg['APPENGINESDK_ARCHIVE_PATH'],
           '-d', cfg['APPENGINESDK_BASEPATH'])
    cwd = cfg['APPENGINESDK_ARCHIVE_DESTDIR']
    retcode = subprocess_call_expect(
        cmd,
        cwd=cwd,
        expectreturncode=0)  # XXX TODO
    return BuildstepResult(
        returncode=retcode,
        returnvalue=OrderedDict__([
            ('cmd', cmd)]))


def parse_versionstr_without_yaml(yamlstr):
    """
    Args:
        yamlstr (str):
    Returns:
        str: the `release: "<versionstr>"` from a yaml string
    """
    import re
    rgxstr = r'^release: "([\d\.]+)"'
    matchlist = re.findall(rgxstr, yamlstr)
    if not len(matchlist):
        raise ValueError((yamlstr, 'does not match rgx', rgxstr))
    elif len(matchlist) > 1:
        raise ValueError(('multiple matches for', rgxstr, 'found in', yamlstr))
    return matchlist[0]


@buildstep
def version_info(cfg):
    versionpath = os.path.join(cfg['APPENGINESDK_PREFIX'], 'VERSION')
    versionstr = None
    yamlstr = None
    try:
        with codecs.open(versionpath, 'r', encoding='utf8') as versionfile:
            yamlstr = versionfile.read()
        versionstr = parse_versionstr_without_yaml(yamlstr)
        returncode = 0
    except:
        returncode = 2
    ctxt = OrderedDict([
        ('versionyamlstr', yamlstr),
        ('versionstr', versionstr),
        ('versionpath', versionpath)])
    return BuildstepResult(
        returncode=returncode,
        returnvalue=ctxt,
        msg=("""{versionpath}\nVERSION:  {versionstr!s}\n{versionyamlstr}"""
             .format(**ctxt)))


def check_env_key_path_exists(cfg, key, name=None):
    path = cfg[key]
    if not os.path.exists(path):
        returncode = 1
        msg = (key, path, 'does not exist')
    else:
        returncode = 0
        msg = (key, path, 'exists')
    if name is None:
        name = 'check_env_key_path_exists({!r})'.format(key)
    return BuildstepResult(
        name=name,
        returncode=returncode,
        msg=msg)


@buildstep
def check(cfg):
    bldr = BuildstepBuilder()

    def _check_exists(key, cfg=cfg):
        bldr.append(func=check_env_key_path_exists,
                    args=(key, cfg))

    _check_exists('APPENGINESDK_PREFIX')
    _check_exists('DEV_APPSERVER')
    _check_exists('_VAR_DATA')
    _check_exists('APPENGINESDK_ARCHIVE_DESTDIR')
    _check_exists('APPENGINESDK_ARCHIVE_PATH')

    bldr.append(('version_info', version_info))
    results = bldr.build_plan(cfg=cfg)
    returncode = 0 if results.success else 1
    return BuildstepResult(
        returncode=returncode,
        returnvalue=OrderedDict__([
            ('results', results)]))


@buildstep
def open_download_url(cfg):
    url = 'https://cloud.google.com/appengine/downloads'
    output = webbrowser.open_new_tab(url)
    returncode = 0 if output else 1
    return BuildstepResult(
        returncode=returncode,
        returnvalue=OrderedDict__(
            url=url))


@buildstep
def open_docs_urls(cfg):
    urls = cfg.setdefault('APPENGINESDK_DOCS_URLS', [
        'https://cloud.google.com/appengine/docs/',
        'https://cloud.google.com/appengine/docs/python/',
    ])
    results = []
    for url in urls:
        results.append(webbrowser.open_new_tab(url))
    returncode = 0 if all(results) else 1
    return BuildstepResult(
        returncode=returncode,
        returnvalue=OrderedDict__(
            urls=urls))


import unittest

class TestInstallAppengineSDK(unittest.TestCase):

    def setUp(self):
        cfg = OrderedDict()
        cfg['APPENGINESDK_ARCHIVE_URL_PREFIX'] = 'http://localhost:8082/'
        self._base_cfg = cfg

    def assertReturncode(self, func, *args, **kwargs):
        retcode = kwargs.pop('code', 0)
        kwargs['cfg'] = self._base_cfg
        output_retcode = func(*args, **kwargs)
        self.assertEqual(output_retcode, retcode)


    def test_main_000(self):
        self.assertReturncode(main)
        self.assertReturncode(main, [])
        self.assertReturncode(main, argv=[])

    def test_main_001_help(self):
        with self.assertRaises(SystemExit):
            self.assertReturncode(main, ['-h'])
            self.assertReturncode(main, ['--help'])

    def test_main_001_list_build_steps(self):
        self.assertReturncode(main, ['--list-steps'])
        self.assertReturncode(main, ['--list-steps', '-v'])

    def test_main_002_config(self):
        self.assertReturncode(main, ['--config'])

    def test_main_010_get_object_name(self):
        TESTNAME1 = 'testname1'

        class _cls:
            name = TESTNAME1

        class _cls2:
            pass

        def _func1():
            pass
        self.assertEqual(get_obj_name(_cls), TESTNAME1)
        self.assertEqual(get_obj_name(_cls2), '_cls2')
        self.assertEqual(get_obj_name(_func1), '_func1')

    def test_main_010_get_object_description(self):
        TESTDESCRIPTION1 = 'testdescription1'
        TESTDESCRIPTION2 = 'testdescription222'

        class _cls:
            description = TESTDESCRIPTION1

        class _cls2:
            """testdescription1"""
            description = TESTDESCRIPTION2
            pass

        def _func1():
            """testdescription1"""
            pass

        def _funcnone():
            pass
        self.assertEqual(get_obj_description(_cls), TESTDESCRIPTION1)
        self.assertEqual(get_obj_description(_cls2), TESTDESCRIPTION2)
        self.assertEqual(get_obj_description(_func1), TESTDESCRIPTION1)
        self.assertEqual(get_obj_description(_funcnone), None)


    def test_main_102_clean_(self):
        self.assertReturncode(main, ['--clean', '--install'])

    def test_main_102_clean(self):
        self.assertReturncode(main, ['--clean', '--download'])
        self.assertReturncode(main, ['--clean', '--download', '--unzip'])
        with self.assertRaises(Exception):
            self.assertReturncode(main, ['--unzip'])
        self.assertReturncode(main, ['--clean', '--unzip'])

    def test_main_103_clean_install(self):
        self.assertReturncode(main, ['--clean', '--install'])

    def test_main_102_print_env(self):
        self.assertReturncode(main, ['--clean', '--install'])
        self.assertReturncode(main, ['--print-env'])
        self.assertReturncode(main, ['--print-env', '-q'])
        self.assertReturncode(main, ['--print-env-all'])
        self.assertReturncode(main, ['--print-env-all', '-q'])

    def test_main_101_print_version(self):
        self.assertReturncode(main, ['--clean', '--install'])
        self.assertReturncode(main, ['--print-version'])
        self.assertReturncode(main, ['--print-version', '-q'])

    def test_main_102_install_s_print_env_all_check(self):
        self.assertReturncode(main, ['--install', '-s', 'print_env_all'])
        self.assertReturncode(main, ['-s', 'check'])
        self.assertReturncode(main, ['--check'])
        with self.assertRaises(SystemExit):
            self.assertReturncode(main, ['-s'])


def main(argv=None, stdout=sys.stdout, stderr=sys.stderr, cfg=None):
    import optparse
    prs = optparse.OptionParser(
        usage="%prog [--config] [--install] [--download|--unzip]")
    prs.add_option('--config',
                   dest='config',
                   default=True,
                   action='store_true',
                   help='Print configuration variables')
    prs.add_option('--check',
                   dest='check',
                   action='store_true',
                   help='Check AppEngine SDK installation')
    prs.add_option('--install',
                   dest='install',
                   action='store_true',
                   help='Install AppEngine SDK [--clean, --download, --unzip]')
    prs.add_option('--clean',
                   dest='clean',
                   action='store_true',
                   help="Remove existing APPENGINESDK_PREFIX")
    prs.add_option('--download',
                   dest='download',
                   action='store_true',
                   help='Download AppEngine SDK')
    prs.add_option('--unzip',
                   dest='unzip',
                   action='store_true',
                   help='Unzip AppEngine SDK in APPENGINESDK_BASEPATH')

    prs.add_option('-s', '--step',
                   dest='steps',
                   action='append',
                   help='Run a named step (see: --list-steps)')

    prs.add_option('--environ',
                   dest='read_from_environ',
                   action='store_true',
                   help='Read environment variables from os.environ into cfg')

    prs.add_option('--version',
                   dest='APPENGINESDK_VERSION',
                   action='store',
                   default=None,
                   help="APPENGINESDK_VERSION to install")

    prs.add_option('--force-download',
                   dest='force_download',
                   action='store_true',
                   default=False,
                   help="(re-)download AppEngine SDK")

    prs.add_option('--print-env',
                   dest='print_env',
                   action='store_true',
                   help=("Print environment variables"))
    prs.add_option('--print-env-all',
                   dest='print_env_all',
                   action='store_true',
                   help=("Print all script cfg environment variables"))

    prs.add_option('--print-version',
                   dest='print_version',
                   action='store_true',
                   help=("Print the version of AppEngine SDK "
                         "from APPENGINESDK_PREFIX/VERSION (*)"))

    prs.add_option('--open-download',
                   dest='open_download',
                   action='store_true',
                   help=(
                       "Open the AppEngine SDK download URL in a browser tab"))
    prs.add_option('--open-docs', '--open-appengine-docs',
                   dest='open_docs',
                   action='store_true',
                   help=("Open the AppEngine SDK docs URL(s) in browser tabs"))

    prs.add_option('--list-steps',
                   dest='list_build_steps',
                   action='store_true',
                   help='Print @buildstep-decorated build functions')

    prs.add_option('-t', '--test',
                   dest='test',
                   action='store_true')
    prs.add_option('-v', '--verbose',
                   dest='verbose',
                   action='store_true',)
    prs.add_option('-q', '--quiet',
                   dest='quiet',
                   action='store_true',)

    _argv = list(argv) if argv is not None else []
    (opts, args) = prs.parse_args(args=_argv)

    log = logging.getLogger(DEFAULT_LOGGER)
    # if -q/--quiet is not specified
    if not opts.quiet:
        # logging.basicConfig() at the top here
        log.setLevel(logging.WARN)

        # if -v/--verbose is specified
        if opts.verbose:
            log.setLevel(logging.DEBUG)
    # if -q/--quiet is specified
    else:
        log.setLevel(logging.ERROR)

    log.info(('install_appenginesdk.version', __version__))
    log.info(('argv', argv))
    log.info(('args', args))

    if opts.test:
        return unittest.main(argv=[sys.argv[0]]+args, exit=False)

    if cfg is None:
        cfg = collections.OrderedDict()

    if opts.APPENGINESDK_VERSION:
        cfg['APPENGINESDK_VERSION'] = opts.APPENGINESDK_VERSION

    cfg['FORCE_DOWNLOAD'] = opts.force_download
    # cfg['opts'] = opts.__dict__

    plan = BuildstepPlan()

    if opts.list_build_steps:
        print_buildsteps()

    if opts.read_from_environ:
        plan.append(
            ('config_from_environ',
                config_from_environ))

    if opts.install or opts.config:
        plan.append(
            ('config',
                config))

    if opts.install or opts.check:
        plan.append(
            ('check/before',
                check))
    if opts.install or opts.clean:
        plan.append(
            ('clean',
                clean))
    if opts.install or opts.download:
        plan.append(
            ('download_zip',
                download_zip))
    if opts.install or opts.unzip:
        plan.append(
            ('unzip',
                unzip))
    if opts.steps:
        for name in opts.steps:
            matching_steps = get_buildstep(name)
            for step in matching_steps:
                key = get_obj_name(step)
                _result = (key, step)
                plan.append(_result)

    if opts.install or (opts.check and any(
            (opts.install, opts.clean, opts.download, opts.unzip))):
        plan.append(
            ('check/after',
                check))

    if opts.install or opts.print_env_all:
        plan.append((
            'print_env_all',
                print_env_all))

    if opts.print_env:
        plan.append((
            'print_env',
                print_env))

    if opts.open_download:
        plan.append((
            'open_download_url',
                open_download_url))
    if opts.open_docs:
        plan.append((
            'open_docs_urls',
                open_docs_urls))

    if opts.print_version:
        result = version_info(cfg)
        versionstr = result.data['msg'][-1]  # NOTE TODO XXX
        print(versionstr)

    if not opts.quiet:
        # print(plan)
        if not (len(plan) == 1 and plan[0].data['name'] == 'config'):
            plan.print_all(argv=_argv, file=stdout)

    for step in plan:
        args = [cfg]
        args.extend(step.data.get('args', []))
        kwargs = step.data.get('kwargs', {})
        func = step.data['func']
        name = step.data['name']
        step.result = func(*args, **kwargs)

    if not opts.quiet:
        # print(plan)
        if not (len(plan) == 1 and plan[0].data['name'] == 'config'):
            plan.print_all(argv=_argv, file=stdout)

    retcode = 0 if plan.success else 1
    return retcode


if __name__ == "__main__":
    sys.exit(main(argv=sys.argv[1:]))
