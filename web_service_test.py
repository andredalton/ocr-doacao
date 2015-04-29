#!/usr/bin/python
# -*- coding: UTF8 -*-

import unittest


class TestWebService(unittest.TestCase):
    def __init__(self, app):
        self.app = app

    def setUp(self):
        pass

if __name__ == '__main__':
    unittest.main()