# Copyright (c) 2013--2014 King's College London
# Created by the Software Development Team <http://soft-dev.org/>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

from grammar_parser.plexer import PriorityLexer
from grammar_parser.gparser import MagicTerminal, Terminal, IndentationTerminal
from incparser.astree import BOS, EOS, TextNode, ImageNode, MultiTextNode
try:
    import __pypy__
except ImportError:
    from PyQt5.QtGui import QImage
import re, os

class IncrementalLexer(object):
    """Deprecated incremental lexer."""
    # XXX needs to be replaced by a lexing automaton to avoid unnecessary
    # relexing of unchanged nodes

    def __init__(self, rules, language=""):
        self.indentation_based = False
        self.language = language
        if rules.startswith("%"):
            config_line = rules.splitlines()[0]     # get first line
            self.parse_config(config_line[1:])      # remove %
            rules = "\n".join(rules.splitlines()[1:]) # remove config line
        pl = PriorityLexer(rules)
        self.regexlist = pl.rules
        self.compiled_regexes = {}
        for regex in self.regexlist:
            self.compiled_regexes[regex] = re.compile(regex)

    def is_indentation_based(self):
        return self.indentation_based

    def parse_config(self, config):
        settings = config.split(",")
        for s in settings:
            name, value = s.split("=")
            if name == "indentation" and value == "true":
                self.indentation_based = True

    def lex(self, text):
        matches = []
        remaining = text
        any_match_found = False
        while remaining != "":
            longest_match = ("", "", 999999)
            for regex in self.regexlist:
                m = self.compiled_regexes[regex].match(remaining)
                if m:
                    result = m.group(0)
                    if len(result) > len(longest_match[0]):
                        new_priority = self.regexlist[regex][0]
                        regex_name = self.regexlist[regex][1]
                        longest_match = (result, regex_name, new_priority)
                    if len(result) == len(longest_match[0]):
                        new_priority = self.regexlist[regex][0]
                        old_priority = longest_match[2]
                        if new_priority < old_priority: # use token with higher priority (smaller numbers have higher priority)
                            regex_name = self.regexlist[regex][1]
                            longest_match = (result, regex_name, new_priority)
            if longest_match[0] != "":
                any_match_found = True
                remaining = remaining[len(longest_match[0]):]
                matches.append(longest_match)
            else:
                matches.append((remaining, ""))
                break
        if any_match_found:
            stripped_priorities = []
            for m in matches:
                stripped_priorities.append((m[0], m[1]))
            return stripped_priorities
        else:
            return [(text, '', 0)]

    def relex(self, node):
        if isinstance(node, BOS):
            return

        start = node
        while True:
            if isinstance(start.symbol, IndentationTerminal):
                start = start.next_term
                break
            if isinstance(start, BOS):
                start = start.next_term
                break
            if start.lookup == "<return>":
                start = start.next_term
                break
            if isinstance(start.symbol, MagicTerminal):
                start = start.next_term
                break
            start = start.prev_term

        # find end node
        end = node
        while True:
            if isinstance(end.symbol, IndentationTerminal):
                end = end.prev_term
                break
            if isinstance(end, EOS):
                end = end.prev_term
                break
            if isinstance(end.symbol, MagicTerminal):
                end = end.prev_term
                break
            if end.lookup == "<return>":
                end = end.prev_term
                break
            end = end.next_term

        token = start
        relex_string = []
        if start is end:
            relex_string = [start.symbol.name]
        else:
            while token is not end.next_term:
                if isinstance(token.symbol, MagicTerminal): # found a language box
                    # start another relexing process after the box
                    next_token = token.next_term
                    self.relex(next_token)
                    break
                if isinstance(token, EOS): # reached end of language box
                    break
                relex_string.append(token.symbol.name)
                token = token.next_term

        success = self.lex("".join(relex_string))

        old_node = start
        old_x = 0
        new_x = 0
        after_startnode = False
        debug_old = []
        debug_new = []
        for match in success:
            if after_startnode:
                if old_node.symbol.name == match[0] and old_node.lookup == match[1]:
                    # XXX optimisation only
                    # from here everything is going to be relexed to the same
                    # XXX check construction location
                    break

            # 1) len(relexed) == len(old) => update old with relexed
            # 2) len(relexed) >  len(old) => update old with relexed and delete following previous until counts <=
            # 3) len(relexed) <  len(old) => insert token

            if new_x < old_x: # insert
                if self.language == "Chemicals":
                    filename = "chemicals/" + node.symbol.name + ".png"
                    if os.path.isfile(filename):
                        additional_node = ImageNode(node, 0)
                        additional_node.image = QImage(filename)
                        old_node.image_src = filename
                    else:
                        additional_node.image = None
                        old_node.image_src = None
                else:
                    additional_node = TextNode(Terminal(match[0]), -1, [], -1)
                additional_node.lookup = match[1]
                old_node.prev_term.parent.insert_after_node(old_node.prev_term, additional_node)
                old_x += 0
                new_x  += len(match[0])
                debug_old.append("")
                debug_new.append(match[0])
            else: #overwrite
                old_x += len(old_node.symbol.name)
                new_x  += len(match[0])
                debug_old.append(old_node.symbol.name)
                debug_new.append(match[0])
                old_node.symbol.name = match[0]
                old_node.lookup = match[1]

                if self.language == "Chemicals":
                    filename = "chemicals/" + old_node.symbol.name + ".png"
                    if os.path.isfile(filename):
                        old_node.image = QImage(filename)
                        old_node.image_src = filename
                    else:
                        old_node.image = None
                        old_node.image_src = None

                old_node = old_node.next_term

            # relexed was bigger than old_node => delete as many nodes that fit into len(relexed)
            while old_x < new_x:
                if old_x + len(old_node.symbol.name) <= new_x:
                    old_x += len(old_node.symbol.name)
                    delete_node = old_node
                    old_node = delete_node.next_term
                    delete_node.parent.remove_child(delete_node)
                else:
                    break

        if old_x != new_x: # sanity check
            raise AssertionError("old_x(%s) != new_x(%s) %s => %s" % (old_x, new_x, debug_old, debug_new))

        return

    def relex_from_node(self, startnode):
        # XXX when typing to not create new node but insert char into old node
        #     (saves a few insertions and is easier to lex)

        # if node itself is a newline it won't be relexed, so do it manually
        if startnode.symbol.name == "\r":
            result = self.lex(startnode.symbol.name)
            startnode.lookup = result[0][1]

        if isinstance(startnode.symbol, IndentationTerminal):
            startnode = startnode.next_term
        else:
            startnode = startnode.prev_term

        if isinstance(startnode, BOS) or isinstance(startnode.symbol, MagicTerminal) or isinstance(startnode.symbol, IndentationTerminal):
            startnode = startnode.next_term

        if isinstance(startnode, EOS):
            # empty line
            return

        # find end node
        end_node = startnode.next_term
        while True:
            if isinstance(end_node.symbol, IndentationTerminal):
                break
            if isinstance(end_node, EOS):
                break
            if isinstance(end_node.symbol, MagicTerminal):
                break
            if end_node.symbol.name == "\r":
                break
            end_node = end_node.next_term

        token = startnode
        relex_string = []
        while token is not end_node:
            if isinstance(token.symbol, MagicTerminal): # found a language box
                # start another relexing process after the box
                next_token = token.next_term
                self.relex(next_token)
                break
            if isinstance(token, EOS): # reached end of language box
                break
            relex_string.append(token.symbol.name)
            token = token.next_term

        success = self.lex("".join(relex_string))

        old_node = startnode
        old_x = 0
        new_x = 0
        after_startnode = False
        debug_old = []
        debug_new = []
        for match in success:
            if after_startnode:
                if old_node.symbol.name == match[0] and old_node.lookup == match[1]:
                    # XXX optimisation only
                    # from here everything is going to be relexed to the same
                    # XXX check construction location
                    break

            # 1) len(relexed) == len(old) => update old with relexed
            # 2) len(relexed) >  len(old) => update old with relexed and delete following previous until counts <=
            # 3) len(relexed) <  len(old) => insert token

            if new_x < old_x: # insert
                if self.language == "Chemicals":
                    filename = "chemicals/" + node.symbol.name + ".png"
                    if os.path.isfile(filename):
                        additional_node = ImageNode(node, 0)
                        additional_node.image = QImage(filename)
                        old_node.image_src = filename
                    else:
                        additional_node.image = None
                        old_node.image_src = None
                else:
                    additional_node = TextNode(Terminal(match[0]), -1, [], -1)
                additional_node.lookup = match[1]
                old_node.prev_term.parent.insert_after_node(old_node.prev_term, additional_node)
                old_x += 0
                new_x  += len(match[0])
                debug_old.append("")
                debug_new.append(match[0])
            else: #overwrite
                old_x += len(old_node.symbol.name)
                new_x  += len(match[0])
                debug_old.append(old_node.symbol.name)
                debug_new.append(match[0])
                old_node.symbol.name = match[0]
                old_node.lookup = match[1]

                if self.language == "Chemicals":
                    filename = "chemicals/" + old_node.symbol.name + ".png"
                    if os.path.isfile(filename):
                        old_node.image = QImage(filename)
                        old_node.image_src = filename
                    else:
                        old_node.image = None
                        old_node.image_src = None

                old_node = old_node.next_term

            # relexed was bigger than old_node => delete as many nodes that fit into len(relexed)
            while old_x < new_x:
                if old_x + len(old_node.symbol.name) <= new_x:
                    old_x += len(old_node.symbol.name)
                    delete_node = old_node
                    old_node = delete_node.next_term
                    delete_node.parent.remove_child(delete_node)
                else:
                    break

        if old_x != new_x: # sanity check
            raise AssertionError("old_x(%s) != new_x(%s) %s => %s" % (old_x, new_x, debug_old, debug_new))

        return

    def relex_import(self, startnode, version=0):
        success = self.lex(startnode.symbol.name)
        bos = startnode.prev_term # bos
        startnode.parent.remove_child(startnode)
        parent = bos.parent
        eos = parent.children.pop()
        last_node = bos
        for match in success:
            node = TextNode(Terminal(match[0]))
            node.version = version
            node.lookup = match[1]
            parent.children.append(node)
            last_node.next_term = node
            last_node.right = node
            node.left = last_node
            node.prev_term = last_node
            node.parent = parent
            last_node = node
        parent.children.append(eos)
        last_node.right = eos # link to eos
        last_node.next_term = eos
        eos.left = last_node
        eos.prev_term = last_node

from treelexer.lexer import Lexer, LexingError

class IncrementalLexerCF(object):
    """
    Incrementally relexes nodes within the parse tree that have been changed.

    When a node changes we need to relex that node and all nodes that are
    dependent on it. This includes nodes before and after the altered node.
    Previous nodes are found by observing their lookaheads. If it reaches the
    changed node they are dependent on it and need to be relexed as well.

    Relexing starts at the earliest node with lookahead into the changed node,
    and continues until the changed node has been passed and relexing doesn't lead
    to any more changes.

    Afterwards the new nodes are merged back into the parse tree, replacing all
    previously relexed nodes.
    """
    def __init__(self, rules=None, language=""):
        self.indentation_based = False
        self.relexed = set()
        if rules:
            if rules.startswith("%"):
                config_line = rules.splitlines()[0]     # get first line
                self.parse_config(config_line[1:])      # remove %
                rules = "\n".join(rules.splitlines()[1:]) # remove config line
            self.createDFA(rules)

    def parse_config(self, config):
        settings = config.split(",")
        for s in settings:
            name, value = s.split("=")
            if name == "indentation" and value == "true":
                self.indentation_based = True

    def from_name_and_regex(self, names, regexs):
        self.lexer = Lexer(list(zip(names, regexs)))

    def createDFA(self, rules):
        # lex lexing rules
        pl = PriorityLexer(rules)
        rules = sorted(list(pl.rules.items()), key=lambda node: node[1][0]) # sort by priority

        # create lexer automaton from rules
        regexs = []
        names = []
        for regex, _ in rules:
            name = pl.rules[regex][1]
            regexs.append(regex)
            names.append(name)
        self.lexer = Lexer(list(zip(names, regexs)))

    def is_indentation_based(self):
        return self.indentation_based

    def lex(self, text):
        tokens = self.lexer.lex(text)
        return self.reformat_tokens(tokens)

    def reformat_tokens(self, tokens):
        l = []
        for t in tokens:
            l.append((t[0], t[1]))
        return l

    def relex_import(self, startnode, version = 0):
        """Optimised relex for freshly imported files."""
        success = self.lex(startnode.symbol.name)
        bos = startnode.prev_term # bos
        parent = bos.parent
        eos = parent.children.pop()
        last_node = bos
        for match in success:
            if match is success[0]:
                # reuse old node for fist node to mimic the behaviour of a
                # normal relex
                node = startnode
                node.symbol.name = match[0]
            else:
                node = TextNode(Terminal(match[0]))
            node.lookup = match[1]
            parent.children.append(node)
            last_node.next_term = node
            last_node.right = node
            node.left = last_node
            node.prev_term = last_node
            node.parent = parent
            last_node = node
            node.mark_changed()
        parent.children.append(eos)
        last_node.right = eos # link to eos
        last_node.next_term = eos
        eos.left = last_node
        eos.prev_term = last_node
        bos.mark_changed()
        eos.mark_changed()
        parent.mark_changed()

    def relex(self, node):
        # find farthest node that has lookahead into node
        # start munching tokens and spit out nodes
        #     if generated node already exists => stop
        #     (only if we passed edited node)

        self.relexed = set()

        if type(node.parent) is MultiTextNode:
            # When changing a node within a MultiNode we need to relex the
            # MultiNode
            node = node.parent

        # find node to start relaxing
        startnode = node
        node = self.find_preceeding_node(node)

        while isinstance(node.symbol, IndentationTerminal):
            node = node.next_term

        if node is startnode:
            past_startnode = True
        else:
            past_startnode = False

        if isinstance(node, EOS):
            # nothing to do here
            return False

        # relex
        read_nodes = []
        generated_tokens = []
        pos = 0  # read tokens
        read = 0 # generated tokens
        current_node = node
        next_token = self.lexer.get_token_iter(node).__next__

        combos = []
        last_read = None

        tokenslength = 0
        readlength = 0
        toks = []
        read = []
        pairs = []
        lookaheads = []
        error = None

        i = 0
        while True:
            try:
                token = next_token()
                lookaheads.append(token[2])
                if not past_startnode:
                    for temp in token[3]:
                        if temp is startnode:
                            past_startnode = True
                            break
                toks.append([x for i,x in enumerate(token) if i != 3])
                tokenslength += tokenlen(token[0])
                for r in token[3]:
                    if not read or r is not read[-1]: # skip already read nodes from previous tokens
                        read.append(r)
                        if not isinstance(r.symbol, IndentationTerminal):
                            readlength += getlength(r)
                if tokenslength == readlength:
                    # Abort relexing if we relexed a node to itself AFTER we
                    # passed `startnode`. This way we avoid relexing nodes that
                    # don't need to be relexed.
                    if past_startnode and read[-1] is not startnode:
                        if len(token[3]) == 1:
                            assert r is token[3][0]
                            if r.symbol.name == token[0] and r.lookup == token[1]:
                                toks.pop()
                                read.pop()
                                break

                    # if new generated tokens match the read tokens, we have a pair
            except StopIteration:
                break
            except LexingError as e:
                if read and type(read[-1]) is MultiTextNode:
                    pairs = []
                    startnode.changed = True
                    raise e
                # Lexer failed to repair everything. See if it managed to lex
                # parts of the changes (toks contains tokens) and if so
                # integrate them into the parse tree. The partly lexed tokens
                # will have bigger lookaheads than usual as they depend on the
                # text parts that couldn't be relexed.
                # Might involve splitting up a node resulting in leftover text
                # that couldn't be lexed as this point. Put that text into a new
                # node and also separate any newlines contained within.
                error = e
                if toks:
                    leftover = readlength - tokenslength
                    if leftover > 0:
                        name = read[-1].symbol.name[-leftover:]
                        l = re.split("(\r)", name)
                        for e in l:
                            if e == "":
                                # Splitting consecutive newlines yields
                                # additional empty strings in the result. Don't
                                # add them into the tree. See
                                # Test_Relexing::test_lexingerror_bug.
                                continue
                            toks.append((e, "<E>", 1))
                    pairs.append((toks, read))
                else:
                    # There are no part matches so remark the startnode as error
                    startnode.changed = True
                if not past_startnode:
                    # When a lexing error occurs before we reached the newly
                    # inserted node (startnode) try to continue lexing from
                    # startnode onwards.
                    # See Test_Relexing::test_newline_after_error
                    next_token = self.lexer.get_token_iter(startnode).__next__
                    past_startnode = True
                    continue
                break

        if not toks:
            # If there is nothing to merge either re-raise the LexingError if
            # there was one or return False (=no changes)
            if error:
                raise error
            else:
                return False

        changed = False
        # We have to remember the location at which we started relexing. This
        # allows us to properly update all lookback values, even if nodes have
        # been inserted before the starting node or nodes were moved into a
        # multitext node. Otherwise we might only update some of the nodes.
        if read[0].ismultichild():
            node_before_changes = read[0].parent.prev_term
        else:
            node_before_changes = read[0].prev_term
        if self.merge_back(toks, read):
            changed = True

        # update lookback counts using lookaheads
        self.update_lookback(node_before_changes.next_term, startnode)

        if error:
            raise error
        return changed

    def update_lookback(self, node, startnode):
        n = node
        la_list = []
        past_node = False
        while True:
            if n is startnode:
                past_node = True
            # indentation tokens are skipped in StringWrapper, so skip them here
            # as well
            while isinstance(n.symbol, IndentationTerminal):
                n = n.next_term
            if isinstance(n, EOS):
                break
            # compute lookback (removes old lookbacks)
            la_list = [(name, la, cnt) for name, la, cnt in la_list if la > 0]
            newlookback = max(la_list, key=lambda item:item[2])[2] if la_list else 0
            if not self.was_relexed(n) and n.lookback == newlookback and past_node:
                break
            n.lookback = newlookback

            # advance
            offset = getlength(n)
            la_list = [(name, la - offset, cnt+1) for name, la, cnt in la_list]

            # add
            la_list.append((n.symbol.name, n.lookahead, 1))

            n = n.next_term

    def was_relexed(self, node):
        return node in self.relexed

    def iter_gen(self, tokens):
        for t in tokens:
            if type(t[0]) is list:
                yield ("new mt", t[1], t[2])
                for x in t[0]:
                    yield (x, t[1], t[2])
                yield ("finish mt", None, None)
            else:
                yield t
        while True:
            yield None

    def iter_read(self, nodes):
        for n in nodes:
            if isinstance(n, MultiTextNode):
                # since we are removing elements from the original list during
                # iteration we need to create a copy to not skip anything
                for x in list(n.children):
                    yield x
            else:
                yield n
        while True:
            yield None

    def remove_check(self, node):
        if isinstance(node.parent, MultiTextNode):
            if len(node.parent.children) == 0:
                node.parent.remove()
            else:
                node.parent.update_children()

    def merge_back(self, tokens, read):
        if len(tokens) == 1 and tokens[0][0] == "\x81":
            return False

        lastread = read[0].prev_term

        it_gen = self.iter_gen(tokens)
        it_read = self.iter_read(read)

        gen = next(it_gen)
        read = next(it_read)

        totalr = 0
        totalg = 0

        reused = set()
        current_mt = None
        changed = False

        while True:
            while read is not None and isinstance(read.symbol, IndentationTerminal):
                read.remove()
                read = next(it_read)
            if gen is None and read is None:
                break

            if read and read.deleted:
                read = next(it_read)
                continue

            if gen is None:
                lengen = 0
            elif gen[0] == "new mt":
                if read and read.ismultichild() and not read.parent in reused:
                    current_mt = read.parent # reuse
                else:
                    current_mt = MultiTextNode() # create new
                    lastread.insert_after(current_mt) # insert multiline under same parent as the nodes it replaces
                    changed = True
                if current_mt.lookup != gen[1]:
                    changed = True
                current_mt.lookup = gen[1]
                current_mt.lookahead = gen[2]
                self.relexed.add(current_mt)
                gen = next(it_gen)
                continue
            elif gen[0] == "finish mt":
                reused.add(current_mt)
                lastread = current_mt
                gen = next(it_gen)
                current_mt.update_children()
                current_mt = None
                continue
            else:
                lengen = len(gen[0])

            if totalr >= totalg + lengen:
                changed = True
                # One node has been split into multiple nodes. Insert all
                # remaining nodes until the lengths add up again.
                new = TextNode(Terminal(gen[0]))
                self.relexed.add(new)
                new.lookup = gen[1]
                if new.lookup == "<E>":
                    # If this token comes from the leftovers of a LexingError,
                    # mark it appropriately
                    new.changed = True  # XXX with error recovery, mark as error
                new.lookahead = gen[2]
                if current_mt and not lastread.ismultichild():
                    current_mt.insert_at_beginning(new)
                else:
                    lastread.insert_after(new)
                lastread = new
                totalg += lengen
                gen = next(it_gen)
            elif totalr + getlength(read) <= totalg:
                changed = True
                # Multiple nodes have been combined into less nodes. Delete old
                # nodes until the lengths add up again.
                read.remove()
                self.remove_check(read)
                totalr += getlength(read)
                read = next(it_read)
            else:
                # Overwrite old nodes with updated values. Move nodes in or out
                # of multinodes if needed.
                totalr += getlength(read)
                totalg += lengen
                if read.lookup != gen[1]:
                    read.mark_changed()
                    self.relexed.add(read)
                    changed = True
                else:
                    read.mark_changed()
                if not isinstance(read.symbol, MagicTerminal):
                    read.symbol.name = gen[0].replace("\x81", "")
                    read.lookup = gen[1]
                    read.lookahead = gen[2]
                    self.relexed.add(read)
                else:
                    read.lookup = gen[1]
                if not current_mt:
                    if read.ismultichild():
                        # Read node was previously part of a multinode but has
                        # been updated to a normal node. Remove it from the
                        # multinode.
                        read.remove(True)
                        read.deleted = False
                        self.remove_check(read)
                        lastread.insert_after(read)
                        changed = True
                else:
                    if not read.ismultichild() or current_mt is not read.parent:
                        # Read node has been moved from a normal node into a
                        # multinode or from one multinode into another
                        # multinode. Remove from old locations and insert into
                        # new location.
                        read.remove(True)
                        read.deleted = False
                        self.remove_check(read)
                        if current_mt.isempty():
                            current_mt.set_children([read])
                        else:
                            lastread.insert_after(read)
                        changed = True
                lastread = read
                read = next(it_read)
                gen = next(it_gen)

        return changed

    def find_preceeding_node(self, node):
        original = node
        if node.lookback == -1:
            node = node.prev_term
            while isinstance(node.symbol, IndentationTerminal):
                node = node.prev_term
        if isinstance(node.symbol, MagicTerminal) and node.lookback <= 0:
            # Token was created next to a language box and the language box is
            # not part of an in-progress string/comment.
            return original
        for i in range(node.lookback):
            while isinstance(node.symbol, IndentationTerminal):
                node = node.prev_term
            node = node.prev_term
        if type(node) is BOS:
            node = node.next_term
        return node

IncrementalLexer = IncrementalLexerCF
import sys

class StringWrapper(object):
    """A wrapper around nodes within the parse tree that makes them appear as a normal Python string.

    Used by the lexer to generate tokens from a stream of nodes."""
    # XXX This is just a temporary solution. To do this right we have to alter
    # the lexer to work on (node, index)-tuples

    def __init__(self, startnode, relexnode):
        self.node = startnode
        self.relexnode = relexnode
        self.length = sys.maxsize
        self.last_node = None

    def __len__(self):
        return self.length

    def __getitem__(self, index):
        startindex = index
        node = self.node
        if isinstance(node, EOS):
            raise IndexError
        currentname = getname(node)
        l = 0
        while index > len(currentname) - 1:
            index -= len(currentname)
            l += len(currentname)
            node = node.next_term
            if node is None:
                raise IndexError
            while isinstance(node.symbol, IndentationTerminal):
                node = node.next_term
            if isinstance(node, EOS):
                # tried to access index out of bounds. Set text length so next
                # call to find_next_token can finish or throw LexingError
                self.length = startindex - index
                raise IndexError
            currentname = getname(node)
        # found index without problem, check if we reached the end of file
        node = node.next_term
        while isinstance(node.symbol, IndentationTerminal):
            node = node.next_term
        if isinstance(node, EOS):
            self.length = startindex + len(currentname[index:])
        return currentname[index]

    def __getslice__(self, start, stop):
        #XXX get rid of slice in lexer.py
        if stop <= start:
            return ""

        name = getname(self.node)
        if start < len(name) and stop < len(name):
            self.nodes = [self.node]
            return name[start: stop]

        text = []
        self.nodes = []
        node = self.node
        i = 0
        while i < stop:
            name = getname(node)
            text.append(name)
            i += len(name)
            if i > start:
                self.nodes.append(node)
            node = node.next_term
            while isinstance(node.symbol, IndentationTerminal):
                node = node.next_term
            if isinstance(node, EOS):
                break

        return "".join(text)[start:stop]

    def make_token(self, start, end, tokentype):
        node = self.node
        i = 0
        text = []
        past_relexnode = False
        read = []
        skip = 0

        if end == -1:
            end = sys.maxsize

        mtokens = []

        for node in iter_tree(node):
            if i >= end:
                break
            if node is self.relexnode:
                past_relexnode = True
            if isinstance(node.symbol, IndentationTerminal):
                if i > start:
                    # only add if it is relevant
                    read.append(node)
                continue
            if isinstance(node, EOS):
                break
            name = getname(node)
            i += len(name)
            if i <= start:
                skip = i
                continue

            # split token at language box
            if isinstance(node.symbol, MagicTerminal):
                if text:
                    if len(mtokens) == 0:
                        # first token: slice at start
                        mtokens.append("".join(text)[start-skip:])
                    else:
                        mtokens.append("".join(text))
                # It doesn't matter what we return here as it will be replaced
                # with the lbox node in merge_back. Just make sure it's 1
                # character long
                mtokens.append("L")
                if type(node.parent) is MultiTextNode:
                    if node.parent not in read:
                        read.append(node.parent)
                else:
                    read.append(node)
                text = []
                continue

            text.append(name)
            # when adding children of a MultiTextNode, add the MultiTextNode to
            # read instead so merge_back can merge everything properly later
            if type(node.parent) is MultiTextNode:
                if node.parent not in read:
                    read.append(node.parent)
            else:
                read.append(node)

        # last token: slice at end
        if text:
            if len(mtokens) == 0:
                mtokens.append("".join(text)[start-skip:end-skip])
            else:
                mtokens.append("".join(text)[:end-i])

        self.last_node = node.prev_term

        while isinstance(read[-1].symbol, IndentationTerminal):
            # remove IndentationTerminals at the end of read that are not
            # actually part of the token
            read.pop()

        tokenname = "".join(text)[(start-skip):(end-skip)]

        # split newlines and calculate length
        newmtokens = []
        r = re.compile("([\r])")
        length = 0
        for t in mtokens:
            if type(t) == str:
                newmtokens.extend([_f for _f in r.split(t) if _f])
            else:
                newmtokens.append(t)
            length += getlength(t)

        if len(newmtokens) == 1:
            return (newmtokens[0], read, length)
        return (newmtokens, read, length)

def getname(node):
    if type(node.symbol) is MagicTerminal:
        return ""
    if type(node.symbol) is IndentationTerminal:
        return ""
    if type(node) is MultiTextNode:
        l = []
        for x in node.children:
            if type(x.symbol) is MagicTerminal:
                l.append("")
            else:
                l.append(x.symbol.name)
        return "".join(l)
    return node.symbol.name

def getlength(node):
    if isinstance(node, TextNode):
        if isinstance(node.symbol, MagicTerminal):
            return 1
        return len(getname(node))
    return len(node)

def tokenlen(token):
    if type(token) is list:
        return sum([len(t) for t in token])
    return len(token)

def iter_tree(node):
    while True:
        if type(node) is EOS:
            raise StopIteration
        if type(node) is MultiTextNode:
            for c in node.children:
                yield c
        else:
            yield node
        node = node.next_term
