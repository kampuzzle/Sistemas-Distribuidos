# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: federado.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0e\x66\x65\x64\x65rado.proto\x12\x04main\"R\n\x15RegisterClientRequest\x12\x11\n\tclient_id\x18\x01 \x01(\t\x12\x11\n\tclient_ip\x18\x02 \x01(\t\x12\x13\n\x0b\x63lient_port\x18\x03 \x01(\x05\"J\n\x16RegisterClientResponse\x12\x19\n\x11\x63onfirmation_code\x18\x01 \x01(\x05\x12\x15\n\rcurrent_round\x18\x02 \x01(\x05\"E\n\x14StartTrainingRequest\x12\x15\n\rcurrent_round\x18\x01 \x01(\x05\x12\x16\n\x0eglobal_weights\x18\x02 \x03(\x02\"E\n\x15StartTrainingResponse\x12\x15\n\rlocal_weights\x18\x01 \x03(\x02\x12\x15\n\rlocal_samples\x18\x02 \x01(\x05\".\n\x14\x45valuateModelRequest\x12\x16\n\x0eglobal_weights\x18\x01 \x03(\x02\")\n\x15\x45valuateModelResponse\x12\x10\n\x08\x61\x63\x63uracy\x18\x01 \x01(\x02\x32\xfa\x01\n\x11\x46\x65\x64\x65ratedLearning\x12M\n\x0eRegisterClient\x12\x1b.main.RegisterClientRequest\x1a\x1c.main.RegisterClientResponse\"\x00\x12J\n\rStartTraining\x12\x1a.main.StartTrainingRequest\x1a\x1b.main.StartTrainingResponse\"\x00\x12J\n\rEvaluateModel\x12\x1a.main.EvaluateModelRequest\x1a\x1b.main.EvaluateModelResponse\"\x00\x32\xa8\x01\n\x0e\x43lientLearning\x12J\n\rStartTraining\x12\x1a.main.StartTrainingRequest\x1a\x1b.main.StartTrainingResponse\"\x00\x12J\n\rEvaluateModel\x12\x1a.main.EvaluateModelRequest\x1a\x1b.main.EvaluateModelResponse\"\x00\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'federado_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _REGISTERCLIENTREQUEST._serialized_start=24
  _REGISTERCLIENTREQUEST._serialized_end=106
  _REGISTERCLIENTRESPONSE._serialized_start=108
  _REGISTERCLIENTRESPONSE._serialized_end=182
  _STARTTRAININGREQUEST._serialized_start=184
  _STARTTRAININGREQUEST._serialized_end=253
  _STARTTRAININGRESPONSE._serialized_start=255
  _STARTTRAININGRESPONSE._serialized_end=324
  _EVALUATEMODELREQUEST._serialized_start=326
  _EVALUATEMODELREQUEST._serialized_end=372
  _EVALUATEMODELRESPONSE._serialized_start=374
  _EVALUATEMODELRESPONSE._serialized_end=415
  _FEDERATEDLEARNING._serialized_start=418
  _FEDERATEDLEARNING._serialized_end=668
  _CLIENTLEARNING._serialized_start=671
  _CLIENTLEARNING._serialized_end=839
# @@protoc_insertion_point(module_scope)
