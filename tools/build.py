#!/usr/bin/env python3
"""면역학 개론 기출 퀴즈 — 문제 데이터 빌더.

이 파일의 문제 목록을 고친 뒤 `python3 tools/build.py` 를 실행하면 ../questions.js 가 다시 만들어집니다.
(검증 포함: id 중복, 정답 번호 범위, 그림 파일 존재 여부)

문제 종류
  mc(...)     객관식 한 문항
  grp(...)    보기를 공유하는 묶음 문항 (Q1, Q2 ...) → 문항마다 하나씩 펼쳐서 저장
  short(...)  주관식 단답 (정답 표현이 여러 개면 acc 에 모두 나열, 대소문자·띄어쓰기·기호는 무시하고 비교)
  lst(...)    주관식 나열형 (need 개 이상 맞히면 정답)
"""
import json, os, re, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

UNITS = [
    ("1", "An overview of immunology"),
    ("2", "Differentiation of immune cells"),
    ("3", "Innate response"),
    ("4", "Complement system"),
    ("5", "Antigen presentation"),
    ("6", "Secondary lymphoid organs"),
    ("7", "[교안 외] 항체와 B cell 활성화"),
    ("8", "[교안 외] T cell 의 종류와 면역 조절"),
    ("9", "[교안 외] 면역 기억 (원본에 시험범위 아님 표기)"),
]
KINDS = [("mc", "객관식"), ("sa", "주관식")]

# (단원, 시작 번호, 소제목)  — 번호는 단원 안의 순번
TOPICS = [
    (1, 1, "선천면역 · 대식세포"), (1, 8, "적응면역 · T cell 과 B cell"), (1, 14, "항체의 구조"),
    (2, 1, "Th subset"),
    (3, 1, "선천면역의 수용성 · 세포 성분"), (3, 6, "Macrophage"), (3, 9, "Neutrophil"), (3, 14, "Natural killer cell"),
    (4, 1, "보체 활성화 경로 · 기능"), (4, 7, "자기 세포 보호"),
    (5, 1, "MHC class I · II"), (5, 8, "Antigen presenting cells"),
    (6, 1, "Lymph node · lymphoid follicle"), (6, 15, "Peyer's patch · Spleen"),
    (7, 1, "항체 클래스"), (7, 7, "IgG 서브클래스 · 보체 · ADCC"), (7, 10, "Class switching 과 cytokine"),
    (7, 13, "B cell · T cell 수용체와 co-receptor"), (7, 15, "알레르기 · Anaphylaxis 용어"),
    (8, 1, "T cell"), (8, 9, "면역 억제 (Restraining the immune system)"),
    (9, 1, "Immunological memory"),
]

Q = []


def topic_of(base):
    u, n = (int(x) for x in base.split("-")[:2])
    t = ""
    for tu, tn, name in TOPICS:
        if tu == u and tn <= n:
            t = name
    return str(u), t


def add(item):
    Q.append(item)


def mc(base, q, opts, ans, src=None, exp=None, fig=None, fixed=False):
    unit, topic = topic_of(base)
    add(dict(id=base, no=base, unit=unit, kind="mc", topic=topic, src=src, q=q, opts=opts, ans=ans, exp=exp,
             fig=("img/%s.jpg" % base) if fig else None, fixed=fixed))


def grp(base, stem, opts, parts, src=None, fig=False, exp=None):
    """parts: [(질문, 정답번호들[, 그 문항만의 보기[, 해설]]), ...]"""
    unit, topic = topic_of(base)
    for i, p in enumerate(parts, 1):
        pq, pans = p[0], p[1]
        popts = p[2] if len(p) > 2 and p[2] else opts
        pexp = p[3] if len(p) > 3 and p[3] else exp
        add(dict(id="%s-Q%d" % (base, i), no="%s Q%d" % (base, i), unit=unit, kind="mc", topic=topic, src=src,
                 q=stem + "\n\n" + pq, opts=popts, ans=pans, exp=pexp,
                 fig=("img/%s.jpg" % base) if fig else None, fixed=True))


def short(base, q, show, acc=None, src=None, exp=None, fig=False, idsuffix=None):
    unit, topic = topic_of(base)
    add(dict(id=base + (idsuffix or ""), no=base + (" " + idsuffix.strip("-") if idsuffix else ""), unit=unit,
             kind="sa", topic=topic, src=src, q=q, show=show, acc=acc or [show], exp=exp,
             fig=("img/%s.jpg" % base) if fig else None))


def shorts(base, stem, parts, src=None, exp=None, fig=False):
    """parts: [(질문, 표시정답, [허용답안])]"""
    unit, topic = topic_of(base)
    for i, (pq, show, acc) in enumerate(parts, 1):
        add(dict(id="%s-Q%d" % (base, i), no="%s Q%d" % (base, i), unit=unit, kind="sa", topic=topic, src=src,
                 q=stem + "\n\n" + pq, show=show, acc=acc or [show], exp=exp,
                 fig=("img/%s.jpg" % base) if fig else None))


def lst(base, q, need, pool, src=None, exp=None, anyof=False):
    """pool: [(표시, [허용답안...]), ...]"""
    unit, topic = topic_of(base)
    add(dict(id=base, no=base, unit=unit, kind="sa", topic=topic, src=src, q=q, need=need, anyof=anyof,
             pool=[dict(s=s, a=a) for s, a in pool], exp=exp, fig=None))


# ───────────────────────── 1. An overview of immunology ─────────────────────────
short("1-1", "아래 빈칸을 채우시오(약자 사용 금지).\n“Danger molecules” which are:\n- characteristic of common microbial invaders.\n- fats and carbohydrates that normally are not found in the human body.\n- “find me and eat me” signals to macrophages\n- are called ____________",
      "pathogen-associated molecular patterns", ["pathogen-associated molecular patterns", "pathogen-associated molecular pattern"], src="23, 22")
short("1-2", "그림을 참조하여 아래 빈칸에 들어갈 적합한 용어를 영어로 답하시오.\nImmunologists like to say that antibodies can “______” these invaders. This term comes from a German word that means “to prepare for eating”.",
      "opsonize", ["opsonize", "opsonise"], src="23, 22", fig=True)
short("1-3", "아래 기술의 용어를 영어 한 단어로 쓰시오.\nA vesicle containing powerful chemicals and enzymes which can destroy bacteria in the cytoplasm of macrophages",
      "lysosome", src="23, 22")
short("1-4", "아래 기술의 용어를 영어 한 단어로 쓰시오.\nA pouch (vesicle) containing a bacterium which is engulfed by a macrophage", "phagosome")
mc("1-5", "Macrophage 의 origin 은?", ["Stem cell", "Dendritic cell", "Monocyte", "Lymphocyte"], [3], src="23, 22")
mc("1-6", "Which of the following play a role as a garbage collector?",
   ["Neutrophils", "Helper T cells", "Natural killer cells", "Killer T cells", "Antigen presenting cells", "Macrophages"], [6], src="23, 22")
lst("1-7", "Innate team 의 player 5 개를 영어 단수형으로 쓰시오. (답칸에 아래 제시된 첫글자 포함해서 쓰시오.)\nM_______\nN_______\nD_______\nC_______\nN_______",
    5, [("macrophage", ["macrophage"]), ("neutrophil", ["neutrophil"]), ("dendritic cell", ["dendritic cell"]),
        ("complement", ["complement"]), ("NK cell (natural killer cell)", ["NK cell", "natural killer cell"])], src="23, 22")
mc("1-8", "Interleukin 2 와 IFN-γ 를 생산하여 분비하는 세포는?",
   ["Macrophage", "Helper T cell", "Dendritic cell", "B cell", "Neutrophil", "Killer T cell"], [2], src="23, 22",
   exp="23 학번 원본 정답은 6 번(killer T cell)으로 표기되어 있으나, 교안(helper T cell = IL-2, IFN-γ 분비)과 22 학번 정답 기준으로 2 번.")
mc("1-9", "APC 에 의해 활성화된 Th cell 이 분비하여 Th cell 의 증식을 촉진하는 growth factor 는?",
   ["Growth hormone", "IL-2", "IL-1", "TNF-α", "IFN-γ", "IFN-α and IFN-β"], [2], src="23, 22",
   exp="“growth factor” 표현은 교안에 없음 — 야마 기준 (교안: helper T cell 이 IL-2, IFN-γ 분비).")
mc("1-10", "바이러스에 감염된 세포를 파괴하는 세포는?",
   ["Neutrophil", "Natural killer cell", "Helper T cell", "Dendritic cell", "Killer T cell"], [2, 5], src="22")
mc("1-11", "T cell 과 B cell 에 대한 설명으로 옳은 것을 모두 고르시오.",
   ["B cells mature in the bone marrow.", "T cells mature in the bone marrow.",
    "B cells specialize in recognizing carbohydrate antigens.", "T cells specialize in recognizing carbohydrate antigens.",
    "B cell will only recognize an antigen if it is “properly presented” by another cell.",
    "T cell will only recognize an antigen if it is “properly presented” by another cell.",
    "B cell can export (secrete) its receptors in the form of antibodies.",
    "T cell can export (secrete) its receptors in the form of antibodies.", "T cells mature in the thymus."],
   [1, 3, 6, 7, 9], src="23, 22",
   exp="3 번은 교안에 “B cells make antibodies that can recognize any organic molecule”로만 나와 있음 — 야마 기준(carbohydrate = T-independent 항원)으로 옳은 선지 처리.")
grp("1-12", "적응면역계 활성화 시 세포들의 역할을 비유한 질문이다.",
    ["macrophage", "natural killer cell", "helper T cell", "dendritic cell", "cytotoxic T cell", "B cell"],
    [("Q1. 미식축구의 quarterback 으로 비유되는 세포는?", [3]),
     ("Q2. 미식축구의 coach 로 비유되는 세포는?", [4], None,
      "교안은 coach 를 특정 세포가 아닌 innate immune system 전체로 설명 — 야마 정답(dendritic cell, 선천-적응 연결 세포) 기준.")],
    src="23")
short("1-13", "lymphatic system 에 대한 아래 기술을 읽고 질문에 답하시오.\nLymph is collected from the tissues of our lower body into lymphatic vessels, and is transported by these vessels, under the influence of muscular contraction, through a series of one-way valves to the upper body. This lymph, plus lymph from the left side of the upper body, is collected into the ( 1 ) and emptied into the ( 2 ) to be recycled back into the blood.\n빈칸 ( 1 )을 채우시오.",
      "thoracic duct", src="23")
grp("1-14", "그림은 B cell 에 의해서 생성되는 주요 단백질의 모식도이다.",
    ["가", "나", "다", "가, 나", "가, 다", "나, 다", "가, 나, 다", "None"],
    [("Q1. 이 단백질의 주요 부위(가, 나, 다)에서 큰포식세포(macrophage)의 Fc receptor 와 결합하는 부위는?", [3]),
     ("Q2. 이 단백질의 주요 부위(가, 나, 다)에서 특이 항원을 인지하고 결합하는 부위는?", [4])],
    src="23, 22", fig=True)

# ───────────────────────── 2. Differentiation of immune cells ─────────────────────────
mc("2-1", "macrophage 를 활성화시키는 Th subset 반응은?", ["Th1", "Th2", "Th17"], [1], src="23")
mc("2-2", "neutrophil recruitment 를 활성화시키는 Th subset 경로는?", ["Th1", "iTreg", "Th2", "Th17"], [4], src="23")
mc("2-3", "Th1 subset response 에 관여하는 사이토카인을 고르시오.", ["IL-12", "IL-4", "TGF-β", "IFN-γ", "IL-17"], [1, 4], src="23",
   exp="교안 02 에는 Th1 = IL-2, IFN-γ까지만 있음. IL-12 는 교안에 없음 — 야마 기준.")
mc("2-4", "Th2 subset response 에 관여하는 사이토카인을 고르시오.", ["IL-12", "IL-4", "TGF-β", "IFN-γ", "IL-17"], [2])
mc("2-5", "Th17 subset 반응을 유도하는 cytokine 은?", ["IL-12", "IL-4", "IL-6 + TGF-β", "IFN-γ", "IL-5"], [3],
   exp="교안 02 에는 Th17 = IL-17 분비, 호중구·염증 자극까지만 있음 — 야마 기준.")
grp("2-6", "TH subset 모식도이다. 질문에 답하시오.", ["가", "나", "다", "라"],
    [("Q1. Th17 cell 은?", [3]), ("Q2. iTreg cell 은?", [4]), ("Q3. Th1 cell 은?", [2]), ("Q4. Th2 cell 은?", [1])], fig=True)
mc("2-7", "iTreg 세포가 분비하는 사이토카인으로 DC 의 B7 에 의한 Th cell co-stimulatory signal 을 block 하는 사이토카인은?",
   ["IL-12", "TNF-α", "IL-10", "IL-23", "TGF-β"], [3], src="23",
   exp="교안 02: Treg = TGF-β, IL-10 으로 T cell 활성 조절. “B7 block” 표현은 교안에 없음 — 야마 기준.")

# ───────────────────────── 3. Innate response ─────────────────────────
lst("3-1", "(2 배점 문제) List cellular components of innate responses.\n(*답안작성 지시사항 : 한가지 종류의 세포로, 영어로, 약자 불허)",
    1, [("macrophage", ["macrophage"]), ("neutrophil", ["neutrophil"]),
        ("natural killer cell", ["natural killer cell"]), ("dendritic cell", ["dendritic cell"])], src="23, 22", anyof=True)
lst("3-2", "(2 배점 문제) List five soluble components of innate responses.\n(*답안작성 지시사항 : 단어 한개로, 영어로, 약자 불허)",
    5, [("lysozyme", ["lysozyme"]), ("lactoferrin", ["lactoferrin"]), ("defensin", ["defensin", "defensins"]),
        ("complement", ["complement"]), ("interferon", ["interferon", "interferons"])])
mc("3-3", "선천면역 수용성 성분으로 아래에서 기술하는 특성을 가지는 것은?\n- attracts leukocytes\n- opsonizes\n- killing of bacteria\n- dilate blood vessels",
   ["lysozyme", "complement", "lactoferrin", "defensin", "interferons (α and β)"], [2], src="23")
short("3-4", "선천면역의 수용성 성분으로 항미생물 펩타이드로, 세균, 바이러스, 진균의 막을 파괴하는 것의 이름을 영어로 쓰시오.",
      "defensin", ["defensin", "defensins"], src="23")
mc("3-5", "바이러스 감염 시 세포에서 분비되어 natural killer cell 을 활성화시키는 cytokine 은? (모두 고르시오)",
   ["IFN-α", "IL-1", "IFN-β", "LPS", "TNF", "IFN-γ", "IL-12"], [1, 3], src="23")
mc("3-6", "resting macrophage 를 activated macrophage 로 변화시키는 성분으로 가장 잘 알려진 것은?",
   ["IL-2", "IFN-γ", "IL-12", "TNF", "LPS", "IL-1"], [2])
lst("3-7", "interferon gamma 를 생산하는 주요 세포 2 가지를 적으시오. (약자 불허)", 2,
    [("helper T cell", ["helper T cell", "T helper cell", "Th cell", "CD4 T cell"]),
     ("NK cell", ["NK cell", "natural killer cell"])], src="23")
short("3-8", "hyperactivated macrophage 가 생산하는 것으로 종양세포와 바이러스 감염세포를 파괴하는 cytokine 의 명칭을 적으시오. (영어로, 약자 불허)",
      "tumor necrosis factor", ["tumor necrosis factor", "tumour necrosis factor", "tumor necrosis factor alpha", "tumor necrosis factor-α"], src="23")
mc("3-9", "Which are the only immune system cells that are licensed to liquify both cells and connective tissue?",
   ["macrophages", "killer T cells", "dendritic cells", "natural killer cells", "neutrophils"], [5], src="23")
_310 = ("Macrophage 와 Neutrophil 의 특성 비교에 대한 문제이다. 질문에 답하시오.\n"
        "- Arrive at local site of infection: ____\n- Phagocytic activity (Yes or No): ____\n"
        "- Effectiveness of bacterial destruction: ____\n- Antigen presentation on class II MHC molecules (Yes or No): ____\n"
        "- Cytokine secretion (Yes or No): ____\n- Life span: ____\n"
        "위에서 나열된 특성에 대한 답으로 해당하는 것을 순서대로 아래 보기에서 골라 보기 숫자로만 이어서 쓰시오.\n"
        "① Very effective  ② Short  ③ Less effective unless activated  ④ Long\n"
        "⑤ Yes  ⑥ Arrive later  ⑦ Arrive first  ⑧ No")
_310exp = ("23 학번은 “Cytokine secretion” 행 없이 5 개 항목으로 출제(neutrophil 75182 / macrophage 65354, 23 3 차 원본 65654 는 3 번째 자리 표기 오류). "
           "Cytokine secretion 행은 교안에 없음 — 22 학번 정답 기준(neutrophil No, macrophage Yes).")
shorts("3-10", _310, [("Q1. neutrophil 에 해당하는 것 6 개 (숫자만 이어서)", "751882", ["751882"]),
                      ("Q2. macrophage 에 해당하는 것 6 개 (숫자만 이어서)", "653554", ["653554"])], src="23, 22", exp=_310exp)
mc("3-11", "그림은 세균이 인체에 침입하였을 때 혈류 순환 중인 호중구가 균이 존재하는 조직부위의 혈관 밖으로 빠져나오는 기전을 묘사한 모식도이다. 정상 조직의 혈관내에서는 빠른 속도로 이동하는 호중구가 염증이 있는 조직의 혈관내에서 이동이 느려져 혈관벽을 따라 천천히 굴러가도록 영향을 준 인자로 큰포식세포가 분비한 사이토카인 두 개, ( 가 )에 들어갈 사이토카인을 고르시오.",
   ["C5a", "IL-1", "TNF", "LPS", "f-met"], [2, 3], src="23, 22", fig=True)
short("3-12", "그림은 세균이 인체에 침입하였을 때 혈류 순환 중인 호중구가 균이 존재하는 조직부위의 혈관 밖으로 빠져나오는 기전을 묘사한 모식도이다. 정상 조직의 혈관내에서는 빠른 속도로 이동하는 호중구가 염증이 있는 조직의 혈관내에서 이동이 느려져 혈관벽을 따라 천천히 굴러가도록 영향을 준 인자로 (1)에 들어갈 알맞은 말을 쓰시오. (약자 불허)",
      "selectin", ["selectin", "selectins"], src="23", fig=True)
mc("3-13", "Neutrophil 이 혈관 밖으로 나가는 기전에서 cytokine 시그날에 의해 neutrophil 의 움직임 속도가 줄어들고 혈관벽을 따라 굴러가게 하는 데 관여하는 성분을 모두 고르시오.",
   ["IL-1", "Selectin on neutrophil", "Integrin on neutrophil", "IL-2", "ICAM on neutrophil", "Selectin on endothelial cells",
    "Selectin ligand on endothelial cells", "Selectin ligand in neutrophils", "Integrin on endothelial cells",
    "ICAM on endothelial cells", "TNF", "IL-12"], [1, 6, 8, 11])
mc("3-14", "Natural killer cell 의 “don’t kill” signal 은?",
   ["unusual carbohydrate", "presence of class I MHC molecule", "unusual proteins", "loss of class I MHC molecule",
    "loss of class II MHC molecule", "presence of class II MHC molecule"], [2], src="23, 22")
mc("3-15", "세포질에 과립(granule)이 존재하는 면역세포로 바이러스에 감염된 세포를 인식 후 세포자멸사(apoptosis)를 유도한다. 이 세포의 활성은 I 형 인터페론(α, β)에 의해서 증가된다. 이 면역세포는 바이러스 감염세포뿐만 아니라, 암세포에도 같은 작용을 한다. 이 면역세포는?",
   ["호중구(neutrophil)", "자연살해세포(natural killer cell)", "비만세포(mast cell)", "큰포식세포(macrophage)", "세포독성 T 세포(cytotoxic T cell)"], [2], src="23")

# ───────────────────────── 4. Complement system ─────────────────────────
lst("4-1", "List three pathways of complement activation.\n(*답안작성 지시사항 : 영어로, 한 단어로)", 3,
    [("classical", ["classical"]), ("alternative", ["alternative"]), ("lectin", ["lectin"])], src="23, 22")
lst("4-2", "(2 배점 문제) List four major functions of complement system.\n(*답안작성 지시사항 : 영어로, 약자 허용)", 4,
    [("MAC", ["MAC", "membrane attack complex", "cell lysis", "lysis"]),
     ("opsonin", ["opsonin", "opsonization", "opsonisation"]),
     ("chemoattractant", ["chemoattractant", "chemotaxis"]),
     ("anaphylatoxin", ["anaphylatoxin", "anaphylatoxins"])], src="23, 22")
shorts("4-3", "보체의 활성화 경로별 C3 convertase 이름을 쓰시오. (약자 가능)",
       [("Q1. alternative pathway 에 의해 생성되는 C3 convertase", "C3bBb", None),
        ("Q2. classical pathway 에 의해 생성되는 C3 convertase", "C4b2a", None),
        ("Q3. lectin pathway 에 의해 생성되는 C3 convertase", "C4b2a", None)], src="23, 22")
short("4-4", "보체의 활성화 경로 중 lectin pathway 에서 C3 convertase 형성에 바로 기여한 것의 이름을 쓰시오. (약자 가능)",
      "MASP (MBP-associated serine protease)",
      ["MASP", "MASP-2", "MBP-associated serine protease", "MBL-associated serine protease",
       "mannose-binding lectin-associated serine protease"], src="23, 22")
_45 = "Complement system 활성화 과정 모식도이다. 질문에 답하시오."
_dot = ["적색 도트 1", "적색 도트 2", "적색 도트 3", "적색 도트 4", "적색 도트 5", "적색 도트 6"]
grp("4-5", _45, ["가", "나", "다"],
    [("Q1. Alternative pathway 는? (가, 나, 다 중 선택)", [3]),
     ("Q2. Lectin pathway 는? (가, 나, 다 중 선택)", [2]),
     ("Q3. Classical pathway 는? (가, 나, 다 중 선택)", [1]),
     ("Q4. opsonin 기능이 있는 보체를 고르시오. (적색 도트 번호, 1~6)", [2], _dot),
     ("Q5. 혈관 투과성을 증가시키는 보체를 고르시오. (적색 도트 번호, 1~6)", [1, 4], _dot),
     ("Q6. 백혈구를 유인하는 보체를 고르시오. (적색 도트 번호, 1~6)", [1, 4], _dot)],
    src="23, 22", fig=True)
mc("4-6", "antigen 을 opsonization 할 수 있는 성분을 모두 고르시오.",
   ["interferon", "antibody", "lysozyme", "complement", "albumin"], [2, 4], src="23")
lst("4-7", "List three proteins that prevent the formation of membrane attack complexes (complements) on the surface of our own cells. (약자 허용)", 3,
    [("MCP", ["MCP", "membrane cofactor protein", "CD46"]),
     ("DAF", ["DAF", "decay accelerating factor", "decay-accelerating factor", "CD55"]),
     ("CD59", ["CD59", "protectin"])], src="23")

# ───────────────────────── 5. Antigen presentation ─────────────────────────
mc("5-1", "핵을 가진 모든 세포막에 존재하는 MHC 클래스는?", ["Class I MHC", "Class II MHC", "Both class I MHC and class II MHC"], [1], src="23, 22")
mc("5-2", "인체 세포 바깥에서 유래된 문제의 정보를 전달하는 MHC class 는?", ["Class I MHC", "Class II MHC"], [2], src="23, 22")
mc("5-3", "What type of MHC molecules do helper T cells recognize?", ["Class I MHC molecules", "Class II MHC molecules", "None"], [2], src="22")
mc("5-4", "Which of the following make class II MHC molecule?",
   ["Lymphocytes", "Antigen presenting cells", "Neutrophils", "Natural killer cells", "Vascular endothelial cells"], [2], src="22")
mc("5-5", "Class II MHC molecule 을 발현하는 세포는? (모두 고르시오)",
   ["Respiratory epithelial cells", "B cells", "Dendritic cells", "Macrophages", "Helper T cells", "Killer T cells"], [2, 3, 4], src="23, 22")
mc("5-6", "Dendritic cell 이 가지는 MHC class 는? (모두 고르시오)", ["Class I MHC", "Class II MHC", "None of the options"], [1, 2], src="23, 22")
grp("5-7", "MHC molecule class I 과 class II 에 관한 기술이다. 질문에 답하시오.",
    ["ER 에서 invariant chain 과 결합, 세포내 항원결합을 차단하고 endosome 으로 유리된다",
     "Helper T 세포에 항원을 제시한다",
     "ER 에서 조립된다",
     "Killer T 세포가 인지, 결합하여 세포내부를 들여다보고 세포 감염/파괴 여부를 결정한다",
     "표적 항원은 proteasome 에 의해서 단백질이 작은 조각으로 잘라진다",
     "세포 외부에서 벌어지는 일을 게시한다(세포외 항원을 게시한다)",
     "Endosome 과 phagosome 융합, 분해된 펩티드가 invariant chain 을 대치하여 결합한다",
     "세포 내부에서 벌어지는 일을 게시한다(세포내 항원을 게시한다)",
     "모든 유핵세포 표면에 존재한다",
     "ER 에서 peptide 항원과 결합한 후 세포표면으로 이동한다",
     "항원전달세포에만 존재한다"],
    [("Q1. (3 배점 문제) MHC Class I 분자에 해당하는 기술 6 개를 고르시오.", [3, 4, 5, 8, 9, 10]),
     ("Q2. (3 배점 문제) MHC Class II 분자에 해당하는 기술 6 개를 고르시오.", [1, 2, 3, 6, 7, 11])],
    src="23, 22",
    exp="3 번(“ER 에서 조립된다”)은 class I·II 모두 해당. 22 학번 원본은 정답이 색(빨간색)으로만 표시되어 있어 23 학번 정답으로 확인.")
grp("5-8", "항원전달세포(antigen presenting cell, APC)에 관한 설명이다. 질문에 답하시오.",
    ["선천면역계와 적응면역계 사이에서 다리와 같은 역할을 한다",
     "조직에서 병균과 싸운다",
     "항원 경험 T세포에 반복적 자극을 주어 T세포 활성을 유지시켜 전투에 계속 참여하도록 한다",
     "마치 포도주 감정가 같은 역할을 한다",
     "처음 항원전달을 위해 helper T세포에 의해 활성이 되어야 한다",
     "항원전달세포로서 재감염 초기에 주요 역할을 한다",
     "비무장 사진기자처럼 전투 사진을 찍고 기사를 제출하기 위해 전쟁터를 떠난다",
     "적응면역 반응을 개시한다",
     "항원전달을 위해 림프절로 이동하지 않는다",
     "활성화되면 초강력 항원전달세포가 된다(Super-APC)",
     "항원전달세포로 작용한다",
     "림프절로 이동하여 항원을 naive T세포에 전달한다",
     "적응면역이 활성화된 이후 항원전달에 가장 유용하다",
     "항원수용체를 이용하여 적은 양의 항원을 농축하여 helper T세포에 전달, 활성화시킬 수 있다",
     "불가사리 같은 모양을 한다"],
    [("Q1. 수지상세포(dendritic cell, DC)에 해당하는 기술 7 개를 고르시오.", [1, 4, 7, 8, 11, 12, 15]),
     ("Q2. 큰포식세포(macrophage)에 해당하는 기술 5 개를 고르시오.", [2, 3, 9, 11, 13]),
     ("Q3. B cell 에 해당하는 기술 5 개를 고르시오.", [5, 6, 10, 11, 14], None, "23 학번 3 차에는 14 개 보기·DC 6 개로 출제된 변형이 있음(내용은 동일).")],
    src="23, 22")
mc("5-9", "다음 세포 중 helper T cell 과 killer T cell 양쪽에 항원을 제시할 수 있는 APC 는?",
   ["dendritic cell", "follicular dendritic cell", "macrophage", "B cell", "NK cell", "monocyte"], [1], src="23")
mc("5-10", "killer T cell 에 처음 항원을 제시하는 세포는?",
   ["macrophage", "dendritic cell", "B cell", "helper T cell", "monocyte", "NK cell"], [2], src="23")
mc("5-11", "T cell 활성화를 위해 T cell receptor crosslinking 에 필요한 T cell receptor 총 수를 감소시켜 효율적인 T cell 활성화를 유도하는 단백질로 DC 표면에 있는 것은?",
   ["CD40L", "CD4", "CD3", "MHC", "B7", "CD40"], [5], src="23",
   exp="교안 05: APC 의 B7 이 T cell 의 CD28 에 결합(co-stimulation). “TCR crosslinking 수 감소” 표현은 교안에 없음 — 야마 기준.")

# ───────────────────────── 6. Secondary lymphoid organs ─────────────────────────
mc("6-1", "림프절(lymph node) 안에서 T cell 이 주로 밀집하여 존재하는 부위는?",
   ["lymphoid follicle", "medullary sinus", "cortex", "paracortex"], [4], src="23")
mc("6-2", "다음 중 lymph node 의 paracortex area 에 존재하는 것을 모두 고르시오.",
   ["B cell", "killer T cell", "HEV", "helper T cell", "dendritic cell", "follicular dendritic cell", "M cell"], [2, 3, 4, 5], src="23")
short("6-3", "혈류에서 순환하는 B cell 또는 T cell 이 lymph node 안으로 들어가는 길(작은 혈관내 특수한 부위)의 명칭을 영어로 적으시오. (약자 불허)",
      "high endothelial venule", ["high endothelial venule", "high endothelial venules"], src="23")
mc("6-4", "lymph node 안 구조물 중 macrophage 가 주로 존재하는 부위는?",
   ["lymphoid follicle", "medullary sinus", "paracortex", "marginal sinus", "cortex", "periarteriolar lymphocyte sheath"], [4], src="23",
   exp="23 학번 3 차 원본 정답은 “medullary sinus”로 표기되어 있으나, 교안(marginal sinus = macrophage)과 23 학번 4 차 정답 기준으로 4 번.")
mc("6-5", "antigen 이 lymph node 로 운반되는 방법을 모두 고르시오.",
   ["by macrophages", "by lymph", "by dendritic cells", "by B cells", "by blood"], [2, 3], src="23")
short("6-6", "체내 진입한 항원을 림프절에 있는 T cell 에게 보여주는 방법이다. 빈칸을 채우시오. (영어 소문자)\nAntigen presenting cells carry the antigen into the lymph node display for T cells. Antigen bound by complement or by antibodies can be carried by the lymph into the lymph node. There the antigen will be captured by ____________ for display to B cells.",
      "follicular dendritic cell", ["follicular dendritic cell", "follicular dendritic cells"], src="23")
mc("6-7", "다음 중 follicular dendritic cells 의 특징으로 옳은 것을 모두 고르시오.",
   ["are produced in bone marrow", "express complement receptors on the cell surface", "present antigens to T cells",
    "deliver foreign antigens from tissues to lymph nodes", "express Fc receptors on the cell surface", "are in a starfish form"], [2, 5, 6], src="23")
mc("6-8", "follicular dendritic cell 이 표면에 가지는 수용체를 모두 고르시오.",
   ["complement receptor", "TCR", "Fc receptor", "BCR", "CD4 coreceptor"], [1, 3], src="23")
mc("6-9", "primary lymphoid follicle 안에 있는 주요 세포를 모두 고르시오.",
   ["T cells", "antigen presenting cells", "B cells", "follicular dendritic cells", "plasma cells"], [3, 4], src="23")
shorts("6-10", "다음 빈칸에 들어갈 용어를 순서대로 영어로 입력하시오. (약자 불허)\nThese B cells whose receptors are crosslinked by their cognate antigens hanging from these follicular dendritic “trees” proliferate to build up their numbers. Follicle begins to grow and become a center of B cell development. This active lymphoid follicle is called a ( 1 ) lymphoid follicle or a ( 2 ) center.",
       [("( 1 ) 에 들어갈 말", "secondary", None), ("( 2 ) 에 들어갈 말", "germinal", None)], src="23")
mc("6-11", "다음 중 lymphoid follicle 안에서 B cell 이 apoptotic death 로부터 구조되는 것은? (정답 3 개)",
   ["BCR crosslinking by antigens", "APC co-stimulation", "T cell co-stimulation", "BCR affinity for antigen", "MHC combination with antigen"],
   [1, 3, 4], src="23")
mc("6-12", "secondary lymphoid organ 안에서 B cell 이 증식하는 장소는?",
   ["lymphoid follicle", "medullary sinus", "paracortex", "marginal sinus", "high endothelial venule"], [1], src="23")
mc("6-13", "B cell 의 항원에 대한 affinity 를 변화시키는 기전은?",
   ["rearrangement of BCR gene segments", "somatic hypermutation of BCR", "modification of B cell MHC class II molecule",
    "variation of BCR mRNA expression", "class switching of BCR", "modification of cognate antigen structures",
    "modification of B cell complement receptor", "modification of B cell PAMP receptor"], [2], src="23")
short("6-14", "아래 기술의 용어를 영어 한 단어로 쓰시오.\nthe tiny region of the cognate antigen that a BCR actually binds to", "epitope", ["epitope", "epitopes"],
      src="23", exp="교안 06 그림에 “Epitope” 표기만 있고 정의 문장은 없음 — 야마 기준.")
short("6-15", "장내에 존재하는 외부 항원이 Peyer’s patches 에 들어가는 방법으로 빈칸을 영어로 채우시오.\nthrough ________",
      "M cell", ["M cell", "M cells", "microfold cell", "microfold cells"], src="23")
short("6-16", "spleen 에 존재하는 항원제시세포로, T cell 부위로 이동하여 항원을 전달하는 세포의 명칭을 영어로 적으시오. (약자 불허)",
      "resident dendritic cell", ["resident dendritic cell", "resident dendritic cells"], src="23")
mc("6-17", "spleen 에서 항원 전달 전 dendritic cell 이 위치하는 곳은?",
   ["artery", "marginal sinus", "B cell area", "PALS", "lymphoid follicle", "vein"], [2], src="23")
mc("6-18", "spleen 에서 T cell area 는?",
   ["artery", "periarteriolar lymphocyte sheath", "red pulp", "lymphoid follicle", "marginal sinus"], [2], src="23")
mc("6-19", "다음 중 spleen 에 없는 것을 모두 고르시오.",
   ["Incoming lymphatics", "High endothelial venule", "Outgoing lymphatics", "Lymphoid follicle", "Marginal sinus", "T cell area", "M cell"],
   [1, 2, 3, 7],
   exp="교안: spleen 은 incoming lymphatics·HEV 없음, M cell 은 Peyer’s patch 구조. Outgoing lymphatics 는 교안에 언급이 없어 역대 모음 표시 정답 기준.")

# ───────────────────────── 7. [교안 외] 항체와 B cell 활성화 ─────────────────────────
mc("7-1", "Which part of antibody determines its class?", ["Light chain", "Fc tail", "Heavy chain", "Fab regions"], [2], src="22")
_ig5 = ["IgM", "IgE", "IgD", "IgG", "IgA"]
grp("7-2", "항체 클래스의 분포와 특성에 관한 질문이다. (보기에서 고르시오)", _ig5,
    [("Q1. 가장 긴 수명을 가지는 항체 클래스는?", [4]),
     ("Q2. 사람 혈청에 가장 많이 존재하는 항체 클래스는?", [4]),
     ("Q3. 태반을 통과할 수 있는 항체 클래스는?", [4]),
     ("Q4. 인체(우리 몸 전체)에서 가장 많이 존재하는 항체 클래스는?", [5]),
     ("Q5. 모유로 분비되어 아기의 장점막을 코팅하여 장점막 감염을 방어하는 항체는?", [5]),
     ("Q6. 점막에 존재하는 항체로, 4 개의 항원 결합 부위를 가지는 형태로 존재하는 항체는?", [5])], src="22")
grp("7-3", "항체 클래스의 기능에 관한 질문이다. (보기에서 고르시오)", _ig5,
    [("Q1. 바이러스 또는 세균 감염 시 ‘early antibody’로 작용하여 병원체에 결합, 감염을 막는 ‘중화작용(neutralization)’을 잘하는 항체 클래스는?", [1]),
     ("Q2. Anaphylaxis 의 원인이 되는 항체 클래스는?", [2]),
     ("Q3. Prausnitz-Küstner(PK) test 와 관련이 높은 항체 클래스는?", [2]),
     ("Q4. 1967 년 Kimishige Ishizaka 와 부인 Teruko 가 발견한 항체 클래스는?", [2])], src="23, 22")
mc("7-4", "Virgin B cell 이 처음 활성화시 주로 만들어지는 항체 클래스는?", ["IgA", "IgM", "IgG", "IgD", "IgE"], [2], src="22")
grp("7-5", "항체 클래스 전환(class switching)에 관한 질문이다. (보기에서 모두 고르시오)", _ig5,
    [("Q1. 다음 항체 클래스 중 mRNA splicing 기전에 의해 결정되는 것은?", [1, 3]),
     ("Q2. 다음 항체 중 DNA 상 class switching 없이 생성되는 것은?", [1, 3]),
     ("Q3. 항체의 DNA 상 switching signal 이 없는 constant region 부위는? (예: IgD 의 constant region = IgD)", [3])], src="23, 22")
mc("7-6", "IFN-γ 에 의해 class switching 되어 생산이 유도되는 항체는?", ["IgG3", "IgD", "IgA", "IgM", "IgE"], [1], src="23, 22")
grp("7-7", "항체 클래스·서브클래스에 관한 질문이다. (보기에서 고르시오)",
    ["IgM", "IgG2", "IgA2", "IgD", "IgG1", "IgG3", "IgG4", "IgA1", "IgE"],
    [("Q1. Complement activation 을 가장 잘 하는 항체 클래스는?", [1]),
     ("Q2. 병균과 결합력이 강해 opsonization 에 가장 효과적인 항체 클래스는?", [5])], src="23, 22")
grp("7-8", "IgG 서브클래스에 관한 질문이다. (보기에서 고르시오)", ["IgG1", "IgG2", "IgG3", "IgG4"],
    [("Q1. ADCC(antibody-dependent cellular cytotoxicity)를 가장 잘 매개하는 IgG 서브클래스는?", [3]),
     ("Q2. IgG 서브클래스 중 complement fixation 을 가장 잘하는 클래스는?", [3])], src="23, 22")
mc("7-9", "다음 중 NK cell 이 가지는 receptor 는?",
   ["IgG1 Fc receptor", "IgG2 Fc receptor", "IgG3 Fc receptor", "IgG4 Fc receptor", "IgE Fc receptor", "None of the listed"], [3], src="22")
grp("7-10", "Th cell 이 분비하여 B cell 에 작용하는 cytokine 에 관한 질문이다. (보기에서 고르시오)",
    ["IL-1", "IL-5", "IL-2", "IL-4", "IFN-γ", "TGF-β"],
    [("Q1. 기생충 방어에 적합한 항체 클래스의 변환 생성을 위해 Th cell 이 분비하여 B cell 에 작용하는 cytokine 은?", [4]),
     ("Q2. 감기 바이러스 감염으로부터 방어하기 위해 적합한 항체 클래스의 변환 생성을 위해 Th cell 이 분비하여 B cell 에 작용한 cytokine 두 개는?", [2, 6]),
     ("Q3. Complement 활성화가 강력한 IgG 서브클래스의 변환 생성을 위해 Th cell 이 분비하여 B cell 에 작용하는 cytokine 은?", [5])], src="23, 22")
mc("7-11", "T cell-independent B cell activation 이 가능한 항원 종류는?", ["hapten", "carbohydrate", "protein"], [2], src="23, 22")
mc("7-12", "그림은 T-dependent B cell activation 의 모식도이다. B cell 활성을 위한 보조 자극(co-stimulation)으로 부호 (1) 단백을 고르시오.",
   ["B7", "CD40", "CD28", "CD40L", "CTLA-4"], [4], src="23", fig=True)
grp("7-13", "T cell · B cell activation 에 관하여 질문에 답하시오. (보기에서 고르시오)",
    ["peptide + MHC", "B7", "BCR + CD3", "CD4 or CD8", "BCR + Igα, Igβ", "TCR + CD3", "CD40L", "TCR + MHC", "TCR + Igα, Igβ", "complement receptor"],
    [("Q1. B cell 의 receptor 는?", [5]),
     ("Q2. B cell 의 signal amplifier 는?", [10]),
     ("Q3. B cell 의 co-receptor 는?", [10]),
     ("Q4. T 세포 의존형 B cell activation 에 기여하는 것은?", [7]),
     ("Q5. T cell 의 receptor 는?", [6]),
     ("Q6. T cell 의 co-receptor 는?", [4]),
     ("Q7. T cell 의 signal amplifier 는?", [2]),
     ("Q8. antigen presenting cell 을 activation 시키는 것은?", [7])], src="23, 22",
    exp="B cell 의 signal amplifier = complement receptor(C3d–CR2)는 교안 04 에 있음. 나머지 항목은 교안 외 — 야마 기준.")
mc("7-14", "항체의 유전자가 모듈식 디자인에 의해 형성된다는 것을 발견한 사람은?",
   ["Elie Metchnikoff", "Edward Jenner", "Shibasaburo Kitasato", "Paul Ehrlich", "Susumu Tonegawa", "Thucydides", "Robert Koch",
    "Louis Pasteur", "Emil von Behring", "Jules Bordet"], [5])
short("7-15", "노벨상 수상자인 Charles Richet 이 처음 만든 용어이다. ‘첫번째 주사가 방어에 역효과를 나타냈다’는 결과를 기술한 용어를 쓰시오. (*답안작성 지시사항 : 영어로, 약자 불허)",
      "anaphylaxis", src="23, 22")
short("7-16", "(2 배점 문제) 1919 년 재생불량빈혈 환자가 수혈을 받은 후 뉴욕 센트럴 파크에서 말을 타던 중 천식 발작이 생겼다. Ramirez 박사는 수혈한 혈액의 공여자가 말에 알러지가 있는 사람이었음을 발견하였다. 혈액에 의해 알러지가 전파될 수 있다는 증례 논문을 발표하였다. 이후 알러지를 갖고있는 개체의 혈청에 존재하여 알러지를 매개할 수 있는 성분을 일컫는 용어가 탄생했다. 이 용어가 무엇인지 영어 한 단어 단수형으로 쓰시오.",
      "reagin", src="23, 22")
mc("7-17", "In 1921, Prausnitz and Kustner passively sensitized the skin of healthy subjects and transferred positive skin test results, a method referred to as the Prausnitz-Kustner (PK) test.\n건강한 피험자의 피부를 수동적으로 감작시켜 양성 반응을 전달하기 위해 피부에 주사한 성분은?",
   ["알러지 증상을 발현하는 사람에서 분리한 CD4 Th cell", "알러지 증상을 발현하는 사람에서 분리한 mast cell", "알러지 증상을 발현하는 사람의 혈청",
    "알러지 증상을 발현하는 사람의 알러지 유발 물질", "알러지 증상을 발현하는 사람에서 분리한 dendritic cell"], [3], src="22")

# ───────────────────────── 8. [교안 외] T cell 의 종류와 면역 조절 ─────────────────────────
mc("8-1", "다음 T cell 에 대한 설명 중 옳은 것은?",
   ["γδ T cell 은 CD4 나 CD8 co-receptor 를 발현한다.", "αβ T cell 은 peptide 항원은 인지하지만 MHC 분자는 인지 못한다.",
    "γδ receptor 는 αβ receptor 보다 더 다양성이 많다.", "95% 이상 순환 T cell 의 TCR 은 γδ receptor 이다.",
    "γδ T cell 은 unpresented 항원에 중점을 둔다."], [5], src="23, 22")
grp("8-2", "다음 T cell type 에 관한 질문이다. (보기에서 고르시오)", ["αβ T cells", "γδ T cells", "NKT cells"],
    [("Q1. lipids 항원을 인지할 수 있는 것은?", [3]),
     ("Q2. 외부 환경과 접하는 인체 부위에 많이 분포하는 것은?", [2]),
     ("Q3. lipid 항원을 제시받아 결핵(tuberculosis) 방어에 중요한 역할을 하는 것은?", [3])], src="23, 22")
mc("8-3", "NKT cells 의 특성으로 옳은 것을 모두 고르시오.",
   ["have TCRs", "recognize unpresented antigen", "recognize antigens presented by MHC class II molecules",
    "recognize antigens presented by MHC class I molecules", "recognize lipid antigens"], [1, 5], src="23")
mc("8-4", "NKT cell 에 대한 설명으로 옳은 것을 모두 고르시오.",
   ["순환 T cell 의 10%를 차지한다.", "carbohydrate 항원을 인지한다.", "αβ receptor 와 γδ receptor 둘 다 가진다.",
    "receptor diversity 가 매우 제한되어 있다.", "class II MHC 분자에 의한 항원제시를 받는다.",
    "NKT cell 은 다양성이 제한된 γδ receptor 를 가진다.", "NKT cell 은 αβ receptor 도 γδ receptor 도 모두 가지고 있지 않다.",
    "NKT cell 은 다양성이 많은 αβ receptor 를 가진다.", "NKT cell 은 다양성이 제한된 αβ receptor 를 가진다.",
    "NKT cell 은 다양성이 많은 γδ receptor 를 가진다."], [4, 9])
mc("8-5", "What is the major antigen type recognized by T cell receptor?",
   ["Polysaccharide", "Fat", "Lipopolysaccharide", "Protein", "Nucleic acid", "Mannose"], [4])
mc("8-6", "T cell 에서 항원 인지 신호를 핵으로 전달하는데 기여하는 단백질은?", ["TCR", "CD8", "CD3", "CD4", "Igα", "Igβ"], [3])
mc("8-7", "T cell 이 활성화된 이후에 T cell 표면에 발현이 점점 증가되는 분자로 DC 의 B7 과 결합하여 T cell 비활성화에 관여하는 것은?",
   ["CD40L", "TCR", "CD28", "CD4", "CTLA-4"], [5])
mc("8-8", "LPS 를 감지하는 TLR type 은?", ["TLR1", "TLR2", "TLR3", "TLR4"], [4], src="23",
   exp="교안 03 에 LPS(danger signal)는 있으나 TLR 종류는 없음 — 야마 기준.")
mc("8-9", "intestinal macrophage 의 특성을 모두 고르시오.",
   ["Do not secrete cytokines", "Can phagocytose bacteria", "Cannot phagocytose bacteria", "Secrete cytokines"], [1, 2])
mc("8-10", "침입한 병균과 싸우는 반복된 자극에 대한 재활성화에 지친 T 세포를 제거하는 기전은?",
   ["Neutrophil-mediating killing", "ADCC-mediating killing", "Complement-mediating killing(MAC)",
    "CTL-mediating killing by recognition of MHC class I-bound antigen expressed on exhausted T cell", "FAS-mediating killing"], [5])

# ───────────────────────── 9. [교안 외] 면역 기억 ─────────────────────────
_ex9 = "추가 지식으로 판단 (교안 밖)."
mc("9-1", "림프구의 분화에 관한 설명으로 옳은 것은?",
   ["Negative selection 이란 self Ag 를 인지하는 세포는 아포토시스를 겪는 것을 말한다.", "Double negative cell 이란 MHC 와 Ag 가 없는 세포를 말한다.",
    "B 림프구는 흉선(thymus)로 이주한다.", "최종적으로 성숙된 림프구는 CD4 와 CD8 이 사라진다.",
    "Positive selection 이란 MHC 를 인지하는 세포는 아포토시스를 겪는 것을 말한다."], [1], exp=_ex9)
mc("9-2", "다음 중 평생 면역을 제공하는 항체를 생산하는 세포는?",
   ["Long-lived plasma cell", "Short-lived plasma cell", "Central memory B cell"], [1], exp=_ex9)
mc("9-3", "B cell 이 침입자에 대한 반응으로 생겨난 세포 중에서 침입에 대하여 즉각적인 항체 보호를 제공하는 것은?",
   ["Long-lived plasma cell", "Short-lived plasma cell", "Central memory B cell"], [2], exp=_ex9)
mc("9-4", "병원균이 인체에 침입 후 병원균-특이적인 B, T 세포들의 증식에 소요되는 시간은?",
   ["1-2 개월", "1-2 일", "1-2 시간", "1-2 년", "1-2 주"], [5], exp=_ex9)


# ───────────────────────── 검증 및 출력 ─────────────────────────
def validate():
    ids, errs = set(), []
    for q in Q:
        if q["id"] in ids:
            errs.append("id 중복: " + q["id"])
        ids.add(q["id"])
        if q["kind"] == "mc":
            n = len(q["opts"])
            if not q["ans"] or any(a < 1 or a > n for a in q["ans"]):
                errs.append("정답 번호 범위 오류: %s (보기 %d개, 정답 %s)" % (q["id"], n, q["ans"]))
            if len(set(q["ans"])) != len(q["ans"]):
                errs.append("정답 번호 중복: " + q["id"])
        else:
            if "pool" in q:
                if q["need"] > len(q["pool"]):
                    errs.append("need 가 pool 보다 큼: " + q["id"])
            elif not q.get("acc"):
                errs.append("허용 답안 없음: " + q["id"])
        if q.get("fig") and not os.path.exists(os.path.join(ROOT, q["fig"])):
            errs.append("그림 파일 없음: %s (%s)" % (q["id"], q["fig"]))
        if q["unit"] not in dict(UNITS):
            errs.append("알 수 없는 단원: " + q["id"])
    return errs


def clean(q):
    return {k: v for k, v in q.items() if v not in (None, False, "")}


def main():
    errs = validate()
    if errs:
        print("\n".join(errs))
        sys.exit(1)
    data = dict(
        version=1,
        built=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        title="면역학 개론 기출 퀴즈",
        units=[dict(id=i, name=n) for i, n in UNITS],
        kinds=[dict(id=i, name=n) for i, n in KINDS],
        questions=[clean(q) for q in Q],
    )
    out = os.path.join(ROOT, "questions.js")
    with open(out, "w", encoding="utf-8") as f:
        f.write("/* 자동 생성 파일 — tools/build.py 로 만들어집니다. 직접 수정하지 마세요. */\n")
        f.write("window.QUIZ_DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n")
    mcn = sum(1 for q in Q if q["kind"] == "mc")
    print("OK: %d문항 (객관식 %d · 주관식 %d) → %s" % (len(Q), mcn, len(Q) - mcn, out))
    per = {}
    for q in Q:
        per[q["unit"]] = per.get(q["unit"], 0) + 1
    print("단원별:", ", ".join("%s단원 %d" % (u, per[u]) for u in sorted(per)))


if __name__ == "__main__":
    main()
