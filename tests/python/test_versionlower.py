#!/usr/bin/python
import unittest
#import lib.playonlinux as playonlinux
import string

def VersionLower(version1, version2):
    version1 = string.split(version1, "-")
    version2 = string.split(version2, "-")

    try:
        if(version1[1] != ""):
            dev1 = True
    except:
        dev1 = False

    try:
        if(version1[2] != ""):
            dev2 = True
    except:
        dev2 = False

    if(version1[0] == version2[0]):
        if(dev1 == True and dev2 == False):
            return True
        else:
            return False

    version1 = [ int(digit) for digit in string.split(version1[0],".") ]
    version2 = [ int(digit) for digit in string.split(version2[0],".") ]

    if(version1[0] < version2[0]):
        return True
    elif(version1[0] == version2[0]):
        if(version1[1] < version2[1]):
            return True
        elif(version1[1] == version2[1]):
            if(version1[2] < version2[2]):
                return True
            else:
                return False
        else:
            return False
    else:
        return False

class TestVersionLower(unittest.TestCase):

    def test_major_greater(self):
        self.assertTrue(VersionLower("4.0.0", "5.0.0"))

    def test_major_equal(self):
        self.assertFalse(VersionLower("4.0.0", "4.0.0"))

    def test_major_lesser(self):
        self.assertFalse(VersionLower("4.0.0", "3.0.0"))

    def test_minor_greater(self):
        self.assertTrue(VersionLower("4.0.0", "4.1.0"))

    def test_minor_equal(self):
        self.assertFalse(VersionLower("4.1.0", "4.1.0"))

    def test_minor_lesser(self):
        self.assertFalse(VersionLower("4.1.0", "4.0.0"))

    def test_tag_greater(self):
        self.assertTrue(VersionLower("4.0.0", "4.0.1"))

    def test_tag_equal(self):
        self.assertFalse(VersionLower("4.0.1", "4.0.1"))

    def test_tag_lesser(self):
        self.assertFalse(VersionLower("4.0.1", "4.0.0"))

# 4.0.0-dev < 4.0.0 < 4.0.1-dev < 4.0.1
    def test_dev_released(self):
        self.assertTrue(VersionLower("4.0.0-dev", "4.0.0"))
        self.assertFalse(VersionLower("4.0.0", "4.0.0-dev"))

    def test_next_dev(self):
        self.assertTrue(VersionLower("4.0.0", "4.0.1-dev"))
        self.assertFalse(VersionLower("4.0.1-dev", "4.0.0"))

    def test_bug_genant(self):
        self.assertFalse(VersionLower("4.1.10-dev", "4.1.9"))

    def test_ca_marchait_avant(self):
        self.assertFalse(VersionLower("4.0.10-dev", "4.0.9"))

if __name__ == '__main__':
    unittest.main()
