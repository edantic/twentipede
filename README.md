# twentipede

Recreating an arcade classic with the Amazon Q CLI.
<br>
<br>

## Requirements

To run this game, you'll need the following:

- python 3.7 or higher
- pygame 2.0 or higher

Pygame is currently the only python dependency and can be installed by itself
(hopefully into a virtualenv you've already created for yourself because you're
cool like that). However, for the most up-to-date requirements, it's usually
safer to just install from the project requirements file with:

```
pip install -r src/twentipede/requirements.txt
```
<br>
<br>

## Running the Game

To play twentipede run the following:

```
python src/twentipede/centipede_roguelike.py
```

Note that on some systems, you may need to replace `python` with `python3`.

The `src/twentipede/README.md` file documents game features and controls at
length, but really, just kill as many bugs as you can.
