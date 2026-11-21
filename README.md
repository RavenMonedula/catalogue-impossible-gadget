# The Forever Kettle

A studio catalogue photograph of an impossible gadget: an electric
kettle plugged into **itself**. Its power cord loops from the base
back into a socket on its own front, and its red "on" light glows —
a kettle that powers itself forever. One accessory only: a single
teacup with a wisp of steam beside it.

## What the program does

`main.py` draws the catalogue photo with PIL only (no network, no
randomness, fully deterministic) and writes it to
`/output/entry.png` (1024×1024 PNG):

- clean light-grey-to-white vertical gradient backdrop, soft drop
  shadow and a faint floor reflection under the product
- stainless-steel kettle body built from brushed horizontal gradient
  bands with a bright highlight stripe, dark lid, knob, spout and
  handle, glowing red power light, and a tiny `PERPETUA` brand mark
- black power cord (smooth Catmull-Rom spline) looping out of the
  base and back into the socket on the kettle's own front
- one white teacup on a saucer with two wisps of steam

No text explains the joke anywhere; the only text is the product's
own brand mark.

## How to run it

```bash
python3 main.py
# writes /output/entry.png
```

Requires Python 3.13 and Pillow (`pip install pillow`).
