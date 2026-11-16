# Replies summary

A summary of the 111 replies to [@ashen_one's post](https://x.com/ashen_one/status/2122000927418699866), pulled 2026-11-16. They're grouped by theme with each point credited to its author's handle; likes are in parentheses where it helps. Every reply is quoted in full in [`raw-replies.md`](raw-replies.md).

> **How to read this.** Plain bullets are what repliers said. Anything marked **Our notes** we checked ourselves against docs or Hugging Face on 2026-11-16, and it isn't from the thread.

---

## 1. The headline: training is easy, data is the project

This was the strongest consensus in the thread.

- **[@johnroodepic](https://x.com/johnroodepic/status/2122008709681565717)** (80 likes, the top reply): "the training run is the cheap part. what you actually need is a few hundred successful blender tool-call traces to train on, and nobody publishes those. run the mcp off a small model with a tight schema and two worked examples, log every call that worked, and fine-tune on your own log later. **that dataset is the whole project.**"
- **[@yasu0x1](https://x.com/yasu0x1/status/2122001957535834134)**: "the training part is easy, finding good blender animation data to train on is the hard bit."
- **[@csgriff_](https://x.com/csgriff_/status/2122290083952796076)**: "Effort: **70% training data, 5% tun config, 25% evals**. Start with QLORA, Unsloth is simple. ~$100 per run on AWS 3-4 days."
- **[@tensorfiend](https://x.com/tensorfiend/status/2122216307634708948)**: good data costs more time and money than the fine-tune, and mid or poor data won't make the model any good.
- **[@LottoLabs](https://x.com/LottoLabs/status/2122140085831475671)**: "It's all data bro that's the first lesson."
- **[@LightyLightyHi](https://x.com/LightyLightyHi/status/2122208029613724029)**: to beat stock Qwen 4 at your task you need data better than Alibaba's on that specific task, and "a couple hundred examples might do it."
- The same point from [@mikeytag](https://x.com/mikeytag/status/2122303062044004503), [@viiskb](https://x.com/viiskb/status/2122215795023282584), [@iam_Dyeus](https://x.com/iam_Dyeus/status/2122222283930664971), [@MikeBrave_Maker](https://x.com/MikeBrave_Maker/status/2122140015455244389), [@LHershberger06](https://x.com/LHershberger06/status/2122293082276479069), [@BarryDeenTech](https://x.com/BarryDeenTech/status/2122184525660799284) and [@jobelshaji95](https://x.com/jobelshaji95/status/2122189061968269813) ("Basically a bunch of clean blender traces").

**Takeaway:** start collecting data now. It doesn't depend on Qwen 4, and it's what will make the model good.

## 2. Method: LoRA or QLoRA, not full fine-tuning or training from scratch

- **[@naveen_saradhi_](https://x.com/naveen_saradhi_/status/2122001914938482855)** (39 likes): "Start with LoRA/QLoRA fine-tuning. You don't need to train from scratch. Learn the basics with a smaller model first, then experiment with Blender workflows." Ashen replied "noted."
- [@handeh777](https://x.com/handeh777/status/2122001480244662674), [@fufeng1688](https://x.com/fufeng1688/status/2122118879438918055), [@LHershberger06](https://x.com/LHershberger06/status/2122293082276479069), [@Okada_DeFi0x](https://x.com/Okada_DeFi0x/status/2122038297484828968) and [@eclecticleaps](https://x.com/eclecticleaps/status/2122211553240097125) all said LoRA, not full fine-tuning.
- [@aphiticus1](https://x.com/aphiticus1/status/2122178727996190889): it's "a couple of epochs" compared with training from scratch, and anywhere from hours to weeks depending on model size and GPU.
- **aLoRA** (activated LoRA): [@trydotworks](https://x.com/trydotworks/status/2122149567454126288) and [@Abomination81](https://x.com/Abomination81/status/2122177088279240991). @Abomination81 also suggested an "obliterated" (abliterated) model and neuron tweaking. That isn't needed for this goal.
- [@hatsunama](https://x.com/hatsunama/status/2122183882426433623) asked whether the goal is "neuron editing or just simple post training." It's simple post-training.

## 3. Tools people recommended

| Tool | Who recommended it | Notes |
| --- | --- | --- |
| **Unsloth** (most mentioned) | [@tymofii](https://x.com/tymofii/status/2122008706711957634), [@heyartzy](https://x.com/heyartzy/status/2122010262068752767), [@AetheriaFeng](https://x.com/AetheriaFeng/status/2122025437429903641), [@eyoussef](https://x.com/eyoussef/status/2122052746258100564), [@jobelshaji95](https://x.com/jobelshaji95/status/2122189061968269813), [@csgriff_](https://x.com/csgriff_/status/2122290083952796076), [@OliNorwell](https://x.com/OliNorwell/status/2122276546337718605), [@navin_hill](https://x.com/navin_hill/status/2122203456119197708), [@Reveur_7](https://x.com/Reveur_7/status/2122250064609607905) | @eyoussef: free Colab notebooks, "including one for tool calling. You could run the whole loop on a current small Qwen now, then swap in Qwen 4 once it's supported." Links: [fine-tuning guide](https://unsloth.ai/docs/get-started/fine-tuning-llms-guide), [Qwen3.8 training guide](https://unsloth.ai/docs/models/qwen3.8/train) |
| **Axolotl** | [@tymofii](https://x.com/tymofii/status/2122008706711957634), [@grok](https://x.com/grok/status/2122215688756486153) | YAML-config trainer |
| **LLaMA-Factory** | [@grok](https://x.com/grok/status/2122215688756486153) | |
| **HF PEFT + TRL** | [@grok](https://x.com/grok/status/2122244957335392581), [@eclecticleaps](https://x.com/eclecticleaps/status/2122211553240097125) | |
| **Hugging Face Jobs** | [@wussupitsluke](https://x.com/wussupitsluke/status/2122233812390384089), [@TheEdgarMoreau](https://x.com/TheEdgarMoreau/status/2122271977331368115) | "real easy to used, affordable" |
| **Colab / Kaggle + W&B** | [@navin_hill](https://x.com/navin_hill/status/2122203456119197708) | "[unsloth. colab/kaggle. huggingface. weights and biases]" |
| **Prime Intellect, Fireworks** (hosted post-training / RL) | [@Jeremy_](https://x.com/Jeremy_/status/2122001921368101025), [@iamanishx](https://x.com/iamanishx/status/2122258741844484271) | Ashen said he doesn't want to host anything, only publish on HF. These would just be for training compute. |
| **Cloudflare** | [@robeotx](https://x.com/robeotx/status/2122218050787352732) | Said Cloudflare has a free fine-tuning API "on Muse Glimmer right now up till the 30th." Unverified. |
| Other mentions | [@SandipanKundu42](https://x.com/SandipanKundu42/status/2122197521439367364) (Tensorant MCP, self-promo), [@Antonionocode](https://x.com/Antonionocode/status/2122226981521527217) (Fable), [@einarvollset](https://x.com/einarvollset/status/2122151685737050559) ([autoresearch.sfcompute.com](https://autoresearch.sfcompute.com)), [@kavin_anand](https://x.com/kavin_anand/status/2122257993815478537) (Sail Research rollouts), [@sudotechnoir](https://x.com/sudotechnoir/status/2122244479629336893) (Nous Hermes Agent), [@Mawuko](https://x.com/Mawuko/status/2122251051424272812) ([HOOTi Magnet](https://magnet.hooti.ai/models)), [@BullieverX](https://x.com/BullieverX/status/2122177432815890892) ([TokenOS GPU price index](https://TokenOS.ai)), [@IHAD18BTCIN2013](https://x.com/IHAD18BTCIN2013/status/2122284301869834417) (Google Vertex, "expensive") | Not evaluated |

**Our notes (verified 2026-11-16):**
- Unsloth's Qwen3.8 guide: QLoRA on Qwen3.8-27B fits in **24 GB**, LoRA needs **>36 GB**, free Kaggle notebooks give 30 hrs/week on 2×T4, and export goes to GGUF. Unsloth Studio says Mac (MLX) *training* is "coming", so it isn't on Mac yet.
- On a Mac, **`mlx-lm`** does LoRA, QLoRA (point it at a quantized model) and DoRA today. It accepts a `tools` JSONL format, which fits MCP tool calls directly, and supports `--mask-prompt`. `mlx_lm/models/qwen3_5.py` and `qwen3_5_moe.py` exist upstream, and `mlx-community/Qwen3.5-4B-4bit` / `-9B-4bit` are on HF.

## 4. Cost and time: real numbers from the thread

| Who | What they did | Cost / time |
| --- | --- | --- |
| [@vishalskotak](https://x.com/vishalskotak/status/2122193798671609858) | LoRA on **Qwen3.5-0.8B** for tool calling on health data, **on a MacBook (M4)** | "About **$3 of Claude** to write the examples and a few hours of GPU (Local M4)" |
| [@Hyre_agent](https://x.com/Hyre_agent/status/2122185609922105838) | Taught a model tool calls with a small LoRA | "GPU bill was around **12 bucks** plus two days of work" |
| [@csgriff_](https://x.com/csgriff_/status/2122290083952796076) | QLoRA with Unsloth on AWS | "**~$100 per run** on AWS 3-4 days" |
| [@tymofii](https://x.com/tymofii/status/2122008706711957634) | Advice | "Qwen3 14B and Unsloth, a **24GB card** runs LoRA fine. For Blender MCP you need **a few hundred tool-call examples, not millions of tokens**." |
| [@grok](https://x.com/grok/status/2122215688756486153) | Advice | "1k–10k clean instruction pairs", "hours, not days" |
| [@SandeshRajx](https://x.com/SandeshRajx/status/2122191508912890084) | Advice | Keep tasks **under 16K tokens**. Longer contexts need >80 GB cloud GPUs on 27B models. |
| [@fufeng1688](https://x.com/fufeng1688/status/2122118879438918055) | Advice | "a few hundred examples, and you'll know within a day if it's worth scaling" |

The pessimists were mostly about hardware: [@IHAD18BTCIN2013](https://x.com/IHAD18BTCIN2013/status/2122284301869834417) ("heavy doing it locally... ram/vram heavy", start on a 4B), [@Bolmercl](https://x.com/Bolmercl/status/2122195616289927515) ("tons of vram or rent gpu"), [@milllo](https://x.com/milllo/status/2122171122296959472) ("you can never have enough" RAM) and [@dee_cypha](https://x.com/dee_cypha/status/2122292174788198633) ("Time and compute"). A 256 GB M3 Ultra largely takes care of this for 4B–14B LoRA.

## 5. Don't wait for Qwen 4: start on current Qwen

- [@RedFasterX](https://x.com/RedFasterX/status/2122191677448208398): "start NOW tweaking **Qwen 3.5 4b** with the available tools instead of waiting for a future that hasn't happened yet."
- [@tymofii](https://x.com/tymofii/status/2122008706711957634): start now with Qwen3 14B.
- [@eyoussef](https://x.com/eyoussef/status/2122052746258100564): run the whole loop on a small Qwen now, then swap in Qwen 4.
- [@grok](https://x.com/grok/status/2122215688756486153): "Qwen 4 open weights are still pending; practice on current Qwen3.x first."
- [@IHAD18BTCIN2013](https://x.com/IHAD18BTCIN2013/status/2122284301869834417): start on a 4B.
- The one dissent: [@snapsnocaps](https://x.com/snapsnocaps/status/2122007771466072304) predicted "Qwen 4 will be really solid at 3D and anim on launch," which would mean a smaller fine-tuning gain. That's another reason to build the eval first, so you can measure the gain.

## 6. Dataset ideas from the thread

The full plan is in [`dataset-plan.md`](dataset-plan.md). The ideas, credited:

1. **Log your own successful MCP traces.** This is the main recommendation. [@johnroodepic](https://x.com/johnroodepic/status/2122008709681565717): a small model, a tight schema, two worked examples, and log every call that worked. [@crum7355608](https://x.com/crum7355608/status/2122293505016070492): "Do all cad and modeling work through local harnesses and store all reasoning traces, tool calls, and user responses (for subjective good/bad scoring)." [@grok](https://x.com/grok/status/2122245398622245258) said the same: "log only successful traces."
2. **The data has to use the server's real tool names.** [@waitingforASI_](https://x.com/waitingforASI_/status/2122013127516840095): "the blender mcp part needs training examples of real tool calls with that server's tool names and args. blender tutorials won't have those."
3. **Scrape `bpy` scripts and pair them with prompts.** [@amybuildsAI](https://x.com/amybuildsAI/status/2122028003366752750): "scrape blender python scripts, pair them with prompts, train a lora. rough version of the whole thing."
4. **Distill a big model watching Blender.** [@Vidyut](https://x.com/Vidyut/status/2122255883673465078): let a large LLM observe the commands, turn them into scripts, then train a "tiny, tiny LLM" to do things like "give your character hair." Also: include *all* the documentation, add-ons too ([post](https://x.com/Vidyut/status/2122221700125434254)).
5. **Synthetic generation with other models.** [@BarryDeenTech](https://x.com/BarryDeenTech/status/2122184525660799284), and [@vishalskotak](https://x.com/vishalskotak/status/2122193798671609858), who spent $3 of Claude to write the examples.
6. **Mine timelapses for before/after images.** [@xxsaissa](https://x.com/xxsaissa/status/2122209955348353024) proposed splitting Blender timelapses into frames at each change, having a model infer which tool calls turn the before image into the after image, verifying by hand, then training on those traces. It's creative and labor-heavy, so it's a later-phase idea.
7. **Existing public datasets**, listed by [@grok](https://x.com/grok/status/2122245398622245258). **Our notes:** we confirmed each on HF on 2026-11-16:
   - [`PGCRYPT/OpenBlender_Train`](https://huggingface.co/datasets/PGCRYPT/OpenBlender_Train): 31,401 chat-format Q&A pairs over the Blender 5.0 manual and `bpy` API, Apache-2.0.
   - [`FreedomIntelligence/BlendNet`](https://huggingface.co/datasets/FreedomIntelligence/BlendNet): 12k instruction→`bpy` script samples (2k human-annotated), Apache-2.0, from the BlenderLLM paper.
   - [`YipengGao/3DCodeBench`](https://huggingface.co/datasets/YipengGao/3DCodeBench): Grok called it "3DCode". Procedural 3D modeling via code, 10k–100k items, MIT. The card says it's "under final check" and may have non-executable scripts.
   - [`nolabs/deepfabric-blender-mcp`](https://huggingface.co/datasets/nolabs/deepfabric-blender-mcp): Grok called it `alwaysfurther/...`, which redirects here. 1k–10k synthetic Blender MCP rows, and no license listed on the card.
8. **A reference fine-tune to copy.** [@SandeshRajx](https://x.com/SandeshRajx/status/2122191508912890084) pointed to [`ccore/Qwen3.5-4B-3D-Coder`](https://huggingface.co/ccore/Qwen3.5-4B-3D-Coder), a Qwen3.5-4B fine-tune that writes three.js 3D scenes. **Our notes:** about 455k downloads and 1.1k likes, Apache-2.0, trained on `ccore/ThreeJS-3D-Scenes`. It shows a 4B Qwen fine-tune on self-contained one-shot 3D tasks can work very well, so open its dataset to see the format.

## 7. Evals and RL: the part people skip

- [@EternitiesAI](https://x.com/EternitiesAI/status/2122072226350686569): "start with a **held-out eval**; it catches gains that don't generalize."
- [@robeotx](https://x.com/robeotx/status/2122218050787352732): "fine tuning is the easy part. The hard part is building quality evals and then likely **RL runs (particularly relevant for baking in tool calling patterns)**."
- [@MikeBrave_Maker](https://x.com/MikeBrave_Maker/status/2122140015455244389): test several checkpoints "to see when it cooked correctly."
- [@csgriff_](https://x.com/csgriff_/status/2122290083952796076): evals are 25% of the effort.
- [@tensorfiend](https://x.com/tensorfiend/status/2122216307634708948): for RL, "spend time testing different reward functions - this makes a lot of difference."
- [@iamanishx](https://x.com/iamanishx/status/2122258469076279748): "You need to do more rl which is kinda expensive... Fine tune is cheaper tho."
- [@crum7355608](https://x.com/crum7355608/status/2122293505016070492): "Split training between **RLVR and rlhf**." Blender is a good fit for RLVR because a script either runs and produces the right scene state or it doesn't.

**Takeaway:** SFT with LoRA first, eval always, and RL later once there's a verifiable reward such as "scene contains X with property Y, no errors".

## 8. The skills/harness alternative (no weights changed)

- **[@HowToUseAI_](https://x.com/HowToUseAI_/status/2122124431468187791)**: "LOTS of skill/harness modification can go a long way... provide a vast library of examples... distilled into skills instead of actual weights. I do this all the time and it's fantastic."
- [@The_Godhead_Dev](https://x.com/The_Godhead_Dev/status/2122189776174608509): the model is the easy part, but the systems around it (RAG, mistake logging, safety) take the work.

**Our notes:** this fits as phase 0. A Blender skill pack (Ashen's shared brain already catalogs `arjun988/blender-skills`) plus a logging MCP harness gives a better baseline today, and every successful run it produces is training data.

## 9. Disagreements and noise

- **Local vs. rented compute.** Some said rent H100s ([@xavierlois](https://x.com/xavierlois/status/2122224958499877032), [@outsource_](https://x.com/outsource_/status/2122170103706062944), [@joshuahickscorp](https://x.com/joshuahickscorp/status/2122202811261915634)). Others said it's fine locally on a 24 GB card or an M4 MacBook. On a Mac Studio, local works for 4B–14B, and renting is for 27B+ or long context.
- **"Just ask your AI."** [@LLMJunky](https://x.com/LLMJunky/status/2122071389612155108), [@CaminoArcher](https://x.com/CaminoArcher/status/2122287120966443159), [@CryptoPsyo](https://x.com/CryptoPsyo/status/2122205734649909559), [@Cecociccio](https://x.com/Cecociccio/status/2122240806149034083) and [@MattSimmon78102](https://x.com/MattSimmon78102/status/2122234226926133500). [@viiskb disagreed](https://x.com/viiskb/status/2122215976531861556), saying assistants are weak on AI research topics.
- **Off-target or irrelevant:** [@jollyroger1480](https://x.com/jollyroger1480/status/2122191201155588577) (improve Qwen's math, which isn't relevant here), [@Zruft14](https://x.com/Zruft14/status/2122002155221762429) ([DGX Spark end-to-end fine-tune video](https://www.youtube.com/watch?v=2hoNAr-id-E), a useful beginner watch), [@gptnori](https://x.com/gptnori/status/2122007239514788019) ([SEAL, self-adapting LMs](https://github.com/Continual-Intelligence/SEAL), research, not a starting point) and [@figu7511](https://x.com/figu7511/status/2122201906881736863) (their pinned video).
- **Collab offers:** [@fullctx](https://x.com/fullctx/status/2122134317937942586), [@briankluckman](https://x.com/briankluckman/status/2122148909439197202), [@iamsbmalik](https://x.com/iamsbmalik/status/2122243856263790597), [@initeshmethani](https://x.com/initeshmethani/status/2122258321147400383) and [@Solana_Pilot](https://x.com/Solana_Pilot/status/2122262456458149898). Pointers to people: @UniswapVillain → @vydamo_, and @zeeshan_utd → @pratikg.
- **Clarifying questions worth answering:** [@0xHaley_](https://x.com/0xHaley_/status/2122001947356274857) asked whether this is Blender tool use specifically or broader 3D knowledge. Answer: tool use first. [@isssa0x](https://x.com/isssa0x/status/2122005653883326836) asked which part of the Blender side is hardest. [@crystalwizard](https://x.com/crystalwizard/status/2122188651841097962) asked what machine and how much VRAM. Answer: M3 Ultra, 256 GB unified.

## 10. Key links from the thread

- Unsloth fine-tuning guide: https://unsloth.ai/docs/get-started/fine-tuning-llms-guide (@jobelshaji95)
- Unsloth Qwen3.8 training guide: https://unsloth.ai/docs/models/qwen3.8/train (@Reveur_7)
- Reference 3D fine-tune: https://huggingface.co/ccore/Qwen3.5-4B-3D-Coder (@SandeshRajx)
- Datasets: OpenBlender_Train, BlendNet, 3DCodeBench, deepfabric-blender-mcp (@grok, see §6)
- Beginner video, end-to-end small-LLM fine-tune on DGX Spark: https://www.youtube.com/watch?v=2hoNAr-id-E (@Zruft14)
- SEAL, self-adapting LMs (research): https://github.com/Continual-Intelligence/SEAL (@gptnori)
- Autoresearch: https://autoresearch.sfcompute.com (@einarvollset)
