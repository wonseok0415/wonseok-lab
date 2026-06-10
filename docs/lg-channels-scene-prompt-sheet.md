# LG채널 AI 콘테스트 — 씬별 프롬프트 시트 (v2)

> 기획 마스터(`lg-channels-ai-contest-plan.md`) 3번 구성 기반.
> 콘셉트: **"경계를 넘는 지능"** — 공간 자체가 지능이 된다(집→이동→관리→도시).
> **'관리된 인물 현존'**: 한 사람의 하루를 실로 깐다(대부분 얼굴 회피, 👤만 얼굴 클로즈업).
> 시네마틱 앰비언트, 무대사. 총 약 20:40 / 골격 ~56컷.

---

## 0. 사용법

1. 모든 프롬프트 끝에 **고정 스타일 블록 + 고정 네거티브 블록**을 붙여 톤을 통일한다.
2. 각 씬은 **변동 요소(Subject/Scene/Camera/Lighting/Mood)** 만 기술 → 블록과 합쳐 완성.
3. **Midjourney 스틸로 룩 고정 → Kling i2v(주력) → Veo 3.1(히어로 컷).**
4. **모든 텍스트(타이틀·인터타이틀·설명 자막·로고)는 후반 편집 합성** — 영어도 AI 생성 시 깨짐. 프롬프트엔 항상 `no text`. 자막은 **영어 단독**, 이해 필요 구간마다 삽입(📝).
5. **액추에이터 모티프(⚙):** 각 챕터에 우아한 관절·구동 메커니즘 클로즈업 + 엔딩 직전 리빌. **실제 AXIUM 복제 금지** — 일반·우아한 정밀 메커니즘으로(보안·정확성).
6. **인물(👤·人):** 표기 규칙 — `人`= 뒷모습/손/실루엣/소프트포커스(얼굴 회피), `👤`= 얼굴 클로즈업(감정 앵커, **고정 캐릭터 레퍼런스로 생성**).
7. '상태': ☐ 미생성 / ◐ 러프 / ● 확정.

### 🔒 고정 스타일 블록 (전 컷 말미에 부착)
```
cinematic, anamorphic 50mm lens, shallow depth of field, subtle lens flare,
soft volumetric light, subsurface scattering, warm amber + deep navy palette,
bioluminescent cyan light accents, photorealistic, ultra-detailed, 16:9, FHD+
```
### 🚫 고정 네거티브 블록
```
no text, no captions, no logos, no distortion, no warped geometry,
no extra fingers, no crowd artifacts, no watermark, no flicker
```
### 👤 캐릭터 일관성 규칙 (가장 중요)
- **👤 얼굴 컷(3개)** 은 반드시 **하나의 고정 캐릭터 레퍼런스 이미지**에서 생성(Midjourney 캐릭터 레퍼런스 / Kling 다각도 일관성 / Runway 레퍼런스). 의상·헤어·연령 톤 통일, 여러 테이크 후 베스트.
- **人 컷**은 얼굴이 안 보이게 프레이밍(뒤·손·실루엣·소프트포커스) → 정체성 일관성 부담 0.

> ★ = 마이크로 비트(~90초 페이오프), [ ] = 챕터 시각 문법.

---

## 오프닝 (0:00 – 1:00) — 빛이 깨어난다

> **첫 10~15초 FAST 훅:** S01–S02에서 "공간=지능" 한 방.
> ▷ **인터타이틀**(후반): 타이틀 "경계를 넘는 지능 / *Borderless Intelligence*" + 슬로건 *Innovation in Tune with You*

| 씬# | 길이 | 비트 | [P] 변동 프롬프트 (영문) | 사운드 | 상태 |
|-----|------|------|--------------------------|--------|------|
| S01 | 0:00–0:06 | ★훅 | Total darkness, a single warm filament of light ignites and breathes, thousands of cyan data particles awaken around it, slow push-in | sub-bass swell | ☐ |
| S02 | 0:06–0:14 | 훅 | Glowing particles flow through dark space, tracing the wireframe contour of a living room, elegant orbital camera | crystalline chime | ☐ |
| S03 | 0:14–0:30 | | Particle wireframe solidifies into soft architectural surfaces, warm light pooling on the floor, slow dolly forward | rising pad | ☐ |
| S04 | 0:30–0:45 | | The room exhales a wave of warm amber light across walls and ceiling, surfaces softly illuminating | warm tone | ☐ |
| S05 | 0:45–1:00 | 人 | Camera drifts to a bed by a window at dawn; a hand stirs softly under light sheets, morning light gathering toward it (title in post) | quiet breath, BGM intro | ☐ |

---

## Ch.1 집 (1:00 – 6:00) — The Home that Cares  [친밀 마크로]

> ▷ **인터타이틀:** "공간이, 당신을 돌본다 / *The home that cares*"
> 📝 **설명 자막(영어):** "Intelligence, distributed into the space"
> 룩: 새벽 블루 → 아침 웜톤. 모티프: **보이지 않는 안무**(= LG 액추에이터의 정신). 👤 감정 앵커 #1.

| 씬# | 길이 | 비트 | [P] 변동 프롬프트 (영문) | 사운드 | 상태 |
|-----|------|------|--------------------------|--------|------|
| S06 | 1:00–1:12 | 人 | Pre-dawn minimalist bedroom, a figure stirs under sheets (back to camera), faint cyan standby glow along edges, static wide | low hum | ☐ |
| S07 | 1:12–1:24 | | Ceiling panels subtly tilt and breathe, a ripple of soft light travels across the ceiling, slow upward tracking | soft whisper | ☐ |
| ⚙A1 | 1:24–1:32 | ⚙ | Macro: a slender elegant robotic joint smoothly rotating a ceiling/blind panel, exposed precision actuator gleaming softly | refined servo | ☐ |
| S08 | 1:32–1:44 | ★ | Warm amber glow spreads across the floor toward the bed (warmth proxy), low tracking shot near floor | warm chime | ☐ |
| S09 | 1:44–2:00 | 人 | Curtains breathe open on their own, morning light flooding in, air particles drifting; the figure sits up (back) | airy swell | ☐ |
| S10 | 2:00–2:20 | 人 | Close on hands resting on a smart surface as it awakens with gentle interface glow, no face, macro | water trickle | ☐ |
| S11 | 2:20–2:45 | 👤 | HERO — the person's face catches the first morning light, eyes opening calm, the warm room softly orienting around them *(fixed character ref)* | tender pad | ☐ |
| S12 | 2:45–3:05 | | Kitchen surfaces awaken with subtle glow, water gently begins to flow, no hands, close macro | BGM build | ☐ |
| S13 | 3:05–3:25 | | A low rounded domestic robot form (NOT humanoid) glides silently, light trailing, side tracking | smooth whirr | ☐ |
| S14 | 3:25–3:45 | | Light gently flows ahead across the floor toward a doorway, anticipating movement (predictive proxy) | soft motion | ☐ |
| S15 | 3:45–4:10 | ★人 | The person (back/silhouette) walks through; surfaces orient and illuminate toward them in sequence, slow arc | warm resolve | ☐ |
| S16 | 4:10–4:35 | | Hundreds of micro light points across walls pulse once in unison like a calm breath, wide symmetrical | unison chime | ☐ |
| S17 | 4:35–5:00 | | Macro of a warm interface ripple expanding across a smart surface, cyan meeting amber | delicate texture | ☐ |
| S18 | 5:00–5:25 | 人 | Wide of the whole living space in harmonious morning light, plants turning to light, the person (silhouette) preparing to leave by the door | full warm BGM | ☐ |
| S19 | 5:25–6:00 | 전환 | The person steps toward the entrance; through the window a sleek electric van (PBV) waits, light bridging home→vehicle, match-cut prep | transition riser | ☐ |

---

## Ch.2 이동 (6:00 – 10:00) — The Space that Moves (슈필라움)  [흐르는 모션]

> ▷ **인터타이틀:** "머무름이 곧, 이동이 된다 / *The space that moves*"
> 📝 **설명 자막(영어):** "Spielraum — your living room, in motion"
> 룩: 실내 웜 + 창밖 흐르는 풍경광. ⚠️ 스포츠카 아님 — 프리미엄 전기 밴/PBV형 '움직이는 생활공간'.

| 씬# | 길이 | 비트 | [P] 변동 프롬프트 (영문) | 사운드 | 상태 |
|-----|------|------|--------------------------|--------|------|
| S20 | 6:00–6:12 | 전환人 | Light flows from the home threshold into a sleek modern electric van interior, sliding door breathing open, the person stepping in (back), no driver | whoosh | ☐ |
| S21 | 6:12–6:30 | 人 | Spacious modular lounge cabin, warm fabric seats facing, wood + textile, panoramic glass roof, ambient hub glow, person settling (profile/back), slow interior pan | calm BGM | ☐ |
| S22 | 6:30–6:55 | ★人 | Through panoramic windows, landscape flows by in soft motion blur, cabin light shifting warm; the person watches (silhouette), dolly | motion pad | ☐ |
| ⚙A2 | 6:55–7:03 | ⚙ | Macro: refined linear actuators silently gliding the cabin seats and table into a new layout (lounge→studio mode), elegant mechanism | smooth servo | ☐ |
| S23 | 7:03–7:25 | | A compact built-in galley awakens — fridge and warm cabinet glowing softly to life, macro detail | transform tone | ☐ |
| S24 | 7:25–7:50 | | Exterior cinematic: a sleek premium electric van (boxy PBV) gliding along a coastal road at golden hour, light trail, aerial tracking | sweeping BGM | ☐ |
| S25 | 7:50–8:15 | 人 | Cabin reconfigures around the person, ambient light wrapping them, the moving space adapting like a living room, slow arc | warm strings | ☐ |
| S26 | 8:15–8:40 | | Window glass transitions to a soft ambient display blending landscape and gentle data light, dreamlike, push-in | shimmer | ☐ |
| S27 | 8:40–9:10 | | The van's cyan light signature connects to passing infrastructure nodes, subtle network lines, the boundary between home and road dissolving, side tracking | connective pulse | ☐ |
| S28 | 9:10–10:00 | 전환 | Van arrives at a luminous residential tower complex at dusk, light bridging vehicle→architecture, camera rises | transition riser | ☐ |

---

## Ch.3 관리 (10:00 – 13:30) — The Spaces in Concert (ThinQ Pro)  [리듬·기하·스케일 · 최단]

> ▷ **인터타이틀:** "하나의 집에서, 수많은 공간으로 / *From one home to many*"
> 📝 **설명 자막(영어):** "One intelligence, countless spaces"
> 룩: 클린 화이트 + 자연광 + 그린 액센트. **주거단지→오피스**. 사람은 원경 다수 실루엣(얼굴 불필요).

| 씬# | 길이 | 비트 | [P] 변동 프롬프트 (영문) | 사운드 | 상태 |
|-----|------|------|--------------------------|--------|------|
| S29 | 10:00–10:15 | | Slow aerial establishing of a large residential apartment community at morning, many homes, each window softly lit | bright ambient | ☐ |
| S30 | 10:15–10:40 | ★ | Hundreds of apartment windows pulse warm light in gentle coordinated waves, like one breath shared across many homes, high aerial | architectural pad | ☐ |
| S31 | 10:40–11:00 | 人 | Inside a residential building's shared lobby, distant silhouettes moving, surfaces and glass softly reconfiguring, wide tracking | subtle motion | ☐ |
| S32 | 11:00–11:25 | | Macro of a calm constellation of light points connecting into a living map of many managed homes (abstract, NOT literal UI), shallow focus | delicate texture | ☐ |
| ⚙A3 | 11:25–11:33 | ⚙ | Macro: a precise actuator smoothly swinging a glass partition/door, the same elegant joint repeated across many units | refined servo | ☐ |
| S33 | 11:33–12:00 | 전환 | The intelligence extends beyond homes into a commercial office building — a light-filled workspace where ceiling arrays shift warmth zone by zone following an unseen flow of people, overhead descending | warm pulse | ☐ |
| S34 | 12:00–12:30 | ★ | Energy flowing through a building's veins like a calm circulatory system; a faint pulse gently heals a dim node back to warm light (predictive care), exterior orbit | swelling BGM | ☐ |
| S35 | 12:30–13:00 | 人 | Many backlit silhouettes move through a corridor; many doors and surfaces orient toward them in sequence, slow arc | airy strings | ☐ |
| S36 | 13:00–13:30 | 전환 | Green terraces and natural light across the building cluster; camera pulls back and up — the cluster becomes a constellation of light nodes within a larger city grid, scale reveal | epic riser | ☐ |

---

## Ch.4 도시 (13:30 – 18:00) — The City in Tune  [광활 항공 · 클라이맥스]

> ▷ **인터타이틀:** "지능이, 도시가 된다 / *The city in tune*"
> 📝 **설명 자막(영어):** "When intelligence becomes a city"
> 룩: 골든아워→블루아워 시네마틱 + 친환경 그린. 👤 감정 앵커 #2.

| 씬# | 길이 | 비트 | [P] 변동 프롬프트 (영문) | 사운드 | 상태 |
|-----|------|------|--------------------------|--------|------|
| S37 | 13:30–13:48 | ★ | Sweeping aerial of a future city at golden hour, buildings linked by faint flowing light lines, cinematic drone shot | grand BGM | ☐ |
| S38 | 13:48–14:15 | | Energy flows visualized as soft light rivers between districts, calm and orchestrated, high aerial tracking | flowing pad | ☐ |
| S39 | 14:15–14:40 | | Wind turbines and solar fields glowing with cyan energy accents, sustainable infrastructure, slow aerial orbit | airy swell | ☐ |
| ⚙A4 | 14:40–14:50 | ⚙ | Cinematic close-up at scale: an elegant articulated mechanism adjusting building louvers or a wind turbine pitch, the actuator as city-scale muscle, golden hour | deep mechanism | ☐ |
| S40 | 14:50–15:15 | | A serene data center hall, rows of softly pulsing light, cool yet warm-edged, slow dolly through | deep hum | ☐ |
| S41 | 15:15–15:45 | ★人 | The person stands on a high terrace overlooking the vast luminous city at dusk (silhouette/back), the city breathing in light below | reverent pad | ☐ |
| S42 | 15:45–16:10 | | Streets below: ambient public light adjusting to the flow of life, gentle human-scale, descending shot | tender motion | ☐ |
| S43 | 16:10–16:40 | | Transition to blue hour, the whole city breathing in a slow pulse of light, ultra-wide aerial | building BGM | ☐ |
| S44 | 16:40–17:15 | | Light lines from homes, vehicles and buildings converging into the city network, macro-to-macro flow | orchestral build | ☐ |
| S45 | 17:15–17:40 | 👤 | HERO — the person's face lit by the city glow, calm awe, the light network softly reflected in their eyes *(fixed character ref)* | swell | ☐ |
| S46 | 17:40–18:00 | | Cinematic night cityscape fully alive with calm coordinated light, slow majestic orbit, awe and warmth | full orchestral | ☐ |

---

## 연결 + 엔딩 (18:00 – 20:40) — Borderless & 귀가  [몽타주 → 귀가 → resolve]

> 📝 **설명 자막(영어):** "Every motion begins with an actuator" (⚙AR 위에)
> 👤 감정 앵커 #3 (귀가). 아크가 집으로 닫힌다.

| 씬# | 길이 | 비트 | [P] 변동 프롬프트 (영문) | 사운드 | 상태 |
|-----|------|------|--------------------------|--------|------|
| ⚙AR | 18:00–18:25 | ⚙리빌 | HERO REVEAL — cinematic montage of elegant LG-style actuators/joints across home, vehicle and building, the hidden muscles that move every space, beautiful precision macro, warm key light | reveal swell | ☐ |
| S47 | 18:25–18:50 | ★빠름 | Rapid elegant montage morph: home glow → vehicle light → building veins → city network, all one continuous light, seamless, faster tempo | montage swell | ☐ |
| S48 | 18:50–19:20 | | All scales unite into a single breathing web of warm light against deep navy, the boundaries dissolving, slow pull-back | resolve to calm | ☐ |
| S49 | 19:20–19:50 | 전환人 | Match-cut back to the home at night — the person returns through the door, the home warmly waking to welcome them (full circle), light gathering toward them | warm return | ☐ |
| S50 | 19:50–20:15 | 👤 | HERO — the person settles in; the space softens around them, a warm point of light resting beside them like an unseen companion *(fixed character ref)* | tender chord | ☐ |
| S51 | 20:15–20:40 | 엔딩 | The light network softens to a single warm point, then a gentle fade (closing copy + slogan added in post) | final warm chord | ☐ |

> **엔딩 카피(후반 합성, 택1 — 마스터 문서 9번 후보):**
> "삶의 모든 공간이, 당신을 향합니다. / *Every space, in tune with you.*" + *Innovation in Tune with You*

---

## 확장 가이드 (이 골격을 ~150컷으로 늘릴 때)

- 각 챕터의 ★비트 사이를 **B-roll 디테일 컷**(macro 텍스처·빛 반응·공간 디테일)으로 채운다.
- 한 장면당 **2~3개 변형 프롬프트** → Kling 러프로 베스트 선택.
- **👤 얼굴 컷(S11·S45·S50)은 같은 캐릭터 레퍼런스로** — 의상·헤어 통일, 정체성 일관성 유지.
- **人 컷은 얼굴 회피 프레이밍** 유지(뒤·손·실루엣) → 일관성 부담 없이 인물감만.
- 챕터 내 컬러·렌즈·**시각 문법**을 고정해 룩을 지키되, 전환·몽타주엔 템포를 바꿔 단조로움을 깬다.
- 전환 컷은 다음 챕터 색을 미리 1~2초 섞어 자연스럽게 잇는다.
