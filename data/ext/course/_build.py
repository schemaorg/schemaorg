#!/usr/bin/env python
from __future__ import print_function
"""
for context,
i could just use unittest here
but Python uses dict internally (and not OrderedDict)
so I would then have to explicitly relabel each of the test methods
to get a deterministic *build* sequence

  test__0001__main

"""

import collections
import copy
import json
import os
import sys

UNSET = -1234j


class BuildStepJSONEncoder(json.JSONEncoder):

    @staticmethod
    def default(obj):
        if isinstance(obj, BuildStep):
            return obj.__dict__.__str__()
        raise TypeError(repr(obj) + " is not JSON serializable")


def json_dumps(*args, **kwargs):
    if 'indent' not in kwargs:
        kwargs['indent'] = 2
    kwargs['default'] = BuildStepJSONEncoder.default
    return json.dumps(*args, **kwargs)


class OrderedDict(collections.OrderedDict):

    def __str__(self):
        return "OrderedDict(%s)" % (
            json_dumps(self))  # TODO: JSONEncoder

    def __repr__(self):
        return "%s ... \n%s" % (
            collections.OrderedDict.__repr__(self),
            json_dumps(self))  # TODO: JSONEncoder

    def values(self):
        # For equality comparison in Python 3
        # TODO
        return list(collections.OrderedDict.values())


class BuildStep(object):

    def __init__(self, function=None, name=None, requires=None, **kwargs):
        if function is not None:
            self.build = function
        self.name = name
        self.requires = requires if requires is not None else []
        self._result = UNSET
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        self.conf = kwargs

    def build(conf, **kwargs):
        """
        Returns:
            int or BuildStepResult: integer returncode (nonzero on error)
                or BuildStepResult
        """
        raise NotImplemented()

    def copy(self):
        return copy.deepcopy(self)

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, value):
        if self._result is not UNSET:
            raise AttributeError('returnvalue is already set')
        self._result = value


class BuildStepResult(object):

    def __init__(self, conf=None,
                 returncode=None,
                 returnvalue=None,
                 stdout=None,
                 stderr=None,
                 step=None):
        self.data = OrderedDict()
        self.data['conf'] = conf
        self.data['returncode'] = returncode
        self.data['returnvalue'] = returnvalue
        self.data['stdout'] = stdout
        self.data['stderr'] = stderr
        self.data['step'] = step

    def __repr__(self):
        return "BuildStepResult(%s)" % json_dumps(self.data)


class BuildStepBuilder(object):

    def __init__(self, steps=None, conf=None, implicitrequires=None,
                 stdout=sys.stdout,
                 stderr=sys.stderr):
        """

        Kwargs:
            steps (iterable): iterable of BuildSteps
            conf (dict): configuration dict:
            implicitrequires ((None) or bool): if true,
                each added step will have an implicit requires
                edge to the previous step
                (if set, this overwrites the value in ``conf``)

        """
        self.conf = conf if conf is not None else OrderedDict()
        if implicitrequires is not None:
            self.conf['implicitrequires'] = implicitrequires

        self.stdout = stdout
        self.stderr = stderr

        self.steprequires = OrderedDict()
        if steps is None:
            steps = []
        self.steps = steps
        for step in self.steps:
            self.add_step(step)

    def add_step(self, step=None, requires=None, implicitrequires=None,
                 name=None):
        """Add a step to self.steps with the given requires

        Args:
            step (BuildStep): :class:`BuildStep` to add
        Kwargs:
            requires ((None) or list): list of required steps
            implicitrequires ((None) or bool): if true,
                each added step will have an implicit requires
                edge to the most recently added step
            name (str): a name for the step
        Returns:
            BuildStep: step with ``.requires``
        """
        if step is None:
            raise ValueError("step must be defined")
        if not hasattr(step, 'build'):
            step = BuildStep(step, name=name)
        if requires is None:
            requires = []
        if implicitrequires is None:
            implicitrequires = self.conf.get('implicitrequires')
        if implicitrequires and len(self.steps):
            requires.append(self.steps[-1])
        if hasattr(step, 'requires'):
            step_requires = step.requires
            if step_requires:
                requires.extend(step_requires)
        if requires:
            self.steprequires[step] = requires
            step.requires = requires
        if name is not None:
            step.name = name
        self.steps.append(step)
        return step

    def logerror(self, err, file=None):
        # log.exception(err[0], err)
        file = self.stderr if file is None else file
        return _logerror((self, err), file=file)

    def logdebug(self, err, file=None):
        # log.exception(err[0], err)
        file = self.stderr if file is None else file
        return _logdebug((self, err), file=file)

    def build(self, conf=None, skiperrors=False):
        """Build self.steps

        Kwargs:
            conf (dict or (None)):

        """
        if conf is None:
            conf = self.conf
        # Build each step (or function)
        for step in self.steps:
            _conf = conf.copy()  # A BuildStep MAY modify conf
            try:
                if not hasattr(step, 'build'):
                    _step = step
                    step = BuildStep(_step, name=None, requires=None)
                if hasattr(step, 'conf'):
                    _conf.update(step.conf)
                step.result = step.build(_conf)  # step.build()
                step.result.data['step'] = step
                conf = step.result.data['conf']
                self.logdebug((step, 'step.result', step.result))
            except Exception as e:
                self.logerror((step, e))
                if skiperrors:
                    if isinstance(e, KeyboardInterrupt):
                        raise
                    else:
                        pass
                else:
                    raise

        return self.steps  # TODO


def assert_(expr,
            msg=None,
            exc=AssertionError,
            exc_args=None,
            exc_kwargs=None):
    """Assert ``bool(expr)`` and raise an ``AssertionError``, by default

    Args:
        expr (obj): a ``bool()``-able object
    Kwargs:
        msg (obj): a ``str()``-able object for the Exception message
        exc (Exception): an ``Exception`` class to raise
                        (``AssertionError`` by default)
        exc_args   (list): a list of ``*args``   for ``exc(*args, **kwargs)``
        exc_kwargs (dict): a list of ``*kwargs`` for ``exc(*args, **kwargs)``
    Returns:
        bool: ``True`` if ``expr`` evaluates to True with ``bool(expr)``

    Raises:
        exc: ``exc(*exc_args, **exc_kwargs)`` (``AssertionError``)

    .. note::
        Python standard library ``assert`` calls are
        optimized out with ``-O`` / ``PYTHONOPTIMIZE=1``.
    """
    if not bool(expr):
        if exc_args is None:
            exc_args = []
        if exc_kwargs is None:
            exc_kwargs = {}
        if msg:
            exc_args.insert(0, msg)
        raise exc(*exc_args, **exc_kwargs)
    else:
        return True

assertTrue = assert_


def assertEqual(obj1, obj2, msg=None, **kwargs):
    """assert that obj1 == obj2 with a formatted message

    Args:
        obj1 (obj): ``obj1.__cmp__(obj2)`` must return ``0`` when
                    obj1 and obj2 are equal (``==``)
        obj2 (obj): object to compare with obj1 (``obj1.__cmp__(obj2)``)
        msg (obj): a ``str()``-able object for the Exception message
    Kwargs:
        msg (obj): a ``str()``-able object for the Exception message
        exc (Exception): an ``Exception`` class to raise
                        (``AssertionError`` by default)
        exc_args   (list): a list of ``*args``   for ``exc(*args, **kwargs)``
        exc_kwargs (dict): a list of ``*kwargs`` for ``exc(*args, **kwargs)``
    Returns:

    Raises:
        exc: ``exc(*exc_args, **exc_kwargs)`` (``AssertionError``)


    """
    msg = "assertEqual(%r == %r)%s" % (
        obj1, obj2,
        ((" :: %s" % msg) if msg else ""))
    return assert_((obj1 == obj2), msg=msg, **kwargs)


import codecs


class BuildStep__cat(BuildStep):

    def build(self, conf=None, **kwargs):
        conf.update(kwargs)
        print("## %r" % conf['filename'], file=self.stdout)
        stdout, stderr = None, None
        returncode = None
        try:
            with codecs.open(conf['filename'], 'rb', 'utf8') as file_:
                stdout = file_.read()  #
                print(stdout, file=self.stdout)
            returncode = 0
        except Exception as e:
            returncode = 2
            stderr = "## {!r}".format(e)
            pass
        finally:
            return BuildStepResult(conf=conf,
                                   returncode=returncode,
                                   stderr=stderr,
                                   stdout=stdout)


# BuildStep__rdfpipe.build = bld_rdfpipe_test

def bld_rdfpipe_test(conf=None, **kwargs):
    # import subprocess
    import sarge
    if conf is None:
        conf = OrderedDict()
    conf.update(**kwargs)
    logdebug(('conf', conf))

    cmd = sarge.shell_format(
        'rdfpipe -i rdfa:-space_preserve -o {output_format} {filename}',
        **conf)
    p = sarge.run(cmd)  # passthrough interleaved stdout/stderr (nonblocking)
    # if None:
    #     p = sarge.capture_both(cmd)  # capture stdout & stderr
    #     print(p.stdout.text)         # (this blocks & buffers all of stdout)
    #     print(p.stderr.text)         # (this blocks & buffers all of stderr)
    assertEqual(p.returncode, 0,
                "zero returncode :: $ %r" % cmd)
    returncode = 0 if (p.returncode == 0) else 2
    return SargeBuildStepResult__stdout_stderr(
        conf=conf,
        process=p,
        returncode=returncode)


class SargeBuildStepResult__stdout_stderr(BuildStepResult):

    def __init__(self,
                 conf=None,
                 process=None,
                 returncode=None,
                 returnvalue=None,
                 stdout=None,
                 stderr=None):
        if returncode is None:
            returncode = process.returncode
        return super(SargeBuildStepResult__stdout_stderr, self).__init__(
            conf=conf,
            returncode=returncode,
            returnvalue=returnvalue,
            stdout=None if process.stdout is None else process.stdout.text,
            stderr=None if process.stderr is None else process.stderr.text)


class BuildStep__rdfpipe(BuildStep):
    # confkwargs = ['output_format']
    build = staticmethod(bld_rdfpipe_test)


# BuildStep__rdflib_api
from rdflib.term import URIRef
from rdflib.parser import FileInputSource, urljoin, pathname2url


class ExampleFileInputSource(FileInputSource):

    def __init__(self, file, system_id=None):
        """

        Args:
            file (fileobj): an open file object

        Kwargs:
            system_id (None or URIRef): alternate system_id (e.g.
                for reading a file:// URI as though served from an https:// URI)
        Returns:
            ExampleFileInputSource: instance with a system_id URIRef
        ::
            other_system_id = URIRef('https://schema.org/Course#examples/example0')
            with codecs.open(file, 'rb', 'utf8') as file_:
                file_input_source = ExampleFileInputSource(file_, system_id=other_system_id)
        """
        base = urljoin("file:", pathname2url(os.getcwd()))
        if system_id is None:
            system_id = URIRef(urljoin("file:",
                                       pathname2url(file.name)),
                               base=base)
        super(FileInputSource, self).__init__(system_id)
        self.file = file
        self.setByteStream(file)
        # TODO: self.setEncoding(encoding)

    # def __init__(self, file):
    #     self.base = urljoin("file:",
    #                         pathname2url(
    #                             os.path.dirname(
    #                                 os.path.abspath(file.name))))
    #     self.system_id = URIRef(urljoin("file:",
    #                                     pathname2url(file.name)),
    #                             base=self.base)


class BuildStep__rdflib_api(BuildStep):

    def __init__(self, **kwargs):
        super(BuildStep__rdflib_api, self).__init__(**kwargs)
        if 'output_format' in kwargs:
            self.conf['output_format'] = kwargs['output_format']

    def build(self, conf):
        import rdflib
        # from rdflib.parser import StringInputSource, URLInputSource
        # from rdflib.parser import FileInputSource,  urljoin, pathname2url
        from rdflib.plugins.parsers.structureddata import RDFaParser
        from rdflib.term import URIRef
        filename = conf['filename']  # 'course.rdfa.html5.html'
        # _input_uri = pathname2url(filename)
        with open(filename, 'rb') as file:
            _input = ExampleFileInputSource(file)
            # TODO
            default_docid = URIRef(
                'https://schema.org/Course#examples/example0')
            doc_identifier = conf.get('identifier', default_docid)
            g = rdflib.ConjunctiveGraph(
                identifier=doc_identifier)
            parser = RDFaParser()
            parser.parse(_input, g)
        assertTrue(len(g))

        n3_str = g.serialize(format='n3', base=filename)
        print(n3_str, file=self.stdout)
        assertTrue(n3_str)

        # docid = URIRef('https://schema.org/Course#examples/example0')
        # for (s,p,o) in g.triples((system_id, None, None)):
        #     yield (docid, p, o)

        return BuildStepResult(conf=conf, returncode=0,
                               returnvalue={'n3_str': n3_str},
                               stdout=n3_str
                               )


def logdebug(obj, file=sys.stderr):
    print(('DBG', obj), file=file)


def logerror(obj, file=sys.stderr):
    print(('ERR', obj), file=file)

_logerror = logerror
_logdebug = logdebug


def logreturnvalue(obj, file=sys.stdout):
    # print(('TST', _id, obj), file=file)
    # print(('TST', _id, obj.data['returnvalue'], obj.data['step'].name))
    # print(('TST', _id, obj.data))
    print("<STDOUT> %s" % (id(obj)))
    print(obj.data['stdout'], file=file)
    print("</STDOUT>")


import unittest


class TestBuildStepBuilder(unittest.TestCase):

    def test_0001_main(self):
        import os
        here = os.path.dirname(os.path.abspath(__file__))
        FILENAME = 'course.rdfa.html5.html'
        conf = OrderedDict()
        conf['filename'] = os.path.join(here, FILENAME)
        conf['output_format'] = 'turtle'
        builder = BuildStepBuilder(conf=conf, implicitrequires=True)
        builder.add_step(BuildStep(bld_rdfpipe_test, name='cool 0'))
        step = BuildStep(bld_rdfpipe_test, name='cool 1*2')
        builder.add_step(step)
        builder.add_step(step)
        builder.add_step(step.copy(), name='cool 1.2')
        builder.add_step(bld_rdfpipe_test, name='cool 3')
        confstack = builder.build()
        confstack

    def test_0002_main_implicitrequires_true(self):
        pass


class BuildStep__schemaorg_ext(BuildStep):

    def build(self, conf, **kwargs):
        here = os.path.dirname(os.path.abspath(__file__))
        if 'filename' in kwargs:
            conf['filename'] = os.path.join(here, kwargs['filename'])
        elif 'filename' not in conf:
            raise ValueError('filename is not specified in conf or kwargs')
        builder = BuildStepBuilder(conf=conf, implicitrequires=False)
        #builder.add_step(bld_rdfpipe_test, name='bld_rdfpipe_test 1')
        builder.add_step(
            step=BuildStep__cat(filename=conf['filename']))
        builder.add_step(
            name='bld_rdfpipe_test 2',
            step=BuildStep__rdfpipe(output_format='turtle'))
        builder.add_step(
            name='bld_rdfpipe_test_2 output_format=json-ld',
            step=BuildStep__rdfpipe(output_format='json-ld'))
        #builder.add_step(BuildStep__rdflib_api(), name='bld_rdflib_api test 1')
        results = builder.build()
        logdebug(('results', results))
        return results


def main(args=None):
    #results = BuildStep__schemaorg_ext.build(filename='course.rdfa')
    conf = OrderedDict(filename='course.rdfa.html5.html')
    results = BuildStep__schemaorg_ext().build(conf)
    returncode = 7
    if all((r.result and r.result.data['returncode'] == 0) for r in results):
        returncode = 0
    return returncode


if __name__ == "__main__":
    import sys
    sys.exit(main(args=sys.argv[1:]))
