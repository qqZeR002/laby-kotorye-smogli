import pytest

from main import register, vote, leader, distribution_percent, is_tie


@pytest.fixture
def candidates():
    # три кандидата, голосов пока нет
    c = {}
    register(c, "Анна")
    register(c, "Борис")
    register(c, "Вера")
    return c


# ---------- register ----------

def test_register_adds_candidate_with_zero_votes():
    c = {}
    register(c, "Анна")
    assert c == {"Анна": 0}


def test_register_several_candidates(candidates):
    assert len(candidates) == 3
    assert all(v == 0 for v in candidates.values())


def test_register_twice_raises_error(candidates):
    with pytest.raises(ValueError, match="already registered"):
        register(candidates, "Анна")


def test_register_twice_does_not_reset_votes(candidates):
    vote(candidates, "Анна")
    with pytest.raises(ValueError):
        register(candidates, "Анна")
    assert candidates["Анна"] == 1


# ---------- vote ----------

def test_vote_increases_counter(candidates):
    vote(candidates, "Борис")
    vote(candidates, "Борис")
    assert candidates["Борис"] == 2
    assert candidates["Анна"] == 0


def test_vote_for_unknown_candidate_raises_error(candidates):
    with pytest.raises(KeyError):
        vote(candidates, "Глеб")


def test_vote_for_unknown_does_not_add_him(candidates):
    with pytest.raises(KeyError):
        vote(candidates, "Глеб")
    assert "Глеб" not in candidates


def test_vote_in_empty_dict_raises_error():
    with pytest.raises(KeyError):
        vote({}, "Анна")


# ---------- leader ----------

def test_leader_empty_dict_returns_none():
    assert leader({}) is None


def test_leader_single_candidate():
    assert leader({"Анна": 0}) == "Анна"


def test_leader_with_clear_winner(candidates):
    vote(candidates, "Вера")
    vote(candidates, "Вера")
    vote(candidates, "Анна")
    assert leader(candidates) == "Вера"


def test_leader_returns_none_when_tie(candidates):
    vote(candidates, "Анна")
    vote(candidates, "Борис")
    assert leader(candidates) is None


def test_leader_returns_none_when_nobody_voted(candidates):
    # у всех по 0, значит лидера нет
    assert leader(candidates) is None


# ---------- distribution_percent ----------

def test_distribution_empty_dict():
    assert distribution_percent({}) == {}


def test_distribution_without_votes_is_zero(candidates):
    assert distribution_percent(candidates) == {"Анна": 0.0, "Борис": 0.0, "Вера": 0.0}


def test_distribution_simple_case():
    result = distribution_percent({"Анна": 3, "Борис": 1})
    assert result == {"Анна": 75.0, "Борис": 25.0}


def test_distribution_all_votes_for_one():
    result = distribution_percent({"Анна": 5, "Борис": 0})
    assert result["Анна"] == 100.0
    assert result["Борис"] == 0.0


def test_distribution_sum_is_100():
    result = distribution_percent({"Анна": 1, "Борис": 1, "Вера": 1})
    assert sum(result.values()) == pytest.approx(100.0)
    assert result["Анна"] == pytest.approx(33.333, abs=0.001)


def test_distribution_does_not_change_input(candidates):
    vote(candidates, "Анна")
    before = dict(candidates)
    distribution_percent(candidates)
    assert candidates == before


# ---------- is_tie ----------

def test_is_tie_empty_dict():
    assert is_tie({}) is False


def test_is_tie_single_candidate():
    assert is_tie({"Анна": 10}) is False


def test_is_tie_two_equal():
    assert is_tie({"Анна": 2, "Борис": 2}) is True


def test_is_tie_no_tie():
    assert is_tie({"Анна": 3, "Борис": 2}) is False


def test_is_tie_when_all_zero(candidates):
    assert is_tie(candidates) is True


def test_is_tie_only_among_leaders():
    # ничья внизу таблицы не считается
    assert is_tie({"Анна": 5, "Борис": 1, "Вера": 1}) is False


@pytest.mark.parametrize(
    "votes, expected_leader, expected_tie",
    [
        ({"A": 1, "B": 0}, "A", False),
        ({"A": 1, "B": 1}, None, True),
        ({"A": 0, "B": 0, "C": 4}, "C", False),
        ({"A": 4, "B": 4, "C": 4}, None, True),
    ],
)
def test_leader_and_tie_agree(votes, expected_leader, expected_tie):
    assert leader(votes) == expected_leader
    assert is_tie(votes) is expected_tie
