def validate_song(data, kw):
    """
    Generic validation function. Checks that the field in the data dictionary
    is not empty.
    """
    assert data[kw]
