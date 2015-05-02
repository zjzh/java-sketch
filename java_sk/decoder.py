import os
import operator as op
import logging
import re

from lib.typecheck import *
import lib.visit as v
import lib.const as C

import util
from meta import class_lookup
from meta.program import Program
from meta.clazz import Clazz
from meta.method import Method
from meta.field import Field
from meta.statement import Statement
from meta.expression import Expression, to_expression

"""
Finding hole declarations
"""
class HFinder(object):

  def __init__(self):
    self._holes = []

  @property
  def holes(self):
    return self._holes

  @v.on("node")
  def visit(self, node):
    """
    This is the generic method to initialize the dynamic dispatcher
    """

  @v.when(Program)
  def visit(self, node): pass

  @v.when(Clazz)
  def visit(self, node): pass

  @v.when(Field)
  def visit(self, node):
    if node.init and node.init.kind == C.E.HOLE:
      logging.debug("hole: {}.{}".format(node.clazz.name, node.name))
      self._holes.append(node)

  @v.when(Method)
  def visit(self, node): pass

  @v.when(Statement)
  def visit(self, node): return [node]

  @v.when(Expression)
  def visit(self, node): return node


"""
Replacing holes with solutions
"""
class Replacer(object):

  def __init__(self, output_path, holes):
    self._output = output_path
    self._holes = holes

    self._sol = {} # { v : n }

    ## hole assignments for roles
    ## glblInit_fid__cid_????,StmtAssign,accessor_???? = n
    names = map(op.attrgetter("name"), self._holes)
    regex_role = r"({})__(\S+)_\S+ = (\d+)$".format('|'.join(names))

    # interpret the synthesis result
    with open(self._output, 'r') as f:
      for line in f:
        line = line.strip()
        try:
          items = line.split(',')
          func, kind, msg = items[0], items[1], ','.join(items[2:])
          m = re.match(regex_role, msg)
          if m:
            fid, cid, n = m.group(1), m.group(2), m.group(3)
            for hole in self._holes:
              if hole.name == fid and cid in repr(hole.clazz):
                logging.debug("solution: {} = {}".format(repr(hole), n))
                self._sol[hole] = n
        except IndexError: # not a line generated by custom codegen
          pass # if "Total time" in line: logging.info(line)

  @v.on("node")
  def visit(self, node):
    """
    This is the generic method to initialize the dynamic dispatcher
    """

  @v.when(Program)
  def visit(self, node): pass

  @v.when(Clazz)
  def visit(self, node): pass

  @v.when(Field)
  def visit(self, node):
    if node in self._holes:
      cname = node.clazz.name
      fname = node.name
      if node in self._sol:
        n = self._sol[node]
        node.init = to_expression(unicode(n))
        logging.debug("replaced: {}.{} = {}".format(cname, fname, n))
      else: # solution not found?
        logging.error("unresolved: {}.{}".format(cname, fname))

  @v.when(Method)
  def visit(self, node): pass

  @v.when(Statement)
  def visit(self, node): return [node]

  @v.when(Expression)
  def visit(self, node): return node


"""
Replacing collections of interface types with actual classes
"""
class Collection(object):

  __impl = { \
    C.J.MAP: C.J.TMAP, \
    C.J.LST: C.J.LNK, \
    C.J.LNK: C.J.LNK, \
    C.J.STK: C.J.STK, \
    C.J.QUE: C.J.DEQ }

  # autobox type parameters and/or replace interfaces with implementing classes
  # e.g., List<T> x = new List<T>(); => new ArrayList<T>();
  # this should *not* be recursive, e.g., Map<K, List<V>> => TreeMap<K, List<V>>
  @staticmethod
  def repl_itf(tname, init=True):
    if not util.is_collection(tname): return tname
    _ids = util.of_collection(tname)
    ids = map(util.autoboxing, _ids)
    collection = ids[0]
    if init: collection = Collection.__impl[collection]
    generics = ids[1:] # don't be recursive, like map(repl_itf, ids[1:])
    return u"{}<{}>".format(collection, ','.join(generics))


  @v.on("node")
  def visit(self, node):
    """
    This is the generic method to initialize the dynamic dispatcher
    """

  @v.when(Program)
  def visit(self, node): pass

  @v.when(Clazz)
  def visit(self, node): pass

  @v.when(Field)
  def visit(self, node):
    node.typ = Collection.repl_itf(node.typ, False)

  @v.when(Method)
  def visit(self, node): pass

  @v.when(Statement)
  def visit(self, node): return [node]

  @v.when(Expression)
  def visit(self, node):
    if node.kind == C.E.NEW:
      if node.e.kind == C.E.CALL:
        mid = unicode(node.e.f)
        if util.is_class_name(mid):
          node.e.f.id = Collection.repl_itf(mid)

    return node


# white-list checking
@takes(unicode, list_of(unicode))
@returns(bool)
def check_pkg(pname, lst):
  return util.exists(lambda pkg: pname.startswith(pkg), lst)


# trimming
@takes(Program)
@returns(nothing)
def trim(pgr):
  pkgs_java = [u"java.lang", u"java.util"]

  for cls in pgr.classes[:]:
    if cls.pkg and check_pkg(cls.pkg, pkgs_java):
      logging.debug("trimming: {}".format(cls.name))
      pgr.classes.remove(cls)


# build folders for the given package name
# e.g., for x.y, generate x and then y under x if not exist
@takes(str, unicode)
@returns(nothing)
def build_pkg_folders(java_dir, pkg):
  p = java_dir
  for elt in pkg.split('.'):
    p = os.path.join(p, elt)
    if not os.path.exists(p):
      os.makedirs(p)


# find appropriate import statements, generally
@takes(str, unicode, list_of(unicode))
@returns(list_of(unicode))
def find_imports(body, pkg, clss):
  def appear(cls): return cls in body
  return [ '.'.join([pkg, cls]) for cls in filter(appear, clss) ]


@takes(str, Program, str, str)
@returns(nothing)
def to_java(java_dir, pgr, output_path):
  ## clean up result directory
  if os.path.isdir(java_dir): util.clean_dir(java_dir)
  else: os.makedirs(java_dir)

  ## find holes
  hfinder = HFinder()
  pgr.accept(hfinder)
  holes = hfinder.holes

  ## replace holes with resolved answers
  replacer = Replacer(output_path, holes)
  pgr.accept(replacer)

  ## replace collections of interface types with actual classes, if any
  collection_replacer = Collection()
  pgr.accept(collection_replacer)

  ## trimming of the program
  trim(pgr)

  dump(java_dir, pgr, "decoding")


# dump out the given program, which might be
# either an intermediate AST or the final result
@takes(str, Program, optional(str))
@returns(nothing)
def dump(dst_dir, pgr, msg=None):
  def write_imports(imports):
    def write_import(i): return "import {};".format(i)
    return '\n'.join(map(write_import, imports)) + '\n'

  ios = [u"File", u"InputStream", u"FileInputStream", \
      u"InputStreamReader", u"BufferedReader", \
      u"FileNotFoundException", u"IOException"]

  decl_pkgs = set([])
  for cls in pgr.classes:
    if not cls.pkg: continue
    decl_pkgs.add(cls.pkg)

  for cls in pgr.classes:
    ## generate folders according to package hierarchy
    fname = cls.name + ".java"
    if cls.pkg:
      build_pkg_folders(dst_dir, cls.pkg)
      folders = [dst_dir] + cls.pkg.split('.') + [fname]
      java_path = os.path.join(*folders)
    else: java_path = os.path.join(dst_dir, fname)

    ## figure out import statements
    imports = []

    cls_body = str(cls)
    imports.extend(find_imports(cls_body, u"java.util", C.collections))
    imports.extend(find_imports(cls_body, u"java.io", ios))

    for pkg in decl_pkgs:
      if not cls.pkg or cls.pkg != pkg: imports.append(pkg+".*")

    ## generate Java files
    with open(java_path, 'w') as f:
      if cls.pkg: f.write(C.T.PKG + ' ' + cls.pkg + ";\n")
      f.write(write_imports(imports))
      f.write(cls_body)
      if msg: logging.info(" ".join([msg, f.name]))
      else: logging.debug("dumping " + f.name)

