"""
Created on 2023-11-06

@author: wf
"""
from dataclasses import dataclass

import dcm


@dataclass
class Version:
    """
    Version handling for nicepdf
    """

    name = "dcm"
    version = dcm.__version__
    date = "2023-11-06"
    updated = "2024-01-28"
    description = "python based visualization of dynamic competence maps"

    authors = "Wolfgang Fahl"

    doc_url = "https://wiki.bitplan.com/index.php/dcm"
    chat_url = "https://github.com/WolfgangFahl/dcm/discussions"
    cm_url = "https://github.com/WolfgangFahl/dcm"

    license = f"""Copyright 2023 contributors. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied."""

    longDescription = f"""{name} version {version}
{description}

  Created by {authors} on {date} last updated {updated}"""
