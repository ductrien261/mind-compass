"""
Script test toàn bộ pipeline MindCompass Expert System.
Chạy từ thư mục backend: python test_pipeline.py
"""
import sys
sys.path.insert(0, ".")

from core.engine.prolog_engine import (
    run_screening_phase,
    run_fuzzy_phase,
    run_backward_phase,
    PROLOG_AVAILABLE,
)

print("PROLOG_AVAILABLE:", PROLOG_AVAILABLE)
print("=" * 70)


def run_test(label, screen_answers, extra_answers, bw_override=None):
    print("\n" + "#" * 70)
    print(f"# TEST: {label}")
    print("#" * 70)

    # Phase 1: Screening
    p1 = run_screening_phase(screen_answers)

    # Phase 2: Fuzzy + Forward Chaining
    all_ans = dict(screen_answers)
    for q in range(1, 43):
        if q not in all_ans:
            all_ans[q] = extra_answers.get(q, 0)
    p2 = run_fuzzy_phase(all_ans, p1)

    # Phase 3: Backward Chaining
    bw = {q["key"]: "yes" for q in p2["backward_questions"]}
    if bw_override:
        bw.update(bw_override)
    p3 = run_backward_phase(p2["profile"], bw, p2)

    result = "PASS ✓" if p3["profile_verified"] else "WARN (unverified)"
    print(f"\n>> RESULT: {result} | Profile: {p3['profile'].upper()}")
    return p3


# Test 1: MDD + Anxious Distress (D cao + A cao)
run_test(
    "MDD Anxious Distress (D=3, A=3 cao dong thoi)",
    {21: 3, 10: 3, 28: 3, 7: 3, 11: 0, 8: 0},
    {q: 3 for q in [3, 5, 10, 13, 16, 17, 21, 24, 26, 31, 34, 37, 38, 42,
                    2, 4, 7, 9, 15, 19, 20, 23, 25, 28, 30, 36, 40, 41]},
)

# Test 2: GAD Stress Dominant (S cao, D/A thap) 
run_test(
    "GAD Stress Dominant (S cao, n2='no' de xac nhan)",
    {21: 0, 10: 0, 28: 0, 7: 0, 11: 3, 8: 3},
    {q: 3 for q in [1, 6, 8, 11, 12, 14, 18, 22, 27, 29, 32, 33, 35, 39]},
    bw_override={"n2": "no"},
)

#  Test 3: GAD bị từ chối vì lo âu xuất phát từ sự kiện cụ thể
run_test(
    "GAD bi tu choi (n2='yes' - lo au co nguyen nhan cu the)",
    {21: 0, 10: 0, 28: 0, 7: 0, 11: 3, 8: 3},
    {q: 3 for q in [1, 6, 8, 11, 12, 14, 18, 22, 27, 29, 32, 33, 35, 39]},
    bw_override={"n2": "yes"},  # GAD fail vì có nguồn gốc cụ thể
)

print("\n" + "=" * 70)
print("ALL TESTS DONE")
print("=" * 70)
