# Unit tests

Use unittest in tests/test_<domain>.py. Cover observable results and relevant
negative paths. Prove denied access by asserting that the blob reader is not
called. Do not weaken exact external-contract assertions.
