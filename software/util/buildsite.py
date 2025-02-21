#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Program that builds the whole schema.org website."""

# Import standard python libraries
import argparse
import glob
import os
import re
import shutil
import subprocess
import sys
import time
import rdflib
import logging
import colorama

# Import schema.org libraries
if not os.getcwd() in sys.path:
    sys.path.insert(1, os.getcwd())

import software

import software.util.buildfiles as buildfiles
import software.util.buildocspages as buildocspages
import software.util.buildtermpages as buildtermpages
import software.util.copystaticdocsplusinsert as copystaticdocsplusinsert
import software.util.fileutils as fileutils
import software.util.runtests as runtests_lib
import software.util.schemaglobals as schemaglobals
import software.util.schemaversion as schemaversion
import software.util.textutils as textutils
import software.util.pretty_logger as pretty_logger

import software.SchemaExamples.schemaexamples as schemaexamples
import software.SchemaExamples.utils.assign_example_ids
import software.SchemaTerms.localmarkdown
import software.SchemaTerms.sdocollaborators as sdocollaborators
import software.SchemaTerms.sdotermsource as sdotermsource

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def initialize():
    """Initialize various systems, returns the args object"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-a",
        "--autobuild",
        default=False,
        action="store_true",
        help="clear output directory and build all components - overrides all other settings (except -examplesnum)",
    )
    parser.add_argument(
        "-c",
        "--clearfirst",
        default=False,
        action="store_true",
        help="clear output directory before creating contents",
    )
    parser.add_argument(
        "-d",
        "--docspages",
        default=[],
        action="append",
        nargs="*",
        help="create docs page(repeatable) - ALL = all pages",
    )
    parser.add_argument(
        "-e",
        "--examplesnum",
        default=False,
        action="store_true",
        help="Add missing example ids",
    )
    parser.add_argument(
        "-f",
        "--files",
        default=[],
        action="append",
        nargs="*",
        help="create files(repeatable) - ALL = all files",
    )
    parser.add_argument(
        "-o", "--output", help="output site directory (default: ./software/site)"
    )
    parser.add_argument(
        "-r",
        "--runtests",
        default=False,
        action="store_true",
        help="run test scripts before creating contents",
    )
    parser.add_argument(
        "-s",
        "--static",
        default=False,
        action="store_true",
        help="Refresh static docs in site image",
    )
    parser.add_argument(
        "-t",
        "--terms",
        default=[],
        action="append",
        nargs="*",
        help="create page for term (repeatable) - ALL = all terms",
    )
    parser.add_argument(
        "-b",
        "--buildoption",
        default=[],
        action="append",
        nargs="*",
        help="build option(repeatable) - flags to be passed to build code",
    )
    parser.add_argument(
        "--rubytests",
        default=False,
        action="store_true",
        help="run the post generation ruby tests",
    )
    parser.add_argument(
        "--release",
        default=False,
        action="store_true",
        help="create page for term (repeatable) - ALL = all terms",
    )
    args = parser.parse_args()

    for op in args.buildoption:
        schemaglobals - BUILDOPTS.extend(op)

    for ter in args.terms:
        schemaglobals.TERMS.extend(ter)

    for pgs in args.docspages:
        schemaglobals.PAGES.extend(pgs)

    for fls in args.files:
        schemaglobals.FILES.extend(fls)

    if args.output:
        schemaglobals.OUTPUTDIR = args.output

    if args.autobuild or args.release:
        schemaglobals.TERMS = ["ALL"]
        schemaglobals.PAGES = ["ALL"]
        schemaglobals.FILES = ["ALL"]

    ###################################################
    # MARKDOWN INITIALISE
    ###################################################
    software.SchemaTerms.localmarkdown.Markdown.setWikilinkCssClass("localLink")
    software.SchemaTerms.localmarkdown.Markdown.setWikilinkPrePath("/")
    software.SchemaTerms.localmarkdown.Markdown.setWikilinkPostPath("")

    pretty_logger.MakeRootLogPretty()

    return args


def clear():
    if args.clearfirst or args.autobuild:
        log.info(f"Clearing {schemaglobals.OUTPUTDIR} directory")
        if os.path.isdir(schemaglobals.OUTPUTDIR):
            for root, dirs, files in os.walk(schemaglobals.OUTPUTDIR):
                for f in files:
                    if f != ".gitkeep":
                        os.unlink(os.path.join(root, f))
                for d in dirs:
                    shutil.rmtree(os.path.join(root, d))


###################################################
# RUN TESTS
###################################################
def runtests():
    if args.runtests or args.autobuild:
        with pretty_logger.BlockLog(
            logger=log, message="Running test scripts before proceeding…"
        ):
            errorcount = runtests_lib.main("./software/tests/")
            if errorcount:
                log.error(f"Errors returned: {errorcount}")
                sys.exit(errorcount)


###################################################
# INITIALISE Directory
###################################################


def initdir(output_dir, handler_path):
    log.info(f'Building site in "{output_dir}" directory')
    fileutils.createMissingDir(output_dir)
    clear()
    fileutils.createMissingDir(os.path.join(output_dir, "docs"))
    fileutils.createMissingDir(os.path.join(output_dir, "docs/contributors"))
    fileutils.createMissingDir(
        os.path.join(output_dir, "empty")
    )  # For apppengine 404 handler
    fileutils.createMissingDir(
        os.path.join(output_dir, "releases", schemaversion.getVersion())
    )

    gdir = os.path.join(output_dir, "gcloud")
    fileutils.createMissingDir(gdir)

    with pretty_logger.BlockLog(logger=log, message="Copying docs static files"):
        copystaticdocsplusinsert.copyFiles("./docs", "./software/site/docs")

    with pretty_logger.BlockLog(logger=log, message="Preparing GCloud files") as block:
        gcloud_files = glob.glob("software/gcloud/*.yaml")
        for path in gcloud_files:
            shutil.copy(path, gdir)
        block.append("copied %d files" % len(gcloud_files))

    message = "Creating %s from %s for version: %s" % (
        handler_path,
        schemaglobals.HANDLER_TEMPLATE,
        schemaversion.getVersion(),
    )
    with pretty_logger.BlockLog(logger=log, message=message):
        with open(os.path.join(gdir, schemaglobals.HANDLER_TEMPLATE)) as template_file:
            template_data = template_file.read()
        handler_data = template_data.replace("{{ver}}", schemaversion.getVersion())
        with open(os.path.join(gdir, handler_path), mode="w") as yaml_file:
            yaml_file.write(handler_data)


###################################################
# TERMS SOURCE LOAD
###################################################
LOADEDTERMS = False


def loadTerms():
    global LOADEDTERMS
    if LOADEDTERMS:
        return
    LOADEDTERMS = True
    if not sdotermsource.SdoTermSource.SOURCEGRAPH:
        with pretty_logger.BlockLog(logger=log, message="Loading triples files"):
            graph = sdotermsource.SdoTermSource.loadSourceGraph("default")

        with pretty_logger.BlockLog(logger=log, message="Loading contributors"):
            sdocollaborators.collaborator.loadContributors()


###################################################
# BUILD INDIVIDUAL TERM PAGES
###################################################
def processTerms(terms):
    if len(terms):
        with pretty_logger.BlockLog(
            logger=log, message="Building term definition pages", timing=True
        ):
            loadTerms()
            schemaexamples.SchemaExamples.loaded()
            buildtermpages.buildTerms(terms)


###################################################
# BUILD DYNAMIC DOCS PAGES
###################################################
def processDocs(pages):
    if len(pages):
        with pretty_logger.BlockLog(
            logger=log, message="Building dynamic documentation pages", timing=True
        ):
            loadTerms()
            buildocspages.buildDocs(pages)


###################################################
# BUILD FILES
###################################################
def processFiles(files):
    if len(files):
        with pretty_logger.BlockLog(logger=log, message="Building supporting files"):
            loadTerms()
            schemaexamples.SchemaExamples.loaded()
            buildfiles.buildFiles(files)


###################################################
# Run ruby tests
###################################################


def runRubyTests(release_dir):
    with pretty_logger.BlockLog(logger=log, message="Running ruby tests"):
        log.info("Setting up LATEST")
        version = schemaversion.getVersion()
        src_dir = os.path.join(os.getcwd(), release_dir, version)
        dst_dir = os.path.join(os.getcwd(), release_dir, "LATEST")
        if os.path.islink(dst_dir):
            os.unlink(dst_dir)
        os.symlink(src_dir, dst_dir)
        cmd = ["bundle", "exec", "rake"]
        cwd = os.path.join(os.getcwd(), "software/scripts")
        log.info("Running tests")
        subprocess.check_call(cmd, cwd=cwd)
        log.info(f"Cleaning up {dst_dir}")
        os.unlink(dst_dir)


###################################################
# COPY CREATED RELEASE FILES into Data area
###################################################


def copyReleaseFiles(release_dir):
    version = schemaversion.getVersion()
    with pretty_logger.BlockLog(
        message=f"Copying release files for version {version} to data/releases",
        logger=log,
    ):
        srcdir = os.path.join(os.getcwd(), release_dir, version)
        destdir = os.path.join(os.getcwd(), "data/releases/", version)
        fileutils.mycopytree(srcdir, destdir)
        cmd = ["git", "add", destdir]
        subprocess.check_call(cmd)


###################################################
# Main program
###################################################

if __name__ == "__main__":
    args = initialize()

    software.CheckWorkingDirectory()
    log.info(
        f"Version: {schemaversion.getVersion()} Released: {schemaversion.getCurrentVersionDate()}"
    )
    if args.release:
        args.autobuild = True
        log.info("BUILDING RELEASE VERSION")
    if args.examplesnum or args.release or args.autobuild:
        with pretty_logger.BlockLog(
            message="Checking Examples for assigned identifiers", logger=log
        ):
            software.SchemaExamples.utils.assign_example_ids.AssignExampleIds()
    initdir(output_dir=schemaglobals.OUTPUTDIR, handler_path=schemaglobals.HANDLER_FILE)
    runtests()
    processTerms(terms=schemaglobals.TERMS)
    processDocs(pages=schemaglobals.PAGES)
    processFiles(files=schemaglobals.FILES)
    if args.rubytests:
        runRubyTests(release_dir=schemaglobals.RELEASE_DIR)
    if args.release:
        copyReleaseFiles(release_dir=schemaglobals.RELEASE_DIR)
