# AS3600-Concrete-Beam-Charts
 Generator for concrete beam charts as well as predefined charts

[![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/JesseBonanno/IndeterminateBeam/blob/main/docs/examples/simple_demo.ipynb)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/JesseBonanno/IndeterminateBeam/main?filepath=docs%2Fexamples%2Fsimple_demo.ipynb)

Fix links

## Project Purpose

Help with quick sanity checks for bending and shear capacity for concrete beams.

Not to provide a comprehensive and complete design but rather to guide in the range of values to expect.

## Functionality and Usage

Refer to [previously created charts](www.google.com) or create your own chart using the online jupyter notebook.

Default values for the concrete beam initialization are provided below.

Parameters
----------
D : int, optional
    Depth of the concrete beam (mm), by default 200
b : int, optional
    width of the concrete beam (mm), by default 1000
cover : int, optional
    steel cover (mm), by default 20
fc : int, optional
    concrete strength (MPa), by default 32
diameter : float, optional
    diameter of steel reinforcement, by default 7.6
spacing : int, optional
    spacing of steel reinforcement, by default 100
ductility : str, optional
    ductility class of steel, by default 'L'
fsy : int, optional
    yield strength of steel, by default 500
d : int or None, optional
    depth to center or reinforcement is typically calculated
    by using the beam Depth, cover and reinforcment bar diameter,
    but the value can be overrided by specifying an int here,
    by default None

## Contributing

The guidelines for contributing are specified [here](https://github.com/JesseBonanno/IndeterminateBeam/blob/main/CONTRIBUTING.md).

## Support

The guidelines for support are specified [here](https://github.com/JesseBonanno/IndeterminateBeam/blob/main/SUPPORT.md).

## License

[![License](https://img.shields.io/badge/license-MIT-lightgreen.svg)](https://github.com/JesseBonanno/IndeterminateBeam/blob/main/LICENSE.txt)

Copyright (c) 2020, Jesse Bonanno