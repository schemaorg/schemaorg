"""`appengine_config` gets loaded when starting a new application instance."""
import vendor
# insert `lib` as a site directory so our `main` module can load
# third-party libraries, and override built-ins with newer
# versions.
vendor.add('lib')

import os
# Called only if the current namespace is not set.
def namespace_manager_default_namespace_for_request():
    # The returned string will be used as the Google Apps domain.
    applicationVersion="Default"
    if "CURRENT_VERSION_ID" in os.environ:
        applicationVersion = os.environ["CURRENT_VERSION_ID"].split('.')[0]
    return applicationVersion
