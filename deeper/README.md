# Deeperfont
*[Website](http://nbviewer.jupyter.org/github/terryspitz/ipython_notebooks/blob/master/deeper/deeperfont.ipynb)*

Deeperfont is a Neural Network attempt at the 'Font Problem' - that is, how to capture the essence of a font in such a way as to generalise to unseen glyphs and to allow interpolation between different fonts.  This problem was noted as early as 1979 when Donald Knuth wrote the first version of [MetaFont](https://en.wikipedia.org/wiki/Metafont).

For this network initial research suggested the use of [Keras](https://keras.io/) and [Tensorflow](https://www.tensorflow.org/) as best practise for both getting started and long-term research.  

As output the network will generate a set of [glyph outlines](https://en.wikipedia.org/wiki/Glyph).  The encoding of outputs has been considered in a number of ways: 
* raw (x,y) coordinates, for example as expressed in the [TrueType](https://en.wikipedia.org/wiki/TrueType) font file
* incremental coordinate changes (dx,dy)
* a conversion of these outlines to (angle, distance) pairs for each line as in [Turtle graphics](https://en.wikipedia.org/wiki/Turtle_graphics) (best known for its  use in [Logo](https://en.wikipedia.org/wiki/Logo_(programming_language).)  We do not currently model the bezier curves used in the original glyphs; a future enhancement could use a rendered glyph as the source of font coordinates to train against.

Considering the [loss](https://en.wikipedia.org/wiki/Loss_function) or evaluation function we note that the exact sequence of points in the glyph can be varied while generating identical rendered output, for example a line segment can be split into a number of smaller colinear segments.  The network should be free to express its results in any equivalent way.  The evaluation function is therefore required to compare rendered output.  We build an evaluation function in pure Tensorflow using a [scanline algorithm](https://en.wikipedia.org/wiki/Scanline_rendering) to generate a tensor containing the x coordinates of the outline for a set of equi-spaced y line. We use a final lambda layer calling this function to render the outlines.  The predicted and true outlines are then compared by calculating the difference in these coordinates.

We would like access to the trained glyph outlines for which we use a named layer in keras.  Since the loss function using x coordinates is unstable and often NaNs, we plan to train on both the penultimate outlines layer with small weight as well as the final x coordinates, using the [keras functional model API with multiple outputs](https://keras.io/getting-started/functional-api-guide/#multi-input-and-multi-output-models).

As input we provide a [one-hot](https://en.wikipedia.org/wiki/One-hot) vector representing the individual glyphs to render.  In a future enhancement where we train against multiple fonts, this input could also include a feature for font family and font classifications such as serif/sans-serif/script/etc which would allow interpolation over these dimensions.

See also:
* [MetaFont](https://en.wikipedia.org/wiki/Metafont)
* [Metaflop - interactive MetaFont](http://www.metaflop.com/modulator)
* [deepfont](https://erikbern.com/2016/01/21/analyzing-50k-fonts-using-deep-neural-networks.html)
* https://arxiv.org/abs/1507.03196
* https://pypi.python.org/pypi/FontTools
