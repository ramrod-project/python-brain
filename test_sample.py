from .brain.checks import verify, strip
from .brain import brain_pb2 as b
from pytest import raises

SAMPLE_TARGET = {
    "PluginName": "WaterBalloon",
    "Location": "Patio",
    "Port": "West",
    "CompletelyUnrelatedKey": False,
    "CompletelyUnrelatedDoc": {"don't worry": True},
    "CompletelyUnrelatedList": ["stuff in the list"],
}

SAMPLE_BAD_TARGET = {
    "PluginName": "WaterBalloon",
    "CompletelyUnrelatedKey": False,
}
FILTERED_OUTPUT = {
    "PluginName": "WaterBalloon",
    "Location": "Patio",
    "Port": "West",
}




def test_verify():
    assert (verify(SAMPLE_TARGET, b.Target()))

def test_no_verify():
    assert (not verify(SAMPLE_BAD_TARGET, b.Target()))


def test_strip():
    output = strip(SAMPLE_TARGET, b.Target())
    for key, value in output.items():
        assert ( output[key] == FILTERED_OUTPUT[key] )

def test_bad_strip():
    with raises(ValueError):
        output = strip(SAMPLE_BAD_TARGET, b.Target())


if __name__ == "__main__":
    from sys import stderr, argv
    stderr.write("run test with 'pytest %s'" %(argv[0]))
    test_verify()
    test_no_verify()
    test_strip()
