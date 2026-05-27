# -*- coding: utf-8 -*-
"""
스테이빌리티 양평 [가동-숙박동] IoT/G-IoT + 양평 출품 가전 배치도 (v10)

v10 = 실제 건축도면([가동]-숙박동 CAD) 기반 전면 재구성.
  - v8(회사 초안 배치도)/v9(그 파생) 룸 배치 방식 폐기.
  - 좌→우 구역: 거실·주방·다이닝 / (다도·화장실1·보일러) / 침실1+중정1 /
    침실2+중정2 / (화장실2·현관·주출입구).  중정은 각 침실 '앞(하단)'.
  - 수공간이 건물 좌·상·하를 둘러쌈. 우측 E마커(CCTV/도어락), DN 계단.
주의: 룸 치수는 도면 근사치, IoT 마커는 '대표 배치'(원본 좌표 아님).
폰트: §10.3 규칙은 Batang.ttf 이나 컨테이너 미설치 → WenQuanYi 로 렌더.
      Batang 보유 환경에선 FONT_PATH만 교체.
"""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Polygon, Ellipse, Arc, Circle
from matplotlib.font_manager import FontProperties

FONT_PATH = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"   # 양평 환경: Batang.ttf
fp = lambda s=11, w="normal": FontProperties(fname=FONT_PATH, size=s, weight=w)

C_NAVY="#1F4E78"; C_WINE="#A50034"; C_DARKRED="#8B0000"
COL = {"거실":"#F5E6CA","다도":"#FBD9A8","화장실":"#C8E8E8","보일러":"#D5D5D5",
       "침실1":"#F8C8D4","침실2":"#D7C8F0","중정":"#FFF5B7","현관":"#BFBFBF",
       "주출입구":"#EEDDB8","수공간":"#CFE8F3","팬트리":"#E8E8E8"}
IOT = {"I1":("s",C_NAVY,"k",150,"ThinQ ON AI (허브)"),"I2":("o","#163A8A","k",120,"스마트 도어락"),
       "I3":(".","#000000","k",220,"도어 센서"),"I4":("o","#2E8B57","k",120,"모션/조도 센서"),
       "I5":("o","#FFC400","k",120,"온습도 센서"),"I6":("o","#8B5CF6","k",120,"공기질 센서"),
       "I7":("s","#FF8C00","k",120,"스마트 조명 스위치 2구"),"I8":("D","#FF8C00","k",110,"스마트 버튼 2구"),
       "I9":("s","#000000","k",120,"스마트 플러그"),"I10":("^","#D62728","k",150,"보이스 컨트롤러"),
       "I11":("*","#FF69B4","k",260,"헤이홈 무드등")}
GIOT = {"G1":("o","#7B3F00","k",150,""),"G2":("s","#D62728","k",130,""),
        "G3":("o","#FF5C5C","k",130,""),"G4":("o","#C00000","k",130,"")}

fig=plt.figure(figsize=(22,14),dpi=150)
ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,220); ax.set_ylim(0,140); ax.axis("off")

# ===== 타이틀 / 배너 =====
ax.add_patch(Rectangle((6,128),208,9,facecolor=C_NAVY,edgecolor="none"))
ax.text(110,132.5,"스테이빌리티 양평 [가동-숙박동] — IoT / G-IoT + 양평 출품 가전 배치도 (v10 · 실측도면 기반)",
        ha="center",va="center",color="white",fontproperties=fp(21,"bold"))
ax.text(110,125.4,"2026.05.27  |  실제 건축도면 기반 전면 재구성  |  G1=G8 통합  |  G6·G7 3rd 파티  |  가전 모델명 추후  |  (!) 마커는 대표 배치",
        ha="center",va="center",color="#333",fontproperties=fp(10.5))
ax.add_patch(FancyBboxPatch((6,120.2),208,4,boxstyle="round,pad=0.1,rounding_size=1",
            facecolor="#FCE4E4",edgecolor="#C0392B",linewidth=1.2))
ax.text(110,122.2,"(!) SKS(Signature Kitchen Suite) 라인은 ThinQ 연동/스마트루틴 제한 가능성 — HS사업부 확답 전까지 '가능성'으로만 표기",
        ha="center",va="center",color="#7a0000",fontproperties=fp(10.5,"bold"))

# ===== 수공간 (건물 좌·상·하 감쌈) =====
ax.add_patch(FancyBboxPatch((8,31),200,86,boxstyle="round,pad=0.2,rounding_size=2",
            facecolor=COL["수공간"],edgecolor="#7FB3D5",alpha=0.5,linewidth=1.0))
for tx,ty in [(11,73),(105,114.5),(105,33.5)]:
    ax.text(tx,ty,"수공간",ha="center",va="center",color="#2C6E91",fontproperties=fp(9),
            rotation=(90 if tx==11 else 0))

def rect(x,y,w,h,c,name="",fs=12,dashed=False,tc="#222",ny=None,za=2):
    ls=(0,(4,3)) if dashed else "solid"
    ax.add_patch(Rectangle((x,y),w,h,facecolor=c,edgecolor="#555",linewidth=1.4,linestyle=ls,zorder=za))
    if name: ax.text(x+w/2,(y+h-4 if ny is None else ny),name,ha="center",va="top",
                     fontproperties=fp(fs,"bold"),color=tc,zorder=5)

# ===== 건물 구역 (좌→우) : x 16..204, y 36..112 =====
BX0,BY0,BY1=16,36,112
# Z1 거실·주방·다이닝 (16..86)
rect(16,36,70,76,COL["거실"],"거실 · 주방 · 다이닝\n(생활숙박시설 / 숙박동)",13)
# 가구 (얇은 윤곽)
ax.add_patch(FancyBboxPatch((20,92),16,12,boxstyle="round,pad=0.1,rounding_size=1.2",
            facecolor="#EADbc0",edgecolor="#9a8a6a",lw=1.0,zorder=3)); ax.text(28,98,"소파",ha="center",va="center",fontproperties=fp(8),zorder=6)
ax.add_patch(Rectangle((44,104),34,5,facecolor="#E2D4b4",edgecolor="#9a8a6a",lw=1.0,hatch="////",zorder=3)); ax.text(61,106.5,"주방",ha="center",va="center",fontproperties=fp(8),zorder=6)
ax.add_patch(Rectangle((46,78),18,10,facecolor="#E2D4b4",edgecolor="#9a8a6a",lw=1.0,zorder=3)); ax.text(55,83,"식탁",ha="center",va="center",fontproperties=fp(8),zorder=6)
for cx in (44,66):
    for cy in (79.5,86.5): ax.add_patch(Circle((cx,cy),1.0,facecolor="#cdbb95",edgecolor="#9a8a6a",lw=0.6,zorder=3))

# Z2 보일러/다도/화장실1 (86..108)
rect(86,70,22,42,COL["다도"],"다도공간",11,ny=104)
ax.add_patch(Rectangle((88,74),18,2.2,facecolor="#caa56f",edgecolor="#9a7b3a",lw=0.8,zorder=4))  # 다도 단(step)
rect(86,36,22,34,COL["화장실"],"화장실-1\n(내욕실)",10)
ax.add_patch(Rectangle((89,40),7,7,facecolor="white",edgecolor="#4a8",lw=1.0,zorder=4)); ax.text(92.5,43.5,"샤워",ha="center",va="center",fontproperties=fp(6.5),zorder=6)
ax.add_patch(Ellipse((101,44),5,3,facecolor="white",edgecolor="#4a8",lw=1.0,zorder=4))            # 세면
rect(86,104,12,8,COL["보일러"],"보일러실",8,ny=111,za=5)
ax.add_patch(Arc((98,104),9,9,angle=0,theta1=90,theta2=180,edgecolor="#c0392b",lw=1.3,zorder=6))   # 도어 호

# Z3 침실1 + 중정1 (108..140)  중정 = 앞(하단)
rect(108,62,32,50,COL["침실1"],"침실-1\n(마스터 베드룸1)",13)
rect(108,36,32,26,COL["중정"],"중정 1",9,dashed=True,ny=60,tc="#7a6a00")
for cx,cy in [(116,44),(122,48),(130,43),(134,50)]:
    ax.add_patch(Circle((cx,cy),1.6,facecolor="#9CC799",edgecolor="#5a8f57",lw=0.7,zorder=4))
# Z4 침실2 + 중정2 (140..172)
rect(140,62,32,50,COL["침실2"],"침실-2\n(마스터 베드룸2)",13)
rect(140,36,32,26,COL["중정"],"중정-2",9,dashed=True,ny=60,tc="#7a6a00")
for cx,cy in [(148,44),(154,48),(162,43),(166,50)]:
    ax.add_patch(Circle((cx,cy),1.6,facecolor="#9CC799",edgecolor="#5a8f57",lw=0.7,zorder=4))

# Z5 화장실2 / 현관 / 주출입구 (172..204)
rect(172,72,32,40,COL["화장실"],"화장실-2\n(외욕실)",10,ny=110)
ax.add_patch(FancyBboxPatch((176,76),16,8,boxstyle="round,pad=0.1,rounding_size=2.5",
            facecolor="white",edgecolor="#3a89a8",lw=1.2,zorder=4)); ax.text(184,80,"욕조",ha="center",va="center",fontproperties=fp(7),zorder=6)
ax.add_patch(Ellipse((198,80),5,3,facecolor="white",edgecolor="#3a89a8",lw=1.0,zorder=4))
rect(172,36,20,36,COL["현관"],"현관",10,tc="#fff",ny=70)
rect(192,36,12,36,COL["주출입구"],"주출입구",9,ny=70)
# 외부 데크 + 적색 진입 화살표
ax.add_patch(Polygon([(204,40),(216,48),(216,60),(204,68)],closed=True,
            facecolor=COL["주출입구"],edgecolor="#9a7b3a",lw=1.2,zorder=2))
ax.text(210,54,"외부\n데크",ha="center",va="center",fontproperties=fp(8))
ax.annotate("",xy=(196,54),xytext=(208,54),arrowprops=dict(arrowstyle="-|>",color="#D62728",lw=3.2),zorder=8)

# ===== A# 뱃지 (양평 출품 가전) =====
def badge(x,y,code):
    ax.add_patch(FancyBboxPatch((x,y),5.4,3.4,boxstyle="round,pad=0.05,rounding_size=0.8",
                facecolor=C_WINE,edgecolor="none",zorder=7))
    ax.text(x+2.7,y+1.7,code,ha="center",va="center",color="white",fontproperties=fp(9,"bold"),zorder=8)
for i,bx in enumerate([40,48,56,64,72]): badge(bx,99,f"A{i+1}")     # A1~A5 키친(주방 카운터 인근)
badge(24,64,"A6"); badge(40,64,"A10"); badge(54,64,"A9"); badge(66,92,"A8"); badge(18,108,"A7")
badge(112,98,"A6"); badge(124,86,"A11"); badge(112,70,"A17")
badge(144,98,"A6"); badge(156,86,"A11"); badge(144,70,"A17")
badge(88,52,"A15"); badge(196,90,"A15")
# 팬트리 (위치 미정) — 별도 점선 박스
rect(84,18,56,9,COL["팬트리"],"",dashed=True)
ax.text(112,25.5,"팬트리 ( (!) 위치 미정 )",ha="center",va="top",fontproperties=fp(9.5,"bold"),color="#666")
for j,c in enumerate(["A12","A13","A14"]): badge(92+j*12,19,c)

# ===== IoT/G-IoT 마커 (대표 배치) =====
def mk(x,y,code):
    t=GIOT if code.startswith("G") else IOT; m,fc,ec,s,_=t[code]
    ax.scatter([x],[y],marker=m,s=s,facecolor=fc,edgecolor=ec,linewidths=0.8,zorder=9)
# 거실
for p in [(30,104,"I1"),(60,96,"I4"),(70,88,"I5"),(40,82,"I7"),(64,100,"I6"),
          (24,74,"I9"),(20,90,"I11"),(50,72,"I8"),(36,96,"I3"),(46,104,"G1"),(30,68,"G3")]: mk(*p)
# 다도/화장실1/보일러
for p in [(97,96,"I4"),(92,60,"I3"),(101,55,"I6"),(97,108,"G1")]: mk(*p)
# 침실1
for p in [(116,104,"I4"),(132,100,"I5"),(120,88,"I8"),(134,80,"I3"),(132,70,"I11"),(126,104,"G1")]: mk(*p)
# 침실2
for p in [(148,104,"I4"),(164,100,"I5"),(152,88,"I8"),(166,80,"I3"),(164,70,"I11"),(158,104,"G1")]: mk(*p)
# 중정 (모션 센서)
mk(126,52,"I4"); mk(158,52,"I4")
# 화장실2/현관/주출입구
for p in [(190,100,"I4"),(196,96,"I5"),(180,60,"I2"),(186,52,"I3"),(198,46,"I10")]: mk(*p)
# 외곽 G-IoT 카메라/도어벨
mk(14,114,"G2"); mk(206,66,"G2"); mk(200,40,"G4")

# ===== A / E 외곽 마커 =====
def edge(x,y,txt,kind="A"):
    ax.add_patch(Rectangle((x,y),2.6,2.6,facecolor="#fff",edgecolor="#333",lw=1.0,zorder=7))
    ax.text(x+1.3,y+1.3,kind,ha="center",va="center",fontproperties=fp(8,"bold"),zorder=8)
    ax.text(x+3.6,y+1.3,txt,ha="left",va="center",fontproperties=fp(8.5),zorder=8)
edge(40,114,"고정형 취사시설")
edge(176,114,"객실별 욕실설치(샤워실 포함)")
edge(40,32.4,"환기를 위한 창문 설치")
edge(88,32.4,"객실별 욕실설치(샤워실 포함)")
edge(206,98,"객실관리(제어)시스템 CCTV","E")
edge(206,44,"객실관리(제어)시스템 도어락","E")
ax.add_patch(Rectangle((210,74),6,8,facecolor="#eee",edgecolor="#555",lw=1.0,zorder=4)); ax.text(213,78,"DN",ha="center",va="center",fontproperties=fp(8),zorder=6)
ax.text(206,88,"※ 관리실은 외부 위치\n   (본 도면 범위 외)",ha="left",va="center",fontproperties=fp(8),color="#666")

# ===== 하단 범례 3박스 =====
def legbox(x,y,w,h,title,color):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.2,rounding_size=1",
                facecolor="white",edgecolor=color,linewidth=1.6))
    ax.add_patch(Rectangle((x,y+h-4),w,4,facecolor=color,edgecolor="none"))
    ax.text(x+w/2,y+h-2,title,ha="center",va="center",color="white",fontproperties=fp(11.5,"bold"))
legbox(6,4,66,12.5,"■ 출시 IoT (LG전자 홈IoT) — 11종",C_NAVY)
for i,k in enumerate(IOT):
    col=i//4; row=i%4; lx=10+col*22; ly=12.7-row*2.7
    m,fc,ec,s,lab=IOT[k]; ax.scatter([lx],[ly],marker=m,s=70,facecolor=fc,edgecolor=ec,linewidths=0.6)
    ax.text(lx+1.8,ly,f"{k} {lab}",ha="left",va="center",fontproperties=fp(7))
legbox(74,4,66,12.5,"■ G-IoT (PPT 논의 디바이스)",C_DARKRED)
grows=[("G1","써모스탯 (보일러 제어 통합) — (!) KC 미인증, 브컴 확답 전 보류"),("G2","아웃도어 카메라"),
       ("G3","인도어 카메라 (공실 시만 ON)"),("G4","도어벨"),
       ("G5","도어락 — (!) E마커 도어락과 분류 중복 검토"),("G6","전동 샷시 (LX하우시스, 3rd, Lock 미지원)"),
       ("G7","전동 커튼 (마마바-Matter, 3rd)")]
for i,(k,lab) in enumerate(grows):
    col=i//4; row=i%4; lx=78+col*33; ly=12.7-row*2.7
    if k in GIOT: m,fc,ec,s,_=GIOT[k]; ax.scatter([lx],[ly],marker=m,s=70,facecolor=fc,edgecolor=ec,linewidths=0.6)
    elif k=="G5": ax.scatter([lx],[ly],marker="o",s=70,facecolor="#163A8A",edgecolor="k",linewidths=0.6)
    else: ax.plot([lx-1,lx+1],[ly,ly],color="#555",lw=2)
    ax.text(lx+1.8,ly,f"{k} {lab}",ha="left",va="center",fontproperties=fp(6.4))
legbox(142,4,72,12.5,"■ 양평 출품 가전 (A 시리즈) — 16종",C_WINE)
appl=["A1~A5 키친(냉장고/와인셀러/광파오븐/식기세척기/인덕션)","A6 시스템 에어컨(전체)  A7 프리미엄 환기(전체)",
      "A8 OLED M TV  A9 무선 스피커  A10 가습공청기(리빙)","A11 베드룸 공청기(침실1·2)  A17 스타일러(침실1·2)",
      "A12 세탁/건조기  A13 청소기(!)  A14 키오스크(!) (팬트리)","A15 바스에어 듀얼 MX0120BASV(외·내욕실)  ·  A16 사이니지/관리실 → 제외"]
for i,t in enumerate(appl): ax.text(145,13-i*2.5,t,ha="left",va="center",fontproperties=fp(6.6))

ax.text(110,1.4,"※ 중정 1·2는 각 침실 전면(하단).  G1=보일러 제어 통합(별도 모듈 불필요).  G6·G7 3rd 파티.  (!) 표기는 모델/위치/적용여부 미확정.  실측 도면 기반 v10.",
        ha="center",va="center",fontproperties=fp(8.5),color="#444")

out="yangpyeong/스테이빌리티_양평_IoT배치도_v10.png"
fig.savefig(out,dpi=150,facecolor="white"); print("saved",out)
