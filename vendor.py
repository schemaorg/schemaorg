#
# Copyright 2014 Jon Wayne Parrott, [proppy], Michael R. Bernstein
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# Notes:
# - Imported from https://github.com/jonparrott/Darth-Vendor/.
# - Added license header.
# - Renamed `darth.vendor` to `vendor.add` to match upcoming SDK interface.
# - Renamed `position` param to `index` to match upcoming SDK interface.
# - Removed funny arworks docstring.

import site
import os.path
import sys


def add(folder, index=1):
  """
  Adds the given folder to the python path. Supports namespaced packages.
  By default, packages in the given folder take precedence over site-packages
  and any previous path manipulations.

  Args:
    folder: Path to the folder containing packages, relative to ``os.getcwd()``
    position: Where in ``sys.path`` to insert the vendor packages. By default
      this is set to 1. It is inadvisable to set it to 0 as it will override
      any modules in the current working directory.
  """

  # Check if the path contains a virtualenv.
  site_dir = os.path.join(folder, 'lib', 'python' + sys.version[:3], 'site-packages')
  if os.path.exists(site_dir):
    folder = site_dir
  # Otherwise it's just a normal path, make it absolute.
  else:
    folder = os.path.join(os.path.dirname(__file__), folder)

  # Use site.addsitedir() because it appropriately reads .pth
  # files for namespaced packages. Unfortunately, there's not an
  # option to choose where addsitedir() puts its paths in sys.path
  # so we have to do a little bit of magic to make it play along.

  # We're going to grab the current sys.path and split it up into
  # the first entry and then the rest. Essentially turning
  #   ['.', '/site-packages/x', 'site-packages/y']
  # into
  #   ['.'] and ['/site-packages/x', 'site-packages/y']
  # The reason for this is we want '.' to remain at the top of the
  # list but we want our vendor files to override everything else.
  sys.path, remainder = sys.path[:1], sys.path[1:]

  # Now we call addsitedir which will append our vendor directories
  # to sys.path (which was truncated by the last step.)
  site.addsitedir(folder)

  # Finally, we'll add the paths we removed back.
  # The final product is something like this:
  #   ['.', '/vendor-folder', /site-packages/x', 'site-packages/y']
  sys.path.extend(remainder)
