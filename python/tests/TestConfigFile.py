import unittest
import os
import tempfile
from lib.ConfigFile import ConfigFile

class TestConfigFile(unittest.TestCase):
    def setUp(self):
        # Make sure filename is a non-existing filename
        fd, filename = tempfile.mkstemp()
        os.close(fd)
        os.unlink(filename)
        self.filename = filename
        self.config = ConfigFile(filename)

    def test_read_from_non_existing_file(self):
        self.assertEqual(self.config.getSetting('toto'), '')

    def test_write_to_non_existing_file(self):
        self.config.setSetting('toto', 'tata')
        self.assertEqual(self.config.getSetting('toto'), 'tata')

    def test_write_two_settings(self):
        self.config.setSetting('toto', 'tata')
        self.config.setSetting('riri', 'fifi')
        self.assertEqual(self.config.getSetting('toto'), 'tata')
        self.assertEqual(self.config.getSetting('riri'), 'fifi')

    def test_overwrite_setting(self):
        self.config.setSetting('toto', 'tata')
        self.config.setSetting('toto', 'tutu')
        self.assertEqual(self.config.getSetting('toto'), 'tutu')

    def test_delete_setting(self):
        self.config.setSetting('toto', 'tata')
        self.assertEqual(self.config.getSetting('toto'), 'tata')
        self.config.deleteSetting('toto')
        self.assertEqual(self.config.getSetting('toto'), '')

    def test_delete_non_existing_setting(self):
        self.config.setSetting('toto', 'tata')
        self.config.deleteSetting('riri')
        self.assertEqual(self.config.getSetting('toto'), 'tata')

# TODO
# - define and check all allowed characters in both name and value

    def test_equal_sign_in_value(self):
        self.config.setSetting('toto', 'this=that')
        self.assertEqual(self.config.getSetting('toto'), 'this=that')

    def test_ambiguous_values(self):
        self.config.setSetting('toto', 'tata=')
        self.config.setSetting('tata', 'toto=')
        self.assertEqual(self.config.getSetting('toto'), 'tata=')
        self.assertEqual(self.config.getSetting('tata'), 'toto=')

    def tearDown(self):
        try:
            os.unlink(self.filename)
        except:
            pass


if __name__=='__main__':
    unittest.main()
