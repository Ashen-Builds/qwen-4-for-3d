# Raw replies

Every post in the conversation under [@ashen_one's question](https://x.com/ashen_one/status/2122000927418699866), pulled from the X API (`conversation_id:2122000927418699866`) on 2026-11-16 at about 7:25 AM ET.

- Total posts in the conversation, original included: **112**
- Replies: **111**. That's 9 by @ashen_one (including the @bot request), 3 by @grok, 1 by @bot, and **98 from other accounts**
- Like counts were captured when the posts were pulled. Short links (`t.co`) are expanded to the URL X resolved them to.
- Leading @mentions are stripped from the text. Nested replies show which post they answer.

---

## Original post

**@ashen_one** · 332 likes · [link](https://x.com/ashen_one/status/2122000927418699866)

> Need some help and advice here boys
> 
> How hard is it to fine-tune local models? Is it super extensive? Does it take hella tokens and time? 
> 
> When Qwen 4 drops, I want to fine-tune a version of Qwen 4 that excels at 3D modeling and animation (via Blender MCP handling or other stuff)
> 
> I have no idea how to do that. I'm going to figure it out as I go, but before it comes out, does anyone have any advice or resources I can look into?
> 
> Maybe like a YouTube video or just anything that can help 
> 
> thanks : )

---

### 1. @handeh777
0 likes · 2026-11-15 16:19 UTC · [link](https://x.com/handeh777/status/2122001480244662674)

> Hum, Start with LoRA not full fine tuning

### 2. @0xb3hrang
0 likes · 2026-11-15 16:19 UTC · [link](https://x.com/0xb3hrang/status/2122001539925492094)

> In my opinion blender is getting an AI apprentice

### 3. @naveen_saradhi_
39 likes · 2026-11-15 16:20 UTC · [link](https://x.com/naveen_saradhi_/status/2122001914938482855)

> Start with LoRA/QLoRA fine-tuning. You don't need to train from scratch. Learn the basics with a smaller model first, then experiment with Blender workflows.

### 4. @Jeremy_
2 likes · 2026-11-15 16:20 UTC · [link](https://x.com/Jeremy_/status/2122001921368101025)

> Depends to be honest can prob use @PrimeIntellect and make it cheaper. I think the expensive thing is running it

### 5. @0xHaley_
0 likes · 2026-11-15 16:21 UTC · [link](https://x.com/0xHaley_/status/2122001947356274857)

> Would you fine-tune for Blender tool use specifically, or broader 3D knowledge too?

### 6. @superpobe
0 likes · 2026-11-15 16:21 UTC · [link](https://x.com/superpobe/status/2122001960618577948)

> fine tuning local models is pretty manageable start small and test

### 7. @yasu0x1
0 likes · 2026-11-15 16:21 UTC · [link](https://x.com/yasu0x1/status/2122001957535834134)

> the training part is easy, finding good blender animation data to train on is the hard bit

### 8. @Zruft14
9 likes · 2026-11-15 16:21 UTC · [link](https://x.com/Zruft14/status/2122002155221762429)

> honestly i do not know anything about local models, but i do not think its hard. i think there are a couple of methods but for like full fine tuning a friend that does this stuff sent me this https://www.youtube.com/watch?v=2hoNAr-id-E idk if its outdated though but i think it should work still

### 9. @ashen_one
0 likes · 2026-11-15 16:26 UTC · [link](https://x.com/ashen_one/status/2122003331556286742) · ↳ reply to @Jeremy_ ([post](https://x.com/Jeremy_/status/2122001921368101025))

> What does PrimeIntellect do? I don't really want to host it in any way. I just want to put it on Hugging Face if anyone else wants to use it.

### 10. @ashen_one
1 likes · 2026-11-15 16:26 UTC · [link](https://x.com/ashen_one/status/2122003384144379922) · ↳ reply to @naveen_saradhi_ ([post](https://x.com/naveen_saradhi_/status/2122001914938482855))

> Okay, noted. Thank you.

### 11. @Jeremy_
2 likes · 2026-11-15 16:31 UTC · [link](https://x.com/Jeremy_/status/2122004498788847713) · ↳ reply to @ashen_one ([post](https://x.com/ashen_one/status/2122003331556286742))

> Allows you to train your own models

### 12. @isssa0x
0 likes · 2026-11-15 16:35 UTC · [link](https://x.com/isssa0x/status/2122005653883326836)

> what part of the Blender side is hardest?

### 13. @gptnori
1 likes · 2026-11-15 16:42 UTC · [link](https://x.com/gptnori/status/2122007239514788019)

> check this kinda interesting concept might be helpful https://github.com/Continual-Intelligence/SEAL

### 14. @snapsnocaps
2 likes · 2026-11-15 16:44 UTC · [link](https://x.com/snapsnocaps/status/2122007771466072304)

> Qwen 4 will be really solid at 3D and anim on launch

### 15. @tymofii
7 likes · 2026-11-15 16:47 UTC · [link](https://x.com/tymofii/status/2122008706711957634)

> Start now with Qwen3 14B and Unsloth, a 24GB card runs LoRA fine. For Blender MCP you need a few hundred tool-call examples, not millions of tokens. Axolotl or Unsloth notebooks have you covered.

### 16. @johnroodepic
80 likes · 2026-11-15 16:47 UTC · [link](https://x.com/johnroodepic/status/2122008709681565717)

> the training run is the cheap part. what you actually need is a few hundred successful blender tool-call traces to train on, and nobody publishes those. run the mcp off a small model with a tight schema and two worked examples, log every call that worked, and fine-tune on your own log later. that dataset is the whole project.

### 17. @heyartzy
1 likes · 2026-11-15 16:54 UTC · [link](https://x.com/heyartzy/status/2122010262068752767)

> Start with unsloth tutorials for the fine tuning workflow

### 18. @waitingforASI_
0 likes · 2026-11-15 17:05 UTC · [link](https://x.com/waitingforASI_/status/2122013127516840095)

> the blender mcp part needs training examples of real tool calls with that server's tool names and args. blender tutorials won't have those.

### 19. @CryptoZachLA
6 likes · 2026-11-15 17:16 UTC · [link](https://x.com/CryptoZachLA/status/2122015841612939464)

> I’d say @UniswapVillain might be able to give some insight on this, as I also am learning about local LLMs

### 20. @AetheriaFeng
0 likes · 2026-11-15 17:54 UTC · [link](https://x.com/AetheriaFeng/status/2122025437429903641)

> start with unsloth guides they make fine tuning much faster

### 21. @amybuildsAI
4 likes · 2026-11-15 18:04 UTC · [link](https://x.com/amybuildsAI/status/2122028003366752750)

> scrape blender python scripts, pair them with prompts, train a lora. rough version of the whole thing

### 22. @Okada_DeFi0x
0 likes · 2026-11-15 18:45 UTC · [link](https://x.com/Okada_DeFi0x/status/2122038297484828968)

> LoRA fine tuning with a curated Blender dataset could be a great starting point 🤖
>  Would love a follow back 😊

### 23. @ashen_one
0 likes · 2026-11-15 18:53 UTC · [link](https://x.com/ashen_one/status/2122040224490369360) · ↳ reply to @CryptoZachLA ([post](https://x.com/CryptoZachLA/status/2122015841612939464))

> hi

### 24. @ashen_one
7 likes · 2026-11-15 18:53 UTC · [link](https://x.com/ashen_one/status/2122040337640354084) · ↳ reply to @johnroodepic ([post](https://x.com/johnroodepic/status/2122008709681565717))

> hmmm okok

### 25. @UniswapVillain
4 likes · 2026-11-15 18:55 UTC · [link](https://x.com/UniswapVillain/status/2122040791958745321) · ↳ reply to @ashen_one ([post](https://x.com/ashen_one/status/2122040224490369360))

> idt i can help u. 
> https://x.com/vydamo_/status/2113366475306393871?a=iqOPGB0f9noZU-0npbU&s=20
>
> cc: @vydamo_

### 26. @eyoussef
1 likes · 2026-11-15 19:42 UTC · [link](https://x.com/eyoussef/status/2122052746258100564)

> Resource-wise: Unsloth has free Colab notebooks, including one for tool calling. You could run the whole loop on a current small Qwen now, then swap in Qwen 4 once it's supported.

### 27. @LLMJunky
5 likes · 2026-11-15 20:57 UTC · [link](https://x.com/LLMJunky/status/2122071389612155108)

> Just ask your clanker

### 28. @EternitiesAI
0 likes · 2026-11-15 21:00 UTC · [link](https://x.com/EternitiesAI/status/2122072226350686569)

> start with a held-out eval; it catches gains that don't generalize.

### 29. @ashen_one
5 likes · 2026-11-15 21:01 UTC · [link](https://x.com/ashen_one/status/2122072561240637929) · ↳ reply to @LLMJunky ([post](https://x.com/LLMJunky/status/2122071389612155108))

> imma have him ask you

### 30. @LLMJunky
2 likes · 2026-11-15 21:01 UTC · [link](https://x.com/LLMJunky/status/2122072640961884618) · ↳ reply to @ashen_one ([post](https://x.com/ashen_one/status/2122072561240637929))

> I will refer you to my dot

### 31. @fufeng1688
0 likes · 2026-11-16 00:05 UTC · [link](https://x.com/fufeng1688/status/2122118879438918055)

> Fine-tuning sounds scarier than it is — start small with LoRA, a few hundred examples, and you'll know within a day if it's worth scaling 👀

### 32. @HowToUseAI_
1 likes · 2026-11-16 00:27 UTC · [link](https://x.com/HowToUseAI_/status/2122124431468187791)

> Into it. 
>
> In the meantime... LOTS of skill/harness modification can go a long way if you don't have the ability to truly fine tune a model. If you can provide a vast library of examples of data (ironically, that you would fine tune with) you can ask the model to construct harness skills that produce outputs similar to what you want, but via the consumption of those skill & script/code examples that represent the modeling techniques that are aligned with "good", but those are distilled into skills instead of actual weights.
>
> I do this all the time and it's fantastic. Maybe you've already maxed out your potential with this technique but it's worth a shot.

### 33. @fullctx
2 likes · 2026-11-16 01:07 UTC · [link](https://x.com/fullctx/status/2122134317937942586)

> great post, i’m actually interested to do the same btw

### 34. @ashen_one
0 likes · 2026-11-16 01:12 UTC · [link](https://x.com/ashen_one/status/2122135742059040857) · ↳ reply to @fullctx ([post](https://x.com/fullctx/status/2122134317937942586))

> need to

### 35. @MikeBrave_Maker
0 likes · 2026-11-16 01:29 UTC · [link](https://x.com/MikeBrave_Maker/status/2122140015455244389)

> 2 parts are hard, 1. having the equipment, or you can do it on the cloud. 2. gathering and labeling the dataset. after that you have to test what you made to make sure it worked how you wanted, usually multi checkpoints of when you tuned it to see when it cooked correctly

### 36. @LottoLabs
4 likes · 2026-11-16 01:29 UTC · [link](https://x.com/LottoLabs/status/2122140085831475671)

> It’s all data bro that’s the first lesson

### 37. @briankluckman
0 likes · 2026-11-16 02:05 UTC · [link](https://x.com/briankluckman/status/2122148909439197202)

> I’m literally downloading my first local models as we speak to attempt some fine tuning.  Let’s connect and help each other as we learn.

### 38. @trydotworks
1 likes · 2026-11-16 02:07 UTC · [link](https://x.com/trydotworks/status/2122149567454126288)

> You can build an aLoRA for this, I think its more efficient than post-training fully, and much cheaper

### 39. @einarvollset
3 likes · 2026-11-16 02:16 UTC · [link](https://x.com/einarvollset/status/2122151685737050559)

> Just ask your agent to head to https://autoresearch.sfcompute.com

### 40. @riddy567
0 likes · 2026-11-16 03:14 UTC · [link](https://x.com/riddy567/status/2122166368904577265) · ↳ reply to @UniswapVillain ([post](https://x.com/UniswapVillain/status/2122040791958745321))

> https://x.com/riddy567/status/2122166368904577265/photo/1

### 41. @outsource_
1 likes · 2026-11-16 03:29 UTC · [link](https://x.com/outsource_/status/2122170103706062944)

> If your budget is fine to rent gpus you can do anything.

### 42. @milllo
0 likes · 2026-11-16 03:33 UTC · [link](https://x.com/milllo/status/2122171122296959472)

> Helps to have lots of RAM, and you can never have enough.

### 43. @Abomination81
4 likes · 2026-11-16 03:57 UTC · [link](https://x.com/Abomination81/status/2122177088279240991)

> nope, simple.  Use an aLoRA, use an obliterated model, tweak neurons.. simple.. many ways

### 44. @BullieverX
0 likes · 2026-11-16 03:58 UTC · [link](https://x.com/BullieverX/status/2122177432815890892)

> It’s alot easier going through https://TokenOS.ai

### 45. @aphiticus1
0 likes · 2026-11-16 04:03 UTC · [link](https://x.com/aphiticus1/status/2122178727996190889)

> Fine tuning is fast and it takes a couple of epochs compared to training something from scratch.  If its a large language model you can do it anywhere from a few hours to weeks if you have a small GPU.  Just depends on what the model is.

### 46. @VisiveAI
0 likes · 2026-11-16 04:04 UTC · [link](https://x.com/VisiveAI/status/2122178905180352862) · ↳ reply to @eyoussef ([post](https://x.com/eyoussef/status/2122052746258100564))

> Unsloth and Qwen 4 support sounds like a smooth upgrade path. How does tool calling perform with Qwen on Colab?

### 47. @hatsunama
0 likes · 2026-11-16 04:24 UTC · [link](https://x.com/hatsunama/status/2122183882426433623)

> Depends. Are you trying to do neuron editing or just simple post training?

### 48. @BarryDeenTech
3 likes · 2026-11-16 04:26 UTC · [link](https://x.com/BarryDeenTech/status/2122184525660799284)

> You'll just need good data and a GPU to train it on. You can probably synthetically generate it with other models

### 49. @Hyre_agent
4 likes · 2026-11-16 04:30 UTC · [link](https://x.com/Hyre_agent/status/2122185609922105838)

> we taught a model tool calls with a small LoRA. the GPU bill was around 12 bucks plus two days of work, so it’s smaller than it sounds

### 50. @crystalwizard
0 likes · 2026-11-16 04:42 UTC · [link](https://x.com/crystalwizard/status/2122188651841097962)

> what sort of machine do you have, and how much vram do you have?

### 51. @jobelshaji95
3 likes · 2026-11-16 04:44 UTC · [link](https://x.com/jobelshaji95/status/2122189061968269813)

> has a pretty helpful guide on fine tuning. Relatively straightforward, but the harder part imo is getting the training data needed. Basically a bunch of clean blender traces. Link to the unsloth doc - https://unsloth.ai/docs/get-started/fine-tuning-llms-guide

### 52. @The_Godhead_Dev
0 likes · 2026-11-16 04:47 UTC · [link](https://x.com/The_Godhead_Dev/status/2122189776174608509)

> It depends what you want. I just built my home rig and have spent the last 3-4 days tuning. I have my models running quickly, but there's so many other systems to build around them, like good RAG, persistent mistake logging, safety systems (I run mine outside of sandbox), etc.

### 53. @The_Godhead_Dev
0 likes · 2026-11-16 04:48 UTC · [link](https://x.com/The_Godhead_Dev/status/2122190139158044796) · ↳ reply to @The_Godhead_Dev ([post](https://x.com/The_Godhead_Dev/status/2122189776174608509))

> For instance right now I'm working on getting my swarm systems and subagents working through Hermes , this is proving to be the most difficult part so far . Right now my single QFN model is doing better and faster work than my swarm which is annoying .

### 54. @jollyroger1480
0 likes · 2026-11-16 04:53 UTC · [link](https://x.com/jollyroger1480/status/2122191201155588577)

> One thing you can do is improve math. Ask your llm to train and improve the math in qwen. It will be loads faster..takes time running on gpu though crunching the equations.

### 55. @SandeshRajx
5 likes · 2026-11-16 04:54 UTC · [link](https://x.com/SandeshRajx/status/2122191508912890084)

> this one is a good example of a sucessfull finetune https://huggingface.co/ccore/Qwen3.5-4B-3D-Coder
>
> i'd say finetune on tasks that can be finished in under 16K tokens to make the training run manageable. Long context tasks >16K context length will require much more expensive cloud GPUs >80gb if you're planning to finetune the larger 27B models. 
>
> The linked finetune makes threejs 3d scenes, which is a self contained one shot task.

### 56. @RedFasterX
3 likes · 2026-11-16 04:54 UTC · [link](https://x.com/RedFasterX/status/2122191677448208398)

> You should start NOW tweaking Qwen 3.5 4b with the available tools instead of waiting for a future that hasn't happened yet.

### 57. @albustime
1 likes · 2026-11-16 04:59 UTC · [link](https://x.com/albustime/status/2122192730264891880)

> It’s butt easy

### 58. @vishalskotak
1 likes · 2026-11-16 05:03 UTC · [link](https://x.com/vishalskotak/status/2122193798671609858)

> Just did this on a MacBook: fine-tuned Qwen3.5-0.8B (small, I know) with LoRA to call tools for my health data. The training is easy. About $3 of Claude to write the examples and a few hours of GPU (Local M4)

### 59. @Bolmercl
1 likes · 2026-11-16 05:10 UTC · [link](https://x.com/Bolmercl/status/2122195616289927515)

> u will need tons of vram or rent gpu (faster and cheaper tbh)
>
> tons of data too

### 60. @SandipanKundu42
1 likes · 2026-11-16 05:18 UTC · [link](https://x.com/SandipanKundu42/status/2122197521439367364)

> You can use @tensorant for this. Simply connect your agent with Tensorant's MCP and you can simply chat with your agent for the full fine tuning and evaluation process end to end.
>
> Happy to give you a walkthrough personally, feel free to reach out.

### 61. @figu7511
0 likes · 2026-11-16 05:35 UTC · [link](https://x.com/figu7511/status/2122201906881736863)

> You can take a look into my pinned video &amp; it's source code, it is pretty basic, everything built from a prompt (available in the repo). If you have a subscription to any service like goggle Gemini, Claude or openai you can just ask for what you want, hydrogen Gemini is free now

### 62. @joshuahickscorp
0 likes · 2026-11-16 05:39 UTC · [link](https://x.com/joshuahickscorp/status/2122202811261915634)

> depends greatly on your hardware. building a method with an agent after doing your own research shouldn’t be too hard. you could also rent gpus.

### 63. @navin_hill
1 likes · 2026-11-16 05:41 UTC · [link](https://x.com/navin_hill/status/2122203456119197708)

> everything u need to start [unsloth. colab/kaggle. huggingface. weights and biases] tell ur agent to get it fuckin poppin. depending on what target size your model is will determine your constraints and requirements for compute power and clock time.

### 64. @CryptoPsyo
0 likes · 2026-11-16 05:50 UTC · [link](https://x.com/CryptoPsyo/status/2122205734649909559)

> I'd start by asking chat gpt, man.

### 65. @LightyLightyHi
0 likes · 2026-11-16 05:59 UTC · [link](https://x.com/LightyLightyHi/status/2122208029613724029)

> The model is only as good as the data.
> So if you want a model that's better than Qwen4. You need data that is better than Alibaba, on your specific task.
> a couple hundred examples might do it.

### 66. @xxsaissa
0 likes · 2026-11-16 06:07 UTC · [link](https://x.com/xxsaissa/status/2122209955348353024) · ↳ reply to @johnroodepic ([post](https://x.com/johnroodepic/status/2122008709681565717))

> I might be way off, but couldn’t you work from the top down by splicing Blender timelapses into screenshots at each change, have a model pick x tool call(s) on the before IMG that result in the after IMG, (hand verify) and then train on the produced tool traces?

### 67. @xxsaissa
0 likes · 2026-11-16 06:10 UTC · [link](https://x.com/xxsaissa/status/2122210698092843249) · ↳ reply to @xxsaissa ([post](https://x.com/xxsaissa/status/2122209955348353024))

> you could use https://developers.openai.com/api/docs/guides/decisions for decomposing the tool call from the whole MCP catalog and maybe bring that capability into a much smaller B param model. i know nothing about training at all FWIW just my reasoning

### 68. @eclecticleaps
0 likes · 2026-11-16 06:13 UTC · [link](https://x.com/eclecticleaps/status/2122211553240097125)

> There are good instructions on HuggingFace on LoRA training, which may be best way to do this at acceptable  cost. 
> As @johnroodepic said, making a good variety of data traces will be important also. You could start doing that now.

### 69. @aiu60826335
0 likes · 2026-11-16 06:29 UTC · [link](https://x.com/aiu60826335/status/2122215586654822583)

> can you answer this query?

### 70. @grok
0 likes · 2026-11-16 06:30 UTC · [link](https://x.com/grok/status/2122215688756486153) · ↳ reply to @aiu60826335 ([post](https://x.com/aiu60826335/status/2122215586654822583))

> Fine-tuning local models with LoRA/QLoRA is doable on a single 24GB GPU and not overly hard now. Tools like Unsloth or LLaMA-Factory handle most of the complexity. Data quality is the real bottleneck—build 1k–10k clean instruction pairs of Blender Python/MCP examples rather than raw volume. Training runs take hours, not days, for moderate ranks. Qwen 4 open weights are still pending; practice on current Qwen3.x first. Search Unsloth Qwen notebooks or Axolotl YAML examples to start.

### 71. @viiskb
0 likes · 2026-11-16 06:30 UTC · [link](https://x.com/viiskb/status/2122215795023282584)

> Getting data is the hardest part.

### 72. @viiskb
0 likes · 2026-11-16 06:31 UTC · [link](https://x.com/viiskb/status/2122215976531861556) · ↳ reply to @LLMJunky ([post](https://x.com/LLMJunky/status/2122071389612155108))

> It will not work. They're castrated on AI research topics.

### 73. @tensorfiend
0 likes · 2026-11-16 06:32 UTC · [link](https://x.com/tensorfiend/status/2122216307634708948)

> From my experience, I realized getting good data is more expensive (time and money) than actual finetuning. So, I would suggest to spend more time there. A mid or poor quality data used for finetuning is not gonna make the model any good. 
>
> Start with LoRA/QLoRA fine-tuning. For RL, you would have to spend time testing different reward functions - this makes a lot of difference.

### 74. @robeotx
0 likes · 2026-11-16 06:39 UTC · [link](https://x.com/robeotx/status/2122218050787352732)

> has a free API for fine tuning on Muse Glimmer right now up till the 30th. But as somehow else mentioned,fine tuning is the easy part. The hard part is building quality evals and then likely RL runs (particularly relevant for baking in tool calling patterns)

### 75. @Vidyut
1 likes · 2026-11-16 06:54 UTC · [link](https://x.com/Vidyut/status/2122221700125434254)

> I think there's a database of good commands somewhere. Also don't forget the documentation - all the documentation, including for well documented addons.

### 76. @iam_Dyeus
0 likes · 2026-11-16 06:56 UTC · [link](https://x.com/iam_Dyeus/status/2122222283930664971)

> Fine-tuning is easy; getting the correct dataset is hard

### 77. @xavierlois
0 likes · 2026-11-16 07:07 UTC · [link](https://x.com/xavierlois/status/2122224958499877032)

> Wanna rent some H100 to do the job?

### 78. @sushishariq
0 likes · 2026-11-16 07:12 UTC · [link](https://x.com/sushishariq/status/2122226268167135279)

> gotta up your vocab game

### 79. @Antonionocode
0 likes · 2026-11-16 07:15 UTC · [link](https://x.com/Antonionocode/status/2122226981521527217)

> Training is cheap. Fable helps you easily with this. Did it already.

### 80. @tatianajiselle
0 likes · 2026-11-16 07:18 UTC · [link](https://x.com/tatianajiselle/status/2122227711603327128)

> I guess the girls arent allowed to answer? 👀

### 81. @wussupitsluke
0 likes · 2026-11-16 07:42 UTC · [link](https://x.com/wussupitsluke/status/2122233812390384089)

> Huggingface jobs, real easy to used, affordable.

### 82. @MattSimmon78102
0 likes · 2026-11-16 07:44 UTC · [link](https://x.com/MattSimmon78102/status/2122234226926133500)

> The fact that you arent having this conversation with an AI shows you dont know how to use AI.

### 83. @Cecociccio
0 likes · 2026-11-16 08:10 UTC · [link](https://x.com/Cecociccio/status/2122240806149034083)

> Grok can teach you 
> Just ask

### 84. @iamsbmalik
0 likes · 2026-11-16 08:22 UTC · [link](https://x.com/iamsbmalik/status/2122243856263790597)

> I am interested in something similar, let's connect

### 85. @sudotechnoir
1 likes · 2026-11-16 08:24 UTC · [link](https://x.com/sudotechnoir/status/2122244479629336893)

> Hermes Agent can help for sure 🪽

### 86. @peterchurchuk
0 likes · 2026-11-16 08:26 UTC · [link](https://x.com/peterchurchuk/status/2122244836078346315)

> read the post I replied to end explain how we do it.

### 87. @grok
0 likes · 2026-11-16 08:26 UTC · [link](https://x.com/grok/status/2122244957335392581) · ↳ reply to @peterchurchuk ([post](https://x.com/peterchurchuk/status/2122244836078346315))

> Fine-tuning local models with LoRA or QLoRA is manageable, not extreme. Build a dataset of Blender bpy/MCP instruction pairs (natural language prompts to modeling, animation, or tool-call code). Load a Qwen base via Unsloth or Hugging Face PEFT+TRL, train a few epochs on one solid GPU. Takes hours rather than days and keeps token cost low. Merge the adapters, quantize to GGUF, and run locally. Unsloth Qwen notebooks or HF tutorials are solid starting points.

### 88. @peterchurchuk
0 likes · 2026-11-16 08:27 UTC · [link](https://x.com/peterchurchuk/status/2122245253872951355) · ↳ reply to @grok ([post](https://x.com/grok/status/2122244957335392581))

> Are there any good sources he could use for the blender data if he doesn’t have any?

### 89. @grok
0 likes · 2026-11-16 08:28 UTC · [link](https://x.com/grok/status/2122245398622245258) · ↳ reply to @peterchurchuk ([post](https://x.com/peterchurchuk/status/2122245253872951355))

> Yes. Solid public starters on HF: PGCRYPT/OpenBlender_Train (31k Q&A from Blender 5 docs + full bpy API), FreedomIntelligence/BlendNet (instruction-to-script pairs), and YipengGao/3DCode for procedural modeling. For MCP tool-calling try alwaysfurther/deepfabric-blender-mcp. Best long-term is still generating your own: run a base model against Blender MCP, log only successful traces, then fine-tune on those.

### 90. @Reveur_7
0 likes · 2026-11-16 08:46 UTC · [link](https://x.com/Reveur_7/status/2122250064609607905)

> This is a decent starting point: https://unsloth.ai/docs/models/qwen3.8/train

### 91. @Mawuko
0 likes · 2026-11-16 08:50 UTC · [link](https://x.com/Mawuko/status/2122251051424272812)

> https://magnet.hooti.ai/models

### 92. @zeeshan_utd
1 likes · 2026-11-16 09:08 UTC · [link](https://x.com/zeeshan_utd/status/2122255356026057173)

> is your goto man for this

### 93. @Vidyut
0 likes · 2026-11-16 09:10 UTC · [link](https://x.com/Vidyut/status/2122255883673465078) · ↳ reply to @Vidyut ([post](https://x.com/Vidyut/status/2122221700125434254))

> A good pile of scripts may be useful as well. Just going into Blender and letting a large LLM observe the commands. Then turn them into scripts for smaller models to quickly use. Apply geometry nodes to this, copy the "scalp" vertex group from this mesh separate into a new mesh. Add hair to that mesh... Then you can just tell a tiny, tiny LLM that fits in a sneeze to give your character hair, and it will.

### 94. @kavin_anand
0 likes · 2026-11-16 09:18 UTC · [link](https://x.com/kavin_anand/status/2122257993815478537)

> can make the “hella tokens” part work out :) rollouts and @sailresearchco go hand in hand

### 95. @initeshmethani
0 likes · 2026-11-16 09:19 UTC · [link](https://x.com/initeshmethani/status/2122258321147400383)

> happy to collaborate if you are serious about it

### 96. @iamanishx
0 likes · 2026-11-16 09:20 UTC · [link](https://x.com/iamanishx/status/2122258469076279748)

> You need to do more rl which is kinda expensive and largely depends on the way you are choosing 
>
> Fine tune is cheaper tho ….

### 97. @iamanishx
0 likes · 2026-11-16 09:21 UTC · [link](https://x.com/iamanishx/status/2122258741844484271) · ↳ reply to @iamanishx ([post](https://x.com/iamanishx/status/2122258469076279748))

> Explore @PrimeIntellect @FireworksAI_HQ they lets you do post train

### 98. @Solana_Pilot
0 likes · 2026-11-16 09:36 UTC · [link](https://x.com/Solana_Pilot/status/2122262456458149898)

> hit me up bro, happy to collab with u on this

### 99. @TheEdgarMoreau
0 likes · 2026-11-16 10:14 UTC · [link](https://x.com/TheEdgarMoreau/status/2122271977331368115)

> Use @huggingface

### 100. @OliNorwell
0 likes · 2026-11-16 10:32 UTC · [link](https://x.com/OliNorwell/status/2122276546337718605)

> Look into @UnslothAI - they have many scripts/tools and good tutorials for doing exactly this.

### 101. @IHAD18BTCIN2013
0 likes · 2026-11-16 11:03 UTC · [link](https://x.com/IHAD18BTCIN2013/status/2122284301869834417)

> Start on a smaller model, like a 4B. 
>
> It's heavy doing it locally, a lot of codex/token usage and ram/vram heavy. 
>
> I was trying to build a thin Lora/Qlora skin to go on models but that was getting extensive/expensive.
>
> There's also Googles Vertex platform, expensive as well.

### 102. @CaminoArcher
1 likes · 2026-11-16 11:14 UTC · [link](https://x.com/CaminoArcher/status/2122287120966443159) · ↳ reply to @LLMJunky ([post](https://x.com/LLMJunky/status/2122071389612155108))

> Your bot will explain it in depth and hold your hand through it. 
>
> If there's parts you don't understand make them unexplain. 
>
> They will also tell you exactly what to buy and how to hook everything up and a lot of it they can hook up.

### 103. @csgriff_
3 likes · 2026-11-16 11:26 UTC · [link](https://x.com/csgriff_/status/2122290083952796076)

> Mate it is incredibly easy. But can’t talk to your use case. Effort: 70% training data, 5% tun config, 25% evals. Start with QLORA, Unsloth is simple. ~$100 per run on AWS 3-4 days. I am a clown and I find it simple. Lessons learnt: Main effort is good training data

### 104. @adrianzhang4
1 likes · 2026-11-16 11:33 UTC · [link](https://x.com/adrianzhang4/status/2122291957271777630)

> You need to close all social media including x and put your all time into GitHub.

### 105. @dee_cypha
0 likes · 2026-11-16 11:34 UTC · [link](https://x.com/dee_cypha/status/2122292174788198633)

> Time and compute

### 106. @LHershberger06
0 likes · 2026-11-16 11:37 UTC · [link](https://x.com/LHershberger06/status/2122293082276479069)

> I’d have an ai like codex or hark help you, it’ll do most of the technical work. The most important thing is gathering a lot of quality data which I’ve been working on for weeks for my own model. I’d recommend training a LoRA adapter instead of a full fine tune

### 107. @crum7355608
1 likes · 2026-11-16 11:39 UTC · [link](https://x.com/crum7355608/status/2122293505016070492)

> You need data. Do all cad and modeling work through local harnesses and store all reasoning traces, tool calls, and user responses (for subjective good/bad scoring), data science over traces when enough are accumulated to build training set. Split training between RLVR and rlhf

### 108. @mikeytag
0 likes · 2026-11-16 12:17 UTC · [link](https://x.com/mikeytag/status/2122303062044004503)

> The actual tuning isn’t the hard part. It’s more about coming up with a large, high quality dataset to train on.

### 109. @ashen_one
0 likes · 2026-11-16 12:21 UTC · [link](https://x.com/ashen_one/status/2122304129968300231) · ↳ reply to @adrianzhang4 ([post](https://x.com/adrianzhang4/status/2122291957271777630))

> noted

### 110. @ashen_one
0 likes · 2026-11-16 12:23 UTC · [link](https://x.com/ashen_one/status/2122304482767982741)

> hey @bot read all the replies to this post and summarize them cleanly and deeply and add it to an open source github repo called “qwen 4 for 3d” with action items so i can start today

### 111. @bot
0 likes · 2026-11-16 12:23 UTC · [link](https://x.com/bot/status/2122304513021235661) · ↳ reply to @ashen_one ([post](https://x.com/ashen_one/status/2122304482767982741))

> Got it, sending this straight to your Grok Bot so you can dig in right away.
