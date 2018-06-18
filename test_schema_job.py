from .brain.checks import verify, strip
from .brain import brain_pb2 as b
from .test_schema_target import Good_TARGET
from .test_schema_command import GoodCommand

Goodjob = {"id": "string",
           "JobTarget": Good_TARGET,
           "Status": "string",
           "StartTime": 0,
           "JobCommand": GoodCommand,}

Badjob = {"id": "string",
           "JobTarget": None,
           "Status": "string",
           "StartTime": 0,
           "JobCommand": GoodCommand,
           "testcase": None}

Badjob2 = {"id": 123456,
           "JobTarget": None,
           "Status": "string",
           "StartTime": 0,
           "JobCommand": GoodCommand,
           "testcase": None}

Badjob3 = {"id": "string",
           "JobTarget": True,
           "Status": "string",
           "StartTime": 0,
           "JobCommand": GoodCommand,
           "testcase": None}

Badjob4 = {"id": "string",
           "JobTarget": None,
           "Status": True,
           "StartTime": 0,
           "JobCommand": GoodCommand,
           "testcase": None}

Badjob5 = {"id": "string",
           "JobTarget": None,
           "Status": "string",
           "StartTime": True,
           "JobCommand": GoodCommand,
           "testcase": None}

Badjob6 = {"id": "string",
           "JobTarget": None,
           "Status": "string",
           "StartTime": 0,
           "JobCommand": True,
           "testcase": None}

Badjob7 = {"id": "string",
           "JobTarget": None,
           "Status": "string",
           "StartTime": 0,
           "JobCommand": GoodCommand,
           "testcase": True}

def test_good_job():
    assert verify(Goodjob, b.Job())

def test_bad_job():
    assert not verify(Badjob, b.Job())

def test_bad_job2():
    assert not verify(Badjob2, b.Job())

def test_bad_job3():
    assert not verify(Badjob3, b.Job())

def test_bad_job4():
    assert not verify(Badjob4, b.Job())

def test_bad_job5():
    assert not verify(Badjob5, b.Job())

def test_bad_job6():
    assert not verify(Badjob6, b.Job())

def test_bad_job7():
    assert not verify(Badjob7, b.Job())
