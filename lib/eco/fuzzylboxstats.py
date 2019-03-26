import random, json, glob, os
from grammars.grammars import lang_dict, EcoFile
from treemanager import TreeManager
from grammar_parser.gparser import Nonterminal, Terminal

# helper functions

debug = False

def next_node(node):
    while(node.right is None):
        node = node.parent
    return node.right

def prev_node(node):
    while(node.left is None):
        node = node.parent
    return node.left

def subtree_to_text(subtree):
    l = []
    if subtree.children:
        for child in subtree.children:
            l.append(subtree_to_text(child))
    elif type(subtree.symbol) is Terminal:
        l.append(subtree.symbol.name)
    return "".join(l).replace("\r", "").replace("\t", "").replace("\n", "")

def truncate(string):
    if len(string) > 40:
        return repr(string[:20] + "..." + string[-20:])
    else:
        return repr(string)

class FuzzyLboxStats:

    def __init__(self, main, sub):
        parser, lexer = main.load()
        self.lexer = lexer
        self.parser = parser
        self.ast = parser.previous_version
        self.treemanager = TreeManager()
        self.treemanager.add_parser(parser, lexer, main.name)
        self.treemanager.option_autolbox_insert = True
        self.langname = main.name

        parser.setup_autolbox(main.name)
        self.sub = sub

        self.inserted = 0

        self.faillog = []

    def load_main(self, filename):
        self.filename = filename
        f = open(filename, "r")
        self.content = f.read()
        f.close()
        self.content.replace("\n", "\r")
        self.treemanager.import_file(self.content)
        self.mainexprs = self.find_nonterms_by_name(self.treemanager, self.main_repl_str)
        self.minver = self.treemanager.version

    def reset(self):
        self.parser.reset()
        self.treemanager = TreeManager()
        self.treemanager.add_parser(self.parser, self.lexer, self.langname)
        self.treemanager.import_file(self.content)
        self.mainexprs = self.find_nonterms_by_name(self.treemanager, self.main_repl_str)

    def load_expr(self, filename):
        f = open(filename, "r")
        content = f.read()
        f.close()
        self.replexprs = self.find_expressions(content, self.sub_repl_str)

    def load_expr_from_json(self, filename):
        import json
        with open(filename) as f:
            self.replexprs = json.load(f)

    def set_replace(self, main, sub):
        self.main_repl_str = main
        self.sub_repl_str = sub

    def find_nonterms_by_name(self, tm, name):
        l = []
        bos = tm.get_bos()
        eos = tm.get_eos()
        node = bos.right_sibling()
        while node is not eos:
            # Python: Only replace RHS of expressions, because there is
            # currently a bug that keeps indentation terminals from being
            # inserted before language boxes
            if node.symbol.name == "testlist": # Python only use most right testlist
                if not node.left_sibling():
                    node = next_node(node)
                    continue
            # PHP: Only replace RHS of expressions
            if node.symbol.name == name and (name != "expr_without_variable" or node.children[0].symbol.name == "expr"):
                l.append(node)
                node = next_node(node)
                continue
            if node.children:
                node = node.children[0]
                continue
            node = next_node(node)
        return l

    def find_expressions(self, program, expr):
        parser, lexer = self.sub.load()
        treemanager = TreeManager()
        treemanager.add_parser(parser, lexer, self.sub.name)
        treemanager.import_file(program)

        # find all sub expressions
        l = self.find_nonterms_by_name(treemanager, expr)
        return [subtree_to_text(st).rstrip() for st in l]

    def insert_python_expression(self, expr):
        for c in expr:
            self.treemanager.key_normal(c)

    def delete_expr(self, expr):
        # find first term and last term
        # select + delete
        node = expr
        while type(node.symbol) is Nonterminal:
            if node.children:
                node = node.children[0]
            else:
                node = next_node(node)
        first = node

        node = expr
        while type(node.symbol) is Nonterminal:
            if node.children:
                node = node.children[-1]
            else:
                node = prev_node(node)
        while node.lookup == "<ws>" or node.lookup == "<return>":
            node = node.prev_term
        last = node

        if first.deleted or last.deleted:
            return None

        self.treemanager.select_nodes(first, last)
        deleted = self.treemanager.copySelection()
        self.treemanager.deleteSelection()
        return deleted

    def run(self):
        assert len(self.treemanager.parsers) == 1

        ops = self.main_repl_str, len([subtree_to_text(x) for x in self.mainexprs])
        choices = self.sub_repl_str, len(self.replexprs)
        random.shuffle(self.mainexprs)
        preversion = self.treemanager.version

        inserted_error = 0
        inserted_valid = 0
        noinsert_error = 0
        noinsert_valid = 0
        noinsert_multi = 0

        if len(self.mainexprs) > 10:
            exprchoices = [random.choice(self.mainexprs) for i in range(10)]
        else:
            exprchoices = self.mainexprs
        for e in exprchoices:
            if e.get_root() is None:
                continue
            deleted = self.delete_expr(e)
            before = len(self.treemanager.parsers)
            if deleted:
                choice = random.choice(self.replexprs)
                if debug: print "  Replacing '{}' with '{}':".format(truncate(deleted), choice)
                self.insert_python_expression(choice)
                valid = self.parser.last_status
                if before == len(self.treemanager.parsers):
                    if len(self.parser.error_nodes) > 0 and self.parser.error_nodes[0].autobox and len(self.parser.error_nodes[0].autobox) > 1:
                        noinsert_multi += 1
                        result = "No box inserted (Multi)"
                        self.faillog.append(("multi", self.filename, repr(deleted), repr(choice)))
                    elif valid:
                        noinsert_valid += 1
                        result = "No box inserted (Valid)"
                        self.faillog.append(("valid", self.filename, repr(deleted), repr(choice)))
                    else:
                        noinsert_error += 1
                        result = "No box inserted (Error)"
                        self.faillog.append(("error", self.filename, repr(deleted), repr(choice)))
                else:
                    result = "Box inserted"
                    self.inserted += 1
                    if valid:
                        inserted_valid += 1
                    else:
                        inserted_error += 1
                        self.faillog.append(("inerr", self.filename, repr(deleted), repr(choice)))
                if debug: print "    => {} ({})".format(result, valid)
            else:
                if debug: print "Replacing '{}' with '{}':\n    => Already deleted".format(truncate(subtree_to_text(e)), truncate(choice))
            self.undo(self.minver)
        if debug:
            print("Boxes inserted: {}/{}".format(self.inserted, ops))
            print("Valid insertions:", inserted_valid)
            print("Invalid insertions:", inserted_error)
            print("No insertion (valid):", noinsert_valid)
            print("No insertion (error):", noinsert_error)
            print("No insertion (multi):", noinsert_multi)
        return (inserted_valid, inserted_error, noinsert_valid, noinsert_error, noinsert_multi)

    def undo(self, version):
        while self.treemanager.version != version:
            before = self.treemanager.version
            self.treemanager.version -= 1
            self.treemanager.recover_version("undo", self.treemanager.version + 1)
            self.treemanager.cursor.load(self.treemanager.version, self.treemanager.lines)
            if before == self.treemanager.version:
                exit("Error")

def run_multi(name, main, sub, folder, ext, exprs, mrepl, srepl=None):
    print "Running", name 
    results = []
    faillog = []
    i = 0
    files = [y for x in os.walk(folder) for y in glob.glob(os.path.join(x[0], ext))]
    if len(files) > 200:
        # let's limit files to 200 for now
        files = random.sample(files, 200)
    for filename in files:
        fuz = FuzzyLboxStats(main, sub)
        fuz.set_replace(mrepl, srepl)
        try:
            fuz.load_main(filename)
            fuz.load_expr_from_json(exprs)
            r = fuz.run()
        except Exception, e:
            # We only care about files that parse initially
            sys.stdout.write("s")
            sys.stdout.flush()
            continue
        if r[1] > 0 or r[3] > 0:
            # insert_error and noinsert_error
            sys.stdout.write("x")
            sys.stdout.flush()
        else:
            sys.stdout.write(".")
            sys.stdout.flush()
        results.append(r)
        faillog.extend(fuz.faillog)
        i = i + sum(r)
        #print(i)
        if i > 1000:
            break
    with open("{}_log.json".format(name), "w") as f: json.dump(results, f)
    with open("{}_fail.json".format(name), "w") as f: json.dump(faillog, f, indent=0)
    print


def create_composition(smain, ssub, mainexpr, gmain, gsub, subexpr=None):
    sub = EcoFile(ssub, "grammars/" + gsub, ssub)
    if subexpr:
        sub.name = sub.name + " expr"
        sub.change_start(subexpr)

    main = EcoFile(smain + " + " + ssub, "grammars/" + gmain, smain)
    main.add_alternative(mainexpr, sub)
    lang_dict[main.name] = main
    lang_dict[sub.name] = sub

    return main

if __name__ == "__main__":
    import sys
    args = sys.argv
    wd = "/home/lukas/research/auto_lbox_experiments"

    base = args[1]
    if base == "java":
        javaphp = create_composition("Java", "PHP", "unary_expression", "java15.eco", "php.eco", "expr_without_variable")
        javasql = create_composition("Java", "Sqlite", "unary_expression", "java15.eco", "sqlite.eco")
        javalua = create_composition("Java", "Lua", "unary_expression", "java15.eco", "lua5_3.eco", "explist")
        run_multi("javaphp", javaphp, None, "{}/javastdlib5/".format(wd), '*.java', "{}/phpstmts.json".format(wd), "unary_expression")
        run_multi("javasql", javasql, None, "{}/javastdlib5/".format(wd), '*.java', "{}/sqlstmts.json".format(wd), "unary_expression")
        run_multi("javalua", javalua, None, "{}/javastdlib5/".format(wd), '*.java', "{}/luastmts.json".format(wd), "unary_expression")
    elif base == "lua":
        luaphp  = create_composition("Lua", "PHP", "explist", "lua5_3.eco", "php.eco", "expr_without_variable")
        luasql  = create_composition("Lua", "Sqlite", "explist", "lua5_3.eco", "sqlite.eco")
        luajava = create_composition("Lua", "Java", "explist", "lua5_3.eco", "java15.eco", "unary_expression")
        run_multi("luaphp", luaphp, None, "{}/lua/testes/".format(wd), '*.lua', "{}/phpstmts.json".format(wd), "explist")
        run_multi("luasql", luasql, None, "{}/lua/testes/".format(wd), '*.lua', "{}/sqlstmts.json".format(wd), "explist")
        run_multi("luajava", luajava, None, "{}/lua/testes/".format(wd), '*.lua', "{}/javastmts.json".format(wd), "explist")
    elif base == "php":
        phpjava = create_composition("PHP", "Java", "expr", "php.eco", "java15.eco", "unary_expression")
        phpsql  = create_composition("PHP", "Sqlite", "expr", "php.eco", "sqlite.eco")
        phplua  = create_composition("PHP", "Lua", "expr", "php.eco", "lua5_3.eco", "explist")
        run_multi("phpjava", phpjava, None, "{}/phpfiles/".format(wd), '*.php', "{}/javastmts.json".format(wd), "expr_without_variable")
        run_multi("phpsql", phpsql, None, "{}/phpfiles/".format(wd), '*.php', "{}/sqlstmts.json".format(wd), "expr_without_variable")
        run_multi("phplua", phplua, None, "{}/phpfiles/".format(wd), '*.php', "{}/luastmts.json".format(wd), "expr_without_variable")
    elif base == "sql":
        sqlphp  = create_composition("Sqlite", "PHP",  "expr", "sqlite.eco", "php.eco", "expr_without_variable")
        sqljava = create_composition("Sqlite", "Java", "expr", "sqlite.eco", "java15.eco", "unary_expression")
        sqllua  = create_composition("Sqlite", "Lua",  "expr", "sqlite.eco", "lua5_3.eco", "explist")
        run_multi("sqlphp", sqlphp, None, "{}/sqlfiles/".format(wd), '*.sql', "{}/phpstmts.json".format(wd), "expr")
        run_multi("sqljava", sqljava, None, "{}/sqlfiles/".format(wd), '*.sql', "{}/javastmts.json".format(wd), "expr")
        run_multi("sqllua", sqllua, None, "{}/sqlfiles/".format(wd), '*.sql', "{}/luastmts.json".format(wd), "expr")
