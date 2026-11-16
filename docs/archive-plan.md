# Curated Drive archive

Owner selected core relevant datasets plus our two checkpoints on 2026-11-16. The source manifest is `configs/core-archive.json`. This is a prepared archive selection, not a claim that Drive contains its payloads.

## Selected pack

| Source | Selection | Bytes |
| --- | --- | ---: |
| CCORE Qwen3.5-4B GLB | Original checkpoint/companions, already verified locally | 17,510,218,308 |
| Official Qwen3.5-4B | Original checkpoint/companions, already verified locally | 9,342,905,899 |
| CCORE ThreeJS-3D-GLB-Assets | Complete pinned dataset, 54 files | 1,030,742,497 |
| BlendNet | Complete pinned dataset, 3 files | 22,283,412 |
| Bioinspired3D | Complete pinned dataset, 3 files | 12,429,105 |
| Total | 5 sources, 88 selected files | 27,918,579,221 |

Dataset sizes are summed selected file metadata, not Hub used-storage estimates. Source IDs, immutable revisions, source rights and per-file metadata are in the manifest. The datasets have not been downloaded by this archive task. Both model copies already exist on Studio; duplicating their transfer should be avoided when off-stream upload is practical.

## Searchable secondary index

| Source | Retain for discovery | Why not bulk mirror now |
| --- | --- | --- |
| `PGCRYPT/OpenBlender_Train` | Docs/API Q&A, Apache-2.0 declaration | Lower priority than executable asset examples |
| `ccore/ThreeJS-3D-Scenes` | Older scenes dataset, existing verified copy | Secondary to the GLB specialization |
| `ccore/Qwen3.5-4B-3D-Coder` | Earlier model | Avoid redundant checkpoint variants |
| `YipengGao/3DCodeBench` | Procedural Blender data | Full Hub storage ~283 GB; choose code subsets later |
| `3dcodeverse/3dcodeverse-2m` | Mixed corpus; existing small research selection | Full archive ~1.25 TB and noncommercial/source-specific terms |
| `3dcodeverse/3dcodeverse-qwen3.8-27b-lora` | Larger research comparison | Outside chosen 4B path, noncommercial, requires 27B base |
| `nolabs/deepfabric-blender-mcp` | Synthetic format reference | License unresolved; execution compatibility unverified |
| `noah-thing/neyra-protocol` | Pinned tooling source | Small code reference; not training data or weights |

## Transfer method and stream protection

While the owner streams, no local model inference, training or other new heavy GPU work. A research subagent on the Studio is not separate compute. Large uploads can also compete with stream uplink, so do not start an uncontrolled Studio-to-Drive bulk transfer during the stream.

The connected Drive uploader accepts local file references; no direct Hub-to-Drive server-side import tool has been verified. Off-machine transfer requires an authenticated remote worker (for example a suitable cloud notebook), while off-stream upload can reuse existing Studio copies. Do not claim a remote worker is connected, run paid compute, copy credentials between machines or upload through the Studio while claiming it bypasses the Studio.

Before transfer: select the owner's intended connected Drive account and folder, verify available quota, preserve sharing, inventory the selected bytes, record notices and use resumable transfers. After transfer: verify sizes/checksums and retain a manifest of Drive file IDs. A folder/index alone is not a payload archive. No sharing expansion is authorized.

Resource compilation is productive as a curated, reproducible cache. Unrestricted mirroring mostly adds duplicate model variants, overlapping data and irrelevant assets. Downloaded data still needs quality, rights, compatibility and overlap filtering before training.
