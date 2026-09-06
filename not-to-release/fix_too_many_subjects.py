import os
import udapi

# Fix too-many-subjects errors in UD_Korean-PUD test split.
# 71 errors across 68 sentences (w01075037 has 4 errors).
#
# The dominant pattern is Korean's "double subject" (이중 주어) construction:
#   - Topicalized/outer noun (X-은/는 or X-이/가 as outer semantic subject)
#   - Inner grammatical subject of the predicate (수, 관련이, 공적이, 크기가, …)
# Fix: outer/topicalized noun → nsubj:outer
#
# Secondary patterns:
#   - Percentage/multiplier/measure NPs tagged as nsubj instead of advmod
#     (e.g. "10% 상승하다", "3배 많다", "3천 부만 발행되다", "두 번 쫓겨나다")
#   - Fix: measure NP → advmod

FIXES = {
    # 이름은 (outer topic) + 것이 (clausal subject) under 분명하다
    'n01015033': [('deprel', 4, 'nsubj:outer')],

    # 케이라가 (subject) + 배 (multiplier "3 times") under 많았다
    'n01015036': [('deprel', 35, 'obl')],

    # 항공 (outer agent) + 수 (grammatical subj of 있을지) — 수 있다 construction
    'n01017008': [('deprel', 3, 'nsubj:outer')],

    # 것은 (outer clausal topic) + 수 (grammatical subj of 있다) — 될 수 있다
    'n01023043': [('deprel', 5, 'nsubj:outer')],

    # 주제는 (outer topic) + 대부분이 (inner subject) under 것
    'n01027030': [('deprel', 5, 'nsubj:outer')],

    # 모두가 (outer agent) + 수 (grammatical subj of 있는) — 수 있다
    'n01027049': [('deprel', 1, 'nsubj:outer')],

    # 분석이 (outer subject) + 수 (grammatical subj of 있다고) — 될 수 있다고
    'n01033005': [('deprel', 4, 'nsubj:outer')],

    # 사업과 (outer agent, was nsubj:pass) + 수 (grammatical subj) — 관철될 수 있도록
    'n01034033': [('deprel', 10, 'nsubj:outer')],

    # 용의자가 (outer subject) + 관련이 (inner subj of 있는) — 관련이 있다
    'n01035025': [('deprel', 2, 'nsubj:outer')],

    # RECO가 (outer agent) + 수 (grammatical subj of 있는) — 수 있는
    'n01036033': [('deprel', 3, 'nsubj:outer')],

    # 그는 (outer agent) + 수 (grammatical subj of 있었다) — 탈퇴할 수 있었다
    'n01038025': [('deprel', 1, 'nsubj:outer')],

    # 고객이 (outer agent) + 수 (grammatical subj of 있다고) — 모니터링할 수 있다고
    'n01046057': [('deprel', 10, 'nsubj:outer')],

    # 아기가 (outer agent) + 수 (grammatical subj of 있다는) — 살 수 있다는
    'n01051004': [('deprel', 22, 'nsubj:outer')],

    # 소녀들이 (outer agent) + 수 (grammatical subj of 있도록) — 받아들일 수 있도록
    'n01053036': [('deprel', 13, 'nsubj:outer')],

    # 그는 (outer agent) + 수 (grammatical subj of 있었다) — 감지할 수 있었다
    'n01058064': [('deprel', 1, 'nsubj:outer')],

    # 나는 (outer experiencer) + 느낌이 (inner subj of 듭니다) — 느낌이 들다
    'n01061023': [('deprel', 12, 'nsubj:outer')],

    # 저는 (outer experiencer) + 화도 (inner subj of 나는군요) — 화가 나다
    'n01069023': [('deprel', 10, 'nsubj:outer')],

    # 누가 (outer agent) + 수 (grammatical subj of 있는가) — 멈출 수 있는가
    'n01073004': [('deprel', 1, 'nsubj:outer')],

    # 우리는 (outer agent) + 수 (grammatical subj of 있어야) — 필적할 수 있어야
    'n01074015': [('deprel', 8, 'nsubj:outer')],

    # 그는 (outer topic) + 솜씨가 (inner subject) under 유연하다
    'n01074020': [('deprel', 1, 'nsubj:outer')],

    # 나는 (outer agent) + 수 (grammatical subj of 있다) — 할 수 있다
    'n01080039': [('deprel', 1, 'nsubj:outer')],

    # 우리는 (outer agent) + 수 (grammatical subj of 없다) — 내버려둘 수 없다
    'n01081022': [('deprel', 1, 'nsubj:outer')],

    # 것은 (outer topic, nominalized clause) + 일리가 (inner subj of 있다) — 일리가 있다
    'n01083035': [('deprel', 5, 'nsubj:outer')],

    # 비구름이라도 (outer conditional topic) + 뒤쪽은 (inner subj) under 빛날
    'n01085011': [('deprel', 4, 'nsubj:outer')],

    # 아고라 (outer agent) + 수 (grammatical subj of 있었지만) — 입장할 수 있었지만
    'n01094022': [('deprel', 4, 'nsubj:outer')],

    # 트렌드는 (outer topic) + 관련이 (inner subj of 있다) — 관련이 있다
    'n01125030': [('deprel', 4, 'nsubj:outer')],

    # 그는 (outer topic) + 공적이 (inner subj of 있다) — 공적이 있다
    'n01134015': [('deprel', 1, 'nsubj:outer')],

    # 그는 (outer topic) + 여유가 (inner subj of 있었다) — 여유가 있다
    'n01138007': [('deprel', 14, 'nsubj:outer')],

    # 사이트는 (outer topic) + 타이밍이 (inner subject) under 정확하다
    'n01147085': [('deprel', 10, 'nsubj:outer')],

    # 사람은 (outer topic) + 것이 (inner nominalized subj) under 좋다 — 방문하는 것이 좋다
    'n01147087': [('deprel', 8, 'nsubj:outer')],

    # 건축은 (outer topic) + 수 (grammatical subj of 있다) — 지을 수 있다
    'n01150007': [('deprel', 2, 'nsubj:outer')],

    # 건물은 (outer topic of whole sentence) + 디테일이 (inner subj of 담고) — coordination
    'n01150042': [('deprel', 7, 'nsubj:outer')],

    # 메가바주스는 (outer topic) + 책임이 (inner subj of 있었다) — 책임이 있다
    'w01005020': [('deprel', 4, 'nsubj:outer')],

    # 반투 (outer topic) + 교류가 (inner subj of 없었기) — 교류가 없다
    'w01017046': [('deprel', 9, 'nsubj:outer')],

    # 강은 (outer topic of whole sentence) + 등 (head of river list) under 들어간다
    'w01030096': [('deprel', 3, 'nsubj:outer')],

    # 이곳들은 (outer topic) + 도로가 (inner subj of 없기) — 도로가 없다
    'w01038009': [('deprel', 1, 'nsubj:outer')],

    # 지역은 (outer topic) + 크기가 (inner subj of 비슷했다) — double subject
    'w01050071': [('deprel', 4, 'nsubj:outer')],

    # 약품 (outer topic) + 연구가 (inner subj of 이루어졌다) — coordination
    'w01061050': [('deprel', 12, 'nsubj:outer')],

    # 명령은 (outer topic) + 구석이 (inner subj of 있었기) — 모호한 구석이 있다
    'w01062063': [('deprel', 13, 'nsubj:outer')],

    # 돌은 (outer topic) + 크기가 (inner subj of 미터로) — double subject
    'w01065018': [('deprel', 31, 'nsubj:outer')],

    # 이는 (outer topic) + 수 (grammatical subj of 있다) — 알 수 있다
    'w01067059': [('deprel', 6, 'nsubj:outer')],

    # 증거는 (outer topic) + 가능성이 (inner subj of 있으며) — 가능성이 있다
    'w01072002': [('deprel', 11, 'nsubj:outer')],

    # Four errors in the same sentence:
    # [진학률이 + 10%상승], [가능성이 + 3%감소], [진학률이 + 1%증가], [가능성은 + 1%낮아지게]
    # % is a measure/amount, not a subject
    'w01075037': [
        ('deprel', 9,  'obl'),
        ('deprel', 15, 'obl'),
        ('deprel', 20, 'obl'),
        ('deprel', 28, 'obl'),
    ],

    # 바나나와 (outer topic, originally cultivated in SE Asia) + 재경작이 (inner subj) under 이뤄졌다
    'w01091016': [('deprel', 9, 'nsubj:outer')],

    # 동물은 (outer agent) + 수 (grammatical subj of 있었다) — 제공할 수 있었다
    'w01091045': [('deprel', 2, 'nsubj:outer')],

    # 인류는 (outer topic) + 모두가 (inner subj) under 가수 — 모두가 X이다
    'w01099045': [('deprel', 1, 'nsubj:outer')],

    # 유도요노가 (outer agent) + 책임이 (inner subj of 있다고) — 책임이 있다
    'w01113074': [('deprel', 7, 'nsubj:outer')],

    # 초판은 (passive subj, real subject) + 부만 (measure "only N copies", was nsubj:pass)
    'w01116036': [('deprel', 4, 'obl')],

    # 윌크스는 (real subject) + 번 ("two times", time counter) under 쫓겨났으며
    'w01125034': [('deprel', 4, 'obl')],

    # 조셉 (outer topic) + 관심이 (inner subj of 있었다) — 관심이 있다
    'w01136074': [('deprel', 1, 'nsubj:outer')],

    # 생활이 (outer topic) + 파탄이 (inner subj of 난) — 파탄이 나다 (compound predicate)
    'w01143015': [('deprel', 12, 'nsubj:outer')],

    # 제국이 (outer agent, subject of 잃고) + 관계가 (passive subj of 단절된) under 단절된
    'w01150047': [('deprel', 2, 'nsubj:outer')],

    # 경찰은 (outer agent) + 수 (grammatical subj of 있었다) — 진압할 수 있었다
    'n02002007': [('deprel', 1, 'nsubj:outer')],

    # 아티스트나 (outer conjoined subject) + 계약이 (inner subj of 되어) — 계약이 되다
    'n02081019': [('deprel', 22, 'nsubj:outer')],

    # 물질은 (outer agent) + 수 (grammatical subj of 있다) — 가져올 수 있다
    'n02082017': [('deprel', 3, 'nsubj:outer')],

    # 상황은 (outer topic) + 해결이 (inner subj of 가능하다) — 해결이 가능하다
    'n03006008': [('deprel', 5, 'nsubj:outer')],

    # 위원회 (outer topic) + 수사가 (inner subj of 가능하다) — 수사가 가능하다
    'n03009011': [('deprel', 12, 'nsubj:outer')],

    # 집안은 (outer topic) + 박해가 (inner subj of 있었다) — 박해가 있었다
    'n04001002': [('deprel', 21, 'nsubj:outer')],

    # 수치는 (outer topic) + 관련이 (inner subj of 있으며) — 관련이 있다
    'n04006014': [('deprel', 3, 'nsubj:outer')],

    # 아마존은 (outer topic) + 규모가 (inner subj of 크다) — double subject
    'n04010017': [('deprel', 1, 'nsubj:outer')],

    # 인구가 (real subject) + 명이 (unit "N people", measure) under 증가하였다
    'n05002004': [('deprel', 20, 'obl')],

    # 사람은 (outer topic) + 남작이 (inner subj of 유일했다) — double subject
    'n05003022': [('deprel', 5, 'nsubj:outer')],

    # 이것은 (outer topic) + 관계가 (inner subj of 있다) — 관계가 있다
    'w02002120': [('deprel', 1, 'nsubj:outer')],

    # 그가 (outer agent) + 수 (grammatical subj of 있는) — 사용할 수 있는
    'w02014013': [('deprel', 1, 'nsubj:outer')],

    # 역사는 (outer topic) + 관련이 (inner subj of 있다) — 관련이 있다
    'w03001058': [('deprel', 2, 'nsubj:outer')],

    # 기독교도들이 (outer agent) + 수 (grammatical subj of 없었다) — 읽을 수 없었다
    'w03006024': [('deprel', 4, 'nsubj:outer')],

    # 지역은 (outer topic, was nsubj:pass) + 사이가 (inner passive subj) under 않는다
    'w04004005': [('deprel', 2, 'nsubj:outer')],

    # 이는 (outer topic reference) + 황제도 (inner subj) under 마찬가지
    'w04007049': [('deprel', 32, 'nsubj:outer')],
}


def apply_fixes(doc, fixes):
    fixed = 0
    for bundle in doc.bundles:
        for tree in bundle.trees:
            sid = tree.sent_id
            if sid not in fixes:
                continue
            nodes = {n.ord: n for n in tree.descendants}
            for op in fixes[sid]:
                if op[0] == 'deprel':
                    _, nid, new_deprel = op
                    nodes[nid].deprel = new_deprel
                elif op[0] == 'reparent':
                    _, nid, new_head_id, new_deprel = op
                    nodes[nid].parent = nodes[new_head_id]
                    nodes[nid].deprel = new_deprel
            fixed += 1
    return fixed


if __name__ == '__main__':
    path = os.path.expanduser('ko_pud-ud-test.conllu')
    doc = udapi.Document(path)
    n = apply_fixes(doc, FIXES)
    doc.store_conllu(path)
    print(f"Fixed {n} sentences in {path}")
