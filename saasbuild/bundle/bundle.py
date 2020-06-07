import os
import shlex
import subprocess
from configparser import ConfigParser

from saasbuild.platform import get_executable_path, SYSTEM

# a shorthand for shlex.split on *nix systems
_s = shlex.split if SYSTEM != 'Windows' else lambda x: x


class BundleError(Exception):
    pass


class Bundle:
    def __init__(self, activity_info_path):
        """
        Generates a information
        :param activity_info_path: A full realpath to activity.info
        """
        self.activity_info_path = activity_info_path

        # Read the activity.info and derive attributes
        config = ConfigParser()
        config.read(self.activity_info_path)
        if 'Activity' not in config:
            # if the activity does not have a section [Activity]
            # it then might be an invalid activity file
            raise BundleError(
                "Invalid activity.info file in {}. "
                "The file does not have a [Activity] section".format(self.activity_info_path)
            )
        bundle_activity_section = config['Activity']
        self._name = bundle_activity_section.get('name')
        self._activity_version = bundle_activity_section.get('activity-version')
        self._bundle_id = bundle_activity_section.get('bundle_id')
        self.icon = bundle_activity_section.get('icon')
        self._exec = bundle_activity_section.get('exec')
        self.license = bundle_activity_section.get('license')
        self.repository = bundle_activity_section.get('repository')
        self.summary = bundle_activity_section.get('summary')
        self.url = bundle_activity_section.get('url')
        self.tags = bundle_activity_section.get('tags')
        self.screenshots = bundle_activity_section.get('screenshots', '').split()

    def __repr__(self):
        return '{name} ({path})'.format(name=self._name, path=self.activity_info_path)

    def get_name(self):
        """
        Get the name of the bundle
        :return:
        """
        return self._name

    def get_version(self):
        """
        Get the version of the bundle
        :return:
        """
        return self._activity_version

    def get_bundle_id(self):
        """
        Get the unique identifier of the activity bundle
        :return:
        """
        return self._bundle_id

    def get_icon_name(self):
        """
        Get the name of the icon provided in the activity.info
        :return:
        """
        return self.icon

    def get_icon_path(self):
        """
        Get the path to the icon path
        If the icon does not exist, a fallback icon is used
        :return:
        """
        icon_path = os.path.join(
            os.path.dirname(self.activity_info_path),
            "{}.svg".format(self.icon)
        )
        if self.icon and os.path.exists(icon_path):
            return icon_path
        else:
            # return a dummy icon because the current icon was missing
            return os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'assets', 'activity-helloworld.svg'
            )

    def get_screenshots(self):
        """
        Returns a list of screenshots packaged in the activity
        TODO: Add support to extract screenshot from the screenshot / image directory
        returns screenshot if screenshot keyword is provided
        :return:
        """
        if self.screenshots:
            return self.screenshots
        else:
            raise NotImplementedError()

    def get_license(self):
        """
        Return the str of open source license by which the
        activity's source code is published
        :return:
        """
        return self.license

    def get_url(self):
        """
        Extract the url if it exists
        Returns str, url
        Returns None, if no url is provided
        :return:
        """
        return self.url

    def get_summary(self):
        """
        Extract the summary if it exists
        Returns str, if summary can be derived.
        Returns None, if no summary is provided
        :return:
        """
        return self.summary

    def get_activity_dir(self):
        """
        Returns the activity directory where the activity.info is placed
        >>> a = Bundle('path/to/bundle-activity/activity/activity.info')
        >>> a.get_activity_dir()
        'path/to/bundle-activity'

        :return: path to bundle activity : str
        """
        return os.path.dirname(os.path.dirname(self.activity_info_path))

    def do_generate_bundle(self):
        """
        Generates a .xo file for the activities
        by spawning a subprocess
        :return:
        """
        python_exe = get_executable_path('python3', False) or get_executable_path('python')
        proc = subprocess.Popen(
            _s("{} setup.py dist_xo".format(python_exe)),
            cwd=self.get_activity_dir(),
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
        exit_code = proc.wait(timeout=5000)
        out, err = proc.communicate()
        return exit_code, out.decode(), err.decode()

    def do_install_bundle(self, system=False):
        """
        Install the activity to a user level, if system
        keyword argument is provided to be False,
        otherwise installed to system `/usr` level
        :return:
        """
        flags = '' if system else '--user'
        python_exe = get_executable_path('python3', False) or get_executable_path('python')
        proc = subprocess.Popen(
            _s("{} setup.py install {}".format(python_exe, flags)),
            cwd=self.get_activity_dir(),
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
        exit_code = proc.wait(timeout=5000)
        out, err = proc.communicate()
        return exit_code, out.decode(), err.decode()
