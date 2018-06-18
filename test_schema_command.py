from .brain.checks import verify, strip
from .brain import brain_pb2 as b

GoodCommand = {"CommandName": "anystring", 
              "Tooltip": "otherstring",
              "Output": True,
              "Inputs": [{"Name" : "string", 
                          "Type": "String",
                          "Tooltip": "String",
                          "Value": "String"}], 
              "OptionalInputs": [{"Name" : "string",
                                  "Type": "String",
                                  "Tooltip": "String",
                                  "Value": "String"}]}

BadCommand = {"CommandName": 13, 
              "Tooltip": "otherstring",
              "Output": True,
              "Inputs": [{"Name" : "string", 
                          "Type": "String",
                          "Tooltip": "String",
                          "Value": "String"}], 
              "OptionalInputs": [{"Name" : "string",
                                  "Type": "String",
                                  "Tooltip": "String",
                                  "Value": "String"}]}

BadCommand2 = {"CommandName": "string", 
              "Tooltip": 465,
              "Output": True,
              "Inputs": [{"Name" : "string", 
                          "Type": "String",
                          "Tooltip": "String",
                          "Value": "String"}], 
              "OptionalInputs": [{"Name" : "string",
                                  "Type": "String",
                                  "Tooltip": "String",
                                  "Value": "String"}]}

BadCommand3 = {"CommandName": "string", 
              "Tooltip": "stringy thing",
              "Output": "heyimnotsupposedtobeastring",
              "Inputs": [{"Name" : "string", 
                          "Type": "String",
                          "Tooltip": "String",
                          "Value": "String"}], 
              "OptionalInputs": [{"Name" : "string",
                                  "Type": "String",
                                  "Tooltip": "String",
                                  "Value": "String"}]}

BadCommand4 = {"CommandName": "string", 
              "Tooltip": "stringy thing",
              "Output": True,
              "Inputs": [{"Name" : 21, 
                          "Type": "String",
                          "Tooltip": "String",
                          "Value": "String"}], 
              "OptionalInputs": [{"Name" : "string",
                                  "Type": "String",
                                  "Tooltip": "String",
                                  "Value": "String"}]}

BadCommand5 = {"CommandName": "string", 
              "Tooltip": "stringy thing",
              "Output": True,
              "Inputs": [{"Name" : "string", 
                          "Type": 135,
                          "Tooltip": "String",
                          "Value": "String"}], 
              "OptionalInputs": [{"Name" : "string",
                                  "Type": "String",
                                  "Tooltip": "String",
                                  "Value": "String"}]}

BadCommand6 = {"CommandName": "string", 
              "Tooltip": "stringy thing",
              "Output": True,
              "Inputs": [{"Name" : "string", 
                          "Type": "String",
                          "Tooltip": 24,
                          "Value": "String"}], 
              "OptionalInputs": [{"Name" : "string",
                                  "Type": "String",
                                  "Tooltip": "String",
                                  "Value": "String"}]}

BadCommand7 = {"CommandName": "string", 
              "Tooltip": "stringy thing",
              "Output": True,
              "Inputs": [{"Name" : "string", 
                          "Type": "String",
                          "Tooltip": "String",
                          "Value": 64}],
              "OptionalInputs": [{"Name" : "string",
                                  "Type": "String",
                                  "Tooltip": "String",
                                  "Value": "String"}]}

BadCommand8 = {"CommandName": "string", 
              "Tooltip": "stringy thing",
              "Output": True,
              "Inputs": [{"Name" : "string", 
                          "Type": "String",
                          "Tooltip": "String",
                          "Value": "String"}], 
              "OptionalInputs": [{"Name" : 456,
                                  "Type": "String",
                                  "Tooltip": "String",
                                  "Value": "String"}]}

BadCommand9 = {"CommandName": "string", 
              "Tooltip": "stringy thing",
              "Output": True,
              "Inputs": [{"Name" : "string", 
                          "Type": "String",
                          "Tooltip": "String",
                          "Value": "String"}], 
              "OptionalInputs": [{"Name" : "string",
                                  "Type": 123,
                                  "Tooltip": "String",
                                  "Value": "String"}]}

BadCommand10 = {"CommandName": "string", 
              "Tooltip": "stringy thing",
              "Output": True,
              "Inputs": [{"Name" : "string", 
                          "Type": "String",
                          "Tooltip": "String",
                          "Value": "String"}], 
              "OptionalInputs": [{"Name" : "string",
                                  "Type": "String",
                                  "Tooltip": 126,
                                  "Value": "String"}]}

BadCommand11 = {"CommandName": "string", 
              "Tooltip": "stringy thing",
              "Output": True,
              "Inputs": [{"Name" : "string", 
                          "Type": "String",
                          "Tooltip": "String",
                          "Value": "String"}], 
              "OptionalInputs": [{"Name" : "string",
                                  "Type": "String",
                                  "Tooltip": "String",
                                  "Value": 13}]}

def test_good_command():
    assert verify(GoodCommand, b.Command())

def test_bad_command():
    assert not verify(BadCommand, b.Command())

def test_bad_command2():
    assert not verify(BadCommand2, b.Command())

def test_bad_command3():
    assert not verify(BadCommand3, b.Command())

def test_bad_command4():
    assert not verify(BadCommand4, b.Command())

def test_bad_command5():
    assert not verify(BadCommand5, b.Command())

def test_bad_command6():
    assert not verify(BadCommand6, b.Command())

def test_bad_command7():
    assert not verify(BadCommand7, b.Command())

def test_bad_command8():
    assert not verify(BadCommand8, b.Command())

def test_bad_command9():
    assert not verify(BadCommand9, b.Command())

def test_bad_command10():
    assert not verify(BadCommand10, b.Command())

def test_bad_command11():
    assert not verify(BadCommand11, b.Command())
