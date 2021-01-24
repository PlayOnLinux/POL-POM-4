import json
import os
import threading
import traceback
import urllib.request

from lib import Variables
from wine_versions.WineVersionsTools import fetchUserOS, fetch_supported_archs


class WineVersionFetcher():
    def __init__(self, operating_system):
        self.operating_system = operating_system

    def fetch_all_available_wine_version(self, callback, error):
        thread = threading.Thread(target=self._sync_fetch_all_available_wine_versions, args=(callback, error))
        thread.start()

    def _sync_fetch_all_available_wine_versions(self, callback, error):
        wine_version_url = "https://phoenicis.playonlinux.com/index.php/wine?os=%s" % self.operating_system
        print("Donwloading %s " % wine_version_url)
        try:
            request = urllib.request.Request(wine_version_url, None, {'User-Agent': Variables.userAgent})
            handle = urllib.request.urlopen(request, timeout=5)
            callback(self._convert_phoenicis_wine_versions_to_v4(json.load(handle)))
        except Exception as e:
            error(traceback.format_exc())

    def _sync_fetch_all_installed_wine_version(self):
        architectures = {}
        for architecture in fetch_supported_archs():
            wine_folder = fetchUserOS() + "-" + architecture

            if os.path.exists(Variables.playonlinux_rep + "/wine/" + wine_folder):
                available_versions = [{
                    "name": version,
                } for version in os.listdir(Variables.playonlinux_rep + "/wine/" + wine_folder) if
                    version != "installing"]
            else:
                available_versions = []

            if architecture not in architectures:
                architectures[architecture] = []

            architectures[architecture] += available_versions
        return architectures

    def fetch_all_installed_wine_version(self, callback, error):
        try:
            architectures = self._sync_fetch_all_installed_wine_version()

            callback(architectures)
        except Exception as e:
            error(traceback.format_exc())

    def _convert_phoenicis_wine_versions_to_v4(self, wine_distributions):
        """
        Converts versions from phoenicis format into a format that POL/POM 4 can handle
        """
        architectures = {}
        for wine_distribution in wine_distributions:
            name = wine_distribution["name"]
            architecture = name.split("-")[2]
            distribution = name.split("-")[0]

            if architecture not in architectures:
                architectures[architecture] = []

            for package in wine_distribution["packages"]:
                if distribution == "upstream":
                    package_name = package["version"]
                else:
                    package_name = package["version"] + "-" + distribution

                architectures[architecture] += [{
                    "name": package_name,
                    "architecture": architecture,
                    "sha1sum": package["sha1sum"],
                    "url": package["url"]
                }]


        return architectures

    def calculate_installed_hash(self):
        return hash(json.dumps((self._sync_fetch_all_installed_wine_version())))


