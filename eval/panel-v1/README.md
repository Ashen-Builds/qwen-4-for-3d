# Image-to-asset scoring panel v1

Thirty reference images scored with three tries each (seeds 42, 43, 44) on two models. `manifest.json` lists every image with its kind, category and source.

- `c01` to `c05`: concept-art images made with Codex image generation on November 17, 2026 for this project.
- `h*`: 25 renders from the validation split of `ccore/ThreeJS-3D-GLB-Assets` (MIT as declared on its dataset card), cropped to the subject and resized to 768 px. These 25 were held out of all training. They are in the dataset's own low-poly render style, so they measure the style our model trained on, not the concept art users will bring.

Run with `scripts/run_panel.py`, score with `scripts/score_panel.py` and `scripts/score_likeness.py`. A try counts as working when the program runs, its own Export button produces a file, and the Khronos validator reports zero errors.

Known gap: the panel is short on concept-art images and on characters. More concept images are the next addition.
