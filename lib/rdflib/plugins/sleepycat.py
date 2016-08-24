from rdflib.store import Store, VALID_STORE, NO_STORE
from rdflib.term import URIRef
from rdflib.py3compat import b


def bb(u):
    return u.encode('utf-8')


try:
    from bsddb import db
    has_bsddb = True
except ImportError:
    try:
        from bsddb3 import db
        has_bsddb = True
    except ImportError:
        has_bsddb = False
from os import mkdir
from os.path import exists, abspath
from urllib import pathname2url
from threading import Thread

if has_bsddb:
    # These are passed to bsddb when creating DBs

    # passed to db.DBEnv.set_flags
    ENVSETFLAGS = db.DB_CDB_ALLDB
    # passed to db.DBEnv.open
    ENVFLAGS = db.DB_INIT_MPOOL | db.DB_INIT_CDB | db.DB_THREAD
    CACHESIZE = 1024 * 1024 * 50

    # passed to db.DB.Open()
    DBOPENFLAGS = db.DB_THREAD

import logging
logger = logging.getLogger(__name__)

__all__ = ['Sleepycat']


class Sleepycat(Store):
    context_aware = True
    formula_aware = True
    transaction_aware = False
    graph_aware = True
    db_env = None

    def __init__(self, configuration=None, identifier=None):
        if not has_bsddb:
            raise ImportError(
                "Unable to import bsddb/bsddb3, store is unusable.")
        self.__open = False
        self.__identifier = identifier
        super(Sleepycat, self).__init__(configuration)
        self._loads = self.node_pickler.loads
        self._dumps = self.node_pickler.dumps

    def __get_identifier(self):
        return self.__identifier
    identifier = property(__get_identifier)

    def _init_db_environment(self, homeDir, create=True):
        if not exists(homeDir):
            if create is True:
                mkdir(homeDir)
                      # TODO: implement create method and refactor this to it
                self.create(homeDir)
            else:
                return NO_STORE
        db_env = db.DBEnv()
        db_env.set_cachesize(0, CACHESIZE)  # TODO
        # db_env.set_lg_max(1024*1024)
        db_env.set_flags(ENVSETFLAGS, 1)
        db_env.open(homeDir, ENVFLAGS | db.DB_CREATE)
        return db_env

    def is_open(self):
        return self.__open

    def open(self, path, create=True):
        if not has_bsddb:
            return NO_STORE
        homeDir = path

        if self.__identifier is None:
            self.__identifier = URIRef(pathname2url(abspath(homeDir)))

        db_env = self._init_db_environment(homeDir, create)
        if db_env == NO_STORE:
            return NO_STORE
        self.db_env = db_env
        self.__open = True

        dbname = None
        dbtype = db.DB_BTREE
        # auto-commit ensures that the open-call commits when transactions
        # are enabled

        dbopenflags = DBOPENFLAGS
        if self.transaction_aware is True:
            dbopenflags |= db.DB_AUTO_COMMIT

        if create:
            dbopenflags |= db.DB_CREATE

        dbmode = 0660
        dbsetflags = 0

        # create and open the DBs
        self.__indicies = [None, ] * 3
        self.__indicies_info = [None, ] * 3
        for i in xrange(0, 3):
            index_name = to_key_func(
                i)((b("s"), b("p"), b("o")), b("c")).decode()
            index = db.DB(db_env)
            index.set_flags(dbsetflags)
            index.open(index_name, dbname, dbtype, dbopenflags, dbmode)
            self.__indicies[i] = index
            self.__indicies_info[i] = (index, to_key_func(i), from_key_func(i))

        lookup = {}
        for i in xrange(0, 8):
            results = []
            for start in xrange(0, 3):
                score = 1
                len = 0
                for j in xrange(start, start + 3):
                    if i & (1 << (j % 3)):
                        score = score << 1
                        len += 1
                    else:
                        break
                tie_break = 2 - start
                results.append(((score, tie_break), start, len))

            results.sort()
            score, start, len = results[-1]

            def get_prefix_func(start, end):
                def get_prefix(triple, context):
                    if context is None:
                        yield ""
                    else:
                        yield context
                    i = start
                    while i < end:
                        yield triple[i % 3]
                        i += 1
                    yield ""
                return get_prefix

            lookup[i] = (
                self.__indicies[start],
                get_prefix_func(start, start + len),
                from_key_func(start),
                results_from_key_func(start, self._from_string))

        self.__lookup_dict = lookup

        self.__contexts = db.DB(db_env)
        self.__contexts.set_flags(dbsetflags)
        self.__contexts.open("contexts", dbname, dbtype, dbopenflags, dbmode)

        self.__namespace = db.DB(db_env)
        self.__namespace.set_flags(dbsetflags)
        self.__namespace.open("namespace", dbname, dbtype, dbopenflags, dbmode)

        self.__prefix = db.DB(db_env)
        self.__prefix.set_flags(dbsetflags)
        self.__prefix.open("prefix", dbname, dbtype, dbopenflags, dbmode)

        self.__k2i = db.DB(db_env)
        self.__k2i.set_flags(dbsetflags)
        self.__k2i.open("k2i", dbname, db.DB_HASH, dbopenflags, dbmode)

        self.__i2k = db.DB(db_env)
        self.__i2k.set_flags(dbsetflags)
        self.__i2k.open("i2k", dbname, db.DB_RECNO, dbopenflags, dbmode)

        self.__needs_sync = False
        t = Thread(target=self.__sync_run)
        t.setDaemon(True)
        t.start()
        self.__sync_thread = t
        return VALID_STORE

    def __sync_run(self):
        from time import sleep, time
        try:
            min_seconds, max_seconds = 10, 300
            while self.__open:
                if self.__needs_sync:
                    t0 = t1 = time()
                    self.__needs_sync = False
                    while self.__open:
                        sleep(.1)
                        if self.__needs_sync:
                            t1 = time()
                            self.__needs_sync = False
                        if time() - t1 > min_seconds \
                                or time() - t0 > max_seconds:
                            self.__needs_sync = False
                            logger.debug("sync")
                            self.sync()
                            break
                else:
                    sleep(1)
        except Exception, e:
            logger.exception(e)

    def sync(self):
        if self.__open:
            for i in self.__indicies:
                i.sync()
            self.__contexts.sync()
            self.__namespace.sync()
            self.__prefix.sync()
            self.__i2k.sync()
            self.__k2i.sync()

    def close(self, commit_pending_transaction=False):
        self.__open = False
        self.__sync_thread.join()
        for i in self.__indicies:
            i.close()
        self.__contexts.close()
        self.__namespace.close()
        self.__prefix.close()
        self.__i2k.close()
        self.__k2i.close()
        self.db_env.close()

    def add(self, triple, context, quoted=False, txn=None):
        """\
        Add a triple to the store of triples.
        """
        (subject, predicate, object) = triple
        assert self.__open, "The Store must be open."
        assert context != self, "Can not add triple directly to store"
        Store.add(self, (subject, predicate, object), context, quoted)

        _to_string = self._to_string

        s = _to_string(subject, txn=txn)
        p = _to_string(predicate, txn=txn)
        o = _to_string(object, txn=txn)
        c = _to_string(context, txn=txn)

        cspo, cpos, cosp = self.__indicies

        value = cspo.get(bb("%s^%s^%s^%s^" % (c, s, p, o)), txn=txn)
        if value is None:
            self.__contexts.put(bb(c), "", txn=txn)

            contexts_value = cspo.get(
                bb("%s^%s^%s^%s^" % ("", s, p, o)), txn=txn) or b("")
            contexts = set(contexts_value.split(b("^")))
            contexts.add(bb(c))
            contexts_value = b("^").join(contexts)
            assert contexts_value is not None

            cspo.put(bb("%s^%s^%s^%s^" % (c, s, p, o)), "", txn=txn)
            cpos.put(bb("%s^%s^%s^%s^" % (c, p, o, s)), "", txn=txn)
            cosp.put(bb("%s^%s^%s^%s^" % (c, o, s, p)), "", txn=txn)
            if not quoted:
                cspo.put(bb(
                    "%s^%s^%s^%s^" % ("", s, p, o)), contexts_value, txn=txn)
                cpos.put(bb(
                    "%s^%s^%s^%s^" % ("", p, o, s)), contexts_value, txn=txn)
                cosp.put(bb(
                    "%s^%s^%s^%s^" % ("", o, s, p)), contexts_value, txn=txn)

            self.__needs_sync = True

    def __remove(self, (s, p, o), c, quoted=False, txn=None):
        cspo, cpos, cosp = self.__indicies
        contexts_value = cspo.get(
            b("^").join([b(""), s, p, o, b("")]), txn=txn) or b("")
        contexts = set(contexts_value.split(b("^")))
        contexts.discard(c)
        contexts_value = b("^").join(contexts)
        for i, _to_key, _from_key in self.__indicies_info:
            i.delete(_to_key((s, p, o), c), txn=txn)
        if not quoted:
            if contexts_value:
                for i, _to_key, _from_key in self.__indicies_info:
                    i.put(_to_key((s, p, o), b("")), contexts_value, txn=txn)
            else:
                for i, _to_key, _from_key in self.__indicies_info:
                    try:
                        i.delete(_to_key((s, p, o), b("")), txn=txn)
                    except db.DBNotFoundError:
                        pass  # TODO: is it okay to ignore these?

    def remove(self, (subject, predicate, object), context, txn=None):
        assert self.__open, "The Store must be open."
        Store.remove(self, (subject, predicate, object), context)
        _to_string = self._to_string

        if context is not None:
            if context == self:
                context = None

        if subject is not None \
                and predicate is not None \
                and object is not None \
                and context is not None:
            s = _to_string(subject, txn=txn)
            p = _to_string(predicate, txn=txn)
            o = _to_string(object, txn=txn)
            c = _to_string(context, txn=txn)
            value = self.__indicies[0].get(bb("%s^%s^%s^%s^" %
                                           (c, s, p, o)), txn=txn)
            if value is not None:
                self.__remove((bb(s), bb(p), bb(o)), bb(c), txn=txn)
                self.__needs_sync = True
        else:
            cspo, cpos, cosp = self.__indicies
            index, prefix, from_key, results_from_key = self.__lookup(
                (subject, predicate, object), context, txn=txn)

            cursor = index.cursor(txn=txn)
            try:
                current = cursor.set_range(prefix)
                needs_sync = True
            except db.DBNotFoundError:
                current = None
                needs_sync = False
            cursor.close()
            while current:
                key, value = current
                cursor = index.cursor(txn=txn)
                try:
                    cursor.set_range(key)
                    # Hack to stop 2to3 converting this to next(cursor)
                    current = getattr(cursor, 'next')()
                except db.DBNotFoundError:
                    current = None
                cursor.close()
                if key.startswith(prefix):
                    c, s, p, o = from_key(key)
                    if context is None:
                        contexts_value = index.get(key, txn=txn) or b("")
                        # remove triple from all non quoted contexts
                        contexts = set(contexts_value.split(b("^")))
                        # and from the conjunctive index
                        contexts.add(b(""))
                        for c in contexts:
                            for i, _to_key, _ in self.__indicies_info:
                                i.delete(_to_key((s, p, o), c), txn=txn)
                    else:
                        self.__remove((s, p, o), c, txn=txn)
                else:
                    break

            if context is not None:
                if subject is None and predicate is None and object is None:
                    # TODO: also if context becomes empty and not just on
                    # remove((None, None, None), c)
                    try:
                        self.__contexts.delete(
                            bb(_to_string(context, txn=txn)), txn=txn)
                    except db.DBNotFoundError:
                        pass

            self.__needs_sync = needs_sync

    def triples(self, (subject, predicate, object), context=None, txn=None):
        """A generator over all the triples matching """
        assert self.__open, "The Store must be open."

        if context is not None:
            if context == self:
                context = None

        # _from_string = self._from_string ## UNUSED
        index, prefix, from_key, results_from_key = self.__lookup(
            (subject, predicate, object), context, txn=txn)

        cursor = index.cursor(txn=txn)
        try:
            current = cursor.set_range(prefix)
        except db.DBNotFoundError:
            current = None
        cursor.close()
        while current:
            key, value = current
            cursor = index.cursor(txn=txn)
            try:
                cursor.set_range(key)
                # Cheap hack so 2to3 doesn't convert to next(cursor)
                current = getattr(cursor, 'next')()
            except db.DBNotFoundError:
                current = None
            cursor.close()
            if key and key.startswith(prefix):
                contexts_value = index.get(key, txn=txn)
                yield results_from_key(
                    key, subject, predicate, object, contexts_value)
            else:
                break

    def __len__(self, context=None):
        assert self.__open, "The Store must be open."
        if context is not None:
            if context == self:
                context = None

        if context is None:
            prefix = b("^")
        else:
            prefix = bb("%s^" % self._to_string(context))

        index = self.__indicies[0]
        cursor = index.cursor()
        current = cursor.set_range(prefix)
        count = 0
        while current:
            key, value = current
            if key.startswith(prefix):
                count += 1
                # Hack to stop 2to3 converting this to next(cursor)
                current = getattr(cursor, 'next')()
            else:
                break
        cursor.close()
        return count

    def bind(self, prefix, namespace):
        prefix = prefix.encode("utf-8")
        namespace = namespace.encode("utf-8")
        bound_prefix = self.__prefix.get(namespace)
        if bound_prefix:
            self.__namespace.delete(bound_prefix)
        self.__prefix[namespace] = prefix
        self.__namespace[prefix] = namespace

    def namespace(self, prefix):
        prefix = prefix.encode("utf-8")
        ns = self.__namespace.get(prefix, None)
        if ns is not None:
            return URIRef(ns.decode('utf-8'))
        return None

    def prefix(self, namespace):
        namespace = namespace.encode("utf-8")
        prefix = self.__prefix.get(namespace, None)
        if prefix is not None:
            return prefix.decode('utf-8')
        return None

    def namespaces(self):
        cursor = self.__namespace.cursor()
        results = []
        current = cursor.first()
        while current:
            prefix, namespace = current
            results.append((prefix.decode('utf-8'), namespace.decode('utf-8')))
            # Hack to stop 2to3 converting this to next(cursor)
            current = getattr(cursor, 'next')()
        cursor.close()
        for prefix, namespace in results:
            yield prefix, URIRef(namespace)

    def contexts(self, triple=None):
        _from_string = self._from_string
        _to_string = self._to_string

        if triple:
            s, p, o = triple
            s = _to_string(s)
            p = _to_string(p)
            o = _to_string(o)
            contexts = self.__indicies[0].get(bb(
                "%s^%s^%s^%s^" % ("", s, p, o)))
            if contexts:
                for c in contexts.split(b("^")):
                    if c:
                        yield _from_string(c)
        else:
            index = self.__contexts
            cursor = index.cursor()
            current = cursor.first()
            cursor.close()
            while current:
                key, value = current
                context = _from_string(key)
                yield context
                cursor = index.cursor()
                try:
                    cursor.set_range(key)
                    # Hack to stop 2to3 converting this to next(cursor)
                    current = getattr(cursor, 'next')()
                except db.DBNotFoundError:
                    current = None
                cursor.close()

    def add_graph(self, graph): 
        self.__contexts.put(bb(self._to_string(graph)), "")

    def remove_graph(self, graph): 
        self.remove((None, None, None), graph)

    def _from_string(self, i):
        k = self.__i2k.get(int(i))
        return self._loads(k)

    def _to_string(self, term, txn=None):
        k = self._dumps(term)
        i = self.__k2i.get(k, txn=txn)
        if i is None:
            # weird behavoir from bsddb not taking a txn as a keyword argument
            # for append
            if self.transaction_aware:
                i = "%s" % self.__i2k.append(k, txn)
            else:
                i = "%s" % self.__i2k.append(k)

            self.__k2i.put(k, i, txn=txn)
        else:
            i = i.decode()
        return i

    def __lookup(self, (subject, predicate, object), context, txn=None):
        _to_string = self._to_string
        if context is not None:
            context = _to_string(context, txn=txn)
        i = 0
        if subject is not None:
            i += 1
            subject = _to_string(subject, txn=txn)
        if predicate is not None:
            i += 2
            predicate = _to_string(predicate, txn=txn)
        if object is not None:
            i += 4
            object = _to_string(object, txn=txn)
        index, prefix_func, from_key, results_from_key = self.__lookup_dict[i]
        # print (subject, predicate, object), context, prefix_func, index
        # #DEBUG
        prefix = bb(
            "^".join(prefix_func((subject, predicate, object), context)))
        return index, prefix, from_key, results_from_key


def to_key_func(i):
    def to_key(triple, context):
        "Takes a string; returns key"
        return b("^").join(
            (context,
             triple[i % 3],
             triple[(i + 1) % 3],
             triple[(i + 2) % 3], b("")))  # "" to tac on the trailing ^
    return to_key


def from_key_func(i):
    def from_key(key):
        "Takes a key; returns string"
        parts = key.split(b("^"))
        return \
            parts[0], \
            parts[(3 - i + 0) % 3 + 1], \
            parts[(3 - i + 1) % 3 + 1], \
            parts[(3 - i + 2) % 3 + 1]
    return from_key


def results_from_key_func(i, from_string):
    def from_key(key, subject, predicate, object, contexts_value):
        "Takes a key and subject, predicate, object; returns tuple for yield"
        parts = key.split(b("^"))
        if subject is None:
            # TODO: i & 1: # dis assemble and/or measure to see which is faster
            # subject is None or i & 1
            s = from_string(parts[(3 - i + 0) % 3 + 1])
        else:
            s = subject
        if predicate is None:  # i & 2:
            p = from_string(parts[(3 - i + 1) % 3 + 1])
        else:
            p = predicate
        if object is None:  # i & 4:
            o = from_string(parts[(3 - i + 2) % 3 + 1])
        else:
            o = object
        return (s, p, o), (
            from_string(c) for c in contexts_value.split(b("^")) if c)
    return from_key


def readable_index(i):
    s, p, o = "?" * 3
    if i & 1:
        s = "s"
    if i & 2:
        p = "p"
    if i & 4:
        o = "o"
    return "%s,%s,%s" % (s, p, o)
