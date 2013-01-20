import unittest
import sys
import os

class TestVariables(unittest.TestCase):
    def setUp(self):
        self.environ_backup = os.environ

    def _init(self):
        import lib.Variables as Variables
        Variables.initialization()

    def tearDown(self):
        # Modules unload does not work
        #if 'Variables' in sys.modules:
        #    del(sys.modules['Variables'])
        #    del Variables
        os.environ = self.environ_backup


class TestVariablesNoOS(TestVariables):
    def setUp(self):
        TestVariables.setUp(self)
        if "POL_OS" in os.environ:
            del(os.environ["POL_OS"])
    
    def test_checks_pol_os_present(self):
        self.assertRaises(SystemExit, self._init)


class TestVariablesSupportedOS(TestVariables):
    def _common_variables_present(self):
        self.assertIn('PLAYONLINUX', os.environ)
        self.assertIn('VERSION', os.environ)
        self.assertIn('SITE', os.environ)
        self.assertIn('OS_NAME', os.environ)
        self.assertIn('WINE_SITE', os.environ)
        self.assertIn('GECKO_SITE', os.environ)
        self.assertIn('POL_ID', os.environ)
        self.assertIn('POL_PORT', os.environ)
        self.assertIn('DEBIAN_PACKAGE', os.environ)
        self.assertIn(os.environ['DEBIAN_PACKAGE'], ['TRUE', 'FALSE'])

        self.assertIn('REPERTOIRE', os.environ)
        self.assertIn('POL_USER_ROOT', os.environ)
        self.assertIn('APPLICATION_TITLE', os.environ)
        self.assertIn('TITRE', os.environ)
        self.assertIn('POL_DNS', os.environ)
        self.assertIn('POL_WGET', os.environ)
        self.assertIn('WINEPREFIX', os.environ)
        self.assertIn('WINEDLLOVERRIDES', os.environ)
        self.assertIn('AMD64_COMPATIBLE', os.environ)
        self.assertIn(os.environ['AMD64_COMPATIBLE'], ['True', 'False'])
        self.assertIn('DYLD_LIBRARY_PATH', os.environ)
        self.assertIn('LD_LIBRARY_PATH', os.environ)
        self.assertIn('PATH_ORIGIN', os.environ)
        self.assertIn('LD_PATH_ORIGIN', os.environ)
        self.assertIn('DYLDPATH_ORIGIN', os.environ)
        self.assertIn('WGETRC', os.environ)


class TestVariablesLinux(TestVariablesSupportedOS):
    def setUp(self):
        TestVariablesSupportedOS.setUp(self)
        os.environ["POL_OS"] = "Linux"
        os.environ["MACHTYPE"] = "x86_64"
        TestVariables._init(self)

    def test_linux_environment(self):
        self.assertEqual(os.environ["POL_OS"], "Linux")
        self._common_variables_present()


class TestVariablesOSX(TestVariablesSupportedOS):
    def setUp(self):
        TestVariablesSupportedOS.setUp(self)
        os.environ["POL_OS"] = "Mac"
        os.environ["MACHTYPE"] = "x86_64-apple-darwin12"
        TestVariables._init(self)

    def test_osx_environment(self):
        self.assertEqual(os.environ["POL_OS"], "Mac")
        self._common_variables_present()
        self.assertIn('PLAYONMAC', os.environ)
        self.assertIn('MAGICK_HOME', os.environ)


if __name__=='__main__':
    unittest.main()
