"""
Engine xử lý toàn bộ luồng Expert System:
  1. Prolog Screening  (2 câu / chiều  → skip hoặc ask_more)
  2. Tính điểm tổng   (14 câu hoặc nội suy từ 2 câu)
  3. Fuzzy Logic       (Gaussian MF → Centroid defuzzification)
  4. Lời khuyên đơn chiều
  5. Forward Chaining  – SWI-Prolog/pyswip (candidate_profile/4)
  6. Backward Chaining – SWI-Prolog/pyswip (verify_diagnosis/1)

Nếu pyswip không khả dụng → tự động fallback sang Python thuần.
"""

import math
import logging
import threading
import shutil
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Đường dẫn Knowledge Base
_KB_SRC = Path(__file__).parent.parent / "knowledge_base" / "rules.pl"

_KB_TEMP_DIR: Optional[str] = None
_KB_TEMP_PATH: Optional[str] = None


def _prepare_kb_path() -> Optional[str]:
    global _KB_TEMP_DIR, _KB_TEMP_PATH
    if _KB_TEMP_PATH and os.path.exists(_KB_TEMP_PATH):
        return _KB_TEMP_PATH
    try:
        _KB_TEMP_DIR = tempfile.mkdtemp(prefix="mindcompass_")
        _KB_TEMP_PATH = os.path.join(_KB_TEMP_DIR, "rules.pl")
        shutil.copy2(str(_KB_SRC), _KB_TEMP_PATH)
        logger.info(f"[PROLOG] Knowledge base copied to: {_KB_TEMP_PATH}")
        return _KB_TEMP_PATH
    except Exception as e:
        logger.warning(f"[PROLOG] Could not copy KB to temp: {e}")
        return str(_KB_SRC)


# pyswip Integration
PROLOG_AVAILABLE = False
_prolog_instance = None
_prolog_lock = threading.Lock()


def _init_prolog():
    """Khởi tạo SWI-Prolog và load knowledge base."""
    global _prolog_instance, PROLOG_AVAILABLE
    try:
        from pyswip import Prolog  # noqa: F401
        kb_path = _prepare_kb_path()
        if kb_path is None:
            raise FileNotFoundError("Could not prepare KB path")

        p = Prolog()
        safe_path = kb_path.replace("\\", "/")
        list(p.query(f"consult('{safe_path}')"))
        _prolog_instance = p
        PROLOG_AVAILABLE = True
        logger.info("[PROLOG] SWI-Prolog initialized via pyswip")
    except ImportError:
        logger.warning("[PROLOG] ⚠ pyswip not installed. Install: pip install pyswip")
        logger.warning("[PROLOG] Falling back to Python implementation.")
    except Exception as e:
        logger.warning(f"[PROLOG] ⚠ Could not initialize Prolog: {e}")
        logger.warning("[PROLOG] Falling back to Python implementation.")


_init_prolog()


def _retract_known():
    """Xóa tất cả known/2 facts khỏi Prolog DB."""
    if _prolog_instance is not None:
        try:
            list(_prolog_instance.query("retractall(known(_, _))"))
        except Exception:
            pass


#  Hằng số DASS-42
SCREENING_CFG = {
    "depression": {"q1": 21, "q2": 10, "threshold": 1.5},
    "anxiety":    {"q1": 28, "q2":  7, "threshold": 1.5},
    "stress":     {"q1": 11, "q2":  8, "threshold": 1.5},
}

DIM_QUESTIONS = {
    "depression": [3, 5, 10, 13, 16, 17, 21, 24, 26, 31, 34, 37, 38, 42],
    "anxiety":    [2, 4,  7,  9, 15, 19, 20, 23, 25, 28, 30, 36, 40, 41],
    "stress":     [1, 6,  8, 11, 12, 14, 18, 22, 27, 29, 32, 33, 35, 39],
}

FUZZY_PARAMS = {
    "depression": [
        {"label": "Normal",           "idx": 0, "mean":  0, "sigma": 7.0},
        {"label": "Mild",             "idx": 1, "mean": 11, "sigma": 3.0},
        {"label": "Moderate",         "idx": 2, "mean": 17, "sigma": 3.0},
        {"label": "Severe",           "idx": 3, "mean": 24, "sigma": 3.0},
        {"label": "Extremely Severe", "idx": 4, "mean": 35, "sigma": 7.0},
    ],
    "anxiety": [
        {"label": "Normal",           "idx": 0, "mean":  0, "sigma": 5.0},
        {"label": "Mild",             "idx": 1, "mean":  8, "sigma": 2.5},
        {"label": "Moderate",         "idx": 2, "mean": 12, "sigma": 2.5},
        {"label": "Severe",           "idx": 3, "mean": 17, "sigma": 3.0},
        {"label": "Extremely Severe", "idx": 4, "mean": 31, "sigma": 6.0},
    ],
    "stress": [
        {"label": "Normal",           "idx": 0, "mean":  0, "sigma": 7.0},
        {"label": "Mild",             "idx": 1, "mean": 16, "sigma": 3.0},
        {"label": "Moderate",         "idx": 2, "mean": 22, "sigma": 3.0},
        {"label": "Severe",           "idx": 3, "mean": 29, "sigma": 3.0},
        {"label": "Extremely Severe", "idx": 4, "mean": 38, "sigma": 6.0},
    ],
}

DIM_ADVICE = {
    "depression": [
        "Trầm cảm: Bạn đang ổn định. Duy trì lối sống lành mạnh nhé!",
        "Trầm cảm: Có dấu hiệu nhẹ. Tập thể dục, ngủ đủ giấc và chia sẻ với người thân.",
        "Trầm cảm: Mức độ vừa. Nên gặp chuyên viên tư vấn để được hỗ trợ.",
        "Trầm cảm: Mức độ nặng. Cần tìm gặp chuyên gia tâm lý càng sớm càng tốt.",
        "Trầm cảm: Rất nặng. Cần can thiệp y tế khẩn cấp, liên hệ bác sĩ ngay.",
    ],
    "anxiety": [
        "Lo âu: Không có dấu hiệu lo âu. Rất tốt!",
        "Lo âu: Hơi lo âu. Thử tập hít thở sâu và thiền định.",
        "Lo âu: Mức độ vừa. Hạn chế caffeine, nghỉ ngơi và thư giãn.",
        "Lo âu: Nặng. Những cơn hoảng loạn có thể xảy ra, cần sự hỗ trợ chuyên gia.",
        "Lo âu: Rất nặng. Tìm kiếm hỗ trợ y tế ngay lập tức.",
    ],
    "stress": [
        "Căng thẳng: Bạn kiểm soát căng thẳng rất tốt!",
        "Căng thẳng: Có chút căng thẳng. Hãy thư giãn và nghỉ ngơi.",
        "Căng thẳng: Vừa. Cần cân bằng lại công việc và cuộc sống.",
        "Căng thẳng: Nặng. Nguy cơ kiệt sức, hãy tạm dừng và gặp chuyên gia.",
        "Căng thẳng: Rất nặng. Đang quá tải nghiêm trọng, cần can thiệp y tế.",
    ],
}

PROFILE_ADVICE = {
    "maladaptive_crisis":   "MỨC ĐỘ NGUY HIỂM: Bạn đang kiệt sức hoàn toàn về mặt tâm lý. Xin đừng cố chịu đựng một mình, hãy liên hệ ngay với bác sĩ tâm lý hoặc đường dây hỗ trợ y tế khẩn cấp để được giúp đỡ.",
    "mdd_anxious_distress": "MỨC ĐỘ NẶNG (Trầm cảm kèm Lo âu): Bạn đang mang một gánh nặng tâm lý rất lớn. Hãy bắt đầu từ những hoạt động nhỏ nhất để tìm lại niềm vui và tìm một bác sĩ chuyên khoa đồng hành.",
    "panic_disorder":       "MỨC ĐỘ NẶNG (Hoảng sợ cấp tính): Cơ thể bạn đang phản ứng thái quá với sự lo âu. Khi cơn hoảng sợ đến, hãy tập hít thở sâu, chạm vào các đồ vật xung quanh để kéo tâm trí về hiện tại. Bạn nên gặp chuyên gia để học cách kiểm soát triệt để triệu chứng này.",
    "gad_stress_dominant":  "MỨC ĐỘ VỪA - NẶNG (Lo âu & Căng thẳng kéo dài): Bạn đang bị quá tải và khó ngừng suy nghĩ. Hãy thử các bài tập kéo giãn cơ bắp, dành ra một 'khung giờ lo lắng' cố định thay vì lo âu cả ngày, và trò chuyện với tư vấn viên để giải tỏa.",
    "social_anxiety":       "MỨC ĐỘ VỪA - NẶNG (Lo âu xã hội): Những nỗi sợ phán xét đang làm đảo lộn cuộc sống của bạn. Trị liệu hành vi nhận thức (CBT) đã được chứng minh là cực kỳ hiệu quả để giúp bạn lấy lại sự tự tin.",
    "pure_depression":      "MỨC ĐỘ NẶNG (Trầm cảm): Bạn đang đánh mất năng lượng và niềm vui sống. Hãy duy trì một thời gian biểu sinh hoạt cố định, giữ kết nối với những người bạn tin tưởng và đi khám tâm lý để được hỗ trợ phương pháp trị liệu phù hợp.",
    "low_risk":             "MỨC ĐỘ AN TOÀN: Không có dấu hiệu nào đáng lo ngại. Sức khỏe tinh thần của bạn hiện tại rất ổn định. Hãy tiếp tục duy trì lối sống lành mạnh, ngủ đủ giấc và vận động thể chất đều đặn nhé.",
}

BACKWARD_QUESTIONS = {
    # pure_depression (MDD)
    "a1":  "Bạn có cảm thấy buồn, trống rỗng hoặc tuyệt vọng gần như cả ngày, mỗi ngày không?",
    "a2":  "Bạn có mất hứng thú hoặc niềm vui với hầu hết hoạt động từng yêu thích không?",
    "a3":  "Bạn có thay đổi cân nặng rõ rệt (>5%) hoặc thay đổi cảm giác thèm ăn không?",
    "a4":  "Bạn có bị mất ngủ hoặc ngủ quá nhiều gần như mỗi ngày không?",
    # gad_stress_dominant
    "n1":  "Bạn có lo lắng thái quá về nhiều vấn đề khác nhau liên tục trong hơn 6 tháng qua không?",
    "n2":  "Những lo lắng này có xuất phát từ một sự kiện cụ thể không? (như mất người thân, bệnh tật...)",
    "n3":  "Sự lo âu có đi kèm căng cơ, mệt mỏi, khó tập trung hoặc mất ngủ không?",
    "n4":  "Bạn có cảm thấy khó hoặc không thể ngừng lo lắng dù bản thân muốn không?",
    # panic_disorder
    "d1a": "Bạn có từng đột ngột bị tim đập mạnh, khó thở, vã mồ hôi hoặc run rẩy không rõ nguyên nhân không?",
    "d1b": "Những cơn đó có ập đến bất ngờ và đạt đỉnh điểm chỉ trong vài phút không?",
    "d2":  "Sau các cơn đó, bạn có lo lắng kéo dài rằng chúng sẽ tái phát không?",
    "d4":  "Bạn có né tránh những nơi hoặc tình huống cụ thể vì sợ cơn hoảng loạn tái phát không?",
    # social_anxiety
    "f1":  "Bạn có sợ hãi rõ rệt khi phải xuất hiện trước đám đông hoặc tương tác xã hội không?",
    "f2":  "Nỗi sợ này có liên quan đến việc bị người khác đánh giá tiêu cực không?",
    "f3":  "Bạn có cảm thấy lo âu gần như ngay lập tức khi gặp tình huống xã hội đó không?",
    "f4":  "Bạn có né tránh các tình huống xã hội đó, hoặc chịu đựng với cảm giác rất khó chịu không?",
    "f5":  "Nỗi sợ này có không cân xứng với mức nguy hiểm thực tế của tình huống không?",
    "f6":  "Nó có ảnh hưởng rõ đến công việc, học tập hoặc các mối quan hệ của bạn không?",
}

BACKWARD_FLOW = {
    "pure_depression":     ["a1", "a2", "a3", "a4"],
    "mdd_anxious_distress":["a1", "a2", "n1"],   
    "gad_stress_dominant": ["n1", "n2", "n3", "n4"],
    "panic_disorder":      ["d1a", "d1b", "d2", "d4"],
    "social_anxiety":      ["f1", "f2", "f3", "f4", "f5", "f6"],
    "maladaptive_crisis":  [],
    "low_risk":            [],
}

# Ngưỡng xác nhận (chỉ dùng khi Python fallback)
CONFIRM_THRESHOLD = {
    "pure_depression":     3,
    "mdd_anxious_distress":2,
    "gad_stress_dominant": 3,
    "panic_disorder":      2,
    "social_anxiety":      4,
    "maladaptive_crisis":  0,
    "low_risk":            0,
}


#  Hàm toán học 
def _gaussmf(x: float, mean: float, sigma: float) -> float:
    """Gaussian membership function."""
    return math.exp(-((x - mean) ** 2) / (2 * sigma ** 2))


#  Bước 1: Prolog Screening 
def _prolog_screening(dim: str, answers: Dict[int, int]) -> Dict[str, Any]:
    """
    Kiểm tra 2 câu sàng lọc của mỗi chiều.
    Trả về: { action: 'skip'|'ask_more', q1, q2, v1, v2, threshold, reason }
    """
    cfg = SCREENING_CFG[dim]
    q1, q2, thr = cfg["q1"], cfg["q2"], cfg["threshold"]
    v1 = answers.get(q1, 0)
    v2 = answers.get(q2, 0)

    if v1 <= thr and v2 <= thr:
        action = "skip"
        reason = f"Rủi ro thấp: Q{q1}={v1} và Q{q2}={v2} đều ≤ {thr}"
    else:
        action = "ask_more"
        reason = f"Cần đánh giá thêm: Q{q1}={v1} hoặc Q{q2}={v2} vượt ngưỡng {thr}"

    logger.info(f"[SCREENING] {dim}: {action} | {reason}")
    print(f"\n[{dim.upper()} — Prolog Screening]")
    print(f"   Q{q1}={v1}, Q{q2}={v2}  | threshold={thr} → {action.upper()}")
    print(f"   Lý do: {reason}")

    return {"action": action, "q1": q1, "q2": q2, "v1": v1, "v2": v2, "threshold": thr, "reason": reason}


#  Bước 2: Tính điểm 
def _compute_score(dim: str, answers: Dict[int, int], action: str, v1: int, v2: int) -> Dict[str, Any]:
    """Tính tổng điểm cho từng chiều."""
    all_qs = DIM_QUESTIONS[dim]

    if action == "ask_more":
        detail = {q: answers.get(q, 0) for q in all_qs}
        total = sum(detail.values())
        method = "Tổng 14 câu đầy đủ"
    else:
        total = round((v1 + v2) / 2 * 14)
        detail = {}
        method = f"Nội suy từ 2 câu: ({v1}+{v2})/2 × 14"

    print(f"   BƯỚC 2 — Tính điểm ({method}): {total}/42")
    if detail:
        items = [f"Q{q}={v}" for q, v in detail.items()]
        print(f"   Chi tiết: {' | '.join(items)}")

    return {"total": total, "detail": detail, "method": method}


#  Bước 3 & 4: Fuzzy Logic 
def _fuzzy_evaluate(dim: str, total: int) -> Dict[str, Any]:
    """Fuzzification (Gaussian MF) + Defuzzification (Centroid)."""
    params = FUZZY_PARAMS[dim]

    print(f"\n   BƯỚC 3 — Fuzzification (Gaussian MF):")
    memberships = []
    for p in params:
        mu = _gaussmf(total, p["mean"], p["sigma"])
        flag = " ◄" if mu > 0.001 else ""
        formula = f"exp(-(({total}-{p['mean']})² / (2×{p['sigma']}²)))"
        print(f"   {p['label']:<20} | {formula:<42} | μ={mu:.3f}{flag}")
        memberships.append({"label": p["label"], "idx": p["idx"], "mu": mu})

    # Centroid defuzzification
    numerator   = sum(m["mu"] * m["idx"] for m in memberships)
    denominator = sum(m["mu"] for m in memberships)
    crisp = (numerator / denominator) if denominator > 0 else 0.0

    print(f"\n   BƯỚC 4 — Defuzzification (Centroid):")
    parts = [f"({m['mu']:.3f}×{m['idx']})" for m in memberships]
    print(f"   Tử số = {' + '.join(parts)}")
    print(f"          = {numerator:.3f}")
    print(f"   Mẫu số = {denominator:.3f}")
    print(f"   → CRISP = {crisp:.4f} (thang 0-4)")

    if   crisp < 0.5: label_idx = 0
    elif crisp < 1.5: label_idx = 1
    elif crisp < 2.5: label_idx = 2
    elif crisp < 3.5: label_idx = 3
    else:             label_idx = 4

    label = ["Normal", "Mild", "Moderate", "Severe", "Extremely Severe"][label_idx]
    print(f"   → Kết luận: {label.upper()} (label_idx={label_idx})")

    return {
        "fuzzy_value": round(crisp, 4),
        "label_idx":   label_idx,
        "label":       label,
        "memberships": [{"label": m["label"], "mu": round(m["mu"], 4)} for m in memberships],
    }


# Bước 6: Forward Chaining 
def _forward_chaining(d10: int, a10: int, s10: int) -> str:
    """
    Forward Chaining — nhận diện profile nghi ngờ từ D/A/S fuzzy scores.
    Ưu tiên: SWI-Prolog → Python fallback.
    Query Prolog: candidate_profile(Profile, D10, A10, S10)
    """
    print(f"\n[BƯỚC 6 — Forward Chaining] D×10={d10}, A×10={a10}, S×10={s10}")

    if PROLOG_AVAILABLE and _prolog_instance is not None:
        print("   → Engine: SWI-Prolog (pyswip)")
        with _prolog_lock:
            try:
                query = f"candidate_profile(Profile, {d10}, {a10}, {s10})"
                print(f"   → Query: {query}")
                results = list(_prolog_instance.query(query))
                if results:
                    profile = str(results[0]["Profile"])
                    print(f"   → Prolog → Profile: {profile.upper()}")
                    return profile
                else:
                    print("   → Prolog: Không match rule nào → xử lý fallback")
            except Exception as e:
                logger.warning(f"[PROLOG] Forward chaining error: {e}. Using Python fallback.")

    print("   → Engine: Python fallback")
    if d10 >= 30 and a10 >= 30 and s10 >= 30:
        profile = "maladaptive_crisis"
    elif a10 >= 25 and d10 <= 15 and s10 <= 20:
        profile = "panic_disorder"
    elif s10 >= 25 and d10 <= 15 and a10 <= 15:
        profile = "gad_stress_dominant"
    elif d10 >= 25 and a10 < 25 and s10 < 25:
        profile = "pure_depression"
    elif a10 >= 20 and s10 >= 20:
        profile = "social_anxiety"
    elif d10 < 15 and a10 < 15 and s10 < 15:
        profile = "low_risk"
    else:
        mx = max(d10, a10, s10)
        if   mx == d10: profile = "pure_depression"
        elif mx == a10: profile = "panic_disorder"
        else:           profile = "gad_stress_dominant"

    print(f"   → Python → Profile: {profile.upper()}")
    return profile


# Bước 7: Backward Chaining Verification
def _verify_diagnosis(profile: str, known_answers: Dict[str, str]) -> bool:
    """
    Backward Chaining — xác minh profile bằng SWI-Prolog.

    Cơ chế:
      1. assert known(Q, Answer) cho mỗi câu trả lời đã biết
      2. query verify_diagnosis(Profile)
      3. Prolog dùng luật ask_symptom/ask_symptom_no để kiểm tra
      4. retractall(known(_, _)) để dọn dẹp

    Fallback Python: đếm "yes" vs CONFIRM_THRESHOLD.
    """
    bw_flow = BACKWARD_FLOW.get(profile, [])

    # Profiles không cần xác minh backward
    if len(bw_flow) == 0:
        print(f"   → Profile {profile.upper()} tự động xác nhận (không cần backward)")
        return True

    if PROLOG_AVAILABLE and _prolog_instance is not None:
        print(f"\n   → Engine: SWI-Prolog — xác minh verify_diagnosis({profile})")
        with _prolog_lock:
            try:
                # Bước 1: Xóa sạch known facts cũ
                _retract_known()

                # Bước 2: Assert tất cả câu trả lời đã biết
                for q, ans in known_answers.items():
                    fact = f"known({q}, {ans})"
                    _prolog_instance.assertz(fact)
                    print(f"     assertz({fact})")

                # Bước 3: Query xác minh
                query_str = f"verify_diagnosis({profile})"
                print(f"   → Query: {query_str}")
                results = list(_prolog_instance.query(query_str))
                verified = len(results) > 0
                status = "ĐÃ XÁC NHẬN ✓" if verified else "CHƯA ĐỦ TIÊU CHÍ ✗"
                print(f"   → Prolog → {status}")
                return verified

            except Exception as e:
                logger.warning(f"[PROLOG] Backward chaining error: {e}. Using Python fallback.")
            finally:
                # Bước 4: Dọn dẹp facts
                _retract_known()

    print(f"\n   → Engine: Python fallback — xác minh {profile.upper()}")
    threshold = CONFIRM_THRESHOLD.get(profile, 0)
    confirm_score = sum(1 for k in bw_flow if known_answers.get(k, "no") == "yes")
    verified = confirm_score >= threshold
    status = "ĐÃ XÁC NHẬN ✓" if verified else "CHƯA ĐỦ TIÊU CHÍ ✗"
    print(f"   → Python → {confirm_score}/{len(bw_flow)} triệu chứng ≥ ngưỡng {threshold}: {status}")
    return verified


def run_screening_phase(answers: Dict[int, int]) -> Dict[str, Any]:
    """
    Giai đoạn 1: Nhận 6 câu sàng lọc (2 câu × 3 chiều).
    Trả về: quyết định skip/ask_more cho từng chiều + danh sách câu cần hỏi thêm.
    """
    print("\n" + "="*70)
    print(f"{'HỆ CHUYÊN GIA — GIAI ĐOẠN 1: SÀNG LỌC':^70}")
    print("="*70)
    engine_status = "SWI-Prolog ✅" if PROLOG_AVAILABLE else "Python fallback ⚠"
    print(f"   [Engine: {engine_status}]")

    result = {}
    questions_needed = []

    for dim in ["depression", "anxiety", "stress"]:
        screening = _prolog_screening(dim, answers)
        result[dim] = {"screening": screening}

        if screening["action"] == "ask_more":
            needed = [q for q in DIM_QUESTIONS[dim] if q not in answers]
            questions_needed.extend(needed)
            result[dim]["needs_full_questions"] = True
        else:
            result[dim]["needs_full_questions"] = False

    print(f"\n📋 Câu hỏi cần hỏi tiếp: {sorted(set(questions_needed))}")
    return {
        "phase": "screening_done",
        "screening": result,
        "questions_needed": sorted(set(questions_needed)),
    }


def run_fuzzy_phase(answers: Dict[int, int], screening_result: Dict) -> Dict[str, Any]:
    """
    Giai đoạn 2: Fuzzy Logic + Forward Chaining (Prolog).
    Trả về: kết quả từng chiều + profile nghi ngờ + câu backward chaining.
    """
    print("\n" + "="*70)
    print(f"{'HỆ CHUYÊN GIA — GIAI ĐOẠN 2: FUZZY + FORWARD CHAINING':^70}")
    print("="*70)

    final = {}
    dim_labels = {
        "depression": "TRẦM CẢM (Depression)",
        "anxiety":    "LO ÂU (Anxiety)",
        "stress":     "CĂNG THẲNG (Stress)",
    }

    for dim in ["depression", "anxiety", "stress"]:
        s = screening_result["screening"][dim]
        scr = s["screening"]
        print(f"\n[{dim_labels[dim]}]")
        print("-" * 70)

        if scr["action"] == "skip":
            print(f"   => Bỏ qua (rủi ro thấp).")
            final[dim] = {
                "screening_action": "skip",
                "total_score": 0,
                "fuzzy_value": 0.0,
                "label_idx":   0,
                "label":       "Normal",
                "advice":      DIM_ADVICE[dim][0],
                "memberships": [],
            }
            continue

        score_res = _compute_score(dim, answers, scr["action"], scr["v1"], scr["v2"])
        fuzzy_res = _fuzzy_evaluate(dim, score_res["total"])

        advice = DIM_ADVICE[dim][fuzzy_res["label_idx"]]
        print(f"\n   BƯỚC 5 — Lời khuyên: {advice}")

        final[dim] = {
            "screening_action": scr["action"],
            "total_score":      score_res["total"],
            "fuzzy_value":      fuzzy_res["fuzzy_value"],
            "label_idx":        fuzzy_res["label_idx"],
            "label":            fuzzy_res["label"],
            "advice":           advice,
            "memberships":      fuzzy_res["memberships"],
        }

    # Forward Chaining
    d10 = round(final["depression"]["fuzzy_value"] * 10)
    a10 = round(final["anxiety"]["fuzzy_value"] * 10)
    s10 = round(final["stress"]["fuzzy_value"] * 10)
    profile = _forward_chaining(d10, a10, s10)

    # Chuẩn bị câu hỏi backward chaining
    bw_flow = BACKWARD_FLOW.get(profile, [])
    bw_questions = [
        {"key": k, "text": BACKWARD_QUESTIONS[k]}
        for k in bw_flow
        if k in BACKWARD_QUESTIONS
    ]

    print(f"\n[BƯỚC 7 — Backward Chaining cần hỏi: {[q['key'] for q in bw_questions]}]")

    # In bảng tổng kết
    print("\n" + "="*70)
    print(f"{'TỔNG KẾT':^70}")
    print("="*70)
    print(f"  {'Chiều':<25} | {'Điểm':^6} | {'Fuzzy':^7} | Kết luận")
    print("-" * 70)
    for dim, label in dim_labels.items():
        r = final[dim]
        print(f"  {label:<25} | {r['total_score']:>3}/42 | {r['fuzzy_value']:.3f}  | {r['label'].upper()}")

    return {
        "phase": "fuzzy_done",
        "dimensions": final,
        "profile":    profile,
        "backward_questions": bw_questions,
        "needs_backward": len(bw_questions) > 0,
    }


def run_backward_phase(profile: str, known_answers: Dict[str, str], fuzzy_result: Dict) -> Dict[str, Any]:
    """
    Giai đoạn 3: Backward Chaining (Prolog) → xác nhận profile cuối.
    known_answers: { "a1": "yes", "a2": "no", "n1": "yes", ... }
    """
    print("\n" + "="*70)
    print(f"{'HỆ CHUYÊN GIA — GIAI ĐOẠN 3: BACKWARD CHAINING':^70}")
    print("="*70)
    print(f"  Profile nghi ngờ: {profile.upper()}")

    bw_flow = BACKWARD_FLOW.get(profile, [])

    # In chi tiết câu trả lời
    detail = []
    for k in bw_flow:
        ans = known_answers.get(k, "no")
        mark = "✓" if ans == "yes" else "✗"
        text = BACKWARD_QUESTIONS.get(k, k)
        detail.append({"key": k, "text": text, "answer": ans})
        print(f"   [{mark}] {text}")

    verified = _verify_diagnosis(profile, known_answers)
    final_profile = profile if verified else "low_risk"

    # Đếm confirm_score để hiển thị
    confirm_score = sum(1 for k in bw_flow if known_answers.get(k, "no") == "yes")

    engine_name = "SWI-Prolog" if PROLOG_AVAILABLE else "Python"
    print(f"\n  → [{engine_name}] Xác nhận: {'ĐÃ XÁC NHẬN' if verified else 'CHƯA ĐỦ TIÊU CHÍ'} ({confirm_score}/{len(bw_flow)} triệu chứng)")
    print(f"  → Profile cuối: {final_profile.upper()}")

    profile_adv = PROFILE_ADVICE.get(final_profile, PROFILE_ADVICE["low_risk"])
    print(f"\n[KẾT LUẬN] {profile_adv}")
    print("="*70)

    return {
        "phase":            "complete",
        "profile":          final_profile,
        "profile_verified": verified,
        "confirm_score":    confirm_score,
        "confirm_total":    len(bw_flow),
        "profile_advice":   profile_adv,
        "confirm_detail":   detail,
        "dimensions":       fuzzy_result.get("dimensions", {}),
    }