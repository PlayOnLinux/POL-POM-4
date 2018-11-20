import subprocess

class dpiFetcher():
    def fetchDPI(self):
        try:
            process = subprocess.Popen("xrdb -query|grep Xft.dpi|awk '{print $2}'", stdout=subprocess.PIPE, shell=True)
            (output, err) = process.communicate()
            return int(output)
        except ValueError:
            return 96

    # Should be fixed as possible...
    def fetch_extra_pixel(self):
        factor = self.fetchDPI() / 96
        print(factor)
        return 68.75 * factor - 50
