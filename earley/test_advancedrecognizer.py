from gparser import Parser, Nonterminal, Terminal
from recognizer_advanced import AdvancedRecognizer
from recognizer import StateSet, State, Production

E = Nonterminal("E")
plus = Terminal("\"+\"")
a = Terminal("\"a\"")

grammar = """
    E ::= E "+" E
        | "a"
"""

inputstring = "a+a"

p = Parser(grammar)
p.parse()

S0 = [
    State(Production(None, [E]), 0, 0),
    State(Production(E, [E, plus, E]), 0, 0),
    State(Production(E, [a]), 0, 0),
]

S1 = [
    State(Production(E, [a]), 1, 0),
    State(Production(None, [E]), 1, 0),
    State(Production(E, [E, plus, E]), 1, 0),
]

S2 = [
    State(Production(E, [E, plus, E]), 2, 0),
    State(Production(E, [E, plus, E]), 0, 2),
    State(Production(E, [a]), 0, 2),
]

S3 = [
    State(Production(E, [a]), 1, 2),
    State(Production(E, [E, plus, E]), 3, 0),
    State(Production(E, [E, plus, E]), 1, 2),
    State(Production(None, [E]), 1, 0),
    State(Production(E, [E, plus, E]), 1, 0),
]

r = AdvancedRecognizer(p.start_symbol, p.rules, inputstring)

def test_recognizer_manual_0():
    r.read_current_input_symbol()
    for i in range(len(S0)):
        assert S0[i] == r.statesets[0].elements[i]

    assert len(r.statesets[1].elements) == 1
    assert S1[0] == r.statesets[1].elements[0]

def test_recognizer_manual_1():
    r.pos += 1
    r.read_current_input_symbol()
    for i in range(len(S1)):
        assert S1[i] == r.statesets[1].elements[i]

    assert len(r.statesets[2].elements) == 1
    assert S2[0] == r.statesets[2].elements[0]

def test_recognizer_manual_2():
    r.pos += 1
    r.read_current_input_symbol()
    for i in range(len(S2)):
        assert S2[i] == r.statesets[2].elements[i]

    assert len(r.statesets[3].elements) == 1
    assert S3[0] == r.statesets[3].elements[0]

def test_recognizer_manual_3():
    r.pos += 1
    r.read_current_input_symbol()
    for i in range(len(S3)):
        assert S3[i] == r.statesets[3].elements[i]

def test_auto():
    r = AdvancedRecognizer(p.start_symbol, p.rules, inputstring)
    assert r.isvalid()
