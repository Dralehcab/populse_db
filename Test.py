import os
from model.DatabaseModel import createDatabase, TAG_ORIGIN_RAW, TAG_TYPE_STRING
from database.Database import Database
import unittest
import shutil

path = os.path.relpath(os.path.join(".", "test.db"))

class TestDatabaseMethods(unittest.TestCase):

    def test_database_creation(self):
        """
        Tests the database creation
        """
        global path

        if os.path.exists(path):
            os.remove(path)
        createDatabase(path)
        self.assertTrue(os.path.exists(path))

    def test_database_constructor(self):
        """
        Tests the database constructor
        """
        global path

        # Testing without the database file existing
        if os.path.exists(path):
            os.remove(path)
        Database(path)
        self.assertTrue(os.path.exists(path))

        # Testing with the database file existing
        os.remove(path)
        createDatabase(path)
        Database(path)
        self.assertTrue(os.path.exists(path))

    def test_add_tag(self):
        """
        Tests the method adding a tag
        """
        global path

        if os.path.exists(path):
            os.remove(path)
        database = Database(path)
        database.add_tag("PatientName", True, TAG_ORIGIN_RAW, TAG_TYPE_STRING, None, None, "Name of the patient")
        tag = database.get_tag("PatientName")
        self.assertEqual(tag.name, "PatientName")
        self.assertTrue(tag.visible)
        self.assertEqual(tag.origin, TAG_ORIGIN_RAW)
        self.assertEqual(tag.type, TAG_TYPE_STRING)
        self.assertIsNone(tag.unit)
        self.assertIsNone(tag.default_value)
        self.assertEqual(tag.description, "Name of the patient")
        # TODO Testing tag table creation

    def test_get_tag(self):
        """
        Tests the method giving the Tag object of a tag
        """
        global path

        if os.path.exists(path):
            os.remove(path)
        database = Database(path)
        database.add_tag("PatientName", True, TAG_ORIGIN_RAW, TAG_TYPE_STRING, None, None, "Name of the patient")
        tag = database.get_tag("PatientName")
        self.assertIsInstance(tag, database.classes["tag"])
        tag = database.get_tag("Test")
        self.assertIsNone(tag)

    def test_remove_tag(self):
        """
        Tests the method removing a tag
        """
        global path

        if os.path.exists(path):
            os.remove(path)
        database = Database(path)
        database.add_tag("PatientName", True, TAG_ORIGIN_RAW, TAG_TYPE_STRING, None, None, "Name of the patient")
        database.remove_tag("PatientName")
        tag = database.get_tag("PatientName")
        self.assertIsNone(tag)
        # TODO Testing tag table removal

    def test_add_scan(self):
        """
        Tests the method adding a scan
        """
        global path

        if os.path.exists(path):
            os.remove(path)
        database = Database(path)
        database.add_scan("scan1", "159abc")
        database.add_scan("scan2", "def753")
        scan = database.get_scan("scan1")
        self.assertIsInstance(scan, database.classes["path"])

    def test_get_current_value(self):
        """
        Tests the method giving the current value, given a tag and a scan
        """
        global path

        if os.path.exists(path):
            os.remove(path)
        database = Database(path)
        database.add_scan("scan1", "159abc")
        database.add_scan("scan2", "def753")
        database.add_tag("PatientName", True, TAG_ORIGIN_RAW, TAG_TYPE_STRING, None, None, "Name of the patient")
        value = database.get_current_value("scan1", "PatientName")
        self.assertIsNone(value)
        database.add_value("scan1", "PatientName", "test")
        value = database.get_current_value("scan1", "PatientName")
        self.assertEqual(value, "test")

    def test_get_initial_value(self):
        """
        Tests the method giving the current value, given a tag and a scan
        """
        global path

        if os.path.exists(path):
            os.remove(path)
        database = Database(path)
        database.add_scan("scan1", "159abc")
        database.add_scan("scan2", "def753")
        database.add_tag("PatientName", True, TAG_ORIGIN_RAW, TAG_TYPE_STRING, None, None, "Name of the patient")
        value = database.get_initial_value("scan1", "PatientName")
        self.assertIsNone(value)
        database.add_value("scan1", "PatientName", "test")
        value = database.get_initial_value("scan1", "PatientName")
        self.assertEqual(value, "test")

    def test_add_value(self):
        """
        Tests the method adding a value
        """
        global path

        if os.path.exists(path):
            os.remove(path)
        database = Database(path)
        database.add_scan("scan1", "159abc")
        database.add_scan("scan2", "def753")
        database.add_tag("PatientName", True, TAG_ORIGIN_RAW, TAG_TYPE_STRING, None, None, "Name of the patient")
        database.add_value("scan1", "PatientName", "test")
        value = database.get_current_value("scan1", "PatientName")
        self.assertEqual(value, "test")

    def test_save_modifications(self):
        """
        Tests the method saving the modifications
        """

        if os.path.exists(path):
            os.remove(path)
        database = Database(path)
        database.add_scan("scan1", "159abc")
        database.add_scan("scan2", "def753")
        database.add_tag("PatientName", True, TAG_ORIGIN_RAW, TAG_TYPE_STRING, None, None, "Name of the patient")
        database.add_value("scan1", "PatientName", "test")
        shutil.copy(path, os.path.join(".", "test_origin.db"))
        shutil.copy(database.temp_file, os.path.join(".", "test_temp.db"))
        database.save_modifications()
        shutil.copy(path, os.path.join(".", "test_origin_after_commit.db"))

        # Testing that the original file is empty
        database = Database(os.path.join(".", "test_origin.db"))
        tag = database.get_tag("PatientName")
        self.assertIsNone(tag)
        value = database.get_current_value("scan2", "PatientName")
        self.assertIsNone(value)

        # Testing that the temporary file was updated
        database = Database(os.path.join(".", "test_temp.db"))
        tag = database.get_tag("PatientName")
        self.assertIsInstance(tag, database.classes["tag"])
        value = database.get_current_value("scan1", "PatientName")
        self.assertEqual(value, "test")

        # Testing that the temporary file was updated
        database = Database(os.path.join(".", "test_origin_after_commit.db"))
        tag = database.get_tag("PatientName")
        self.assertIsInstance(tag, database.classes["tag"])
        value = database.get_current_value("scan1", "PatientName")
        self.assertEqual(value, "test")

        # Testing that the save_modifications method uptades the original file
        os.remove(os.path.join(".", "test_origin.db"))
        os.remove(os.path.join(".", "test_temp.db"))
        os.remove(os.path.join(".", "test_origin_after_commit.db"))

    def test_remove_scan(self):
        """
        Tests the method that removes a scan
        """

        if os.path.exists(path):
            os.remove(path)
        database = Database(path)
        database.add_scan("scan1", "159abc")
        database.add_scan("scan2", "def753")
        database.remove_scan("scan1")
        scan = database.get_scan("scan1")
        self.assertIsNone(scan)

    def test_get_scan(self):
        """
        Tests the method adding a scan
        """
        global path

        if os.path.exists(path):
            os.remove(path)
        database = Database(path)
        database.add_scan("scan1", "159abc")
        database.add_scan("scan2", "def753")
        scan = database.get_scan("scan1")
        self.assertIsInstance(scan, database.classes["path"])
        scan = database.get_scan("scan3")
        self.assertIsNone(scan)

if __name__ == '__main__':
    unittest.main(exit=False)
    os.remove(path)