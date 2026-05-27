# -*- coding: utf-8 -*-
"""
스테이빌리티 양평 [가동-숙박동] IoT/G-IoT + 양평 출품 가전 배치도 (v9) 생성기

주의:
- 원본 v8 matplotlib 스크립트가 제공되지 않아, v8 배치도 이미지 + CLAUDE.md 스펙
  (§5.4 도면 충실 반영, §10 색상/폰트/레이아웃) 기준으로 재생성한 도면입니다.
- 룸 비율은 도면/사진 기준 근사치이며, IoT 마커는 '대표 배치'입니다(원본 좌표 아님).
- 한국어 폰트: CLAUDE.md §10.3 규칙은 '/usr/share/fonts/Batang.ttf' 이지만
  본 컨테이너에 미설치 → WenQuanYi Zen Hei(한글 지원 CJK 폰트)로 렌더.
  Batang.ttf 보유 환경에서는 FONT_PATH만 교체하면 정자체로 출력됩니다.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Polygon
from matplotlib.font_manager import FontProperties

# ---- 폰트 (§10.3 패턴: FontProperties(fname=...)) ----
FONT_PATH = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"  # 양평 환경에선 Batang.ttf 로 교체
fp = lambda s=11, w="normal": FontProperties(fname=FONT_PATH, size=s, weight=w)

# ---- §10.1 / §10.2 색상 ----
C_NAVY="#1F4E78"; C_WINE="#A50034"; C_DARKRED="#8B0000"
COL = {
    "거실":"#F5E6CA", "다도":"#FBD9A8", "화장실":"#C8E8E8", "보일러":"#D5D5D5",
    "침실1":"#F8C8D4", "침실2":"#D7C8F0", "중정":"#FFF5B7", "현관":"#BFBFBF",
    "주출입구":"#EEDDB8", "수공간":"#CFE8F3", "팬트리":"#E8E8E8",
}

# IoT 마커 정의: code -> (marker, facecolor, edgecolor, size, label)
IOT = {
    "I1":("s", C_NAVY,  "k", 150, "ThinQ ON AI (허브)"),
    "I2":("o", "#163A8A","k", 120, "스마트 도어락"),
    "I3":(".", "#000000","k", 220, "도어 센서"),
    "I4":("o", "#2E8B57","k", 120, "모션/조도 센서"),
    "I5":("o", "#FFC400","k", 120, "온습도 센서"),
    "I6":("o", "#8B5CF6","k", 120, "공기질 센서"),
    "I7":("s", "#FF8C00","k", 120, "스마트 조명 스위치 2구"),
    "I8":("D", "#FF8C00","k", 110, "스마트 버튼 2구"),
    "I9":("s", "#000000","k", 120, "스마트 플러그"),
    "I10":("^","#D62728","k", 150, "보이스 컨트롤러"),
    "I11":("*","#FF69B4","k", 260, "헤이홈 무드등"),
}
GIOT = {
    "G1":("o","#7B3F00","k",150,"써모스탯 (24V AC 우회, 보일러 제어 통합)"),
    "G2":("s","#D62728","k",130,"아웃도어 카메라"),
    "G3":("o","#FF5C5C","k",130,"인도어 카메라 (공실 시만 ON)"),
    "G4":("o","#C00000","k",130,"도어벨"),
}

fig = plt.figure(figsize=(22,14), dpi=150)
ax = fig.add_axes([0,0,1,1]); ax.set_xlim(0,230); ax.set_ylim(0,140); ax.axis("off")

# ================= 타이틀 / 배너 =================
ax.add_patch(Rectangle((6,128),218,9, facecolor=C_NAVY, edgecolor="none"))
ax.text(115,132.5,"스테이빌리티 양평 [가동-숙박동] — IoT / G-IoT + 양평 출품 가전 배치도 (v9)",
        ha="center", va="center", color="white", fontproperties=fp(22,"bold"))
ax.text(115,125.4,"2026.05.27  |  G1=G8 통합(써모스탯에 보일러 제어 포함)  |  G6·G7 3rd 파티  |  가전 모델명 추후 업데이트  |  (!) 마커는 대표 배치",
        ha="center", va="center", color="#333", fontproperties=fp(11))
# §5.5 SKS 빨강 배너
ax.add_patch(FancyBboxPatch((6,120.2),218,4, boxstyle="round,pad=0.1,rounding_size=1",
            facecolor="#FCE4E4", edgecolor="#C0392B", linewidth=1.2))
ax.text(115,122.2,"(!) SKS(Signature Kitchen Suite) 라인은 ThinQ 연동/스마트루틴 제한 가능성 — HS사업부 확답 전까지 '가능성'으로만 표기",
        ha="center", va="center", color="#7a0000", fontproperties=fp(11,"bold"))

# ================= 수공간 (건물 좌·상·하 둘러쌈) =================
ax.add_patch(FancyBboxPatch((8,52),210,64, boxstyle="round,pad=0.2,rounding_size=2",
            facecolor=COL["수공간"], edgecolor="#7FB3D5", alpha=0.5, linewidth=1.0))
ax.text(11.5,113.5,"수공간", ha="left", va="top", color="#2C6E91", fontproperties=fp(10), rotation=90)

# ================= 룸 정의 =================
def room(x,y,w,h,color,name,fs=12,dashed=False,name_dy=None,alpha=1.0,tc="#222"):
    ls = (0,(4,3)) if dashed else "solid"
    ax.add_patch(Rectangle((x,y),w,h, facecolor=color, edgecolor="#555",
                 linewidth=1.3, linestyle=ls, alpha=alpha, zorder=2))
    ny = y+h-4 if name_dy is None else y+name_dy
    ax.text(x+w/2, ny, name, ha="center", va="top", fontproperties=fp(fs,"bold"),
            color=tc, zorder=5)

# building interior: x 14..200 (width 186), y 56..114 (height 58). 거실 37%≈69
GX0, GW = 14, 186
x1=GX0;              w1=round(GW*0.37)   # 거실
x2=x1+w1;            w2=20               # 다도/화장실1
x3=x2+w2;            w3=39               # 침실1
x4=x3+w3;            w4=39               # 침실2
x5=x4+w4;            w5=GX0+GW-x5        # 화장실2/현관
Y0, H = 56, 58

room(x1,Y0,w1,H, COL["거실"], "거실 · 주방 · 다이닝\n(생활숙박시설 / 숙박동)", 13)
room(x2,Y0+H*0.55,w2,H*0.45, COL["다도"], "다도공간", 11)
room(x2,Y0,w2,H*0.55, COL["화장실"], "화장실-1\n(내욕실)", 11)
room(x3,Y0,w3,H, COL["침실1"], "침실-1\n(마스터 베드룸1)", 13)
room(x4,Y0,w4,H, COL["침실2"], "침실-2\n(마스터 베드룸2)", 13)
room(x5,Y0+H*0.5,w5,H*0.5, COL["화장실"], "화장실-2\n(외욕실)", 11)
room(x5,Y0,w5,H*0.5, COL["현관"], "현관", 11, tc="#fff")

# 보일러실 (상단 소형)
room(x2+w2-3, Y0+H-9, 12, 9, COL["보일러"], "보일러실", 9)
# 중정 1·2 (소형, 점선)
room(x3+w3-12, Y0+10, 11, 16, COL["중정"], "중정 1", 9, dashed=True)
room(x4+w4-12, Y0+10, 11, 16, COL["중정"], "중정-2", 9, dashed=True)
# 주출입구 (외부 데크) — 우측 외부
ax.add_patch(Polygon([(x5+w5,Y0+8),(x5+w5+18,Y0+H/2),(x5+w5,Y0+H-8)],
             closed=True, facecolor=COL["주출입구"], edgecolor="#9a7b3a", linewidth=1.3, zorder=2))
ax.text(x5+w5+5.5, Y0+H/2, "주출입구\n(외부 데크)", ha="left", va="center", fontproperties=fp(10,"bold"))

# 팬트리 (위치 미정) — 별도 점선 박스
room(86,40,52,10, COL["팬트리"], "", dashed=True)
ax.text(112,48.5,"팬트리 ((!) 위치 미정)", ha="center", va="top", fontproperties=fp(10,"bold"), color="#666")

# ================= A# 뱃지 (양평 출품 가전) =================
def badge(x,y,code):
    ax.add_patch(FancyBboxPatch((x,y),5.4,3.4, boxstyle="round,pad=0.05,rounding_size=0.8",
                 facecolor=C_WINE, edgecolor="none", zorder=6))
    ax.text(x+2.7,y+1.7,code, ha="center", va="center", color="white",
            fontproperties=fp(9,"bold"), zorder=7)

# 거실/키친
for i,bx in enumerate([20,28,36,44,52]): badge(bx,58.5,f"A{i+1}")      # A1~A5 키친
badge(22,96,"A6"); badge(40,96,"A10"); badge(54,86,"A9"); badge(34,72,"A8")
badge(12,116,"A7")  # 프리미엄 환기 (전체) 표식 - 좌상단
# 침실
badge(x3+6,96,"A6"); badge(x3+16,84,"A11"); badge(x3+16,70,"A17")
badge(x4+6,96,"A6"); badge(x4+16,84,"A11"); badge(x4+16,70,"A17")
# 욕실 바스에어
badge(x2+7,62,"A15"); badge(x5+w5-7,Y0+H*0.5+10,"A15")
# 팬트리
badge(94,41,"A12"); badge(104,41,"A13"); badge(114,41,"A14")

# ================= IoT 마커 (대표 배치) =================
def mk(x,y,code,table=None):
    table = (GIOT if code.startswith("G") else IOT) if table is None else table
    m,fc,ec,s,_=table[code]
    ax.scatter([x],[y], marker=m, s=s, facecolor=fc, edgecolor=ec, linewidths=0.8, zorder=8)

# 거실: 허브/센서/스위치/무드등 등
mk(30,104,"I1"); mk(60,100,"I4"); mk(70,92,"I5"); mk(46,82,"I7"); mk(64,78,"I6")
mk(24,76,"I9"); mk(18,66,"I11"); mk(48,66,"I8"); mk(38,88,"I3")
mk(40,104,"G1"); mk(26,68,"G3")
# 다도/화장실1
mk(x2+10,100,"I4"); mk(x2+8,66,"I3"); mk(x2+12,60,"I6")
# 침실1
mk(x3+10,100,"I4"); mk(x3+22,96,"I5"); mk(x3+8,80,"I8"); mk(x3+24,76,"I3"); mk(x3+12,64,"I11"); mk(x3+20,104,"G1")
# 침실2
mk(x4+10,100,"I4"); mk(x4+22,96,"I5"); mk(x4+8,80,"I8"); mk(x4+24,76,"I3"); mk(x4+12,64,"I11"); mk(x4+20,104,"G1")
# 화장실2/현관/주출입구
mk(x5+8,96,"I4"); mk(x5+12,92,"I5"); mk(x5+8,68,"I2"); mk(x5+12,62,"I3")
mk(x5+w5+6,Y0+H/2+4,"I10")

# 외곽 G-IoT 카메라/도어벨
mk(12,118,"G2"); mk(x5+w5+8,Y0+H-6,"G2"); mk(x5+w5+6,Y0+10,"G4")

# ================= A / E 외곽 마커 라벨 =================
def edge_label(x,y,txt,kind="A"):
    fcc = "#fff"; ec="#333"
    ax.add_patch(Rectangle((x,y),2.6,2.6, facecolor=fcc, edgecolor=ec, linewidth=1.0, zorder=6))
    ax.text(x+1.3,y+1.3,kind, ha="center", va="center", fontproperties=fp(8,"bold"), zorder=7)
    ax.text(x+3.6,y+1.3,txt, ha="left", va="center", fontproperties=fp(9), zorder=7)

edge_label(16,116.5,"고정형 취사시설")
edge_label(x2+2,116.5,"객실별 욕실설치(샤워실 포함)")
edge_label(x5-6,116.5,"객실별 욕실설치(샤워실 포함)")
edge_label(16,52.5,"환기를 위한 창문 설치")
edge_label(x4,52.5,"환기를 위한 창문 설치")
edge_label(204,96,"객실관리(제어)시스템 CCTV","E")
edge_label(204,60,"객실관리(제어)시스템 도어락","E")
ax.text(204,72,"※ 관리실은 외부에 위치\n   (본 도면 범위 외)", ha="left", va="center",
        fontproperties=fp(8.5), color="#666")

# ================= 하단 범례 =================
def legbox(x,y,w,h,title,color):
    ax.add_patch(FancyBboxPatch((x,y),w,h, boxstyle="round,pad=0.2,rounding_size=1",
                 facecolor="white", edgecolor=color, linewidth=1.6))
    ax.add_patch(Rectangle((x,y+h-4.2),w,4.2, facecolor=color, edgecolor="none"))
    ax.text(x+w/2,y+h-2.1,title, ha="center", va="center", color="white", fontproperties=fp(12,"bold"))

# 1) LG 출시 IoT
legbox(6,5,72,42,"■ 출시 IoT (LG전자 홈IoT) — 11종", C_NAVY)
keys=list(IOT.keys())
for i,k in enumerate(keys):
    col=i//6; row=i%6
    lx=10+col*35; ly=39-row*5.4
    m,fc,ec,s,lab=IOT[k]
    ax.scatter([lx],[ly], marker=m, s=max(70,s*0.6), facecolor=fc, edgecolor=ec, linewidths=0.7)
    ax.text(lx+2.6,ly,f"{k} {lab}", ha="left", va="center", fontproperties=fp(8.3))

# 2) G-IoT
legbox(82,5,70,42,"■ G-IoT (PPT 논의 디바이스)", C_DARKRED)
giot_rows=[
    ("G1","써모스탯 (24V AC 우회, 보일러 제어 통합) — (!) KC 미인증, 브컴 확답 전 보류"),
    ("G2","아웃도어 카메라"),
    ("G3","인도어 카메라 (공실 시만 ON)"),
    ("G4","도어벨"),
    ("G5","도어락 — (!) 기존 객실관리(E마커) 도어락과 분류 중복 검토"),
    ("G6","전동 샷시 (LX하우시스, 3rd 파티, Lock 미지원)"),
    ("G7","전동 커튼 (마마바-Matter, 3rd 파티)"),
]
for i,(k,lab) in enumerate(giot_rows):
    ly=39-i*5.0
    if k in GIOT:
        m,fc,ec,s,_=GIOT[k]; ax.scatter([86.5],[ly],marker=m,s=90,facecolor=fc,edgecolor=ec,linewidths=0.7)
    elif k=="G5":
        ax.scatter([86.5],[ly],marker="o",s=90,facecolor="#163A8A",edgecolor="k",linewidths=0.7)
    else:
        ax.plot([85,88],[ly,ly], color="#555", lw=2)  # 3rd파티 선
    ax.text(89.5,ly,f"{k} {lab}", ha="left", va="center", fontproperties=fp(7.8))

# 3) 양평 출품 가전 리스트
legbox(156,5,68,42,"■ 양평 출품 가전 (A 시리즈) — 16종", C_WINE)
appl=[
    "A1~A5 키친(냉장고/와인셀러/광파오븐/식기세척기/인덕션)",
    "A6 시스템 에어컨(전체)   A7 프리미엄 환기(전체)",
    "A8 OLED M TV   A9 무선 스피커   A10 가습공청기(리빙)",
    "A11 베드룸 공청기(침실1·2)",
    "A12 세탁/건조기   A13 청소기 (!)   A14 키오스크 (!) (팬트리)",
    "A15 바스에어시스템 듀얼 MX0120BASV(외·내욕실)",
    "A17 스타일러(침실1·2)   ·   A16 사이니지/관리실 → 범위 외(제외)",
]
for i,t in enumerate(appl):
    ax.text(159,40-i*5.0,t, ha="left", va="center", fontproperties=fp(7.6))

# 하단 주석
ax.text(115,2.2,
    "※ G1(써모스탯)이 보일러 제어 통합 → 별도 보일러 연동 모듈 불필요.  G6·G7은 3rd 파티(LX하우시스/마마바).  "
    "양평 출품 가전 모델명 추후 업데이트.  (!) 표기는 모델/위치/적용여부 미확정.",
    ha="center", va="center", fontproperties=fp(9), color="#444")

out="yangpyeong/스테이빌리티_양평_IoT배치도_v9.png"
fig.savefig(out, dpi=150, facecolor="white", bbox_inches=None)
print("saved", out)
