# Auto generated from dcm_schema.yaml by pythongen.py version: 0.9.0
# Generation date: 2024-01-20T16:57:40
# Schema: learner-schema
#
# id: https://dcm.org/learner-schema
# description: Schema for representing learners and their achievements.
# license: https://creativecommons.org/publicdomain/zero/1.0/

import dataclasses
import sys
import re
from jsonasobj2 import JsonObj, as_dict
from typing import Optional, List, Union, Dict, ClassVar, Any
from dataclasses import dataclass
from linkml_runtime.linkml_model.meta import EnumDefinition, PermissibleValue, PvFormulaOptions

from linkml_runtime.utils.slot import Slot
from linkml_runtime.utils.metamodelcore import empty_list, empty_dict, bnode
from linkml_runtime.utils.yamlutils import YAMLRoot, extended_str, extended_float, extended_int
from linkml_runtime.utils.dataclass_extensions_376 import dataclasses_init_fn_with_kwargs
from linkml_runtime.utils.formatutils import camelcase, underscore, sfx
from linkml_runtime.utils.enumerations import EnumDefinitionImpl
from rdflib import Namespace, URIRef
from linkml_runtime.utils.curienamespace import CurieNamespace
from linkml_runtime.linkml_model.types import Float, Integer, String

metamodel_version = "1.7.0"
version = None

# Overwrite dataclasses _init_fn to add **kwargs in __init__
dataclasses._init_fn = dataclasses_init_fn_with_kwargs

# Namespaces
DCM = CurieNamespace('dcm', 'https://dcm.org/learner-schema/')
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
DEFAULT_ = DCM


# Types

# Class references



@dataclass
class Learner(YAMLRoot):
    """
    An individual learner with a unique identifier and a list of achievements.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DCM.Learner
    class_class_curie: ClassVar[str] = "dcm:Learner"
    class_name: ClassVar[str] = "Learner"
    class_model_uri: ClassVar[URIRef] = DCM.Learner

    learner_id: Optional[str] = None
    achievements: Optional[Union[Union[dict, "Achievement"], List[Union[dict, "Achievement"]]]] = empty_list()

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.learner_id is not None and not isinstance(self.learner_id, str):
            self.learner_id = str(self.learner_id)

        if not isinstance(self.achievements, list):
            self.achievements = [self.achievements] if self.achievements is not None else []
        self.achievements = [v if isinstance(v, Achievement) else Achievement(**as_dict(v)) for v in self.achievements]

        super().__post_init__(**kwargs)


@dataclass
class Achievement(YAMLRoot):
    """
    A record of an achievement attained by a learner.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = DCM.Achievement
    class_class_curie: ClassVar[str] = "dcm:Achievement"
    class_name: ClassVar[str] = "Achievement"
    class_model_uri: ClassVar[URIRef] = DCM.Achievement

    path: Optional[str] = None
    level: Optional[int] = None
    score: Optional[float] = None
    date_assessed_iso: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.path is not None and not isinstance(self.path, str):
            self.path = str(self.path)

        if self.level is not None and not isinstance(self.level, int):
            self.level = int(self.level)

        if self.score is not None and not isinstance(self.score, float):
            self.score = float(self.score)

        if self.date_assessed_iso is not None and not isinstance(self.date_assessed_iso, str):
            self.date_assessed_iso = str(self.date_assessed_iso)

        super().__post_init__(**kwargs)


# Enumerations


# Slots
class slots:
    pass

slots.learner_id = Slot(uri=DCM.learner_id, name="learner_id", curie=DCM.curie('learner_id'),
                   model_uri=DCM.learner_id, domain=None, range=Optional[str])

slots.achievements = Slot(uri=DCM.achievements, name="achievements", curie=DCM.curie('achievements'),
                   model_uri=DCM.achievements, domain=None, range=Optional[Union[Union[dict, Achievement], List[Union[dict, Achievement]]]])

slots.path = Slot(uri=DCM.path, name="path", curie=DCM.curie('path'),
                   model_uri=DCM.path, domain=None, range=Optional[str])

slots.level = Slot(uri=DCM.level, name="level", curie=DCM.curie('level'),
                   model_uri=DCM.level, domain=None, range=Optional[int])

slots.score = Slot(uri=DCM.score, name="score", curie=DCM.curie('score'),
                   model_uri=DCM.score, domain=None, range=Optional[float])

slots.date_assessed_iso = Slot(uri=DCM.date_assessed_iso, name="date_assessed_iso", curie=DCM.curie('date_assessed_iso'),
                   model_uri=DCM.date_assessed_iso, domain=None, range=Optional[str])
