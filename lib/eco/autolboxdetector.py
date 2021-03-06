from grammars.grammars import lang_dict
from incparser.astree import BOS, EOS, TextNode
from grammar_parser.gparser import MagicTerminal, Terminal, Nonterminal, IndentationTerminal
from incparser.syntaxtable import Shift, Reduce, Goto, Accept
import config

ws_tokens = ["<ws>", "<return>", "<slcomment>", "<mlcomment>"]
PARSE_AFTER_TOKENS = 10

def get_lookup(la):
    """Get the lookup symbol of a node. If no such lookup symbol exists use
    the nodes symbol instead."""
    if la.lookup != "":
        lookup_symbol = Terminal(la.lookup)
    else:
        lookup_symbol = la.symbol
    if isinstance(lookup_symbol, IndentationTerminal):
        lookup_symbol = Terminal(lookup_symbol.name)
    return lookup_symbol

class NewAutoLboxDetector(object):
    """Automatic languagebox detector that runs during parsing when an error
    occurs. Similar to error recovery it uses the current parse stack to
    determine a location where a language box can be inserted and then tries to
    wrap the error into that box."""
    def __init__(self, origparser, origlexer):
        self.op = origparser
        self.ol = origlexer
        self.olang = None
        self.langs = {}
        self.mode_limit_tokens_new = False

    def preload(self, langname):
        if langname in self.langs:
            return

        main = lang_dict[langname]
        self.olang = langname
        self.mode_limit_tokens_new = main.auto_limit_new

        # preload nested languages
        for sub in main.included_langs:
            self.langs[sub] = get_recognizer(sub, langname)

    def pop_lookahead(self, node):
        while not node.right_sibling():
            node = node.parent
        return node.right_sibling()

    def find_terminal(self, node, version=None):
        startnode = node
        while type(node) is not BOS:
            if node.get_attr("children", version):
                node = node.get_attr("children", version)[-1]
            elif type(node.symbol) is Terminal:
                break
            else:
                if node.new:
                    return
                while not node.get_attr("left", version):
                    node = node.get_attr("parent", version)
                    if node is startnode:
                        return None
                node = node.get_attr("left", version)
        return node.next_term

    def detect_lbox(self, errornode):
        # Try history based heuristic first; if it fails to find an automatic
        # language box, try the stack based one; if that fails, try the
        # line-based heuristic.
        valid = []
        maxd = 0
        if config.AUTOLBOX_HEURISTIC_HIST:
            valid.extend(self.heuristic_history(errornode))
        if config.AUTOLBOX_HEURISTIC_STACK:
            valid.extend(self.heuristic_stack(errornode))
        if config.AUTOLBOX_HEURISTIC_LINE:
            valid.extend(self.heuristic_line(errornode))

        filtered = set()
        valid.sort(key=lambda x: x[0].position + x[3], reverse=True)
        pv = self.op.prev_version
        maxdist = 0
        for start, end, lang, dist, split, lbox, error in valid:
            if maxdist == 0:
                # find the valid candidate with the furthest reach
                if self.parse_after_lbox_h2(lbox, end, start, pv, error, split):
                    maxdist = self.abs_parse_distance + dist
                    filtered.add((start, end, lang, split))
            else:
                # check if remaining candidates can parse as far as the
                # candidate with the furthest reach
                newdist = maxdist - start.position - dist
                if self.parse_after_lbox_h2(lbox, end, start, pv, error, split, maxdist=newdist):
                    dist = self.abs_parse_distance + dist
                    if dist >= maxdist:
                        filtered.add((start, end, lang, split))

        valid = list(filtered)

        if errornode.autobox is False:
            # XXX Currently, we don't suggest any language boxes for an error
            # if the user had to revert an automatically inserted box. However,
            # we might want to consider showing suggestions if the suggested
            # box differs from the one the user reverted.
            return False # don't use this node for autoboxes anymore
        if len(valid) > 0:
            errornode.autobox = valid
            return True
        else:
            errornode.autobox = None
            return False

    def heuristic_line(self, errornode):
        valid = []
        for sub in self.langs:
            lbox = MagicTerminal("<{}>".format(sub))
            node = errornode.prev_term
            while True:
                element = self.op.syntaxtable.lookup(node.state, lbox)
                if type(element) in [Reduce, Shift]:
                    r = self.langs[sub]
                    r.mode_limit_tokens_new = self.mode_limit_tokens_new
                    start = node.next_term
                    result = r.parse(start)
                    if r.possible_ends:
                        for e, enddist, split in r.possible_ends:
                            if e.lookup == "<ws>" or e.lookup == "<return>":
                                continue
                            valid.append((start, e, sub, enddist, split, lbox, errornode))
                if node.lookup == "<return>" or type(node) is BOS or node.ismultinode():
                    break
                node = node.prev_term
        return valid

    def heuristic_history(self, errornode):
        valid = []
        ws = ["<ws>", "<return>"]
        searched = set()
        pv = self.op.prev_version
        for sub in self.langs:
            lbox = MagicTerminal("<{}>".format(sub))
            parent = errornode.parent
            while parent is not None:
                if parent.get_attr("parent", pv) is None: # Root
                    # If we've reached the root, try inserting the box after
                    # BOS, i.e. the beginning of the file
                    left = parent.get_attr("children", pv)[0] # bos
                else:
                    left = parent.get_attr("left", pv)
                while left and type(left.symbol) is Nonterminal and len(left.get_attr("children", pv)) == 0:
                    # If left is an empty nonterminal, keep going left until we
                    # find a non-empty nonterminal or a terminal
                    left = left.get_attr("left", pv)
                if left:
                    state = left.state
                    element = self.op.syntaxtable.lookup(state, lbox)
                    if type(element) in [Reduce, Shift]:
                        term = self.find_terminal(left, pv)
                        if term and term not in searched:
                            tleft = term.prev_term # left's most right terminal
                            if type(term) is EOS:
                                parent = parent.get_attr("parent", pv)
                                continue
                            while term and term.lookup in ws:
                                # skip whitespace
                                term = term.next_term
                            element = self.op.syntaxtable.lookup(tleft.state, lbox)
                            if type(element) not in [Reduce, Shift]:
                                # Usually if `lbox` can be shifted after `left`
                                # this means it should also be shiftable after
                                # `left`'s most right terminal. However, that
                                # terminal might have changed and caused an error
                                # which was isolated, which means that `lbox` isn't
                                # valid after all.
                                parent = parent.get_attr("parent", pv)
                                continue
                            r = self.langs[sub]
                            r.mode_limit_tokens_new = self.mode_limit_tokens_new
                            result = r.parse(term)
                            if r.possible_ends:
                                for e, enddist, split in r.possible_ends:
                                    if e.lookup in ws:
                                        continue
                                    valid.append((term, e, sub, enddist, split, lbox, errornode))
                                    searched.add(term)
                parent = parent.get_attr("parent", pv)
        return valid

    def parse_after_lbox_h2(self, lbox, end, parent, version, errornode, split=None, maxdist=0):
        # XXX Can reuse preparsed ir as long as parent is the same
        root = parent.get_root(version)
        p, l = lang_dict[root.name].load()
        ir = IncrementalRecognizer(p.syntaxtable, l.lexer, root.name, None)
        ir.errornode = errornode
        if root is not parent:
            # if the parent is already the root we don't need to preparse
            # anything
            ir.preparse(root, parent, version)
        # try parsing lbox + one more non-ws terminal
        check = ir.parse_single(TextNode(lbox)) and ir.parse_after(end.next_term, split, maxtoks=PARSE_AFTER_TOKENS, maxdist=maxdist)
        self.abs_parse_distance = ir.abs_parse_distance
        return check and (ir.seen_error or self.contains_errornode(parent, end, errornode))

    def heuristic_stack(self, errornode):
        # Find position on stack where lbox would be valid
        valid = []
        for sub in self.langs:
            lbox = MagicTerminal("<{}>".format(sub))
            cut = len(self.op.stack) - 1
            while cut >= 0:
                top = self.op.stack[cut]
                if isinstance(top, EOS):
                    top = top.parent.children[0] # bos
                    state = 0
                else:
                    state = self.op.stack[cut].state
                # get all possible sublangs
                element = self.op.syntaxtable.lookup(state, lbox)
                if type(element) in [Reduce, Shift]:
                    term = self.find_terminal(top)
                    if type(term) is EOS:
                        cut = cut - 1
                        continue
                    if term:
                        n = term
                        # See if we can get a valid language box using the Recogniser
                        r = self.langs[sub]
                        r.mode_limit_tokens_new = self.mode_limit_tokens_new
                        result = r.parse(n)
                        if r.possible_ends:
                            # Filter results and test if remaining file can be
                            # parsed after shifting the language box
                            for e, enddist, split in r.possible_ends:
                                if e.lookup == "<ws>" or e.lookup == "<return>":
                                    continue
                                valid.append((n, e, sub, enddist, split, lbox, errornode))
                cut = cut - 1
        return valid

    def contains_errornode(self, start, end, errornode):
        while start is not end:
            if start is errornode:
                return True
            start = start.next_term
        if start is errornode:
            return True
        return False

    def parse_after_lbox_h1(self, lbox, end, cut, errornode=None, split=None, distance=1):
        self.abs_parse_distance = 0
        parsed_tokens = 0
        # copy stack
        stack = []
        for i in range(cut+1):
            stack.append(self.op.stack[i].state)
            self.abs_parse_distance += self.op.stack[i].textlength()
        after_end = end.next_term
        # do all reductions until there's a shift or accept (whitespace doesn't
        # count)
        lboxnode = TextNode(lbox)
        la = lboxnode
        if split:
            token = self.ol.lex(end.symbol.name[split:])
            splitla = TextNode(Terminal(token[0][1]))
            splitla.next_term = after_end
            la.next_term = splitla
        else:
            la.next_term = after_end
        while True:
            if la.deleted:
                la = la.next_term
                continue
            element = self.op.syntaxtable.lookup(stack[-1], self.op.get_lookup(la))
            if type(element) is Reduce:
                for i in range(element.amount()):
                    stack.pop()
                goto = self.op.syntaxtable.lookup(stack[-1], element.action.left)
                assert goto is not None
                stack.append(goto.action)
                continue
            if type(element) is Shift:
                if errornode and la is errornode:
                    return True
                # if whitespace continue
                if la.lookup in ws_tokens or la is lboxnode:
                    stack.append(element.action)
                    if la is not lboxnode:
                        self.abs_parse_distance += len(la.symbol.name)
                    la = la.next_term
                    continue
                if not errornode:
                    stack.append(element.action)
                    self.abs_parse_distance += len(la.symbol.name)
                    parsed_tokens += 1
                    if parsed_tokens == distance:
                        return True
                    la = la.next_term
                    continue
            if type(element) is Accept:
                return True
            if parsed_tokens > 0:
                return True
            return False

    def check_remove_lbox(self, lbox):
        r = IncrementalRecognizer(self.op.syntaxtable, self.ol.lexer, self.olang, None)
        stack = [s.state for s in self.op.stack]
        r.state = stack
        result = r.parse(lbox.symbol.ast.children[0].next_term, lbox.next_term, self.op.last_status)
        if result:
            lbox.tbd = "remove"

from inclexer.inclexer import StringWrapper
from treelexer.lexer import LexingError
from incparser.incparser import FinishSymbol

class Recognizer(object):
    """A parser that simulates parsing some input without actually creating a
    parse tree. Used to test if some input is valid in some language."""

    def __init__(self, syntaxtable, lexer, lang, outer):
        self.syntaxtable = syntaxtable
        self.lexer = lexer
        self.lang = lang
        self.outer = outer
        self.state = [0]
        self.reached_eos = False
        self.seen_error = False
        self.possible_ends = []
        self.last_read = None
        self.mode_limit_tokens_new = False
        self.abs_parse_distance = 0
        self.last_token_value = ""
        self.last_split = 0
        self.errornode = None

    def reset(self):
        self.state = [0]
        self.reached_eos = False
        self.seen_error = False
        self.possible_ends = []
        self.last_read = None
        self.abs_parse_distance = 0
        self.last_token_value = ""

    def parse(self, startnode, ppmode=False):
        # as we are reusing recogisers now, reset it
        if not ppmode:
            self.reset()

        self.tokeniter = self.lexer.get_token_iter(startnode).__next__
        token = self.next_token()
        minversion = startnode.version
        if not ppmode and not self.valid_start(token):
            return None
        while True:
            if ppmode and self.reached_eos:
                return True
            element = self.syntaxtable.lookup(self.state[-1], token)
            if isinstance(element, Shift):
                self.abs_parse_distance += len(self.last_token_value)
                self.state.append(element.action)
                if self.is_finished() and self.last_read:
                    if self.mode_limit_tokens_new is False or self.last_read.version >= minversion:
                        self.possible_ends.append((self.last_read, self.abs_parse_distance, self.last_split))
                    self.last_read = None
                token = self.next_token()
                continue
            elif isinstance(element, Reduce):
                i = 0
                while i < element.amount():
                   self.state.pop()
                   i += 1
                goto = self.syntaxtable.lookup(self.state[-1], element.action.left)
                assert isinstance(goto, Goto)
                self.state.append(goto.action)
                continue
            elif isinstance(element, Accept):
                return self.last_read
            else:
                return None

    def next_token(self):
        try:
            t = self.tokeniter()
            self.last_read = t[3][-1]
            self.last_token_value = t[0]
            self.last_split = t[4]
            return Terminal(t[1])
        except StopIteration:
            self.reached_eos = True
            return FinishSymbol() # No more tokens to read
        except LexingError:
           return FinishSymbol() # Couldn't continue lexing with given language

    def valid_start(self, token):
        if token.name in ["<ws>", "<return>"]:
            return False
        if not lang_dict[self.outer].auto_allows(self.lang, token.name):
            return False
        return True

    def is_finished(self):
        result = self.syntaxtable.lookup(self.state[-1], FinishSymbol())
        states = list(self.state)
        while isinstance(result, Reduce):
            i = 0
            for i in range(result.amount()):
                states.pop()
            goto = self.syntaxtable.lookup(states[-1], result.action.left)
            states.append(goto.action)
            result = self.syntaxtable.lookup(states[-1], FinishSymbol())
        if isinstance(result, Accept):
            return True
        return False

    def temp_parse(self, states, terminal):
        while True:
            element = self.syntaxtable.lookup(states[-1], terminal)
            if type(element) is Shift:
                states.append(element.action)
                return True
            elif type(element) is Reduce:
                i = 0
                while i < element.amount():
                   states.pop()
                   i += 1
                goto = self.syntaxtable.lookup(states[-1], element.action.left)
                assert isinstance(goto, Goto)
                states.append(goto.action)
                continue
            else:
                return False

    def parse_lex_single(self, node):
        self.tokeniter = self.lexer.get_token_iter(node).__next__
        token = self.next_token()
        while True:
            if not self.temp_parse(self.state, token):
                return False
            token = self.next_token()
            if self.last_read is not node or type(token) is FinishSymbol:
                return True

class RecognizerIndent(Recognizer):

    def __init__(self, syntaxtable, lexer, lang, outer):
        Recognizer.__init__(self, syntaxtable, lexer, lang, outer)
        self.todo = []
        self.indents = [0]
        self.last_ws = 0
        self.logical_line = False

    def parse(self, node):
        self.indents = [0]
        self.todo = []
        Recognizer.parse(self, node)

    def reset(self):
        self.todo = []
        self.indents = [0]
        self.last_ws = 0
        self.logical_line = False
        Recognizer.reset(self)

    def get_token_iter(self):
        try:
            return self.tokeniter()
        except StopIteration:
            return None
        except LexingError:
            return None

    def is_logical(self, tok):
        if tok == "<ws>":
            return False
        if tok == "<return>":
            return False
        return True

    def next_token(self):
        if self.todo:
           return self.todo.pop(0)

        tok1 = self.get_token_iter()
        if tok1 is None:
            self.todo.append(Terminal("NEWLINE"))
            while self.indents[-1] != 0:
                self.todo.append(Terminal("DEDENT"))
                self.indents.pop()
            self.todo.append(FinishSymbol())
            return self.todo.pop(0)

        if type(tok1[3][-1].symbol) is not MagicTerminal\
               and tok1[3][-1].symbol.name.endswith(tok1[0]):
            # only use fully parsed nodes as possible ends
            self.last_read = tok1[3][-1]
            self.last_token_value = tok1[0]
            self.last_split = tok1[4]

        if tok1[1] == "<return>":
            if self.logical_line: # last line was logical
                self.todo.append(Terminal("NEWLINE"))
                self.logical_line = False
                self.last_ws = 0
            return Terminal(tok1[1]) # parse <return> token first

        if tok1[1] == "<ws>":
            self.last_ws = len(tok1[0])
            return Terminal(tok1[1])

        if self.is_logical(tok1[1]):
            if self.logical_line is False: # first logical token in this line
                self.logical_line = True
                if self.last_ws > self.indents[-1]:
                    self.todo.append(Terminal("INDENT"))
                    self.indents.append(self.last_ws)
                elif self.last_ws == self.indents[-1]:
                    pass
                else:
                    while self.last_ws < self.indents[-1]:
                        self.todo.append(Terminal("DEDENT"))
                        self.indents.pop()
                self.todo.append(Terminal(tok1[1]))
                return self.todo.pop(0)
        return Terminal(tok1[1])

    def is_finished(self):
        states = list(self.state)
        if self.temp_parse(states, Terminal("NEWLINE")):
            element = self.syntaxtable.lookup(states[-1], FinishSymbol())
            if element:
                return True
            elif self.temp_parse(states, Terminal("DEDENT")):
                return True
        return False

class IncrementalRecognizer(Recognizer):

    def preparse(self, outer_root, stop, version=None):
        """Puts the recogniser into the state just before `stop`."""
        path_to_stop = set()
        parent = stop.get_attr("parent", version)
        while parent is not None:
            path_to_stop.add(parent)
            parent = parent.get_attr("parent", version)

        # setup parser to the state just before lbox
        node = outer_root.get_attr("children", version)[1]
        while True:
            if node.get_attr("deleted", version):
                node = node.get_attr("right", version)
                continue
            if node is stop:
                # Reached stop node
                return True
            if node not in path_to_stop:
                # Skip/Shift nodes that are not parents of the language box
                lookup = get_lookup(node)
                element = self.syntaxtable.lookup(self.state[-1], lookup)
                if type(element) is Goto:
                    self.abs_parse_distance += node.textlength(version)
                    self.state.append(element.action)
                elif type(element) is Shift:
                    self.abs_parse_distance += node.textlength(version)
                    self.state.append(element.action)
                elif type(element) is Reduce:
                    i = 0
                    while i < element.amount():
                       self.state.pop()
                       i += 1
                    goto = self.syntaxtable.lookup(self.state[-1], element.action.left)
                    assert isinstance(goto, Goto)
                    self.state.append(goto.action)
                    continue
                else:
                    return False
                node  = node.get_attr("right", version)
            else:
                if node.get_attr("children", version):
                    node = node.get_attr("children", version)[0]
                else:
                    node = node.get_attr("right", version)

    def orig_parse(self, node):
        return Recognizer.parse(self, node, ppmode=True)

    def parse(self, node, follow, status):
        """Parse normally starting at `node`."""

        # parsing a language box is successful if the last token in the box has
        # been processed without errors and we can parse at least one terminal
        # following the lbox contents. Unless the languagebox has errors
        # in which we prioritise the outer language even if the following nodes
        # (i.e. the context) can't be parsed

        # try parsing lbox content in outer language
        Recognizer.parse(self, node, ppmode=True)
        if self.reached_eos:
            if status is False:
                return True
            if self.parse_after(follow):
                return True
        return False

    def parse_lex_single(self, node):
        return Recognizer.parse_lex_single(self, node)

    def parse_until(self, start, end):
        node = start.next_term
        while True:
            lookup = get_lookup(node)
            if not self.temp_parse(self.state, lookup):
                return False
            if node is end:
                return True
            node = node.next_term

    def parse_after(self, la, split=None, maxtoks=1, maxdist=0):
        """Checks if la can be parsed in the current state. If la is whitespace,
        continue until we can parse the next non-whitespace token."""
        parsed_tokens = 0
        parsed_distance = 0
        if split:
            token = self.lexer.lex(la.prev_term.symbol.name[split:])
            tmpla = la
            la = TextNode(Terminal(token[0][1]))
            la.next_term = tmpla
        while True:
            lookup = get_lookup(la)
            element = self.syntaxtable.lookup(self.state[-1], lookup)

            # If we see the errornode here and the parse table action is
            # either Shift or Accept, then the inserted language box has fixed
            # the error without wrapping it inside the box
            if la is self.errornode and type(element) in [Shift, Accept]:
                self.seen_error = True

            if type(element) is Reduce:
                for i in range(element.amount()):
                    self.state.pop()
                goto = self.syntaxtable.lookup(self.state[-1], element.action.left)
                assert goto is not None
                self.state.append(goto.action)
                continue

            if type(element) is Shift:
                # if whitespace continue
                if la.lookup in ws_tokens:
                    self.state.append(element.action)
                    self.abs_parse_distance += len(la.symbol.name)
                    parsed_distance += len(la.symbol.name)
                    la = la.next_term
                    continue
                self.state.append(element.action)
                self.abs_parse_distance += len(la.symbol.name)
                parsed_tokens += 1
                parsed_distance += len(la.symbol.name)
                if parsed_tokens >= maxtoks and parsed_distance >= maxdist:
                    return True
                la = la.next_term
                continue

            if type(element) is Accept:
                return True
            if parsed_tokens > 0:
                return True
            return False

    def parse_single(self, la):
        while True:
            lookup = get_lookup(la)
            element = self.syntaxtable.lookup(self.state[-1], lookup)

            if type(element) is Reduce:
                for i in range(element.amount()):
                    self.state.pop()
                goto = self.syntaxtable.lookup(self.state[-1], element.action.left)
                assert goto is not None
                self.state.append(goto.action)
                continue

            if type(element) is Shift:
                self.state.append(element.action)
                return True
                
            if type(element) is Accept:
                return True
            return False

def get_recognizer(lang, outer):
        main = lang_dict[lang]
        parser, lexer = main.load()
        if lexer.indentation_based:
            return RecognizerIndent(parser.syntaxtable, lexer.lexer, lang, outer)
        else:
            return Recognizer(parser.syntaxtable, lexer.lexer, lang, outer)
