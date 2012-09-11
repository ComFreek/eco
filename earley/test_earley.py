from gparser import Parser, Rule, Nonterminal, Terminal
from recognizer import Recognizer, State, Production

grammar1 = """
E ::= E \"+\" E
    | \"a\"
"""

class TestRecognizer(object):

    def setup_method(self, method):
        p = Parser(grammar1)
        p.parse()
        self.p = p.rules

    def test_production(self):
        p1 = Production(Nonterminal("E"), [Terminal("a")])
        p2 = Production(Nonterminal("E"), [Terminal("a")])
        assert p1 == p2

    def test_state(self):
        p = Production(Nonterminal("E"), [Terminal("a")])
        s = State(p, 0, 0, Recognizer.terminal)
        assert s.equals_str("E ::= .a | 0")

    def test_state2(self):
        p = Production(Nonterminal("E"), [Nonterminal("E"), Terminal("\"+\""), Nonterminal("E")])
        s = State(p, 1, 0, Recognizer.terminal)
        assert s.equals_str("E ::= E.\"+\"E | 0")

    def test_state_nextsymbol(self):
        p = Production(Nonterminal("E"), [Nonterminal("E"), Terminal("\"+\""), Nonterminal("E")])
        s = State(p, 1, 0, Recognizer.terminal)
        assert s.next_symbol() == Terminal("\"+\"")

    def test_recognizer_init(self):
        r = Recognizer(self.p, "a+a")
        s0 = r.statesets[0]
        assert s0.elements[0].equals_str("None ::= .E | 0")

    def test_recognizer_predict(self):
        r = Recognizer(self.p, "a+a")
        r.predict()
        s0 = r.statesets[0]
        assert s0.elements[0].equals_str("None ::= .E | 0")
        assert s0.elements[1].equals_str("E ::= .E\"+\"E | 0")
        assert s0.elements[2].equals_str("E ::= .\"a\" | 0")
