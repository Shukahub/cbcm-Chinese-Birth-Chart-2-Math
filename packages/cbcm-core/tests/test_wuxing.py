"""五行代数属性测试（验证 docs/04-wuxing.md）。核心：相克 = 相生²。"""

from cbcm import wuxing


def test_xiangke_is_xiangsheng_squared():
    # 相克 σ²(x) = 相生(相生(x))
    for x in range(5):
        assert wuxing.ke(x) == wuxing.sheng(wuxing.sheng(x))


def test_sheng_is_5_cycle():
    # 相生是 5-循环，遍历全部 5 行
    visited = [False] * 5
    x = 0
    for _ in range(5):
        visited[x] = True
        x = wuxing.sheng(x)
    assert all(visited)
    assert x == 0  # 回到起点


def test_relations_cover_all_5_classes():
    # 任一对行的关系 ∈ {0,1,2,3,4}，且 5 类都出现
    classes = set()
    for x in range(5):
        for y in range(5):
            r = wuxing.rel(x, y)
            assert 0 <= r < 5
            classes.add(r)
    assert classes == {0, 1, 2, 3, 4}


def test_relation_matrix_is_circulant():
    # 循环差分表：每行是上一行的循环右移
    M = wuxing.relation_matrix()
    for x in range(5):
        for y in range(5):
            assert M[x][y] == (y - x) % 5
    # M[x][y] 与 M[y][x] 互补（生↔被生、克↔被克）
    for x in range(5):
        for y in range(5):
            if x != y:
                assert (M[x][y] + M[y][x]) % 5 == 0


def test_stem_wuxing_mapping():
    # 甲乙木、丙丁火、戊己土、庚辛金、壬癸水
    expected = {0: 0, 1: 0, 2: 1, 3: 1, 4: 2, 5: 2, 6: 3, 7: 3, 8: 4, 9: 4}
    for stem, wx in expected.items():
        assert wuxing.stem_wuxing(stem) == wx


def test_relational_semantics():
    # 木(0)生火(1)，木克土(2)，金(3)克木(0)→ 木被金克
    assert wuxing.rel(0, 1) == wuxing.REL_SHENG   # 我生
    assert wuxing.rel(0, 2) == wuxing.REL_KE      # 我克
    assert wuxing.rel(0, 3) == wuxing.REL_KEI     # 克我
    assert wuxing.rel(0, 4) == wuxing.REL_SHENGI  # 生我
    assert wuxing.rel(0, 0) == wuxing.REL_BIHE    # 比和
