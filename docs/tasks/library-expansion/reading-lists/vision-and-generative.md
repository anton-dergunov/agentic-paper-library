# Reading list: vision and generative

The library's vision folder is strong on transformer backbones (ViT, DeiT, Swin, ConvNeXt), pose, perceptual metrics and Segment Anything; vision-language has CLIP, SigLIP 2, Flamingo, LLaVA, Cambrian-1, BLINK and ColPali; diffusion has DDPM, DDIM, latent diffusion, DiT, flow matching, consistency models and several 2024-25 system papers; gans-and-vaes holds only StyleGAN2, AttnGAN, the VAE paper and a few others; speech-and-audio is mostly piano transcription plus Whisper and F5-TTS. The list adds the detection and promptable-segmentation lineage (DETR to SAM 3) and 3D geometry (NeRF, Gaussian splatting, VGGT); for vision-language, the encoder-and-connector recipes and current open models (BLIP-2, SigLIP, Qwen2.5/3-VL, PaliGemma 2, Molmo) plus the multimodal embedding and retrieval line most relevant to search (UniIR, VLM2Vec, GME, jina-embeddings-v4, ViDoRe V3); for diffusion, the theory and guidance papers that are missing (Score SDE, ADM, CFG, EDM, rectified flow, SD3, ControlNet), few-step distillation, editing and video, RL and preference tuning, and the link to text and unified models; the founding GAN, VQ-VAE and flow papers; and speech self-supervision, codec-based audio language models, and omni and full-duplex speech models. Topics left out: representation-learning (DINO, MAE are already there), world models and robotics, and trustworthy-ML work on generative models.

## Proposed

| # | Paper | Year | arXiv / URL | Folder | Why |
|--:|---|--:|---|---|---|
| 1 | End-to-End Object Detection with Transformers | 2020 | 2005.12872 | vision-and-multimodal/vision | DETR: set-prediction detection without anchors or NMS; the transformer detector every later one builds on. |
| 2 | Faster R-CNN: Towards Real-Time Object Detection with Region Proposal Networks | 2015 | 1506.01497 | vision-and-multimodal/vision | Two-stage detector with learned region proposals; the reference baseline of detection. |
| 3 | Mask R-CNN | 2017 | 1703.06870 | vision-and-multimodal/vision | Adds a mask branch to Faster R-CNN; the standard instance-segmentation baseline. |
| 4 | DETRs Beat YOLOs on Real-time Object Detection | 2023 | 2304.08069 | vision-and-multimodal/vision | RT-DETR: first real-time end-to-end transformer detector; the practical successor to YOLO-style pipelines. |
| 5 | Grounding DINO: Marrying DINO with Grounded Pre-Training for Open-Set Object Detection | 2023 | 2303.05499 | vision-and-multimodal/vision | Text-prompted open-vocabulary detection; the common building block in language-driven vision pipelines. |
| 6 | SAM 2: Segment Anything in Images and Videos | 2024 | 2408.00714 | vision-and-multimodal/vision | Extends Segment Anything (in library) to video with a streaming memory; the current promptable segmentation standard. |
| 7 | SAM 3: Segment Anything with Concepts | 2025 | 2511.16719 | vision-and-multimodal/vision | Promptable concept segmentation from text or exemplars; moves SAM from clicks to open-vocabulary concepts. |
| 8 | Depth Anything V2 | 2024 | 2406.09414 | vision-and-multimodal/vision | Monocular depth trained with synthetic labels and pseudo-labelled real images; widely used depth foundation model. |
| 9 | VGGT: Visual Geometry Grounded Transformer | 2025 | 2503.11651 | vision-and-multimodal/vision | Feed-forward transformer predicting cameras, depth and point maps from many views; the new baseline for 3D geometry. |
| 10 | NeRF: Representing Scenes as Neural Radiance Fields for View Synthesis | 2020 | 2003.08934 | vision-and-multimodal/vision | Neural radiance fields; the origin of learned novel-view synthesis and neural rendering. |
| 11 | 3D Gaussian Splatting for Real-Time Radiance Field Rendering | 2023 | 2308.04079 | vision-and-multimodal/vision | Explicit Gaussian scene representation with real-time rendering; displaced NeRF in practice. |
| 12 | BLIP-2: Bootstrapping Language-Image Pre-training with Frozen Image Encoders and Large Language Models | 2023 | 2301.12597 | vision-and-multimodal/vision-language | Q-Former bridges a frozen image encoder and a frozen LLM cheaply; the template for connector-style VLMs. |
| 13 | Improved Baselines with Visual Instruction Tuning | 2023 | 2310.03744 | vision-and-multimodal/vision-language | LLaVA-1.5: a simple MLP connector plus better data gives a strong open baseline; extends Visual Instruction Tuning (in library). |
| 14 | Sigmoid Loss for Language Image Pre-Training | 2023 | 2303.15343 | vision-and-multimodal/vision-language | SigLIP: pairwise sigmoid loss replacing CLIP's softmax; the encoder behind most open VLMs (SigLIP 2 is in library). |
| 15 | DataComp: In search of the next generation of multimodal datasets | 2023 | 2304.14108 | vision-and-multimodal/vision-language | Benchmark where the dataset, not the model, is the variable; shows filtering drives CLIP quality. |
| 16 | Perception Encoder: The best visual embeddings are not at the output of the network | 2025 | 2504.13181 | vision-and-multimodal/vision-language | Contrastive vision encoder whose best features sit in intermediate layers; a 2025 reference encoder for VLMs. |
| 17 | Qwen2.5-VL Technical Report | 2025 | 2502.13923 | vision-and-multimodal/vision-language | Native-resolution ViT, document parsing and long video; the most-used open VLM family. |
| 18 | Qwen3-VL Technical Report | 2025 | 2511.21631 | vision-and-multimodal/vision-language | Latest Qwen VLM with 256K interleaved context, dense and MoE variants; current open-model reference. |
| 19 | PaliGemma 2: A Family of Versatile VLMs for Transfer | 2024 | 2412.03555 | vision-and-multimodal/vision-language | SigLIP plus Gemma 2 at several sizes and resolutions; study of what transfer-oriented VLM design buys. |
| 20 | Molmo and PixMo: Open Weights and Open Data for State-of-the-Art Vision-Language Models | 2024 | 2409.17146 | vision-and-multimodal/vision-language | Fully open VLM with human-spoken captions and pointing data; a reference for data-centric VLM training. |
| 21 | MMMU: A Massive Multi-discipline Multimodal Understanding and Reasoning Benchmark for Expert AGI | 2023 | 2311.16502 | vision-and-multimodal/vision-language | College-level multimodal exam; the headline VLM benchmark in model reports. |
| 22 | Evaluating Object Hallucination in Large Vision-Language Models | 2023 | 2305.10355 | vision-and-multimodal/vision-language | POPE: simple polling protocol for object hallucination; the standard VLM hallucination metric. |
| 23 | MM-LLMs: Recent Advances in MultiModal Large Language Models | 2024 | 2401.13601 | vision-and-multimodal/vision-language | Survey of architectures, training recipes and benchmarks of multimodal LLMs. |
| 24 | UniIR: Training and Benchmarking Universal Multimodal Information Retrievers | 2023 | 2311.17136 | vision-and-multimodal/vision-language | M-BEIR benchmark and instruction-conditioned retriever over mixed text/image queries; defines universal multimodal retrieval. |
| 25 | VLM2Vec: Training Vision-Language Models for Massive Multimodal Embedding Tasks | 2024 | 2410.05160 | vision-and-multimodal/vision-language | Turns a VLM into a multimodal embedder and introduces the MMEB benchmark; the standard recipe. |
| 26 | VLM2Vec-V2: Advancing Multimodal Embedding for Videos, Images, and Visual Documents | 2025 | 2507.04590 | vision-and-multimodal/vision-language | Extends MMEB and the embedder to video and visual documents. |
| 27 | GME: Improving Universal Multimodal Retrieval by Multimodal LLMs | 2024 | 2412.16855 | vision-and-multimodal/vision-language | MLLM-based embedder for text, image and visual-document retrieval with synthetic fused data; strong open baseline. |
| 28 | jina-embeddings-v4: Universal Embeddings for Multimodal Multilingual Retrieval | 2025 | 2506.18902 | vision-and-multimodal/vision-language | Single model with dense and late-interaction (ColPali-style) outputs for text and visual documents; production-oriented. |
| 29 | ViDoRe V3: A Comprehensive Evaluation of Retrieval Augmented Generation in Complex Real-World Scenarios | 2026 | 2601.08620 | vision-and-multimodal/vision-language | Human-annotated multimodal RAG benchmark that extends the ViDoRe line behind ColPali (in library). |
| 30 | Score-Based Generative Modeling through Stochastic Differential Equations | 2020 | 2011.13456 | generative-models/diffusion | Unifies score matching and DDPM as SDEs with probability-flow ODEs; the theoretical frame of modern diffusion. |
| 31 | Diffusion Models Beat GANs on Image Synthesis | 2021 | 2105.05233 | generative-models/diffusion | ADM and classifier guidance; the paper that made diffusion the default image generator. |
| 32 | Classifier-Free Diffusion Guidance | 2022 | 2207.12598 | generative-models/diffusion | Guidance without a classifier; used in every text-to-image system. |
| 33 | Elucidating the Design Space of Diffusion-Based Generative Models | 2022 | 2206.00364 | generative-models/diffusion | EDM: disentangles the design choices of noise schedule, preconditioning and sampler; the reference for training and sampling. |
| 34 | Flow Straight and Fast: Learning to Generate and Transfer Data with Rectified Flow | 2022 | 2209.03003 | generative-models/diffusion | Rectified flow: straight-path transport between noise and data; the objective behind SD3 and Flux (complements Flow Matching in library). |
| 35 | Scaling Rectified Flow Transformers for High-Resolution Image Synthesis | 2024 | 2403.03206 | generative-models/diffusion | Stable Diffusion 3: MM-DiT with rectified flow; the architecture recipe for current open text-to-image models. |
| 36 | Adding Conditional Control to Text-to-Image Diffusion Models | 2023 | 2302.05543 | generative-models/diffusion | ControlNet: spatial conditioning via a trainable copy of the encoder; the standard control mechanism. |
| 37 | Improved Distribution Matching Distillation for Fast Image Synthesis | 2024 | 2405.14867 | generative-models/diffusion | DMD2: one- to four-step generators via distribution matching plus GAN loss; the leading few-step distillation recipe. |
| 38 | Wan: Open and Advanced Large-Scale Video Generative Models | 2025 | 2503.20314 | generative-models/diffusion | Open large video diffusion transformer with a full training recipe; the open reference for text-to-video. |
| 39 | FLUX.1 Kontext: Flow Matching for In-Context Image Generation and Editing in Latent Space | 2025 | 2506.15742 | generative-models/diffusion | Unified instruction-based editing and generation with flow matching; the current editing baseline. |
| 40 | Simple and Effective Masked Diffusion Language Models | 2024 | 2406.07524 | generative-models/diffusion | MDLM: a clean masked-diffusion objective that makes discrete diffusion competitive for text. |
| 41 | Transfusion: Predict the Next Token and Diffuse Images with One Multi-Modal Model | 2024 | 2408.11039 | generative-models/diffusion | One transformer trained with next-token loss on text and diffusion loss on images; the template for unified multimodal generators. |
| 42 | Representation Alignment for Generation: Training Diffusion Transformers Is Easier Than You Think | 2024 | 2410.06940 | generative-models/diffusion | REPA: aligning DiT features to a pretrained encoder speeds training about 17x; links to RAE (in library). |
| 43 | Understanding Diffusion Models: A Unified Perspective | 2022 | 2208.11970 | generative-models/diffusion | Tutorial deriving VAE, DDPM, score and guidance views in one place; best on-ramp to the maths. |
| 44 | Diffusion Model Alignment Using Direct Preference Optimization | 2023 | 2311.12908 | generative-models/diffusion | Diffusion-DPO: preference tuning of text-to-image models without a reward model. |
| 45 | Flow-GRPO: Training Flow Matching Models via Online RL | 2025 | 2505.05470 | generative-models/diffusion | Online RL (GRPO) for flow models; the main recipe for RL post-training of image generators. |
| 46 | Generative Adversarial Networks | 2014 | 1406.2661 | generative-models/gans-and-vaes | The original adversarial framework; foundational for generative modelling. |
| 47 | Wasserstein GAN | 2017 | 1701.07875 | generative-models/gans-and-vaes | Wasserstein loss that stabilises GAN training; the standard fix of the era. |
| 48 | A Style-Based Generator Architecture for Generative Adversarial Networks | 2018 | 1812.04948 | generative-models/gans-and-vaes | StyleGAN: style-modulated generator; extends StyleGAN2 (in library) back to its source. |
| 49 | Large Scale GAN Training for High Fidelity Natural Image Synthesis | 2018 | 1809.11096 | generative-models/gans-and-vaes | BigGAN: scale and truncation trick; showed GANs scale on ImageNet. |
| 50 | Unpaired Image-to-Image Translation using Cycle-Consistent Adversarial Networks | 2017 | 1703.10593 | generative-models/gans-and-vaes | CycleGAN: cycle consistency for unpaired translation; widely reused idea. |
| 51 | Neural Discrete Representation Learning | 2017 | 1711.00937 | generative-models/gans-and-vaes | VQ-VAE: discrete latent codebook; the basis of image tokenisers and latent generative models. |
| 52 | Taming Transformers for High-Resolution Image Synthesis | 2020 | 2012.09841 | generative-models/gans-and-vaes | VQGAN: perceptual-and-adversarial autoencoder plus autoregressive transformer; the tokeniser and autoencoder lineage behind latent diffusion. |
| 53 | An Introduction to Variational Autoencoders | 2019 | 1906.02691 | generative-models/gans-and-vaes | Kingma and Welling's survey/tutorial on VAEs; the standard reference. |
| 54 | Normalizing Flows: An Introduction and Review of Current Methods | 2019 | 1908.09257 | generative-models/gans-and-vaes | Survey of flow-based models with exact likelihood; the missing third pre-diffusion family. |
| 55 | The GAN is dead; long live the GAN! A Modern GAN Baseline | 2025 | 2501.05441 | generative-models/gans-and-vaes | R3GAN: a regularised loss and modern backbone beat StyleGAN2 and rival diffusion; shows GANs are a live baseline. |
| 56 | wav2vec 2.0: A Framework for Self-Supervised Learning of Speech Representations | 2020 | 2006.11477 | vision-and-multimodal/speech-and-audio | Contrastive self-supervised speech pretraining; made low-label ASR practical. |
| 57 | HuBERT: Self-Supervised Speech Representation Learning by Masked Prediction of Hidden Units | 2021 | 2106.07447 | vision-and-multimodal/speech-and-audio | Masked prediction of clustered units; source of discrete speech tokens used by speech LMs. |
| 58 | Conformer: Convolution-augmented Transformer for Speech Recognition | 2020 | 2005.08100 | vision-and-multimodal/speech-and-audio | Convolution plus attention encoder; the dominant ASR architecture. |
| 59 | Neural Codec Language Models are Zero-Shot Text to Speech Synthesizers | 2023 | 2301.02111 | vision-and-multimodal/speech-and-audio | VALL-E: TTS as language modelling over codec tokens with 3-second prompts. |
| 60 | Voicebox: Text-Guided Multilingual Universal Speech Generation at Scale | 2023 | 2306.15687 | vision-and-multimodal/speech-and-audio | Flow-matching speech infilling model; the base of F5-TTS (in library) and non-autoregressive TTS. |
| 61 | High Fidelity Neural Audio Compression | 2022 | 2210.13438 | vision-and-multimodal/speech-and-audio | EnCodec: neural codec whose tokens underlie audio language models. |
| 62 | AudioLM: a Language Modeling Approach to Audio Generation | 2022 | 2209.03143 | vision-and-multimodal/speech-and-audio | Semantic plus acoustic tokens for long-range audio generation; origin of audio LMs. |
| 63 | Simple and Controllable Music Generation | 2023 | 2306.05284 | vision-and-multimodal/speech-and-audio | MusicGen: single-stage transformer over codec tokens; the open music baseline. |
| 64 | CLAP: Learning Audio Concepts From Natural Language Supervision | 2022 | 2206.04769 | vision-and-multimodal/speech-and-audio | CLIP for audio: shared audio-text embeddings for retrieval and zero-shot classification. |
| 65 | Moshi: a speech-text foundation model for real-time dialogue | 2024 | 2410.00037 | vision-and-multimodal/speech-and-audio | Full-duplex spoken dialogue model with parallel text and audio streams; reference for real-time voice. |
| 66 | Qwen2.5-Omni Technical Report | 2025 | 2503.20215 | vision-and-multimodal/speech-and-audio | Thinker-Talker model taking text, image, audio and video and streaming speech; the open omni-model reference. |
| 67 | Voxtral | 2025 | 2507.13264 | vision-and-multimodal/speech-and-audio | Open speech-understanding models with long-context audio input; the recent open ASR/audio-LLM release. |
| 68 | MMAU: A Massive Multi-Task Audio Understanding and Reasoning Benchmark | 2024 | 2410.19168 | vision-and-multimodal/speech-and-audio | Standard benchmark for audio-language model understanding and reasoning. |
| 69 | Recent Advances in Speech Language Models: A Survey | 2024 | 2410.03751 | vision-and-multimodal/speech-and-audio | Survey of speech LMs, tokenisers and evaluation. |

## Considered, not proposed

| Paper | Year | arXiv / URL | Folder | Why not |
|---|--:|---|---|---|
| EfficientNet: Rethinking Model Scaling for Convolutional Neural Networks | 2019 | 1905.11946 | vision-and-multimodal/vision | Classification-backbone era; ConvNeXt and ViTs are in library |
| YOLOv10: Real-Time End-to-End Object Detection | 2024 | 2405.14458 | vision-and-multimodal/vision | Incremental YOLO variant; RT-DETR carries the end-to-end idea |
| DUSt3R: Geometric 3D Vision Made Easy | 2023 | 2312.14132 | vision-and-multimodal/vision | Superseded by VGGT |
| Depth Anything 3 | 2025 | 2511.10647 | vision-and-multimodal/vision | Recent, little uptake yet; V2 is the reference |
| VideoMAE | 2022 | 2203.12602 | vision-and-multimodal/vision | Self-supervised video; fits representation-learning list |
| V-JEPA 2 | 2025 | 2506.09985 | vision-and-multimodal/vision | Self-supervised video world model; belongs to representation-learning/robotics lists |
| DINOv2, DINOv3, MAE, DINO, MoCo, ResNet | 2021 | 2304.07193 2508.10104 2111.06377 2104.14294 1911.05722 1512.03385 | vision-and-multimodal/vision | Already in library under other folders |
| ALIGN: Scaling Up Visual and Vision-Language Representation Learning With Noisy Text Supervision | 2021 | 2102.05918 | vision-and-multimodal/vision-language | Overlaps CLIP (in library) |
| BLIP | 2022 | 2201.12086 | vision-and-multimodal/vision-language | Superseded by BLIP-2 and LLaVA-style models |
| CoCa: Contrastive Captioners are Image-Text Foundation Models | 2022 | 2205.01917 | vision-and-multimodal/vision-language | Influential but little used in current stacks |
| Qwen2-VL | 2024 | 2409.12191 | vision-and-multimodal/vision-language | Superseded by Qwen2.5-VL and Qwen3-VL |
| InternVL3 | 2025 | 2504.10479 | vision-and-multimodal/vision-language | Overlaps Qwen VL reports; cut for depth |
| PaliGemma | 2024 | 2407.07726 | vision-and-multimodal/vision-language | Superseded by PaliGemma 2 |
| MM1: Methods, Analysis & Insights from Multimodal LLM Pre-training | 2024 | 2403.09611 | vision-and-multimodal/vision-language | Closed model; Cambrian-1 and Molmo cover the data-and-design lessons |
| What matters when building vision-language models? (Idefics2) | 2024 | 2405.02246 | vision-and-multimodal/vision-language | Overlaps Cambrian-1 in library |
| MMMU-Pro | 2024 | 2409.02813 | vision-and-multimodal/vision-language | Variant of MMMU; cut for depth |
| E5-V | 2024 | 2407.12580 | vision-and-multimodal/vision-language | Overlaps VLM2Vec and GME |
| MM-Embed | 2024 | 2411.02571 | vision-and-multimodal/vision-language | Overlaps UniIR and GME |
| jina-clip-v2 | 2024 | 2412.08802 | vision-and-multimodal/vision-language | Superseded by jina-embeddings-v4 |
| RzenEmbed | 2025 | 2510.27350 | vision-and-multimodal/vision-language | Leaderboard-driven, little uptake yet |
| Reasoning-Augmented Representations for Multimodal Retrieval | 2026 | 2602.07125 | vision-and-multimodal/vision-language | Recent, no uptake yet |
| Reproducible scaling laws for contrastive language-image learning (OpenCLIP) | 2022 | 2212.07143 | vision-and-multimodal/vision-language | Overlaps DataComp |
| Demystifying CLIP Data (MetaCLIP) | 2023 | 2309.16671 | vision-and-multimodal/vision-language | Overlaps DataComp |
| Video-MME | 2024 | 2405.21075 | vision-and-multimodal/vision-language | Video-specific benchmark; cut for depth |
| MathVista | 2023 | 2310.02255 | vision-and-multimodal/vision-language | Narrower than MMMU |
| DocVQA | 2020 | 2007.00398 | vision-and-multimodal/vision-language | Saturated; ViDoRe V3 and ColPali carry document retrieval |
| SmolVLM | 2025 | 2504.05299 | vision-and-multimodal/vision-language | Small-model niche |
| Chameleon: Mixed-Modal Early-Fusion Foundation Models | 2024 | 2405.09818 | vision-and-multimodal/vision-language | Unified generation; Transfusion proposed instead |
| Emu3: Next-Token Prediction is All You Need | 2024 | 2409.18869 | vision-and-multimodal/vision-language | Overlaps Chameleon/Transfusion |
| Improved DDPM | 2021 | 2102.09672 | generative-models/diffusion | Covered by ADM and EDM |
| SDXL | 2023 | 2307.01952 | generative-models/diffusion | Superseded by SD3 |
| Imagen (Photorealistic Text-to-Image Diffusion Models with Deep Language Understanding) | 2022 | 2205.11487 | generative-models/diffusion | Closed model, superseded; latent diffusion and DALL-E 2 in library |
| Imagen 3 | 2024 | 2408.07009 | generative-models/diffusion | Closed-model report with little method detail |
| Progressive Distillation | 2022 | 2202.00512 | generative-models/diffusion | Superseded by DMD2 |
| Latent Consistency Models | 2023 | 2310.04378 | generative-models/diffusion | Consistency Models in library; DMD2 preferred |
| One-step Diffusion with Distribution Matching Distillation | 2023 | 2311.18828 | generative-models/diffusion | Superseded by DMD2 |
| Adversarial Diffusion Distillation | 2023 | 2311.17042 | generative-models/diffusion | Overlaps DMD2 |
| Video Diffusion Models | 2022 | 2204.03458 | generative-models/diffusion | Dated; Stable Video Diffusion and Wan cover video |
| CogVideoX | 2024 | 2408.06072 | generative-models/diffusion | Overlaps Wan |
| HunyuanVideo | 2024 | 2412.03603 | generative-models/diffusion | Overlaps Wan |
| Genie: Generative Interactive Environments | 2024 | 2402.15391 | generative-models/diffusion | Interactive world models; belongs to robotics/world-model lists, Diffusion Game Engines in library |
| Emu Edit | 2023 | 2311.10089 | generative-models/diffusion | Overlaps FLUX Kontext |
| InstructPix2Pix | 2022 | 2211.09800 | generative-models/diffusion | Superseded by Kontext-style editors |
| Prompt-to-Prompt | 2022 | 2208.01626 | generative-models/diffusion | Technique paper; cut for depth |
| IP-Adapter | 2023 | 2308.06721 | generative-models/diffusion | Useful adapter, cut for depth after ControlNet |
| Large Language Diffusion Models (LLaDA) | 2025 | 2502.09992 | generative-models/diffusion | Already in library (llm/architecture) |
| Discrete Diffusion Modeling by Estimating the Ratios of the Data Distribution (SEDD) | 2023 | 2310.16834 | generative-models/diffusion | Overlaps MDLM |
| Mercury: Ultra-Fast Language Models Based on Diffusion | 2025 | 2506.17298 | generative-models/diffusion | Product report with little method detail |
| Step-by-Step Diffusion: An Elementary Tutorial | 2024 | 2406.08929 | generative-models/diffusion | Overlaps Understanding Diffusion Models and On the Mathematics of Diffusion Models (in library) |
| Training Diffusion Models with Reinforcement Learning (DDPO) | 2023 | 2305.13301 | generative-models/diffusion | Superseded by Diffusion-DPO and Flow-GRPO |
| DanceGRPO | 2025 | 2505.07818 | generative-models/diffusion | Overlaps Flow-GRPO |
| Qwen-Image Technical Report | 2025 | 2508.02324 | generative-models/diffusion | Qwen-Image-Layered in library covers the family |
| SANA | 2024 | 2410.10629 | generative-models/diffusion | Efficiency niche |
| Mean Flows for One-step Generative Modeling | 2025 | 2505.13447 | generative-models/diffusion | Recent, uptake unclear |
| Visual Autoregressive Modeling | 2024 | 2404.02905 | generative-models/diffusion | Autoregressive alternative; no clear folder fit |
| Guiding a Diffusion Model with a Bad Version of Itself | 2024 | 2406.02507 | generative-models/diffusion | Niche guidance variant |
| Extracting Training Data from Diffusion Models | 2023 | 2301.13188 | generative-models/diffusion | Belongs to trustworthy-ml list |
| ArcFlow | 2026 | 2602.09014 | generative-models/diffusion | Recent distillation variant, no uptake |
| DCGAN | 2015 | 1511.06434 | generative-models/gans-and-vaes | Dated; GAN and WGAN carry the lineage |
| Improved Training of Wasserstein GANs | 2017 | 1704.00028 | generative-models/gans-and-vaes | Overlaps WGAN |
| Progressive Growing of GANs | 2017 | 1710.10196 | generative-models/gans-and-vaes | Superseded by StyleGAN |
| pix2pix | 2016 | 1611.07004 | generative-models/gans-and-vaes | CycleGAN covers translation |
| VQ-VAE-2 | 2019 | 1906.00446 | generative-models/gans-and-vaes | Superseded by VQGAN |
| Real NVP / Glow | 2016 | 1605.08803 1807.03039 | generative-models/gans-and-vaes | Normalizing-flows review covers them |
| Scaling up GANs for Text-to-Image Synthesis (GigaGAN) | 2023 | 2303.05511 | generative-models/gans-and-vaes | Little uptake after diffusion |
| Alias-Free GANs (StyleGAN3) | 2021 | 2106.12423 | generative-models/gans-and-vaes | Incremental over StyleGAN2 |
| NVAE | 2020 | 2007.03898 | generative-models/gans-and-vaes | Niche hierarchical VAE |
| Pixel Recurrent Neural Networks | 2016 | 1601.06759 | generative-models/gans-and-vaes | Autoregressive pixel models; dated |
| Spectral Normalization for GANs | 2018 | 1802.05957 | generative-models/gans-and-vaes | Technique; cut for depth |
| Distil-Whisper | 2023 | 2311.00430 | vision-and-multimodal/speech-and-audio | Whisper in library; distillation variant |
| Fast Conformer | 2023 | 2305.05084 | vision-and-multimodal/speech-and-audio | Incremental over Conformer |
| SeamlessM4T | 2023 | 2308.11596 | vision-and-multimodal/speech-and-audio | Translation-focused |
| Google USM | 2023 | 2303.01037 | vision-and-multimodal/speech-and-audio | Closed model |
| NaturalSpeech 3 | 2024 | 2403.03100 | vision-and-multimodal/speech-and-audio | Overlaps VALL-E and Voicebox |
| SoundStream | 2021 | 2107.03312 | vision-and-multimodal/speech-and-audio | Overlaps EnCodec |
| MusicLM | 2023 | 2301.11325 | vision-and-multimodal/speech-and-audio | Closed; MusicGen proposed |
| Stable Audio Open | 2024 | 2407.14358 | vision-and-multimodal/speech-and-audio | Music niche |
| Qwen2-Audio | 2024 | 2407.10759 | vision-and-multimodal/speech-and-audio | Superseded by Qwen2.5-Omni |
| Qwen3-Omni | 2025 | 2509.17765 | vision-and-multimodal/speech-and-audio | Overlaps Qwen2.5-Omni; recent |
| Kimi-Audio | 2025 | 2504.18425 | vision-and-multimodal/speech-and-audio | Overlaps Qwen omni models |
| GPT-4o System Card | 2024 | 2410.21276 | vision-and-multimodal/speech-and-audio | Safety report, not method |
| Spirit LM | 2024 | 2402.05755 | vision-and-multimodal/speech-and-audio | Overlaps Moshi |
| CosyVoice / CosyVoice 2 | 2024 | 2407.05407 2412.10117 | vision-and-multimodal/speech-and-audio | Overlap VALL-E and F5-TTS (in library) |
| Seed-TTS | 2024 | 2406.02430 | vision-and-multimodal/speech-and-audio | Closed model |
