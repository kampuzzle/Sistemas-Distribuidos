# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: mineracao.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0fmineracao.proto\x12\x04main\"\x1b\n\tintResult\x12\x0e\n\x06result\x18\x01 \x01(\x05\"A\n\x0cstructResult\x12\x0e\n\x06status\x18\x01 \x01(\x05\x12\x0e\n\x06result\x18\x02 \x01(\t\x12\x11\n\tchallenge\x18\x03 \x01(\x05\"&\n\rtransactionId\x12\x15\n\rtransactionId\x18\x01 \x01(\x05\"F\n\rchallengeArgs\x12\x15\n\rtransactionId\x18\x01 \x01(\x05\x12\x10\n\x08\x63lientId\x18\x02 \x01(\x05\x12\x0c\n\x04seed\x18\x03 \x01(\x05\"\x06\n\x04void2\xce\x02\n\x03\x61pi\x12/\n\x10getTransactionId\x12\n.main.void\x1a\x0f.main.intResult\x12\x34\n\x0cgetChallenge\x12\x13.main.transactionId\x1a\x0f.main.intResult\x12<\n\x14getTransactionStatus\x12\x13.main.transactionId\x1a\x0f.main.intResult\x12\x37\n\x0fsubmitChallenge\x12\x13.main.challengeArgs\x1a\x0f.main.intResult\x12\x31\n\tgetWinner\x12\x13.main.transactionId\x1a\x0f.main.intResult\x12\x36\n\x0bgetSolution\x12\x13.main.transactionId\x1a\x12.main.structResultb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'mineracao_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _INTRESULT._serialized_start=25
  _INTRESULT._serialized_end=52
  _STRUCTRESULT._serialized_start=54
  _STRUCTRESULT._serialized_end=119
  _TRANSACTIONID._serialized_start=121
  _TRANSACTIONID._serialized_end=159
  _CHALLENGEARGS._serialized_start=161
  _CHALLENGEARGS._serialized_end=231
  _VOID._serialized_start=233
  _VOID._serialized_end=239
  _API._serialized_start=242
  _API._serialized_end=576
# @@protoc_insertion_point(module_scope)
