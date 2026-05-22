#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

if os.getcwd() not in sys.path:
    sys.path.insert(1, os.getcwd())
import software

import util.schema as schema


if __name__ == "__main__":
    print(schema.getVersion())
