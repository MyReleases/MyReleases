# Rebuilding the card

The profile card is generated, not drawn by hand.

    python scripts/build_readme.py

This rewrites `README.md` and the `assets/readme*.svg` files.

- The text, its timing and the layout live at the top of `build_readme.py`.
- The drawing comes from `assets/dots-source.txt` (braille dot art).
- The card is cut into slices so that the e-mail and the X handle can be real links.
- `--inset` builds the smaller drawing with margins around it.
