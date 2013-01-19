import unittest
import os
import tempfile
from ConfigFile import ConfigFile

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

    def test_delete_setting(self):
        self.config.setSetting('toto', 'tata')
        self.assertEqual(self.config.getSetting('toto'), 'tata')
        self.config.deleteSetting('toto')
        self.assertEqual(self.config.getSetting('toto'), '')

    def tearDown(self):
        try:
            os.unlink(self.filename)
        except:
            pass

if __name__=='__main__':
    unittest.main()
