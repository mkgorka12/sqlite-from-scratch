import pytest
from src.database import Database

@pytest.fixture
def db():
    database = Database("Chinook_Sqlite.sqlite")
    with database as active_db:
        yield active_db

def test_page_size(db):
    assert db.page_size == 1024

# sql command to get all objects in database:
# SELECT name FROM sqlite_master 
@pytest.mark.parametrize("expected_object_name", [
    'Album',
    'Artist',
    'Customer',
    'Employee',
    'Genre',
    'Invoice',
    'InvoiceLine',
    'MediaType',
    'Playlist',
    'PlaylistTrack',
    'sqlite_autoindex_PlaylistTrack_1',
    'Track',
    'IFK_AlbumArtistId',
    'IFK_CustomerSupportRepId',
    'IFK_EmployeeReportsTo',
    'IFK_InvoiceCustomerId',
    'IFK_InvoiceLineInvoiceId',
    'IFK_InvoiceLineTrackId',
    'IFK_PlaylistTrackTrackId',
    'IFK_TrackAlbumId',
    'IFK_TrackGenreId',
    'IFK_TrackMediaTypeId'
])
def test_get_object_names(db, expected_object_name):
    assert expected_object_name in db.object_names
