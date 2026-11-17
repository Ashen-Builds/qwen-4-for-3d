# Common GLB review harness

Same shared lighting, exposure, normalized framing, pixel ratio1 and60fps cap for every panel. Source-based adapter model generation is unaffected. Animation starts at the same logical scene time after asynchronous GLB loads. Buttons0/2/4seconds pause and seek every loaded mixer together for repeatable screenshots. No geometry/material/motion curves are authored or changed by this harness.

Place this bundle under a dedicated localhost artifact directory with control/asset.glb and ours/asset.glb, per-arm result.json containing explicit mode/assistance labels, and comparison-report.json. Three.jsr160 is served from /vendor/three. Missing/failed exports stay visible; never substitute repaired diagnostics without labels. Use a distinct label when showing historical repairedCCORE reference beside a raw candidate; that picture is not a matched raw-mode test.

This version has static syntax verification only until the next actual GLB browser review. The screenshot receipt must record the actual asset hashes, camera/view choice and selected time; a viewer file by itself does not establish rendered quality.
