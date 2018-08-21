import typing
from enum import IntEnum

from .common import CAPI
from ._ffi import ffi
from .graph import map_graph
from .errors import consume_errors


class ResultOrder(IntEnum):
    Normal = 0
    Inverted = 1
    Random = 2


class CorpusStorageManager:
    def __init__(self, db_dir='data/', use_parallel=True):
        self.__cs = CAPI.annis_cs_new(db_dir.encode('utf-8'), use_parallel)

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        CAPI.annis_cs_free(self.__cs)
        self.__cs = ffi.NULL


    def list(self):
        err = ffi.new("AnnisErrorList **")
        orig = CAPI.annis_cs_list(self.__cs, err)
        consume_errors(err)

        orig_size = int(CAPI.annis_vec_str_size(orig))

        copy = []
        for idx, _ in enumerate(range(orig_size)):
            corpus_name = ffi.string(CAPI.annis_vec_str_get(orig, idx))
            copy.append(corpus_name.decode('utf-8'))
        return copy
    
    def count(self, corpora, query_as_aql):
        result = int(0)
        for c in corpora:
            err = ffi.new("AnnisErrorList **")
            result = result + CAPI.annis_cs_count(self.__cs, c.encode('utf-8'), query_as_aql.encode('utf-8'), err)
            consume_errors(err)
        
        return result

    def find(self, corpora, query_as_aql, offset=0, limit=10, order=ResultOrder.Normal):
        result = []
        for c in corpora:
            err = ffi.new("AnnisErrorList **")
            vec = CAPI.annis_cs_find(self.__cs, c.encode('utf-8'), query_as_aql.encode('utf-8'), offset, limit, int(order), err)
            consume_errors(err)

            vec_size = CAPI.annis_vec_str_size(vec)
            for i in range(vec_size):
                result_str = ffi.string(CAPI.annis_vec_str_get(vec, i)).decode('utf-8')
                result.append(result_str)
        return result

    def subgraph(self, corpus_name : str, node_ids, ctx_left=0, ctx_right=0):
        c_node_ids = CAPI.annis_vec_str_new()
        for nid in node_ids:
            CAPI.annis_vec_str_push(c_node_ids, nid.encode('utf-8'))
        
        err = ffi.new("AnnisErrorList **")
        db = CAPI.annis_cs_subgraph(self.__cs, corpus_name.encode('utf-8'), c_node_ids, ctx_left, ctx_right, err)
        consume_errors(err)

        G = map_graph(db)

        CAPI.annis_free(db)
        CAPI.annis_free(c_node_ids)

        return G

    def subcorpus_graph(self, corpus_name : str, document_ids):
        c_document_ids = CAPI.annis_vec_str_new()
        for id in document_ids:
            CAPI.annis_vec_str_push(c_document_ids, id.encode('utf-8'))

        err = ffi.new("AnnisErrorList **")
        db = CAPI.annis_cs_subcorpus_graph(self.__cs, corpus_name.encode('utf-8'), 
        c_document_ids, err)
        consume_errors(err)

        G = map_graph(db)

        CAPI.annis_free(db)
        CAPI.annis_free(c_document_ids)

        return G
        

    def apply_update(self, corpus_name : str, update):
        """ Atomically apply update (add/delete nodes, edges and labels) to the database

        >>> from graphannis.cs import CorpusStorageManager
        >>> from graphannis.graph import GraphUpdate 
        >>> with CorpusStorageManager() as cs:
        ...     with GraphUpdate() as g:
        ...         g.add_node('n1')
        ...         cs.apply_update('test', g)
        """ 
        
        err = ffi.new("AnnisErrorList **")
        CAPI.annis_cs_apply_update(self.__cs,
        corpus_name.encode('utf-8'), update.get_instance(), err)
        consume_errors(err)


    def delete_corpus(self, corpus_name : str):
        """ Delete a corpus from the database

        >>> from graphannis.cs import CorpusStorageManager
        >>> from graphannis.graph import GraphUpdate 
        >>> with CorpusStorageManager() as cs:
        ...     # create a corpus named "test"
        ...     with GraphUpdate() as g:
        ...         g.add_node('anynode')
        ...         cs.apply_update('test', g)
        ...     # delete it
        ...     cs.delete_corpus('test')
        True
        """ 
        err = ffi.new("AnnisErrorList **")
        result = CAPI.annis_cs_delete(self.__cs, corpus_name.encode('utf-8'), err)
        consume_errors(err)
        return result

    def import_relannis(self, corpus_name : str, path):
        """ Import a legacy relANNIS file format into the database
        """ 
        
        err = ffi.new("AnnisErrorList **")
        CAPI.annis_cs_import_relannis(self.__cs,
        corpus_name.encode('utf-8'), path.encode('utf-8'), err)
        consume_errors(err)

