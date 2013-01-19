import unittest
import tempfile
import shutil

from InitEnv import InitEnv

class TestPrefix(InitEnv):
    def setUp(self):
        InitEnv.setUp(self)
        from lib.Prefix import Prefix
        self.old_prefixes_path = Prefix.PREFIXES_PATH
        self.prefixes_path = tempfile.mkdtemp()
        Prefix.PREFIXES_PATH = self.prefixes_path

        self.prefix_name = 'Prefix%d' % (random.randint(1,100000000),)
        self.prefix = Prefix(self.prefix_name)

    def test_getname(self):
        self.assertEqual(self.prefix.getName(), self.prefix_name)

    def test_exists_non_existing(self):
        self.assertFalse(self.prefix.exists())

    def test_exists_existing(self):
        self.assertFalse(self.prefix.exists())
        self.prefix.createPath()
        self.assertTrue(self.prefix.exists())
        
    def test_created_not_created(self):
        self.prefix.createPath()
        self.assertFalse(self.prefix.created())

    def test_exists_deleted(self):
        self.prefix.createPath()
        self.assertTrue(self.prefix.exists())
        self.prefix.delete()
        self.assertFalse(self.prefix.exists())

    def test_get_wine_version_non_existing(self):
        # whatever is supposed to be the right behavior here
        self.assertEqual(self.prefix.getWineVersion(), "")

    def test_get_arch_non_existing(self):
        # whatever is supposed to be the right behavior here
        self.assertEqual(self.prefix.getArch(), "")

    def test_get_shortcuts_list_non_existing(self):
        # whatever is supposed to be the right behavior here
        self.assertEqual(self.prefix.getShortcutList(), [])

    def test_get_shortcuts_list_existing(self):
        self.prefix.createPath()
        self.assertEqual(self.prefix.getShortcutList(), [])

    def test_delete_non_existing(self):
        self.assertEqual(self.prefix.delete(), 0)

    def test_delete_existing(self):
        self.prefix.create()
        self.assertEqual(self.prefix.delete(), 0)

    def test_delete_default(self):
        self.prefix = Prefix("default")
        self.prefix.create()
        self.assertEqual(self.prefix.delete(), 1)

    def test_list_no_prefix(self):
        self.assertEqual(Prefix.getList(), [])

    def test_list_one_prefix(self):
        self.prefix.create()
        self.assertEqual(Prefix.getList(), [self.prefix_name])

    def tearDown(self):
        Prefix.PREFIXES_PATH = self.old_prefixes_path
        shutil.rmtree(self.prefixes_path, ignore_errors=True)
        InitEnv.tearDown(self)


if __name__=='__main__':
    unittest.main()
