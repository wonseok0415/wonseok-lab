# LG채널 AI 콘테스트 — 씬별 프롬프트 시트 (초안 v1)

> 기획 마스터(`lg-channels-ai-contest-plan.md`)의 3번 구성에 따른 **씬바이씬 프롬프트 초안**.
> 콘셉트: **"경계를 넘는 지능"** — 공간 자체가 지능이 된다 (집→이동→오피스→도시).
> 무인물·무대사·시네마틱 앰비언트. 총 20:30 / ~150~200컷 목표 (아래는 핵심 ~46컷 골격).

---

## 0. 사용법

1. 모든 프롬프트 끝에 **고정 스타일 블록 + 고정 네거티브 블록**을 붙여 톤을 통일한다.
2. 각 씬은 **변동 요소(Subject/Scene/Camera/Lighting/Mood)** 만 기술 → 블록과 합쳐 완성.
3. **Kling으로 러프 → 확정 컷만 Veo/Sora 본 제작.**
4. **모든 텍스트(타이틀·인터타이틀·설명 자막·로고)는 후반 편집 합성** — 영어도 AI 생성 시 깨짐. 프롬프트엔 항상 `no text`. 자막은 **영어 단독**, 이해가 필요한 구간마다 삽입(📝 표기).
5. **액추에이터 모티프(⚙ 표기):** 각 챕터에 우아한 관절·구동 메커니즘 클로즈업 1컷 이상 + 엔딩 직전 '메커니즘 리빌'. → "LG가 무엇을 만드는가"를 시청자가 보게 한다. **단, 실제 AXIUM 복제 금지** — 일반적·우아한 정밀 메커니즘으로(보안·정확성).
6. '상태': ☐ 미생성 / ◐ 러프 / ● 확정.

### 🔒 고정 스타일 블록 (전 컷 말미에 부착)
```
cinematic, anamorphic 50mm lens, shallow depth of field, subtle lens flare,
soft volumetric light, subsurface scattering, warm amber + deep navy palette,
bioluminescent cyan light accents, photorealistic, ultra-detailed, 16:9, FHD+
```
### 🚫 고정 네거티브 블록
```
no text, no captions, no logos, no humans (or backlit silhouette only),
no distortion, no warped geometry, no extra fingers, no watermark, no flicker
```

> 표의 [P] = 씬별 변동 프롬프트. 실제 생성 시 `[P] + 고정 스타일 + 고정 네거티브`.
> ★ = 마이크로 비트(약 90초 간격 페이오프 지점).

---

## 오프닝 (0:00 – 1:00) — 빛이 깨어난다

> **첫 10~15초 FAST 훅:** S01–S02에서 "공간=지능" 한 방. 추상 서사는 그 뒤에.
> ▷ **인터타이틀**(후반 합성, S05 부근): 타이틀 "경계를 넘는 지능 / *Borderless Intelligence*" + 슬로건 *Innovation in Tune with You*

| 씬# | 길이 | 비트 | [P] 변동 프롬프트 (영문) | 사운드 | 상태 |
|-----|------|------|--------------------------|--------|------|
| S01 | 0:00–0:06 | ★훅 | Total darkness, a single warm filament of light ignites and breathes, then thousands of cyan data particles awaken around it, slow push-in | sub-bass swell | ☐ |
| S02 | 0:06–0:14 | 훅 | Streams of glowing particles flow through dark space and begin tracing the wireframe contour of a living room, elegant orbital camera | crystalline chime in | ☐ |
| S03 | 0:14–0:30 | | Particle wireframe of a home solidifies into soft architectural surfaces, warm light pooling on the floor, slow dolly forward | rising pad | ☐ |
| S04 | 0:30–0:50 | | The formed room exhales a wave of warm amber light across walls and ceiling, surfaces softly illuminating in response | warm tone resolve | ☐ |
| S05 | 0:50–1:00 | | Camera drifts toward a window as dawn light seeps in, particles settling like dust in morning sun (title added in post) | quiet breath, BGM intro | ☐ |

---

## Ch.1 집 (1:00 – 5:30) — The Home that Cares

> ▷ **인터타이틀**(후반 합성): "공간이, 당신을 돌본다 / *The home that cares*"
> 📝 **설명 자막(영어):** "Intelligence, distributed into the space"
> 룩: 새벽 블루 → 아침 웜톤. 모티프: **보이지 않는 안무** (천장·벽·바닥이 거주자를 향해 반응 = LG 액추에이터의 정신).

| 씬# | 길이 | 비트 | [P] 변동 프롬프트 (영문) | 사운드 | 상태 |
|-----|------|------|--------------------------|--------|------|
| S06 | 1:00–1:08 | | Minimalist modern living room at pre-dawn, blue hour, everything still, faint cyan standby glow along edges, static wide | low ambient hum | ☐ |
| S07 | 1:08–1:18 | | Ceiling panels subtly tilt and breathe, a ripple of soft light travels across the ceiling, slow upward tracking | soft mechanical whisper | ☐ |
| S08 | 1:18–1:30 | ★ | Warm amber glow spreads across the floor surface like sunrise, indicating gentle warmth, low tracking shot near floor | warm chime | ☐ |
| S09 | 1:30–1:45 | | Curtains breathe open on their own, morning light flooding in, air particles drifting, smooth reveal | airy swell | ☐ |
| S10 | 1:45–2:00 | | Kitchen surfaces awaken with subtle interface glow, water gently begins to flow, no hands, close macro details | water trickle, BGM build | ☐ |
| S11 | 2:00–2:20 | | A low, abstract domestic robot form (soft rounded silhouette, NOT humanoid) glides silently, light trailing, side tracking | smooth whirr | ☐ |
| S12 | 2:20–2:45 | | Light gently flows ahead across the floor toward a doorway, anticipating movement, the space leaning toward an unseen presence | tender pad | ☐ |
| S13 | 2:45–3:10 | ★ | Backlit human silhouette enters frame (face unseen); surrounding surfaces softly illuminate and orient toward them, slow arc | warm resolve | ☐ |
| S14 | 3:10–3:35 | | Hundreds of micro light points across walls pulse once in unison like a calm breath, wide symmetrical shot | unison chime | ☐ |
| S15 | 3:35–4:00 | | Sunlight climbs the wall as time-lapse, plants turning toward light, the home fully warm and awake, slow orbit | bright pad | ☐ |
| S16 | 4:00–4:30 | | Close on a warm interface ripple expanding across a smart surface, bioluminescent cyan meeting amber, macro | delicate texture | ☐ |
| S17 | 4:30–5:00 | | Wide of the whole living space in harmonious morning light, everything in quiet orchestrated motion, slow push-in | full warm BGM | ☐ |
| S18 | 5:00–5:30 | 전환 | Camera drifts past the window; outside, a sleek electric van (PBV) waits, light bridging from home to vehicle, match-cut prep | transition riser | ☐ |
| ⚙A1 | ~8s | ⚙ | Macro close-up: a slender elegant LG robotic joint/actuator smoothly rotating a ceiling or cabinet panel, exposed precision mechanism gleaming softly, graceful motion *(insert near S07–S08)* | refined servo hum | ☐ |

---

## Ch.2 이동 (5:30 – 10:00) — The Space that Moves (슈필라움)

> ▷ **인터타이틀**(후반 합성): "머무름이 곧, 이동이 된다 / *The space that moves*"
> 룩: 실내 웜 + 창밖 흐르는 풍경광. 모티프: **슈필라움** — LG×기아 PV5형 가변 모빌리티 라운지(차량=거실).
> 📝 **설명 자막(영어):** "Spielraum — your living room, in motion"
> ⚠️ 스포츠카 아님. 프리미엄 전기 밴/PBV 형태의 '움직이는 생활공간'.

| 씬# | 길이 | 비트 | [P] 변동 프롬프트 (영문) | 사운드 | 상태 |
|-----|------|------|--------------------------|--------|------|
| S19 | 5:30–5:42 | 전환 | Light flows from the home threshold into the interior of a sleek modern electric van, sliding door breathing open, no driver, smooth approach | whoosh, soft tone | ☐ |
| S20 | 5:42–6:00 | | Spacious modular lounge cabin of a premium electric van, warm fabric seats facing each other, wood and soft textile, panoramic glass roof, ambient hub glow, slow interior pan | calm BGM | ☐ |
| S21 | 6:00–6:25 | ★ | Through panoramic windows, landscape flows by in soft motion blur, cabin light shifting warm with the scenery, dolly | gentle motion pad | ☐ |
| S22 | 6:25–6:50 | | A compact built-in galley awakens — fridge and warm cabinet glowing softly to life, no hands, macro detail | soft transform tone | ☐ |
| S23 | 6:50–7:15 | | Cabin reconfigures itself: seats and a low table glide into a new layout (lounge transforming to studio mode), light anticipating, wide | mechanical hush | ☐ |
| S24 | 7:15–7:45 | | Exterior cinematic shot: a sleek premium electric van (boxy PBV silhouette) gliding along a coastal road at golden hour, light trail behind, aerial tracking | sweeping BGM | ☐ |
| S25 | 7:45–8:15 | ★ | Backlit passenger silhouette relaxes as ambient cabin light wraps around them, the moving space adapting like a living room, slow arc | warm strings | ☐ |
| S26 | 8:15–8:45 | | Window glass transitions to a soft ambient display blending landscape and gentle data light, dreamlike, push-in | shimmer | ☐ |
| S27 | 8:45–9:15 | | The van's cyan light signature connects to passing infrastructure nodes, subtle network lines, the boundary between home and road dissolving, side tracking | connective pulse | ☐ |
| S28 | 9:15–10:00 | 전환 | Van arrives at a luminous building complex at dusk, light bridging from vehicle to architecture, camera rises toward the structures | transition riser | ☐ |
| ⚙A2 | ~8s | ⚙ | Macro close-up: refined linear actuators silently gliding the cabin seats and table into a new layout, exposed elegant mechanism — the muscle behind the moving space *(insert near S23)* | smooth servo | ☐ |

---

## Ch.3 관리 (10:00 – 14:30) — The Spaces in Concert (ThinQ Pro)

> ▷ **인터타이틀**(후반 합성): "하나의 집에서, 수많은 공간으로 / *From one home to many*"
> 📝 **설명 자막(영어):** "One intelligence, countless spaces" (주거단지→오피스 확장 구간에)
> 룩: 클린 화이트 + 자연광 + 그린 액센트. 모티프: **여러 공간이 한 호흡으로** — ThinQ Pro로
> **주거단지에서 시작해 오피스까지** 수많은 공간이 하나의 지능에 조율. 관제 = '빛의 별자리'(추상, 리터럴 UI 아님).

| 씬# | 길이 | 비트 | [P] 변동 프롬프트 (영문) | 사운드 | 상태 |
|-----|------|------|--------------------------|--------|------|
| S29 | 10:00–10:15 | | Slow aerial establishing of a large residential apartment community at early morning, many homes, each window softly lit | bright ambient | ☐ |
| S30 | 10:15–10:40 | ★ | Hundreds of apartment windows pulse warm light in gentle coordinated waves, like one breath shared across many homes, high aerial | architectural pad | ☐ |
| S31 | 10:40–11:05 | | Inside a clean residential building's shared lobby, surfaces and glass softly reconfiguring, anticipating the day, wide tracking | subtle motion | ☐ |
| S32 | 11:05–11:35 | | Macro of a calm constellation of light points connecting into a living map of many managed homes (abstract asset map as light, NOT literal UI), shallow focus | delicate texture | ☐ |
| S33 | 11:35–12:00 | 전환 | The same intelligence extends beyond homes into a commercial office building — a light-filled workspace where ceiling arrays shift warmth zone by zone following an unseen flow of people, overhead descending | warm pulse | ☐ |
| S34 | 12:00–12:30 | ★ | Energy flowing through a building's veins like a calm circulatory system; a faint pulse gently heals a dim node back to warm light (predictive care), exterior orbit | swelling BGM | ☐ |
| S35 | 12:30–13:00 | | Backlit silhouettes move through a corridor; many doors and surfaces orient toward them in sequence, slow arc | airy strings | ☐ |
| S36 | 13:00–13:30 | | Green terraces and natural light integrate across the building cluster, sustainable warm-tech harmony, slow crane up | bright pad | ☐ |
| S37 | 13:30–14:30 | 전환 | Camera pulls back and up; the building cluster becomes a constellation of light nodes within a larger city grid, scale reveal | epic riser | ☐ |
| ⚙A3 | ~8s | ⚙ | Macro close-up: a precise actuator smoothly swinging a glass partition or door, the same elegant joint repeated across many units — one mechanism, countless spaces *(insert near S31–S33)* | refined servo | ☐ |

---

## Ch.4 도시 (14:30 – 19:00) — The City in Tune

> ▷ **인터타이틀**(후반 합성): "지능이, 도시가 된다 / *The city in tune*"
> 📝 **설명 자막(영어):** "When intelligence becomes a city"
> 룩: 골든아워→블루아워 시네마틱 + 친환경 그린. 모티프: **지능이 도시 스케일로**.

| 씬# | 길이 | 비트 | [P] 변동 프롬프트 (영문) | 사운드 | 상태 |
|-----|------|------|--------------------------|--------|------|
| S38 | 14:30–14:45 | ★ | Sweeping aerial of a future city at golden hour, buildings linked by faint flowing light lines, cinematic drone shot | grand BGM | ☐ |
| S39 | 14:45–15:15 | | Energy flows visualized as soft light rivers between districts, calm and orchestrated, high aerial tracking | flowing pad | ☐ |
| S40 | 15:15–15:45 | | Wind turbines and solar fields glowing with cyan energy accents, sustainable infrastructure, slow aerial orbit | airy swell | ☐ |
| S41 | 15:45–16:15 | | A serene data center hall, rows of softly pulsing light, cool yet warm-edged, slow dolly through | deep hum | ☐ |
| S42 | 16:15–16:45 | ★ | Streets below: ambient public light adjusting to the flow of life, gentle and human-scale, descending shot | tender motion | ☐ |
| S43 | 16:45–17:15 | | Transition to blue hour, the whole city breathing in a slow pulse of light, ultra-wide aerial | reverent pad | ☐ |
| S44 | 17:15–17:45 | | Light lines from homes, vehicles, buildings all converging into the city network, macro-to-macro flow | building BGM | ☐ |
| S45 | 17:45–19:00 | | Cinematic night cityscape fully alive with calm coordinated light, awe and warmth, slow majestic orbit | full orchestral pad | ☐ |
| ⚙A4 | ~8s | ⚙ | Cinematic close-up at scale: an elegant articulated mechanism adjusting building louvers or a wind turbine pitch, the actuator as city-scale muscle, golden hour | deep mechanism tone | ☐ |

---

## 연결 + 엔딩 (19:00 – 20:30) — Borderless

> 📝 **설명 자막(영어):** "Every motion begins with an actuator" (⚙AR 리빌 위에)

| 씬# | 길이 | 비트 | [P] 변동 프롬프트 (영문) | 사운드 | 상태 |
|-----|------|------|--------------------------|--------|------|
| ⚙AR | 19:00–19:20 | ⚙리빌 | HERO REVEAL — cinematic montage of elegant LG actuators/joints across home, vehicle and building, the hidden muscles that move every space, beautiful precision macro, warm key light | reveal motif swell | ☐ |
| S46 | 19:20–19:45 | ★ | Rapid elegant montage morph: home glow → vehicle light → building veins → city network, all one continuous light, seamless | montage swell | ☐ |
| S47 | 19:45–20:10 | | All scales unite into a single breathing web of warm light against deep navy, the boundaries dissolving, slow pull-back | resolve to calm | ☐ |
| S48 | 20:10–20:40 | 엔딩 | The light network softens to a single warm point, then gentle fade (closing copy + slogan added in post) | final warm chord | ☐ |

> **엔딩 카피(후반 합성, 택1 — 마스터 문서 9번 후보):**
> "삶의 모든 공간이, 당신을 향합니다. / Every space, in tune with you."
> + 슬로건 *Innovation in Tune with You*

---

## 확장 가이드 (이 골격을 ~150컷으로 늘릴 때)

- 각 챕터의 ★비트 사이를 **B-roll 디테일 컷**(macro 텍스처, 빛 반응, 공간 디테일)으로 채운다.
- 한 장면당 **2~3개 변형 프롬프트**를 만들어 Kling 러프로 베스트를 고른다.
- 챕터 내 컬러·렌즈를 고정 블록으로 유지해 룩 일관성을 지킨다.
- 전환(transition) 컷은 다음 챕터 색을 미리 1~2초 섞어 자연스럽게 잇는다.
