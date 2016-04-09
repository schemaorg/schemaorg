#!/usr/bin/env python

import codecs
import collections
import logging
import os
import pprint

import jinja2

from collections import OrderedDict

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()


class TemplateBuilder(object):

    def __init__(self, templatedir, **kwargs):
        envargs = OrderedDict()
        context = OrderedDict()
        context['escape_xhtml'] = jinja2.escape
        envargs['loader'] = jinja2.FileSystemLoader(templatedir)
        envargs['autoescape'] = kwargs.get('autoescape', True)
        if envargs.get('autoescape'):
            envargs.setdefault('extensions', [])
            envargs['extensions'].append('jinja2.ext.autoescape')
        self.env = jinja2.Environment(**envargs)
        self.context = context

    def render(self, templatename, context):
        tmpl = self.env.loader.load(self.env, templatename)
        ctxt = self.context.copy()
        ctxt.update(context)
        return tmpl.render(ctxt)


DOCKERFILE_TEMPLATE_ARGS = [
    ('Dockerfile.Ubuntu-14.04', 'Dockerfile.Debian.jinja',
     {'os': 'Ubuntu',
      'osrelease': '14.04',
      'os_family': 'Debian'}),
    ('Dockerfile.Ubuntu-15.04', 'Dockerfile.Debian.jinja',
     {'os': 'Ubuntu',
      'osrelease': '15.04',
      'os_family': 'Debian'}),
    ('Dockerfile.Ubuntu-16.04', 'Dockerfile.Debian.jinja',
     {'os': 'Ubuntu',
      'osrelease': '16.04',
      'os_family': 'Debian'}),
    ('Dockerfile.Fedora-23', 'Dockerfile.RedHat.jinja',
     {'os': 'Fedora',
      'osrelease': '23',
      'os_family': 'RedHat'}),
    ('Dockerfile.CentOS-7', 'Dockerfile.RedHat.jinja',
     {'os': 'CentOS',
      'osrelease': '7',
      'os_family': 'RedHat'}),
]


def build__project_properties__schemaorg_cfg(cfg):
    """
    Args:
        cfg (dict): configuration dict/OrderedDict
    Returns:
        None
    """
    cfg['project_orgname'] = cfg.get("project_orgname", "schemaorg")
    cfg['project_name'] = cfg.get("project_name", "schemaorg")
    cfg['project_path'] = cfg.get(
        'project_path',
        "{}/{}".format(cfg['project_orgname'], cfg['project_name']))
    cfg['project_src_rev'] = "sdo-deimos" # XXX
    cfg['project_https_url'] = (
        'https://github.com/{project_path}')
    cfg['project_src_rev_url_tmpl'] = (
        'https://github.com/{project_path}/tree/{rev}')
    cfg['project_src_rev_url'] = (
        cfg['project_src_rev_url_tmpl'].format(
            rev=cfg['project_src_rev'],
            **cfg))


def build__project_properties(cfg):
    """
    Args:
        cfg (dict): configuration dict/OrderedDict
    Returns:
        None
    """
    cfg['project_orgname'] = cfg['project_orgname']
    cfg['project_name'] = cfg['project_name']
    cfg['project_path'] = cfg.get(
        'project_path',
        "{}/{}".format(cfg['project_orgname'], cfg['project_name']))
    cfg['project_src_rev'] = cfg.get(
        'project_src_rev',
        'master')
    # cfg['project_https_url'] = (
    #     'https://github.com/{project_path}')
    # cfg['project_src_rev_url_tmpl'] = (
    #     'https://github.com/{project_path}/tree/{rev}')
    # cfg['project_src_rev_url'] = (
    #     cfg['project_src_rev_url_tmpl'].format(
    #         rev=cfg['project_src_rev'],
    #         **cfg))


def build__docker_properties(cfg):
    """
    Args:
        cfg (dict): configuration dict/OrderedDict
    Returns:
        None
    """
    required_keys = ['os', 'osrelease', 'os_family']
    for key in required_keys:
        if key not in cfg:
            raise ValueError(('key', key, 'must be set'))

    cfg['docker_orgname'] = cfg.get(  # 'schemaorg'
        'docker_orgname',
        cfg.get('project_orgname'))
    # cfg['docker_tag_name'] = cfg.get(
    #     'docker_tag_name')
    cfg['docker_tag'] = cfg.get(
        'docker_tag',          # 'schemaorg:Fedora-23[docker_tag_suffix]'
        "{}{}-{}{}".format(
            ('{}:'.format(cfg['docker_tag_name'])
             if cfg.get('docker_tag_name') is not None else ''),
            cfg['os'],
            cfg['osrelease'],
            ('-{}'.format(cfg['docker_tag_suffix'])
             if cfg.get('docker_tag_suffix') is not None else '')))
    cfg['docker_dockerfile'] = cfg.get(
        'docker_dockerfile',
        "Dockerfile.{}".format(cfg['docker_tag']))  # Dockerfile.Fedora-23

    if 'project_src_rev_url' in cfg:
        cfg['docker_dockerfile_url'] = cfg.get(
            'docker_dockerfile_url',
            '{}/docker/{}'.format(
                cfg['project_src_rev_url'], cfg['docker_dockerfile']))

    if 'docker_from_name' not in cfg:
        cfg['docker_from_name'] = cfg['os'].lower()  # fedora
    cfg['docker_from_tag'] = cfg.get(
        'docker_from_tag',
        cfg['osrelease'])  # 23
    cfg['docker_from'] = cfg.get(
        'docker_from',               # Fedora:23
        "{}:{}".format(cfg['docker_from_name'], cfg['docker_from_tag']))


def build_all_dockerfiles(templates, destdir, templatepath=None):
    """

    Args:
        templates (tuples): (outputfilename, templatename, {context})
        destdir (str): path prefix for ``outputfilename`` s
    Kwargs:
        templatepath (None, str): path prefix for where to write files
            (``<templateepath>``/<templatename.jinja>)

            .. note:: This defaults to ``os.path.dirname(__file__)`` (``.``)

    Yields:
        tuple: (context:OrderedDict, jinja_output:unicode)
    """
    if templatepath is None:
        templatepath = os.path.dirname(__file__)
    builder = TemplateBuilder(templatepath, autoescape=False)
    for outputfilename, templatename, _context in templates:
        _context['_outputfilename'] = outputfilename
        _context['_templatename'] = templatename
        build__project_properties__schemaorg_cfg(_context)
        build__project_properties(_context)
        build__docker_properties(_context)
        context = collections.OrderedDict()
        context['cfg'] = _context
        outputfilepath = os.path.join(destdir, outputfilename)
        jinja_output = builder.render(templatename, context)
        with codecs.open(outputfilepath, 'w', encoding='utf-8') as f:
            f.write(jinja_output)
            yield context, jinja_output


def main(argv=None):
    import optparse
    prs = optparse.OptionParser(
        usage=(
            "%(progname)s --all [-i templatepathprefix/] [-o outputprefix/ ]"))
    prs.add_option('--all',
                   dest='all',
                   action='store_true',
                   help='Build [all] Dockerfiles with jinja2')
    prs.add_option('-i', '--input-dir', '--template-path',
                   dest='templatedir',
                   action='store_true',
                   default='.',
                   help='Directory prefix of templates')
    prs.add_option('-o', '--output-dir',
                   dest='destdir',
                   default='.',
                   action='store',
                   help='Directory prefix to write templated output to')
    _argv = list(argv) if argv is not None else []
    opts, args = prs.parse_args(_argv)

    if not opts.all:
        prs.error("Specify '--all' to build the templates")
    if opts.all:
        for context, jinja_output in build_all_dockerfiles(
            DOCKERFILE_TEMPLATE_ARGS,
            opts.destdir,
            opts.templatedir
        ):
            log.info(('context', context))
            log.info(('jinja_output', jinja_output))
            print(pprint.pformat(context))
            print(jinja_output)

if __name__ == "__main__":
    import sys
    sys.exit(main(argv=sys.argv[1:]))
