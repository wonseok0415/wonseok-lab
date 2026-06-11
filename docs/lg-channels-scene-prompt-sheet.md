# LG채널 AI 콘테스트 — 씬별 프롬프트 시트 (v3)

> 기획 마스터(`lg-channels-ai-contest-plan.md`) 3번 구성 기반.
> 콘셉트: **"경계를 넘는 지능"** — 공간 자체가 지능이 된다(집→이동→공간들→도시).
> **가족(부부+아이)의 하루**가 감정의 실. 얼굴 앵커는 **주인공 1인 × 3컷(👤)** 만.
> AXIUM 4영역(Home/Hospitality/Logistics/Manufacturing)은 **하이브리드**로: 환대는 Ch.3,
> 물류·제조는 Ch.4 '무대 뒤', ⚙AR 리빌에서 수렴. 총 약 20:40 / 골격 ~58컷.

---

## 0. 사용법

1. 모든 프롬프트 끝에 **고정 스타일 블록 + 고정 네거티브 블록**을 붙여 톤을 통일한다.
2. 각 씬은 **변동 요소(Subject/Scene/Camera/Lighting/Mood)** 만 기술 → 블록과 합쳐 완성.
3. **Midjourney 스틸로 룩 고정 → Kling i2v(주력) → Veo 3.1(히어로 컷).**
4. **모든 텍스트는 후반 편집 합성** — 영어도 AI 생성 시 깨짐. 프롬프트엔 항상 `no text`. 자막은 **영어 단독**(📝).
5. **액추에이터(⚙):** 각 챕터에 우아한 관절·구동 클로즈업 + 엔딩 직전 4영역 리빌. **AXIUM 공식 홈페이지 공개 이미지를 i2v 레퍼런스로 활용 가능**(내부 기밀 자산은 배제, 왜곡 재현 주의).
6. **인물 표기:** `人`=얼굴 회피(뒷모습·손·실루엣·소프트포커스) / `👤`=주인공 얼굴 클로즈업(고정 레퍼런스) / **아이·배우자 얼굴 생성 금지**(항상 人).
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
- **주인공**: 단 하나의 고정 캐릭터 레퍼런스 세트에서 👤 3컷(S11·S45·S51) 생성. 아래 **캐릭터 레퍼런스 정의** 참조.
- **배우자·아이**: 얼굴 절대 노출 금지 — 손·뒷모습·실루엣·소프트포커스만. (아이 얼굴은 AI 왜곡 빈발 + 글로벌 방영 민감성)
- 가족 와이드 컷은 **역광 실루엣**으로 통일하면 일관성 부담 0.

---

## 0.5 캐릭터 레퍼런스 정의 (✅ 확정)

### 주인공 — "JUN" (워킹네임)
| 항목 | 정의 | 근거 |
|------|------|------|
| 정체성 | **30대 중반 한국인 아버지**, 따뜻하고 차분한 인상 | '가전=엄마' 클리셰 회피·신선함, 엔딩(잠든 아이 안기)과 정합, K-브랜드 정체성. *여성 버전 필요 시 [CHAR] 블록 한 줄만 교체* |
| 외형 | 짧고 단정한 검은 머리, 면도한 깔끔한 얼굴, 부드러운 눈매, 보통 체격. **안경·수염·문신 등 변동 잦은 디테일 배제**(AI 일관성) | 단순할수록 컷 간 동일성 유지 쉬움 |
| 의상 (**하루 단일 복장**) | **웜 베이지 니트(이너 화이트 티) + 네이비 팬츠** | 의상=일관성의 절반. 아침 집·오피스·레스토랑·테라스 모두 성립. 팔레트(앰버+네이비) 정합 |

**[CHAR] 고정 블록 (👤 컷 + 주인공 등장 人 컷 프롬프트 앞에 부착):**
```
A Korean man in his mid-30s, short neat black hair, clean-shaven, gentle warm
eyes, medium build, wearing a warm beige knit sweater over a white tee and
navy trousers
```

### 가족 (얼굴 금지 — 실루엣·의상 일관성용)
**[SPOUSE] 블록:** `a Korean woman in her mid-30s, shoulder-length dark hair softly tied, ivory cardigan and sage-green pants (face never visible)`
**[CHILD] 블록:** `a 5-year-old little girl, soft dark bobbed hair, mustard-yellow hoodie and grey pants (face never visible)`
> 딸의 **머스터드 옐로 후드 + 단발머리 실루엣** = 얼굴 없이도 '같은 아이'임을 색·형태로 추적시키는 장치(전 챕터 시각 앵커).

### 마스터 레퍼런스 생성 (본 제작 1단계)
Midjourney로 아래 1장을 먼저 확정(여러 테이크 → 베스트 1세트 고정):
```
character reference sheet of [CHAR], front view + three-quarter view + profile
view, neutral soft studio light, plain warm grey background, photorealistic,
ultra-detailed, consistent identity across all views --ar 16:9
```
+ 감정 변형 스틸 3장(같은 세트에서): ① calm morning smile in soft window light (S11용)
② quiet awe, face lit by distant city glow at night (S45용) ③ content, eyes closing, holding a sleeping little daughter over the shoulder (S51용)

### 워크플로우 (얼굴 컷 절대 규칙)
1. 마스터 시트 + 감정 스틸 3장을 **캐릭터 레퍼런스 기능**(MJ --cref 등)으로 생성·확정
2. **확정 스틸을 i2v 소스로** Kling/Veo에 입력해 👤 영상 생성 (텍스트만으로 얼굴 재생성 금지)
3. 수용 기준: 3컷을 나란히 놓고 ① 동일인 식별 가능 ② 의상 동일 ③ 눈·치아·손 아티팩트 없음 ④ 과도한 미화/언캐니 없음 — 하나라도 실패 시 재생성
4. 人 컷도 주인공 등장 시 [CHAR] 블록 부착(실루엣에서도 의상 색·체형이 일관성을 만든다)

> ★ = 마이크로 비트(~90초 페이오프), [ ] = 챕터 시각 문법.

---

## 0.6 보이지 않는 동반자 "the Presence" 정의 (✅ 핵심 인지장치)

> 목표: 관객이 **"저 빛 = 가족을 돌보는 지능"** 임을 즉시 읽게 한다. (자비스의 본질 = 목소리가 아니라 **행위성**)
> "예쁜 입자"가 아니라 **행위성·일관성·소리·캡션·리빌** 5개 장치로 '캐릭터'로 만든다.

| 요소 | 정의 |
|------|------|
| **형태** | **따뜻한 앰버 빛 한 점**(미세한 시안 코어), 움직일 때 짧은 빛 궤적(wisp). 흩어진 입자 아님 — *하나의 점*. 전 챕터 동일 형태 |
| **톤** | 절제된 볼류메트릭 글로우. ⚠️ 요정·스프라이트(만화적) 금지 — 마법이 아니라 '존재의 시선' |
| **행위성(★핵심)** | 늘 **인지→의도→돌봄**의 3박. 빛이 *알아채고(미세 펄스) → 향하고(살짝 기울임) → 공간이 응답한다(표면 데움·길 밝힘·수면 시 어두워짐)*. 행동의 주체는 빛, 효과는 공간 |
| **소리(목소리 대체)** | 빛이 행동할 때마다 **고유 2~3음 따뜻한 모티프 차임**. = 무음성 영화의 '목소리'. **이 모티프가 곧 메인 BGM 테마의 씨앗**(음악 아크와 연결) |
| **일관성** | 같은 형태 + 같은 차임 + 같은 3박 행동을 집·차·식당·도시 **모든 공간에서** 반복 → "같은 존재가 어디든 함께" |
| **오프닝 학습** | 첫 60~90초에 빛이 **인지→돌봄을 또렷이 1회 시연** + 캡션으로 정체 각인 (관객에게 '규칙'을 가르침) |
| **엔딩 리빌** | ⚙AR에서 그 빛 = **LG의 지능·움직임(액추에이터)** 으로 정체 회수. S51에서 가족 곁에 머묾 |

**📝 인지용 캡션(영어, 후반 합성):** 오프닝 "It wakes when you wake." / 중반 1회 "Always here. In every space." / 리빌 "Every motion begins with an actuator."

---

## 오프닝 (0:00 – 1:00) — the Presence가 깨어난다

> **첫 10~15초 FAST 훅 + 동반자 '학습' 구간:** 빛이 *인지→돌봄*을 또렷이 시연해 정체를 각인.
> ▷ **인터타이틀**(후반): 타이틀 "경계를 넘는 지능 / *Borderless Intelligence*" + 슬로건 *Innovation in Tune with You*
> 📝 **캡션:** "It wakes when you wake."

| 씬# | 길이 | 비트 | [P] 변동 프롬프트 (영문) | 사운드 | 상태 |
|-----|------|------|--------------------------|--------|------|
| S01 | 0:00–0:08 | ★훅 | Total darkness; a single warm amber point of light (faint cyan core) ignites and gently breathes, alive and aware, slow push-in | motif chime (first note) | ☐ |
| S02 | 0:08–0:16 | 훅 | The light point drifts forward with intent, a soft wisp trailing; as it passes, the wireframe contour of a family living room blooms into being around it | motif chime resolves | ☐ |
| S03 | 0:16–0:30 | | The room solidifies into soft warm surfaces; the light point hovers, *perceives* (a subtle pulse), then turns toward a darkened hallway | rising pad | ☐ |
| S04 | 0:30–0:45 | 학습 | CARE DEMO — the light point flows ahead down the hall and, a beat before, gently warms a glow across a child's bedroom door; the space responds to its intent | warm tone + chime | ☐ |
| S05 | 0:45–1:00 | 人 | The light settles by the family bed at dawn; an adult hand stirs into the gathering morning light, the point resting nearby like a quiet guardian (title in post) | quiet breath, BGM intro | ☐ |

---

## Ch.1 집 (1:00 – 6:00) — The Home that Cares  [친밀 마크로]

> ▷ **인터타이틀:** "공간이, 가족을 돌본다 / *The home that cares*"
> 📝 **설명 자막(영어):** "Intelligence, distributed into the space"
> 룩: 새벽 블루 → 아침 웜톤. 모티프: **보이지 않는 안무**. 가족(부부+아이)의 아침. 👤 앵커 #1.

| 씬# | 길이 | 비트 | [P] 변동 프롬프트 (영문) | 사운드 | 상태 |
|-----|------|------|--------------------------|--------|------|
| S06 | 1:00–1:12 | 人 | Dawn bedroom: the father rises slowly into the soft light, sitting at the bed's edge (back to camera) as the room's glow gently lifts with him, static wide | low hum | ☐ |
| S07 | 1:12–1:24 | | Ceiling panels subtly tilt and breathe, a ripple of soft light travels across the ceiling, slow upward tracking | soft whisper | ☐ |
| ⚙A1 | 1:24–1:32 | ⚙ | Macro: a slender elegant robotic joint smoothly rotating a ceiling/blind panel, exposed precision actuator gleaming softly | refined servo | ☐ |
| S08 | 1:32–1:44 | ★ | The light point drifts to the kitchen and warms the counter a beat before the family arrives, warm amber glow blooming across the surface (warmth proxy), low tracking | warm chime | ☐ |
| S09 | 1:44–2:00 | 人 | A little girl's bedroom: curtains breathe open on their own, morning light flooding over a small sleeping silhouette with soft bobbed hair (face hidden in pillow), air particles drifting | airy swell | ☐ |
| S10 | 2:00–2:20 | 人 | Close on a little girl's small hand reaching into morning light, her father's hand gently meeting it, no faces, macro backlit | tender piano | ☐ |
| S11 | 2:20–2:45 | 👤 | HERO — the protagonist parent's face catches the first morning light, calm smile, child soft-focus in foreground, the warm room orienting around them *(fixed character ref)* | tender pad | ☐ |
| S12 | 2:45–3:05 | | Kitchen surfaces awaken with subtle glow, water gently begins to flow, breakfast warmth rising (no hands), close macro | water trickle, BGM build | ☐ |
| S13 | 3:05–3:25 | 人 | A low rounded domestic robot form (NOT humanoid) glides silently past the child's feet, light trailing, low side tracking | smooth whirr | ☐ |
| S14 | 3:25–3:45 | | The light point flows ahead across the floor toward the kitchen, lighting the family's path a step before they walk it (anticipatory care) | soft motion | ☐ |
| S15 | 3:45–4:10 | ★人 | Backlit family silhouettes at the breakfast table in golden morning light, surfaces softly orienting toward them, slow arc | warm resolve | ☐ |
| S16 | 4:10–4:35 | | Hundreds of micro light points across walls pulse once in unison like a calm breath, wide symmetrical | unison chime | ☐ |
| S17 | 4:35–5:00 | 人 | The spouse's hands pack a small lunchbox as cabinet surfaces glow helpfully; the child's silhouette runs past, soft focus | delicate texture | ☐ |
| S18 | 5:00–5:25 | 人 | Wide of the whole living space in harmonious morning light, the family (silhouettes) gathering by the door | full warm BGM | ☐ |
| S19 | 5:25–6:00 | 전환人 | The protagonist and child step toward the entrance; through the window a sleek electric van (PBV) waits, light bridging home→vehicle | transition riser | ☐ |

---

## Ch.2 이동 (6:00 – 9:30) — The Space that Moves (슈필라움)  [흐르는 모션]

> ▷ **인터타이틀:** "머무름이 곧, 이동이 된다 / *The space that moves*"
> 📝 **설명 자막(영어):** "Spielraum — your living room, in motion" / 🔆 동반자 캡션 "Always here. In every space."
> 룩: 실내 웜 + 창밖 흐르는 풍경광. 주인공+아이의 이동. ⚠️ 스포츠카 아님 — 프리미엄 전기 밴/PBV.
> 🔆 **the Presence:** 빛의 점이 차 안까지 따라옴(같은 형태·차임) → '어디든 함께'를 증명하는 핵심 구간.

| 씬# | 길이 | 비트 | [P] 변동 프롬프트 (영문) | 사운드 | 상태 |
|-----|------|------|--------------------------|--------|------|
| S20 | 6:00–6:12 | 전환人 | The light point drifts from the home threshold into a sleek electric van interior ahead of them (proving it follows), sliding door breathing open, father and daughter stepping in (backs), no driver | whoosh + motif chime | ☐ |
| S21 | 6:12–6:30 | 人 | Spacious modular lounge cabin, warm fabric seats facing, wood + textile, panoramic glass roof; the child kneels at the window (back), parent beside, slow pan | calm BGM | ☐ |
| S22 | 6:30–6:55 | ★人 | Through panoramic windows, landscape flows by in soft motion blur; the little girl's small silhouette (mustard hoodie) traces it with a finger, cabin light shifting warm | motion pad | ☐ |
| ⚙A2 | 6:55–7:03 | ⚙ | Macro: refined linear actuators silently gliding the cabin seats and a small table into family layout, elegant exposed mechanism | smooth servo | ☐ |
| S23 | 7:03–7:25 | | A compact built-in galley awakens — a warm cabinet glowing to life with a child's snack, macro detail | transform tone | ☐ |
| S24 | 7:25–7:50 | | Exterior cinematic: a sleek premium electric van (boxy PBV) gliding along a tree-lined riverside road at morning gold, light trail, aerial tracking | sweeping BGM | ☐ |
| S25 | 7:50–8:15 | 人 | The light point hovers between the father and daughter, the cabin warming in response, the moving space adapting like a living room, slow arc from behind | warm strings + chime | ☐ |
| S26 | 8:15–8:40 | | Window glass transitions to a soft ambient display blending landscape and gentle data light, dreamlike, push-in | shimmer | ☐ |
| S27 | 8:40–9:00 | | The van's cyan light signature connects to passing infrastructure nodes, the boundary between home and road dissolving, side tracking | connective pulse | ☐ |
| S28 | 9:00–9:30 | 전환人 | The van pauses; the little girl's silhouette (mustard hoodie) hops off toward a school gate in morning light, her father watching from the doorway of the van, then the van glides on toward glowing towers | transition riser | ☐ |

---

## Ch.3 공간들 (9:30 – 13:30) — The Spaces in Concert (ThinQ Pro + Hospitality)  [리듬·기하·스케일]

> ▷ **인터타이틀:** "하나의 집에서, 수많은 공간으로 / *From one home to many*"
> 📝 **설명 자막(영어):** "One intelligence, countless spaces"
> 룩: 클린 화이트 + 자연광→황혼 웜. **주거단지(ThinQ Pro)→오피스(낮)→환대(저녁·가족 레스토랑 식사)**. 시간이 낮→황혼으로 흐른다.

| 씬# | 길이 | 비트 | [P] 변동 프롬프트 (영문) | 사운드 | 상태 |
|-----|------|------|--------------------------|--------|------|
| S29 | 9:30–9:45 | | Slow aerial establishing of a large residential apartment community at morning, many homes, each window softly lit | bright ambient | ☐ |
| S30 | 9:45–10:10 | ★ | Hundreds of apartment windows pulse warm light in gentle coordinated waves, like one breath shared across many homes, high aerial | architectural pad | ☐ |
| S31 | 10:10–10:30 | 人 | Inside a residential lobby, distant silhouettes moving, surfaces and glass softly reconfiguring, wide tracking | subtle motion | ☐ |
| S32 | 10:30–10:55 | | Macro of a calm constellation of light points connecting into a living map of many managed homes (abstract, NOT literal UI), shallow focus | delicate texture | ☐ |
| S33 | 10:55–11:25 | 전환人 | The intelligence extends into a commercial office — a light-filled workspace where ceiling arrays shift warmth zone by zone following an unseen flow of people; the protagonist's silhouette works at a desk as daylight slowly turns to late afternoon gold | warm pulse | ☐ |
| ⚙A3 | 11:25–11:33 | ⚙ | Macro: a precise actuator smoothly swinging a glass partition, the same elegant joint repeated across many rooms | refined servo | ☐ |
| S34 | 11:33–12:05 | ★人 | Evening reunion — a warm restaurant inside a hotel at dusk: the spouse and daughter (silhouettes) arrive and join the father at the table as a graceful service robot glides over with warm dishes; the same light point hovers softly above the family table | gentle bell tone + chime | ☐ |
| S35 | 12:05–12:30 | 人 | Close: family hands sharing warm dishes, the little girl's small hand reaching for bread, the table surface softly glowing in welcome, no faces | warm texture | ☐ |
| S36 | 12:30–13:00 | | Dusk: energy flowing through the hotel and building veins like a calm circulatory system; a faint pulse gently heals a dim node back to warm light (predictive care), exterior orbit | swelling BGM | ☐ |
| S37 | 13:00–13:30 | 전환 | Camera pulls back and up at blue hour — homes, offices and the glowing restaurant become a constellation of light nodes within a larger city grid, scale reveal | epic riser | ☐ |

---

## Ch.4 도시 (13:30 – 18:00) — The City in Tune  [광활 항공 · 순수 감정 클라이맥스]

> ▷ **인터타이틀:** "지능이, 도시가 된다 / *The city in tune*"
> 📝 **설명 자막(영어):** "When intelligence becomes a city"
> 룩: 골든아워→블루아워 + 친환경 그린. **물류·제조는 여기서 빼고 엔딩 ⚙AR 리빌에 집중**(climax 온기 보호). 👤 앵커 #2.

| 씬# | 길이 | 비트 | [P] 변동 프롬프트 (영문) | 사운드 | 상태 |
|-----|------|------|--------------------------|--------|------|
| S38 | 13:30–13:55 | ★ | Sweeping aerial of a future city at deep dusk, buildings linked by faint flowing light lines, cinematic drone shot | grand BGM | ☐ |
| S39 | 13:55–14:25 | | Energy flows visualized as soft light rivers between districts, calm and orchestrated, high aerial tracking | flowing pad | ☐ |
| S40 | 14:25–14:55 | | Wind turbines and solar fields glowing with cyan energy accents, sustainable infrastructure feeding the city, slow aerial orbit | airy swell | ☐ |
| S41 | 14:55–15:25 | | Streets below: ambient public light gently adjusting to the flow of life, human-scale warmth, slow descending shot | tender motion | ☐ |
| S42 | 15:25–16:00 | ★人 | After dinner, the father steps onto the hotel's high terrace overlooking the vast luminous city (silhouette/back), the light point resting at his side, spouse and daughter soft-focus in the warm doorway behind, the city breathing in light below | reverent pad | ☐ |
| S43 | 16:00–16:35 | | Transition to blue hour, the whole city breathing in a slow pulse of light, ultra-wide aerial | building BGM | ☐ |
| S44 | 16:35–17:10 | | Light lines from homes, vehicles and buildings converging into the city network, macro-to-macro flow | orchestral build | ☐ |
| S45 | 17:10–17:35 | 👤 | HERO — the protagonist's face lit by the city glow, calm awe, the light network softly reflected in their eyes *(fixed character ref)* | swell | ☐ |
| S46 | 17:35–18:00 | | Cinematic night cityscape fully alive with calm coordinated light, slow majestic orbit, awe and warmth | full orchestral | ☐ |

---

## 연결 + 엔딩 (18:00 – 20:40) — Borderless & 귀가  [⚙리빌 → 몽타주 → 귀가 resolve]

> 📝 **설명 자막(영어):** ⚙AR 위에 "Every motion begins with an actuator" → 4영역 라벨 "Home · Hospitality · Logistics · Manufacturing" (후반 합성)
> 👤 앵커 #3 (귀가). **가족이 함께 귀가** — 잠든 아이를 안고 들어오며 아크가 닫힌다.

| 씬# | 길이 | 비트 | [P] 변동 프롬프트 (영문) | 사운드 | 상태 |
|-----|------|------|--------------------------|--------|------|
| ⚙AR | 18:00–18:30 | ⚙리빌 | The same warm light point (the Presence) drifts to the center of the city network and opens to reveal, at its core, one elegant actuator joint rotating in precision macro (companion→intelligence reveal); around it four worlds bloom in quadrant montage — a home robot's arm, a restaurant service robot, a warehouse mobile robot, a factory collaborative arm — all moved by the same joint, warm key light *(official AXIUM imagery as i2v ref)* | reveal: full motif swell | ☐ |
| S47 | 18:30–18:55 | ★빠름 | Rapid elegant montage morph: home glow → vehicle light → many-space constellation → city network, all one continuous light, seamless, faster tempo | montage swell | ☐ |
| S48 | 18:55–19:20 | | All scales unite into a single breathing web of warm light against deep navy, the boundaries dissolving, slow pull-back | resolve to calm | ☐ |
| S49 | 19:20–19:50 | 전환人 | Match-cut back to the home at night — the front door opens before they reach it, warm light spilling out to greet the returning family silhouettes (full circle) | warm return | ☐ |
| S50 | 19:50–20:10 | ★人 | The father carries his sleeping daughter down the hallway (backlit silhouettes), lights dimming gently ahead of each step, the spouse's hand resting on his shoulder, pure warmth | emotional peak | ☐ |
| S51 | 20:10–20:25 | 👤 | HERO — the father's face over his sleeping daughter's shoulder (her face hidden), eyes closing content; the same warm light point (the Presence) settles beside the family and softly pulses its motif one last time *(fixed character ref)* | tender chord (final motif) | ☐ |
| S52 | 20:25–20:40 | 엔딩 | The light network softens to a single warm point, then a gentle fade → closing copy **"Unseen, always with you."** then slogan + LG logo (all in post) | final warm chord | ☐ |

> **엔딩 카피(✅ 확정 — 화면 영어 단독, 후반 합성):**
> **"Unseen, always with you."** (참고 한글: 보이지 않아도, 늘 곁에)
> 시퀀스: 빛이 한 점으로 잦아듦 → 카피 페이드인 → 슬로건 *Innovation in Tune with You* + LG 로고

---

## 확장 가이드 (이 골격을 ~150컷으로 늘릴 때)

- 각 챕터의 ★비트 사이를 **B-roll 디테일 컷**(macro 텍스처·빛 반응·공간 디테일)으로 채운다.
- 한 장면당 **2~3개 변형 프롬프트** → Kling 러프로 베스트 선택.
- **👤 얼굴 컷(S11·S45·S51)은 같은 캐릭터 레퍼런스로** — 의상·헤어 통일. **아이·배우자 얼굴 금지** 유지.
- 가족 와이드는 역광 실루엣 통일 → 일관성 부담 0.
- 챕터 내 컬러·렌즈·시각 문법 고정, 전환·몽타주엔 템포 변화로 단조로움을 깬다.
- 전환 컷은 다음 챕터 색을 미리 1~2초 섞어 자연스럽게 잇는다.
- ⚙ 컷은 AXIUM 공식 페이지 공개 이미지를 i2v 레퍼런스로 쓰면 정확도↑ (왜곡 재현 주의).
