import unittest
import traitcapture
from traitcapture import orm
from traitcapture.orm import TableBase, Accession, Species, User
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from tempfile import mkstemp
from shutil import copy2, rmtree, copytree
import os
from os import path, makedirs


TEST_DIR = path.dirname(__file__)
DATA_DIR = path.join(TEST_DIR, "data")
OUT_DIR = path.join(TEST_DIR, "out")
TEMPLATE_DB = path.join(DATA_DIR, "test.db")


class BaseTest(unittest.TestCase):
    """Base of all tests, includes tmp dir creation/deletion"""
    def setUp(self):
        makedirs(OUT_DIR)

    def tearDown(self):
        rmtree(OUT_DIR)


class BaseORMTest(BaseTest):
    """Base of all ORM-testing cases, creates a db engine"""
    def setUp(self):
        super(BaseTest, self).setUp()
        db_fh, self.db_fn = mkstemp()
        self.engine = create_engine("sqlite://")
        orm.Session = sessionmaker(bind=self.engine)
        orm.TableBase.metadata.create_all(self.engine)
        self.session = orm.Session()
        usr = User(
                user_name="test",
                given_name="test",
                family_name="user",
                email="test@example.com",
                phone="+6123456789",
                organisation="test organisation"
                )
        spe = Species(
                genus="Test",
                species="testii",
                family="testaceae",
                abbreviation="Tte",
                )
        self.session.add(usr)
        self.session.add(spe)
        self.session.commit()

    def tearDown(self):
        super(BaseTest, self).tearDown()
        self.session.close()
        os.remove(self.db_fn)


class TestORMSetup(BaseTest):
    # don't explicity use unittests here, we just want errors to be raised
    def test_ormsetup_inmemory(self):
        engine = create_engine("sqlite://")
        session = sessionmaker(bind=engine)()
        TableBase.metadata.create_all(engine)

    def test_orm_generation_function(self):
        db_fn = path.join(OUT_DIR, "test.db")
        orm.main(db_fn)
        self.assertTrue(path.exists(db_fn))

class TestSpecies(BaseORMTest):

    def test_add_species(self):
        """Test adding a species"""
        record = {
                "genus": "Eucalyptus",
                "species": "scoparia",
                "family": "Myrtaceae",
                "abbreviation": "Eusco"
                }
        # Create
        record_instance = Species(**record)
        """Test adding a species"""
        self.assertTrue(isinstance(record_instance, Species))
        # Consistency
        for key, value in record.iteritems():
            self.assertEqual(getattr(record_instance, key), value)
        # Insert
        self.session.add(record_instance)
        self.session.commit()
        self.assertEqual(record_instance.id, 2)

    def test_add_species_noabbrev(self):
        """Test adding species without giving an abbreviation"""
        record = {
                "genus": "Eucalyptus",
                "species": "scoparia",
                "family": "Myrtaceae",
                "abbreviation": ""
                }
        # Create
        record_instance = Species(**record)
        self.assertTrue(isinstance(record_instance, Species))
        # Consistency
        self.assertEqual(record_instance.abbreviation, "Es")
        # Insert
        self.session.add(record_instance)
        self.session.commit()
        self.assertEqual(record_instance.id, 2)

        # add again and check that the abbreviation changes
        record["species"] = "strezleckii"
        record_instance = Species(**record)
        self.session.add(record_instance)
        self.session.commit()
        self.assertEqual(record_instance.abbreviation, "Est")
        self.assertEqual(record_instance.id, 3)


class TestUser(BaseORMTest):
    def test_add_user(self):
        """Test adding a user"""
        record = {
                "user_name": "testuser1",
                "given_name": "test1",
                "family_name": "user",
                "email": "testuser1@example.com",
                "phone_number": "+6123456789",
                "organisation": "test_organisation"
                }
        # Create
        record_instance = User(**record)
        self.assertTrue(isinstance(record_instance, User))
        # Consistency
        for key, value in record.iteritems():
            self.assertEqual(getattr(record_instance, key), value)
        # Insert
        self.session.add(record_instance)
        self.session.commit()
        self.assertEqual(record_instance.id, 2)


class TestAccession(BaseORMTest):
    def test_add_accession(self):
        """Test adding an accession (required fields only)"""
        record = {
                "accession_name": "test_accession",
                "species_id": 1,
                "collector_id": 1,
                "user_id": 1,
                "latitude": 145.0,
                "longitude": 45.0,
                "altitude": 45.0,
                "locality_name": "Nowhere",
                "date_collected": datetime(2012, 12, 12, 12, 12, 12,0)
                }
        # Create
        record_instance = Accession(**record)
        self.assertTrue(isinstance(record_instance, Accession))
        # Consistency
        for key, value in record.iteritems():
            self.assertEqual(getattr(record_instance, key), value)
        # Insert
        self.session.add(record_instance)
        self.session.commit()
        self.assertEqual(record_instance.id, 1)
