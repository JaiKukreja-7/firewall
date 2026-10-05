import sqlite3
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from reporting_demo import create_fixture, validate, open_reader

class ReportingTests(unittest.TestCase):
    def test_read_only_reporting_and_exception(self):
        with TemporaryDirectory() as folder:
            db = Path(folder) / 'db.sqlite'
            create_fixture(db)
            evidence = validate(db)
            self.assertEqual(len(evidence['results']), 13)
            for result in evidence['results']:
                with self.subTest(result['name']):
                    self.assertTrue(result['passed'])

    def test_read_only_uri_independently_rejects_writes(self):
        with TemporaryDirectory() as folder:
            db = Path(folder) / 'db.sqlite'
            create_fixture(db)
            con = sqlite3.connect(db.resolve().as_uri() + '?mode=ro', uri=True)
            try:
                with self.assertRaises(sqlite3.OperationalError):
                    con.execute('UPDATE telemetry SET units=0')
            finally:
                con.close()

    def test_fixture_never_replaces_existing_table(self):
        with TemporaryDirectory() as folder:
            db = Path(folder) / 'db.sqlite'
            create_fixture(db)
            with self.assertRaises(sqlite3.OperationalError):
                create_fixture(db)
            con = open_reader(db)
            try:
                self.assertEqual(len(con.execute('SELECT * FROM telemetry').fetchall()), 2)
            finally:
                con.close()
