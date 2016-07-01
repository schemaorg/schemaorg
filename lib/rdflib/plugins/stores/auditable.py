"""

This wrapper intercepts calls through the store interface and implements
thread-safe logging of destructive operations (adds / removes) in reverse.
This is persisted on the store instance and the reverse operations are
executed In order to return the store to the state it was when the transaction
began Since the reverse operations are persisted on the store, the store
itself acts as a transaction.

Calls to commit or rollback, flush the list of reverse operations This
provides thread-safe atomicity and isolation (assuming concurrent operations
occur with different store instances), but no durability (transactions are
persisted in memory and wont  be available to reverse operations after the
system fails): A and I out of ACID.

"""

from rdflib.store import Store
from rdflib import Graph, ConjunctiveGraph
import threading

destructiveOpLocks = {
    'add': None,
    'remove': None,
}


class AuditableStore(Store):
    def __init__(self, store):
        self.store = store
        self.context_aware = store.context_aware
        # NOTE: this store can't be formula_aware as it doesn't have enough
        # info to reverse the removal of a quoted statement
        self.formula_aware = False  # store.formula_aware
        self.transaction_aware = True  # This is only half true
        self.reverseOps = []
        self.rollbackLock = threading.RLock()

    def open(self, configuration, create=True):
        return self.store.open(configuration, create)

    def close(self, commit_pending_transaction=False):
        self.store.close()

    def destroy(self, configuration):
        self.store.destroy(configuration)

    def query(self, *args, **kw):
        return self.store.query(*args, **kw)

    def add(self, triple, context, quoted=False):
        (s, p, o) = triple
        lock = destructiveOpLocks['add']
        lock = lock if lock else threading.RLock()
        with lock:
            context = context.__class__(self.store, context.identifier) if context is not None else None
            ctxId = context.identifier if context is not None else None
            self.reverseOps.append((s, p, o, ctxId, 'remove'))
            try:
                self.reverseOps.remove((s, p, o, ctxId, 'add'))
            except ValueError:
                pass
            self.store.add((s, p, o), context, quoted)

    def remove(self, (subject, predicate, object_), context=None):
        lock = destructiveOpLocks['remove']
        lock = lock if lock else threading.RLock()
        with lock:
            # Need to determine which quads will be removed if any term is a
            # wildcard
            context = context.__class__(self.store, context.identifier) if context is not None else None
            ctxId = context.identifier if context is not None else None
            if None in [subject, predicate, object_, context]:
                if ctxId:
                    for s, p, o in context.triples((subject, predicate, object_)):
                        try:
                            self.reverseOps.remove((s, p, o, ctxId, 'remove'))
                        except ValueError:
                            self.reverseOps.append((s, p, o, ctxId, 'add'))
                else:
                    for s, p, o, ctx in ConjunctiveGraph(self.store).quads((subject, predicate, object_)):
                        try:
                            self.reverseOps.remove((s, p, o, ctx.identifier, 'remove'))
                        except ValueError:
                            self.reverseOps.append((s, p, o, ctx.identifier, 'add'))
            else:
                try:
                    self.reverseOps.remove((subject, predicate, object_, ctxId, 'add'))
                except ValueError:
                    self.reverseOps.append((subject, predicate, object_, ctxId, 'add'))
            self.store.remove((subject, predicate, object_), context)

    def triples(self, triple, context=None):
        (su, pr, ob) = triple
        context = context.__class__(self.store, context.identifier) if context is not None else None
        for (s, p, o), cg in self.store.triples((su, pr, ob), context):
            yield (s, p, o), cg

    def __len__(self, context=None):
        context = context.__class__(self.store, context.identifier) if context is not None else None
        return self.store.__len__(context)

    def contexts(self, triple=None):
        for ctx in self.store.contexts(triple):
            yield ctx

    def bind(self, prefix, namespace):
        self.store.bind(prefix, namespace)

    def prefix(self, namespace):
        return self.store.prefix(namespace)

    def namespace(self, prefix):
        return self.store.namespace(prefix)

    def namespaces(self):
        return self.store.namespaces()

    def commit(self):
        self.store.commit()
        self.reverseOps = []

    def rollback(self):
        # Aquire Rollback lock and apply reverse operations in the forward
        # order
        with self.rollbackLock:
            for subject, predicate, obj, context, op in self.reverseOps:
                if op == 'add':
                    self.store.add(
                        (subject, predicate, obj), Graph(self.store, context))
                else:
                    self.store.remove(
                        (subject, predicate, obj), Graph(self.store, context))

            self.reverseOps = []
