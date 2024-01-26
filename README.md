# dcm
dynamic competence map - a python based visualization tool
for displaying the development of skills/competences in the context of
defined competence aspects.

[![Join the discussion at https://github.com/WolfgangFahl/dcm/discussions](https://img.shields.io/github/discussions/WolfgangFahl/dcm)](https://github.com/WolfgangFahl/dcm/discussions)
[![pypi](https://img.shields.io/pypi/pyversions/dynamic_competence_map)](https://pypi.org/project/dynamic-competence-map/)
[![Github Actions Build](https://github.com/WolfgangFahl/dcm/actions/workflows/build.yml/badge.svg)](https://github.com/WolfgangFahl/dcm/actions/workflows/build.yml)
[![PyPI Status](https://img.shields.io/pypi/v/dynamic_competence_map.svg)](https://pypi.python.org/pypi/dynamic-competence-map/)
[![GitHub issues](https://img.shields.io/github/issues/WolfgangFahl/dcm.svg)](https://github.com/WolfgangFahl/dcm/issues)
[![GitHub issues](https://img.shields.io/github/issues-closed/WolfgangFahl/dcm.svg)](https://github.com/WolfgangFahl/dcm/issues/?q=is%3Aissue+is%3Aclosed)
[![GitHub](https://img.shields.io/github/license/WolfgangFahl/dcm)](https://www.apache.org/licenses/LICENSE-2.0)

## Demo
* [demo](http://dcm.bitplan.com)

## Motivation ##

The **Dynamic Competence Map** (DCM) is an open-source tool 
designed to support the visualization and analysis of 
personal skills for a given learning context.

The learning context is described in an hierachical way as a multi level CompetenceTree. 
The level names may be adapted to your needs.

## Motivation

The **Dynamic Competence Map** (DCM) is an open-source tool 
designed for mapping and assessing skills in educational and 
professional settings. It uses a hierarchical structure, 
known as the Competence Tree, to organize and display 
skills and competencies.

DCM offers a RESTful API for integration with other 
systems and accepts input in YAML or JSON formats. This 
allows for easy incorporation of the Competence Tree and 
learner achievements, which can also be expressed as 
xAPI statements.

Output from DCM includes a configurable Skillschart, 
presented as SVG for visualization or available through 
an interactive web service. This functionality supports 
a range of uses, from academic research to practical 
applications in skill development and competency management.

## Features

1. **Competence Tree Hierarchy:** DCM is built around a multi-level hierarchy known as the Competence Tree. This hierarchical structure allows for the detailed mapping of skills and competencies, making it suitable for representing complex relationships between various competencies.

2. **Open-Source Python Project:** DCM is implemented as an open-source project in Python, ensuring transparency and flexibility for developers and users.

3. **RESTful API Integration:** DCM provides a RESTful API that allows for seamless integration with other systems. This API enables users to interact programmatically with DCM, making it a versatile tool for skill visualization and assessment.

4. **Input Data Flexibility:** Users can supply the Competence Tree in either YAML or JSON format, providing flexibility in data input. This feature ensures that users can use their preferred data format when working with DCM.

5. **Learner Achievements:** DCM supports the inclusion of Learners' Achievements, which can be supplied as JSON or xAPI statements. This feature allows for the assessment of learners' skills and competencies within the DCM framework.

6. **User-Friendly Interface:** To enhance the user interface and provide a user-friendly experience, DCM utilizes technologies like NiceGUI. This ensures that users can easily interact with the resulting Skillschart and customize their experience.

7. **SVG Rendering:** DCM supports the rendering of SVG images, providing visual representations of skills and competencies. Users can generate SVG images to visualize competency data effectively.

8. **Study Plan Visualization:** DCM includes specific elements for visualizing study plans, study areas, modules, and module elements. This feature is designed to cater to educational contexts and helps learners understand their study paths.

9. **Color Coding and Icons:** DCM provides color coding and icons for Competence Levels, making it easier to distinguish between different levels of competency. This visual representation aids in skill assessment and understanding.

10. **Comprehensive Documentation:** The project includes comprehensive documentation and test cases, ensuring that developers and users have access to clear instructions and examples for working with DCM.

## Documentation
* [Wiki](http://wiki.bitplan.com/index.php/dcm)

## API
* [API documentation](http://dcm.bitplan.com/docs)

### Model
![Class Diagram](http://www.plantuml.com/plantuml/proxy?src=https://raw.githubusercontent.com/WolfgangFahl/dcm/main/dcm.puml?fmt=svg&version=7)

## Authors
* [Wolfgang Fahl](http://www.bitplan.com/Wolfgang_Fahl)

