"""Tests for utils module.

This module is meant for simple utility testing, tests might not be provided
for all utils or contain asserts or true unit tests.

Utils module might be excluded from coverage measures.
"""

import json
import re
import unittest

from nvdlib import utils
from nvdlib.model import Document


class TestUtils(unittest.TestCase):

    def test_rhasattr(self):
        """Test `utils.rhasattr` function."""
        obj = utils.AttrDict(
            **{
                'foo': {
                    'bar': None
                }
            }
        )

        self.assertTrue(utils.rhasattr(obj, 'foo.bar'))
        self.assertTrue(utils.rhasattr(obj, 'foo'))

        obj_with_arrays = utils.AttrDict(
            **{
                'buzz': [
                    obj,
                    obj
                ]
            }
        )

        # ---
        # arrays

        self.assertTrue(utils.rhasattr(obj_with_arrays, 'buzz.foo'))
        self.assertTrue(utils.rhasattr(obj_with_arrays, 'buzz.foo.bar'))

    def test_rgetattr(self):
        """Test `utils.rgetattr` function."""

        obj = utils.AttrDict(
            **{
                'foo': {
                    'bar': True
                }
            }
        )

        self.assertIsInstance(utils.rgetattr(obj, 'foo'), utils.AttrDict)
        self.assertIsInstance(utils.rgetattr(obj, 'foo.bar'), bool)
        self.assertTrue(utils.rgetattr(obj, 'foo.bar'))

    def test_get_cpe(self):
        """Test `utils.get_cpe` function."""
        sample_cve_path = 'data/cve-1.0-sample.json'

        with open(sample_cve_path) as f:
            data = json.loads(f.read())
            doc = Document.from_data(data)

        # default
        cpe_list = utils.get_cpe(doc)

        self.assertEqual(len(cpe_list), 6)

        # application
        cpe_list = utils.get_cpe(doc, cpe_type='application')

        self.assertEqual(len(cpe_list), 0)

        # operating_system
        cpe_list = utils.get_cpe(doc, cpe_type='op')

        self.assertEqual(len(cpe_list), 6)

    def test_get_victims_notation(self):
        """Test `utils.get_victims_notation` function."""
        victims_pattern = r"^(?P<condition>[><=]=)" \
                          r"(?P<version>[^, ]+)" \
                          r"(?:,(?P<series>[^, ]+)){0,1}$"

        # versions in tuple format:
        #   (versionExact, versionEndExcluding, versionEndIncluding,
        #    versionStartIncluding, versionEndExcluding)

        # empty
        version_tuple = (None, None, None, None, None)
        victims_notation = utils.get_victims_notation(version_tuple)

        self.assertIsNone(victims_notation)

        # exact
        version_tuple = ('1.0', None, None, None, None)
        victims_notation = utils.get_victims_notation(version_tuple)

        self.assertTrue(
            all([re.fullmatch(victims_pattern, vn) for vn in victims_notation])
        )
        self.assertEqual(victims_notation, ["==1.0"])

        # including-excluding
        version_tuple = (None, None, '2.0', None, '1.0')
        victims_notation = utils.get_victims_notation(version_tuple)

        print(victims_notation)

        # TODO: should we solve this?
        # self.assertTrue(
        #     all([re.fullmatch(victims_pattern, vn) for vn in victims_notation])
        # )
        self.assertEqual(victims_notation, ['<=2.0', '>1.0'])

        # excluding-excluding
        version_tuple = (None, '2.0', None, None, '1.0')
        victims_notation = utils.get_victims_notation(version_tuple)

        # TODO: should we solve this?
        # self.assertTrue(
        #     all([re.fullmatch(victims_pattern, vn) for vn in victims_notation])
        # )
        self.assertEqual(victims_notation, ['<2.0', '>1.0'])

        # including-including
        version_tuple = (None, None, '2.0', '1.0', None)
        victims_notation = utils.get_victims_notation(version_tuple)

        self.assertTrue(
            all([re.fullmatch(victims_pattern, vn) for vn in victims_notation])
        )
        self.assertEqual(victims_notation, ['<=2.0', '>=1.0'])

    def test_dictionarize(self):
        """Test `utils.dictionarize` function."""
        sample_cve_path = 'data/cve-1.0-sample.json'

        with open(sample_cve_path) as f:
            data = json.loads(f.read())
            doc = Document.from_data(data)

        doc_dict = utils.dictionarize(doc)

        self.assertIsInstance(doc_dict, dict)
        self.assertIsInstance(doc_dict['cve'], dict)
        self.assertIsInstance(doc_dict['impact'], dict)
        self.assertIsInstance(doc_dict['configurations'], dict)
