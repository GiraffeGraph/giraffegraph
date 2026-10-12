import random

import identity_ledger as il

# Two people share the name "S". Person 1 is heard by A, person 2 by B.
DOCUMENTS = [
    [("A", 10), ("S", 1), ("T", 30)],
    [("B", 20), ("S", 2), ("T", 30)],
    [("A", 10), ("S", 1), ("T", 30)],
    [("B", 20), ("S", 2), ("T", 30)],
]


def run(policy, documents=DOCUMENTS, people=None, **kwargs):
    _, tally = il.replay(documents, people or {}, policy, random.Random(0), tally=il.Tally(),
                         **kwargs)
    return tally


def test_name_key_asks_once_per_name_and_reuses_the_first_answer():
    tally = run(il.Policy(fixed_level=0))

    assert tally.mentions == 12
    assert tally.questions == 4  # A, S, T, B
    assert tally.silent_wrong == 2  # "S" after B is answered with person 1, twice


def test_student_context_key_separates_the_two_people():
    tally = run(il.Policy(fixed_level=1))

    assert tally.silent_wrong == 0
    assert tally.questions == 5  # (None,A), (A,S), (S,T), (None,B), (B,S)


def test_guard_question_narrows_the_scope_of_that_name_only():
    # Student B (generation 9) cannot have heard person 1 (generation 2); person 2 fits.
    people = {10: (3, None), 20: (9, None), 1: (2, None), 2: (4, None), 30: (1, None)}
    fact_only = run(il.Policy(fixed_level=0, guard=True), people=people)
    narrowing = run(il.Policy(guard=True), people=people)

    assert fact_only.guard_questions_on_errors == 2
    assert fact_only.silent_wrong == 0
    assert narrowing.guard_questions_on_errors == 1
    assert narrowing.silent_wrong == 0
    # Without narrowing the guard keeps asking about both ends of the same implausible pair.
    assert (narrowing.questions, fact_only.questions) == (5, 7)


def test_guard_bounds():
    people = {1: (7, 160), 2: (3, 94), 3: (11, 250), 4: (None, None)}

    assert not il.implausible(1, 2, people)
    assert il.implausible(2, 1, people)  # the teacher is four generations younger
    assert il.implausible(3, 2, people)  # eight generations and 156 years apart
    assert not il.implausible(1, 4, people)  # nothing known about the teacher


def test_parsing_of_generation_and_death_year():
    assert il.parse_generation("من رؤس الطبقة الثامنة") == 8
    assert il.parse_generation("الحادية عشرة") == 11
    assert il.parse_generation("الثانية عشرة") == 12
    assert il.parse_generation("صحابي") == 1
    assert il.parse_generation("-") is None
    assert il.parse_death_year("197 هـ  أو 198 هـ") == 197
    assert il.parse_death_year("151 هـ : 160 هـ") == 151
    assert il.parse_death_year("None") is None


def test_warming_does_not_count_and_carries_decisions_over():
    ledger, _ = il.replay(DOCUMENTS[:2], {}, il.Policy(fixed_level=1), random.Random(0))
    _, tally = il.replay(DOCUMENTS[2:], {}, il.Policy(fixed_level=1), random.Random(0),
                         ledger=ledger, tally=il.Tally())

    assert tally.mentions == 6
    assert tally.questions == 0
    assert tally.silent_wrong == 0


def test_reviewer_errors_are_counted_and_only_happen_on_ambiguous_names():
    confusable = il.confusable_people(DOCUMENTS)
    tally = run(il.Policy(fixed_level=2), reviewer_error=1.0, confusable=confusable)

    assert confusable == {"S": [1, 2]}
    assert tally.reviewer_wrong == 2  # the two questions about "S"; other names have one person
