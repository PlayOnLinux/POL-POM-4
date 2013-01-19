import unittest
import os

class InitEnv(unittest.TestCase):
    def setUp(self):
        self.environ_backup = os.environ
        os.environ["POL_OS"] = "Linux"
        os.environ["MACHTYPE"] = "x86_64"
        import lib.Variables as Variables
        Variables.initialization()

    def tearDown(self):
        os.environ = self.environ_backup
