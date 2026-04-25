"""
Test tự động toàn bộ pipeline DASS-42 Expert System.
Chạy: python test_cases.py
"""

import sys
import json
from typing import Dict, Any

# Import engine — chạy từ thư mục backend/
sys.path.insert(0, ".")
from backend.core.engine.prolog_engine import (
    run_screening_phase,
    run_fuzzy_phase,
    run_backward_phase,
)

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def ok(msg):  print(f"  {GREEN}✓ {msg}{RESET}")
def fail(msg):print(f"  {RED}✗ {msg}{RESET}")
def info(msg):print(f"  {CYAN}→ {msg}{RESET}")


# ──────────────────────────────────────────────
# TEST CASES
# Cấu trúc mỗi test:
#   name          : tên test
#   answers       : {question_id: score 0-3} — 42 câu DASS
#   backward      : {key: "yes"/"no" hoặc [list options]}
#   expect_profile: profile mong đợi sau forward chaining
#   expect_verified: True/False sau backward chaining
#   note          : giải thích
# ──────────────────────────────────────────────

def base_answers(overrides: Dict[int, int] = {}) -> Dict[int, int]:
    ans = {i: 0 for i in range(1, 43)}
    ans.update(overrides)
    return ans

# Depression questions
DEP_QS = [3, 5, 10, 13, 16, 17, 21, 24, 26, 31, 34, 37, 38, 42]
# Anxiety questions
ANX_QS = [2, 4, 7, 9, 15, 19, 20, 23, 25, 28, 30, 36, 40, 41]
# Stress questions
STR_QS = [1, 6, 8, 11, 12, 14, 18, 22, 27, 29, 32, 33, 35, 39]

TEST_CASES = [

    # TC-01: Low Risk
    {
        "name": "TC-01 — Low Risk (tất cả điểm thấp)",
        "answers": base_answers(),   # toàn 0
        "backward": {},
        "expect_profile": "low_risk",
        "expect_verified": True,
        "note": "Người dùng trả lời 0 hết → không có dấu hiệu gì",
    },

    # TC-02: Low Risk ngưỡng biên 
    {
        "name": "TC-02 — Low Risk (điểm vừa đủ thấp)",
        "answers": base_answers({q: 1 for q in DEP_QS[:3]}),
        "backward": {},
        "expect_profile": "low_risk",
        "expect_verified": True,
        "note": "Vài câu depression = 1, tổng thấp → vẫn low_risk",
    },

    # TC-03: Major Depression — xác nhận
    {
        "name": "TC-03 — Major Depression (đủ tiêu chí DSM)",
        "answers": base_answers({q: 3 for q in DEP_QS}),  # tất cả depression = 3
        "backward": {
            "a1": "yes",
            "a2": "yes",
            "a3": ["a3_b", "a3_d", "a3_e", "a3_f"],  # 4 triệu chứng + a1 đóng góp = 5 ≥ 5
            "a4": "yes",
        },
        "expect_profile": "major_depression",
        "expect_verified": True,
        "note": "Depression cực nặng, backward xác nhận đủ A1+A3(≥4 chọn)+A4",
    },

    # TC-04: Major Depression — không đủ backward 
    {
        "name": "TC-04 — Major Depression (backward không đủ tiêu chí)",
        "answers": base_answers({q: 3 for q in DEP_QS}),
        "backward": {
            "a1": "no",
            "a2": "no",   # cả A1 và A2 đều no → không đủ
            "a3": [],
            "a4": "no",
        },
        "expect_profile": "major_depression",
        "expect_verified": False,  # safety net sẽ giữ profile vì fuzzy cao
        "note": "DASS cao nhưng không nhận A1/A2 → verified=False, safety net giữ profile",
    },

    # TC-05: Major Depression — chỉ A2 yes
    {
        "name": "TC-05 — Major Depression (chỉ A2=yes, không có A1)",
        "answers": base_answers({q: 3 for q in DEP_QS}),
        "backward": {
            "a1": "no",
            "a2": "yes",
            "a3": ["a3_a", "a3_b", "a3_c", "a3_d"],  # 4 + a2 đóng góp 1 = 5 ✓
            "a4": "yes",
        },
        "expect_profile": "major_depression",
        "expect_verified": True,
        "note": "A2=yes đóng góp +1 vào đếm A3, tổng = 5 ≥ 5 → xác nhận",
    },

    # TC-06: Panic Disorder — xác nhận
    {
        "name": "TC-06 — Panic Disorder (đủ tiêu chí)",
        "answers": base_answers({q: 3 for q in ANX_QS}),  # anxiety cao, dep/stress thấp
        "backward": {
            "d1a": "yes",
            "d1b": "yes",
            "d2":  "yes",
            "d4":  ["d4_a", "d4_b", "d4_d", "d4_h"],  # 4 triệu chứng ✓
        },
        "expect_profile": "panic_disorder",
        "expect_verified": True,
        "note": "Anxiety cao, depression/stress thấp, D1a+D1b+D2+D4(≥4) đủ",
    },

    # TC-07: Panic Disorder — D4 không đủ
    {
        "name": "TC-07 — Panic Disorder (D4 chỉ có 3 triệu chứng)",
        "answers": base_answers({q: 3 for q in ANX_QS}),
        "backward": {
            "d1a": "yes",
            "d1b": "yes",
            "d2":  "yes",
            "d4":  ["d4_a", "d4_b", "d4_d"],  # chỉ 3, cần ≥ 4 → fail
        },
        "expect_profile": "panic_disorder",
        "expect_verified": False,
        "note": "D4 chỉ chọn 3/13 triệu chứng, không đủ ngưỡng 4",
    },

    # TC-08: GAD — xác nhận
    {
        "name": "TC-08 — GAD (đủ tiêu chí)",
        "answers": base_answers({q: 3 for q in STR_QS}),  # stress cao
        "backward": {
            "n1": "yes",
            "n2": "no",   # không kiểm soát được → tiếp tục
            "n3": ["n3_a", "n3_b", "n3_f"],  # 3 triệu chứng ✓
            "n4": "yes",
        },
        "expect_profile": "gad_stress_dominant",
        "expect_verified": True,
        "note": "Stress cao, N1+N2=no+N3(≥3)+N4 đủ tiêu chí GAD",
    },

    # TC-09: GAD — N2=yes (kiểm soát được)
    {
        "name": "TC-09 — GAD (N2=yes → dừng sớm)",
        "answers": base_answers({q: 3 for q in STR_QS}),
        "backward": {
            "n1": "yes",
            "n2": "yes",  # kiểm soát được → STOP, không đủ GAD
        },
        "expect_profile": "gad_stress_dominant",
        "expect_verified": False,
        "note": "N2=yes nghĩa là kiểm soát được lo lắng → không đủ tiêu chí GAD",
    },

    # TC-10: GAD — N3 không đủ
    {
        "name": "TC-10 — GAD (N3 chỉ 2 triệu chứng)",
        "answers": base_answers({q: 3 for q in STR_QS}),
        "backward": {
            "n1": "yes",
            "n2": "no",
            "n3": ["n3_a", "n3_c"],  # chỉ 2, cần ≥ 3
            "n4": "yes",
        },
        "expect_profile": "gad_stress_dominant",
        "expect_verified": False,
        "note": "N3 chỉ chọn 2/6 triệu chứng, không đủ ngưỡng 3",
    },

    # TC-11: Social Anxiety — xác nhận
    {
        "name": "TC-11 — Social Anxiety (đủ F1-F6)",
        "answers": base_answers({
            **{q: 2 for q in ANX_QS},
            **{q: 2 for q in STR_QS},
        }),
        "backward": {
            "f1": "yes", "f2": "yes", "f3": "yes",
            "f4": "yes", "f5": "yes", "f6": "yes",
        },
        "expect_profile": "social_anxiety",
        "expect_verified": True,
        "note": "Anxiety+Stress vừa, tất cả F1-F6 đều yes",
    },

    # TC-12: Social Anxiety — thiếu F4
    {
        "name": "TC-12 — Social Anxiety (F4=no)",
        "answers": base_answers({
            **{q: 2 for q in ANX_QS},
            **{q: 2 for q in STR_QS},
        }),
        "backward": {
            "f1": "yes", "f2": "yes", "f3": "yes",
            "f4": "no",  # nỗi sợ không quá mức → fail
            "f5": "yes", "f6": "yes",
        },
        "expect_profile": "social_anxiety",
        "expect_verified": False,
        "note": "F4=no → không đủ tiêu chí social anxiety",
    },

    # TC-13: Maladaptive Crisis
    {
        "name": "TC-13 — Maladaptive Crisis (tất cả cực nặng)",
        "answers": base_answers({
            **{q: 3 for q in DEP_QS},
            **{q: 3 for q in ANX_QS},
            **{q: 3 for q in STR_QS},
        }),
        "backward": {},  # tự động xác nhận
        "expect_profile": "maladaptive_crisis",
        "expect_verified": True,
        "note": "D+A+S đều cực nặng → maladaptive_crisis, không cần backward",
    },

    # TC-14: Edge case — Depression cao nhưng A3 vừa đủ
    {
        "name": "TC-14 — MDD biên (A3 đúng ngưỡng 4+1=5)",
        "answers": base_answers({q: 3 for q in DEP_QS}),
        "backward": {
            "a1": "yes",   # +1 đóng góp
            "a2": "no",
            "a3": ["a3_b", "a3_d", "a3_e", "a3_f"],  # 4 chọn + a1 = 5 ✓
            "a4": "yes",
        },
        "expect_profile": "major_depression",
        "expect_verified": True,
        "note": "Biên: A1 đóng góp +1, chọn đúng 4 → tổng 5 = ngưỡng DSM",
    },

    # TC-15: Edge case — Depression cao nhưng A3 thiếu 1
    {
        "name": "TC-15 — MDD biên (A3 chỉ 4+0=4, thiếu 1)",
        "answers": base_answers({q: 3 for q in DEP_QS}),
        "backward": {
            "a1": "no",
            "a2": "no",    # không đóng góp
            "a3": ["a3_b", "a3_d", "a3_e", "a3_f"],  # 4 chọn, không có +1 = 4 < 5
            "a4": "yes",
        },
        "expect_profile": "major_depression",
        "expect_verified": False,
        "note": "A1=no A2=no nên không có +1, tổng A3=4 < 5 → fail (safety net giữ)",
    },
]


def run_test(tc: Dict[str, Any]) -> bool:
    print(f"\n{BOLD}{CYAN}{'─'*60}{RESET}")
    print(f"{BOLD}{tc['name']}{RESET}")
    print(f"  Note: {tc['note']}")

    answers   = tc["answers"]
    backward  = tc["backward"]
    exp_prof  = tc["expect_profile"]
    exp_ver   = tc["expect_verified"]

    passed = True

    try:
        # Bước 1: Screening
        screening = run_screening_phase(answers)

        # Bước 2: Fuzzy + Forward chaining
        fuzzy = run_fuzzy_phase(answers, screening)
        got_profile = fuzzy["profile"]

        if got_profile == exp_prof:
            ok(f"Forward profile: {got_profile}")
        else:
            fail(f"Forward profile: got={got_profile}, expected={exp_prof}")
            passed = False

        # Bước 3: Backward chaining
        final = run_backward_phase(got_profile, backward, fuzzy)
        got_verified = final["profile_verified"]

        if got_verified == exp_ver:
            ok(f"Backward verified: {got_verified}")
        else:
            fail(f"Backward verified: got={got_verified}, expected={exp_ver}")
            passed = False

        info(f"Final profile: {final['profile']} | Score: {final.get('confirm_score','N/A')}")

    except Exception as e:
        fail(f"Exception: {e}")
        passed = False

    return passed


def main():
    print(f"\n{BOLD}{'='*60}")
    print(f"  MINDCOMPASS — TEST SUITE ({len(TEST_CASES)} test cases)")
    print(f"{'='*60}{RESET}")

    results = []
    for tc in TEST_CASES:
        results.append(run_test(tc))

    passed = sum(results)
    total  = len(results)
    failed = total - passed

    print(f"\n{BOLD}{'='*60}")
    print(f"  KẾT QUẢ: {GREEN}{passed} PASSED{RESET}{BOLD}  |  {RED}{failed} FAILED{RESET}{BOLD}  |  {total} TOTAL")
    print(f"{'='*60}{RESET}\n")

    if failed > 0:
        print(f"{RED}Các test thất bại:{RESET}")
        for i, (r, tc) in enumerate(zip(results, TEST_CASES)):
            if not r:
                print(f"  {RED}✗ {tc['name']}{RESET}")
        sys.exit(1)
    else:
        print(f"{GREEN}Tất cả test đều pass!{RESET}\n")
        sys.exit(0)


if __name__ == "__main__":
    main()