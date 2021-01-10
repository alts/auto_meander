## auto_meander

Anni Albers's *Meander* series is 1) beautiful and 2) formulaic. For these reasons, I think emulating its rules in a generative art program is a good idea.

Examples:

* [*Blue Meander*](http://art.famsf.org/anni-albers/blue-meander-1996743)
* [*Yellow Meander*](http://art.famsf.org/anni-albers/yellow-meander-1996742)
* [*Red Meander II*](http://art.famsf.org/anni-albers/red-meander-ii-1996745)

Running the code requires [Poetry](https://python-poetry.org/) and Python 3.8+

```
poetry install
poetry run ./auto_meander.py
```

This will generate PNG and SVG image files in the `out` directory.
