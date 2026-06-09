# LG채널 AI 콘테스트 — 씬별 프롬프트 시트 (초안 v1)

> 기획 마스터(`lg-channels-ai-contest-plan.md`)의 3번 구성에 따른 **씬바이씬 프롬프트 초안**.
> 콘셉트: **"경계를 넘는 지능"** — 공간 자체가 지능이 된다 (집→이동→오피스→도시).
> 무인물·무대사·시네마틱 앰비언트. 총 20:30 / ~150~200컷 목표 (아래는 핵심 ~46컷 골격).

---

## 0. 사용법

1. 모든 프롬프트 끝에 **고정 스타일 블록 + 고정 네거티브 블록**을 붙여 톤을 통일한다.
2. 각 씬은 **변동 요소(Subject/Scene/Camera/Lighting/Mood)** 만 기술 → 블록과 합쳐 완성.
3. **Kling으로 러프 → 확정 컷만 Veo/Sora 본 제작.**
4. 타이틀·자막·로고는 **후반 편집 합성**(프롬프트엔 `no text`).
5. '상태': ☐ 미생성 / ◐ 러프 / ● 확정.

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

| 씬# | 길이 | 비트 | [P] 변동 프롬프트 (영문) | 사운드 | 상태 |
|-----|------|------|--------------------------|--------|------|
| S01 | 0:00–0:06 | ★훅 | Total darkness, a single warm filament of light ignites and breathes, then thousands of cyan data particles awaken around it, slow push-in | sub-bass swell | ☐ |
| S02 | 0:06–0:14 | 훅 | Streams of glowing particles flow through dark space and begin tracing the wireframe contour of a living room, elegant orbital camera | crystalline chime in | ☐ |
| S03 | 0:14–0:30 | | Particle wireframe of a home solidifies into soft architectural surfaces, warm light pooling on the floor, slow dolly forward | rising pad | ☐ |
| S04 | 0:30–0:50 | | The formed room exhales a wave of warm amber light across walls and ceiling, surfaces softly illuminating in response | warm tone resolve | ☐ |
| S05 | 0:50–1:00 | | Camera drifts toward a window as dawn light seeps in, particles settling like dust in morning sun (title added in post) | quiet breath, BGM intro | ☐ |

---

## Ch.1 집 (1:00 – 5:30) — The Home that Cares

> 룩: 새벽 블루 → 아침 웜톤. 모티프: **보이지 않는 안무** (천장·벽·바닥이 거주자를 향해 반응).

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
| S18 | 5:00–5:30 | 전환 | Camera drifts past the window; outside, a sleek vehicle waits, light bridging from home to car, match-cut prep | transition riser | ☐ |

---

## Ch.2 이동 (5:30 – 10:00) — The Space that Moves

> 룩: 실내 웜 + 창밖 흐르는 풍경광. 모티프: **이동조차 거실** (차량 실내 = 생활공간).

| 씬# | 길이 | 비트 | [P] 변동 프롬프트 (영문) | 사운드 | 상태 |
|-----|------|------|--------------------------|--------|------|
| S19 | 5:30–5:42 | 전환 | Light flows from house threshold into a futuristic vehicle interior, doors breathing open, no driver, smooth approach | whoosh, soft tone | ☐ |
| S20 | 5:42–6:00 | | Spacious lounge-like vehicle cabin, warm fabric seats, panoramic glass, ambient interface glow, slow interior pan | calm BGM | ☐ |
| S21 | 6:00–6:25 | ★ | Through panoramic windows, landscape flows by in soft motion blur, cabin light shifting warm with the scenery, dolly | gentle motion pad | ☐ |
| S22 | 6:25–6:50 | | Cabin surfaces reconfigure subtly — a table glows into being, light anticipating need, macro detail | soft transform tone | ☐ |
| S23 | 6:50–7:15 | | Backlit passenger silhouette relaxes as ambient light wraps around them, the space adapting, slow arc | warm strings | ☐ |
| S24 | 7:15–7:45 | | Exterior cinematic shot: sleek vehicle gliding along a coastal road at golden hour, light trail behind, aerial tracking | sweeping BGM | ☐ |
| S25 | 7:45–8:15 | ★ | Interior: window glass transitions to a soft display of flowing data/landscape blend, ambient and dreamlike, push-in | shimmer | ☐ |
| S26 | 8:15–8:45 | | The vehicle's cyan light signature connects to passing infrastructure light nodes, subtle network lines, side tracking | connective pulse | ☐ |
| S27 | 8:45–9:15 | | Time-of-day shifts to dusk through the glass, cabin glow deepening amber, serene, slow orbit | evening pad | ☐ |
| S28 | 9:15–10:00 | 전환 | Vehicle arrives at a luminous building, light bridging from car to architecture, camera rises toward the structure | transition riser | ☐ |

---

## Ch.3 일터 (10:00 – 14:30) — The Place that Works

> 룩: 클린 화이트 + 자연광 + 그린 액센트. 모티프: **사람의 흐름에 반응하는 빌딩**.

| 씬# | 길이 | 비트 | [P] 변동 프롬프트 (영문) | 사운드 | 상태 |
|-----|------|------|--------------------------|--------|------|
| S29 | 10:00–10:15 | | Grand light-filled atrium of a smart office building, clean white surfaces, vertical garden, slow rising shot | bright ambient | ☐ |
| S30 | 10:15–10:40 | ★ | As light flows across the floor, glass partitions softly reconfigure space, anticipating the day, wide tracking | architectural pad | ☐ |
| S31 | 10:40–11:05 | | Ceiling light arrays shift warmth zone by zone following an unseen flow of people, overhead descending shot | subtle motion | ☐ |
| S32 | 11:05–11:35 | | Backlit silhouettes move through corridors; surfaces and air respond, soft light orienting toward them, slow arc | warm pulse | ☐ |
| S33 | 11:35–12:00 | | Macro of a living interface surface breathing with cyan-amber light, data gently flowing beneath glass | delicate texture | ☐ |
| S34 | 12:00–12:30 | ★ | Building facade at golden hour, energy/light flowing through its veins like a calm circulatory system, exterior orbit | swelling BGM | ☐ |
| S35 | 12:30–13:00 | | Green terraces and natural light integrate with the architecture, sustainable warm-tech harmony, slow crane up | airy strings | ☐ |
| S36 | 13:00–13:30 | | Night falls; the building glows softly, light signature pulsing in calm rhythm, wide establishing | evening hum | ☐ |
| S37 | 13:30–14:30 | 전환 | Camera pulls back and up from the single building to reveal it as one node among many city lights, scale reveal | epic riser | ☐ |

---

## Ch.4 도시 (14:30 – 19:00) — The City in Tune

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

---

## 연결 + 엔딩 (19:00 – 20:30) — Borderless

| 씬# | 길이 | 비트 | [P] 변동 프롬프트 (영문) | 사운드 | 상태 |
|-----|------|------|--------------------------|--------|------|
| S46 | 19:00–19:30 | ★ | Rapid elegant montage morph: home glow → vehicle light → building veins → city network, all one continuous light, seamless | montage swell | ☐ |
| S47 | 19:30–20:00 | | All scales unite into a single breathing web of warm light against deep navy, the boundaries dissolving, slow pull-back | resolve to calm | ☐ |
| S48 | 20:00–20:30 | 엔딩 | The light network softens to a single warm point, then gentle fade (closing copy + slogan added in post) | final warm chord | ☐ |

> **엔딩 카피(후반 합성, 택1 — 마스터 문서 9번 후보):**
> "삶의 모든 공간이, 당신을 향합니다. / Every space, in tune with you."
> + 슬로건 *Innovation in Tune with You*

---

## 확장 가이드 (이 골격을 ~150컷으로 늘릴 때)

- 각 챕터의 ★비트 사이를 **B-roll 디테일 컷**(macro 텍스처, 빛 반응, 공간 디테일)으로 채운다.
- 한 장면당 **2~3개 변형 프롬프트**를 만들어 Kling 러프로 베스트를 고른다.
- 챕터 내 컬러·렌즈를 고정 블록으로 유지해 룩 일관성을 지킨다.
- 전환(transition) 컷은 다음 챕터 색을 미리 1~2초 섞어 자연스럽게 잇는다.
