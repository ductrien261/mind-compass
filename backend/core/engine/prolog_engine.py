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
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

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
        logger.warning("[PROLOG] ⚠ pyswip not installed.")
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


# Hằng số DASS-42

SCREENING_CFG = {
    "depression": {"q1": 21, "q2": 10, "threshold": 1.5},
    "anxiety":    {"q1": 28, "q2":  7, "threshold": 1.5},
    "stress":     {"q1": 11, "q2":  8, "threshold": 1.5},
}

# Hệ số hiệu chỉnh nội suy (tính từ dữ liệu thực tế — Cell 19 notebook v7)
# depression: 2 câu ước lượng thấp hơn thực tế 14.4% → nhân 1.144
# anxiety:    2 câu ước lượng thấp hơn thực tế 11.3% → nhân 1.113
# stress:     2 câu khớp gần đúng (sai số 2.8%)      → nhân 0.972
CORRECTION_FACTORS = {
    "depression": 1.144,
    "anxiety":    1.113,
    "stress":     0.972,
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
    "maladaptive_crisis":
        "MỨC ĐỘ NGUY HIỂM: Bạn đang trong tình trạng khủng hoảng tâm lý nghiêm trọng. "
        "Bạn cần được hỗ trợ y tế khẩn cấp và đánh giá bởi chuyên gia ngay lập tức. "
        "Lưu ý quan trọng: Không nên ở một mình trong lúc này. Nếu có ý nghĩ tự làm hại bản thân, "
        "hãy liên hệ ngay với người thân tin cậy hoặc gọi đường dây nóng hỗ trợ tâm lý ngay lập tức.",

    "major_depression":
        "MỨC ĐỘ NẶNG (Trầm cảm - MDD): Theo WHO mhGAP: "
        "(1) Cố gắng duy trì các hoạt động từng mang lại niềm vui cho bạn, dù chỉ bắt đầu bằng những bước rất nhỏ. "
        "(2) Duy trì thời gian biểu sinh hoạt đều đặn: ngủ, ăn và vận động đúng giờ. "
        "(3) Duy trì kết nối, trò chuyện với gia đình và bạn bè thân thiết. "
        "Bạn nên gặp chuyên gia để được tư vấn các liệu pháp tâm lý phù hợp như CBT hoặc IPT.",

    "panic_disorder":
        "MỨC ĐỘ NẶNG (Rối loạn Hoảng sợ): Theo WHO mhGAP: "
        "(1) Khi cơn hoảng sợ kéo đến: Thực hiện kỹ thuật thở chậm (hít vào chậm trong 3 giây, giữ hơi 2 giây, thở ra chậm 3 giây). "
        "(2) Hãy nhớ rằng cơn hoảng sợ không gây nguy hiểm đến tính mạng dù cảm giác có thể rất dữ dội. "
        "(3) Cố gắng không né tránh các tình huống gây sợ hãi, vì việc đối mặt dần dần sẽ giúp tình trạng không bị nặng hơn. "
        "Nên gặp chuyên gia để được hướng dẫn liệu pháp tiếp xúc có kiểm soát.",

    "gad_stress_dominant":
        "MỨC ĐỘ VỪA-NẶNG (Rối loạn Lo âu lan tỏa / Căng thẳng kéo dài): Theo WHO mhGAP: "
        "(1) Thực hành các kỹ thuật thư giãn: tập thở chậm từ bụng và thư giãn cơ toàn thân hàng ngày. "
        "(2) Xác định các nguồn gây căng thẳng cụ thể và cùng người thân thảo luận cách giải quyết từng vấn đề. "
        "(3) Tiếp tục duy trì các hoạt động xã hội và sinh hoạt thường ngày thay vì rút lui. "
        "Nên chia sẻ tình trạng của mình với người thân tin cậy hoặc tìm gặp tư vấn viên.",

    "social_anxiety":
        "MỨC ĐỘ VỪA-NẶNG (Lo âu xã hội): Theo WHO mhGAP: "
        "(1) Tập tiếp xúc dần dần với các tình huống xã hội thay vì né tránh hoàn toàn. "
        "(2) Áp dụng kỹ thuật thở chậm (Hít 3s - Giữ 2s - Thở 3s) trước khi bước vào tình huống gây lo lắng. "
        "(3) Chủ động tham gia vào các hoạt động cộng đồng phù hợp để tăng cường kết nối. "
        "Nên gặp chuyên gia để được hỗ trợ lộ trình CBT — đã chứng minh hiệu quả cao với lo âu xã hội.",

    "low_risk":
        "MỨC ĐỘ AN TOÀN: Các chỉ số hiện tại của bạn nằm trong phạm vi an toàn. "
        "Theo khuyến nghị: Bạn nên tiếp tục duy trì lối sống lành mạnh để bảo vệ sức khỏe tinh thần: "
        "đảm bảo ngủ đủ giấc, duy trì chế độ ăn cân bằng, vận động thể chất thường xuyên "
        "và nuôi dưỡng các mối quan hệ xã hội tích cực.",
}

# Backward Chaining Questions
#
# type: "yesno"       → render yes/no buttons
# type: "multiselect" → render checkbox list, đếm số lượng chọn
#
# Với multiselect:
#   - "options": danh sách lựa chọn
#   - "min_count": ngưỡng tối thiểu để tính là "pass" (đủ triệu chứng)
#   - "a1_counts_one": True nếu câu A1=yes đã đóng góp 1 vào tổng (MDD đặc biệt)
#
# Logic luồng theo từng profile :
#   MDD:   A1(yn) → if no → A2(yn) → if A1 or A2 = yes → A3(multi,≥5) → A4(yn)
#   GAD:   N1(yn) → N2(yn) → if N2=no (không kiểm soát được) → N3(multi,≥3) → N4(yn)
#   Panic: D1a(yn) → D1b(yn) → D2(yn) → D4(multi,≥4)
#   Social: F1→F2→F3→F4→F5→F6 (tất cả yes/no)

BACKWARD_QUESTIONS: Dict[str, Dict] = {

    # MDD
    "a1": {
        "key": "a1",
        "type": "yesno",
        "text": "Bạn có bao giờ cảm thấy chán nản, thất vọng, hoặc thấy buồn bã, trống rỗng, tuyệt vọng phần lớn thời gian trong ngày, gần như mỗi ngày, kéo dài trong hai tuần không?",
    },
    "a2": {
        "key": "a2",
        "type": "yesno",
        "text": "Bạn có bao giờ cảm thấy ít quan tâm hơn hẳn đến hầu hết mọi thứ, hoặc ít có khả năng tận hưởng những thứ mà bạn từng thích trong phần lớn thời gian, kéo dài trong hai tuần không?",
    },
    "a3": {
        "key": "a3",
        "type": "multiselect",
        "text": "Trong giai đoạn đó, bạn có gặp các triệu chứng nào sau đây không? (Chọn tất cả các triệu chứng bạn gặp)",
        "options": [
            {"value": "a3_a",
                "label": "Cảm giác thèm ăn của bạn có bị giảm đi hoặc tăng lên gần như mỗi ngày không? Trọng lượng cơ thể bạn có bị giảm hoặc tăng mà không do chủ ý không?"},
            {"value": "a3_b", "label": "Bạn có gặp vấn đề về giấc ngủ gần như mỗi đêm không (khó ngủ, thức giấc giữa đêm, thức dậy quá sớm vào buổi sáng hoặc ngủ quá nhiều)?"},
            {"value": "a3_c", "label": "Bạn có nói năng hoặc di chuyển chậm hơn bình thường, hay bạn cảm thấy bồn chồn, không yên, hoặc khó có thể ngồi yên gần như mỗi ngày không?"},
            {"value": "a3_d", "label": "Bạn có cảm thấy mệt mỏi hoặc thiếu năng lượng gần như mỗi ngày không?"},
            {"value": "a3_e", "label": "Bạn có cảm thấy mình vô dụng hoặc có tội lỗi gần như mỗi ngày không?"},
            {"value": "a3_f", "label": "Bạn có gặp khó khăn trong việc tập trung, suy nghĩ hoặc đưa ra quyết định gần như mỗi ngày không?"},
            {"value": "a3_g", "label": "Bạn có suy nghĩ lặp đi lặp lại về cái chết không, hoặc có bất kỳ ý nghĩ nào về việc tự sát, hay có ý định/kế hoạch tự kết liễu đời mình không? Bạn có từng cố gắng tự sát không?"},
        ],
        "min_count": 4,
    },
    "a4": {
        "key": "a4",
        "type": "yesno",
        "text": "Những triệu chứng này có gây ra khó khăn đáng kể hoặc ảnh hưởng rõ rệt đến công việc, học tập, các mối quan hệ hoặc cuộc sống hàng ngày của bạn không?",
    },

    # GAD
    "n1": {
        "key": "n1",
        "type": "yesno",
        "text": "Bạn có lo lắng hoặc bất an quá mức về nhiều việc thường nhật trong suốt 6 tháng qua không? (Ví dụ: công việc, học tập, sức khỏe, tài chính, gia đình...)?",
    },
    "n2": {
        "key": "n2",
        "type": "yesno",
        "text": "Bạn có thấy khó kiểm soát được những nỗi lo lắng của mình không?",
        "stop_if": "no",
        "stop_reason": "Kiểm soát được lo lắng → không đủ tiêu chí GAD (DSM-5 Criterion B)",
    },
    "n3": {
        "key": "n3",
        "type": "multiselect",
        "text": "Khi lo lắng trong 6 tháng qua, bạn có gặp các triệu chứng nào sau đây không? (Chọn tất cả các triệu chứng bạn gặp)",
        "options": [
            {"value": "n3_a", "label": "Cảm thấy bồn chồn, căng thẳng hoặc cảm giác như đang đứng bên bờ vực"},
            {"value": "n3_b", "label": "Bị căng cơ"},
            {"value": "n3_c", "label": "Thấy mệt mỏi, yếu sức hoặc dễ bị kiệt sức"},
            {"value": "n3_d", "label": "Gặp khó khăn khi tập trung hoặc thấy đầu óc mình trở nên trống rỗng"},
            {"value": "n3_e", "label": "Cảm thấy dễ cáu kỉnh/gắt gỏng"},
            {"value": "n3_f",
                "label": "Gặp khó khăn về giấc ngủ (khó ngủ, thức giấc giữa đêm, dậy quá sớm hoặc ngủ quá nhiều)?"},
        ],
        "min_count": 3,
    },
    "n4": {
        "key": "n4",
        "type": "yesno",
        "text": "Những lo lắng và triệu chứng này có gây ra khó khăn đáng kể trong công việc, các mối quan hệ hoặc cuộc sống hàng ngày, hoặc khiến bạn đau khổ rõ rệt không?",
    },

    # Panic Disorder
    "d1a": {
        "key": "d1a",
        "type": "yesno",
        "text": "Bạn có bao giờ, trong nhiều hơn một lần, gặp những giai đoạn hoặc những cơn mà bạn bất ngờ cảm thấy lo âu, rất sợ hãi, khó chịu hoặc bất an, ngay cả trong những tình huống mà hầu hết mọi người đều không cảm thấy như vậy không?",
    },
    "d1b": {
        "key": "d1b",
        "type": "yesno",
        "text": "Những cơn này có tăng lên đến đỉnh điểm trong vòng 10 phút kể từ khi bắt đầu không?",
    },
    "d2": {
        "key": "d2",
        "type": "yesno",
        "text": "Tại bất kỳ thời điểm nào trong quá khứ, có cơn nào trong số đó xảy ra một cách bất ngờ, không thể dự đoán trước hoặc không vì một lý do cụ thể nào không?",
    },
    "d4": {
        "key": "d4",
        "type": "multiselect",
        "text": "Trong cơn tệ nhất bạn từng trải qua, bạn có gặp các triệu chứng nào sau đây không? (Chọn tất cả triệu chứng có trong cơn đó)",
        "options": [
            {"value": "d4_a", "label": "Tim đập nhanh, mạnh hoặc loạn nhịp"},
            {"value": "d4_b", "label": "Đổ mồ hôi hoặc bàn tay ẩm"},
            {"value": "d4_c", "label": "Run rẩy hoặc lắc"},
            {"value": "d4_d", "label": "Khó thở, thở gấp hoặc cảm giác bị nghẹt thở"},
            {"value": "d4_e", "label": "Cảm giác bị nghẹn ở cổ họng"},
            {"value": "d4_f", "label": "Đau ngực, tức ngực hoặc khó chịu ở ngực"},
            {"value": "d4_g", "label": "Buồn nôn, đau bụng hoặc tiêu chảy đột ngột"},
            {"value": "d4_h", "label": "Chóng mặt, loạng choạng, nhẹ đầu hoặc sắp ngất"},
            {"value": "d4_i", "label": "Người nóng bừng hoặc ớn lạnh"},
            {"value": "d4_j", "label": "Tê bì hoặc ngứa ran ở các bộ phận cơ thể"},
            {"value": "d4_k", "label": "Mọi thứ xung quanh trông lạ lẫm, không thực, hoặc cảm thấy tách rời khỏi bản thân"},
            {"value": "d4_l", "label": "Sợ mất kiểm soát hoặc sắp hóa điên"},
            {"value": "d4_m", "label": "Sợ chết"},
        ],
        "min_count": 4,
    },

    # Social Anxiety
    "f1": {
        "key": "f1",
        "type": "yesno",
        "text": "Trong tháng vừa qua, bạn có cảm thấy sợ hãi rõ rệt hoặc lo lắng đáng kể khi bị người khác nhìn, trở thành tâm điểm chú ý, hoặc sợ bị xấu hổ, bẽ mặt hay bị từ chối trong các tình huống xã hội không? (Ví dụ: nói chuyện nhóm, ăn trước mặt người khác, phát biểu, gặp người mới...)",
    },
    "f2": {
        "key": "f2",
        "type": "yesno",
        "text": "Các tình huống xã hội đó hầu như luôn gây ra nỗi sợ hoặc lo âu cho bạn không?",
    },
    "f3": {
        "key": "f3",
        "type": "yesno",
        "text": "Bạn có né tránh các tình huống xã hội đó, hoặc phải chịu đựng chúng với cảm giác rất khó chịu, hay cần có người đi cùng mới dám đối mặt không?",
    },
    "f4": {
        "key": "f4",
        "type": "yesno",
        "text": "Nỗi sợ này có vẻ quá mức so với mức độ nguy hiểm thực sự của tình huống không?",
    },
    "f5": {
        "key": "f5",
        "type": "yesno",
        "text": "Tình trạng né tránh hoặc lo âu xã hội này đã kéo dài ít nhất 6 tháng không?",
    },
    "f6": {
        "key": "f6",
        "type": "yesno",
        "text": "Những nỗi sợ này có gây ra khó khăn đáng kể hoặc ảnh hưởng rõ rệt đến công việc, học tập hoặc các mối quan hệ của bạn không?",
    },
}

#  Backward Flow per profile

BACKWARD_FLOW: Dict[str, List[str]] = {
    "major_depression":     ["a1", "a2", "a3", "a4"],
    "gad_stress_dominant":  ["n1", "n2", "n3", "n4"],
    "panic_disorder":       ["d1a", "d1b", "d2", "d4"],
    "social_anxiety":       ["f1", "f2", "f3", "f4", "f5", "f6"],
    "maladaptive_crisis":   [],
    "low_risk":             [],
}

CONFIRM_THRESHOLD: Dict[str, int] = {
    "major_depression":     3,
    "gad_stress_dominant":  3,   # n1 + n3_pass + n4
    "panic_disorder":       3,   # d1a + d1b + d2 + d4_pass
    "social_anxiety":       4,   # f1..f6 ≥ 4
    "maladaptive_crisis":   0,
    "low_risk":             0,
}


#  Helper: build backward question list for API response

def build_backward_questions(profile: str) -> List[Dict]:
    """
    Trả về list câu hỏi backward cho profile, bao gồm đầy đủ metadata
    để frontend render đúng UI (yesno vs multiselect).
    """
    flow = BACKWARD_FLOW.get(profile, [])
    result = []
    for key in flow:
        q = BACKWARD_QUESTIONS.get(key)
        if q:
            result.append(q)
    return result


# Python fallback: evaluate multiselect answers

def _eval_multiselect(key: str, selected: List[str], known_answers: Dict[str, Any]) -> bool:
    """
    Trả về True nếu số triệu chứng được chọn đạt ngưỡng.
    Với A3 (MDD): cộng thêm 1 nếu A1=yes (A1 đã là 1 trong 9 tiêu chí DSM).
    """
    q = BACKWARD_QUESTIONS[key]
    min_count = q.get("min_count", 1)
    count = len(selected)

    if key == "a3":
        # A1 = yes đã đóng góp 1 triệu chứng (depressed mood)
        if known_answers.get("a1") == "yes":
            count += 1
        # A2 = yes (anhedonia) cũng đóng góp 1 nếu A1=no
        elif known_answers.get("a2") == "yes":
            count += 1

    passed = count >= min_count
    logger.info(
        f"[BACKWARD] multiselect {key}: {count} selected (need ≥{min_count}) → {'PASS' if passed else 'FAIL'}")
    return passed


#  Hàm toán học

def _gaussmf(x: float, mean: float, sigma: float) -> float:
    """Gaussian membership function."""
    return math.exp(-((x - mean) ** 2) / (2 * sigma ** 2))


# Bước 1: Prolog Screening

def _prolog_screening(dim: str, answers: Dict[int, int]) -> Dict[str, Any]:
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
    return {"action": action, "q1": q1, "q2": q2, "v1": v1, "v2": v2, "threshold": thr, "reason": reason}


#  Bước 2: Tính điểm

def _compute_score(dim: str, answers: Dict[int, int], action: str, v1: int, v2: int) -> Dict[str, Any]:
    all_qs = DIM_QUESTIONS[dim]

    if action == "ask_more":
        detail = {q: answers.get(q, 0) for q in all_qs}
        total = sum(detail.values())
        method = "Tổng 14 câu đầy đủ"
    else:
        # Nội suy điểm có hiệu chỉnh theo tỷ lệ thực tế/ước lượng từ dữ liệu
        factor = CORRECTION_FACTORS[dim]
        raw = (v1 + v2) / 2 * 14
        total = min(round(raw * factor), 42)   # cap tại max DASS-42
        method = f"Nội suy từ 2 câu: ({v1}+{v2})/2 × 14 × {factor} (hiệu chỉnh) = {raw:.1f} × {factor} → {total} (cap ≤42)"
        detail = {}

    return {"total": total, "detail": detail, "method": method}


# Bước 3 & 4: Fuzzy Logic

def _fuzzy_evaluate(dim: str, total: int) -> Dict[str, Any]:
    params = FUZZY_PARAMS[dim]

    print(f"\n   BƯỚC 3 — MỜ HÓA (FUZZIFICATION)")
    print(f"   {'Tập mờ':<16} | {'Công thức':<46} | μ")
    print(f"   {'.'*70}")

    memberships = []
    for p in params:
        mu = _gaussmf(total, p["mean"], p["sigma"])
        formula = f"exp(-(({total}-{p['mean']})² / (2×{p['sigma']}²)))"
        flag = " ◄" if mu > 0.001 else ""
        label_short = p['label'].replace("Extremely Severe", "Ext. Severe")
        print(f"   {label_short:<16} | {formula:<46} | {mu:.3f}{flag}")
        memberships.append({"label": p["label"], "idx": p["idx"], "mu": mu})

    numerator = sum(m["mu"] * m["idx"] for m in memberships)
    denominator = sum(m["mu"] for m in memberships)
    crisp = (numerator / denominator) if denominator > 0 else 0.0

    parts_num = " + ".join(f"({m['mu']:.3f}×{m['idx']})" for m in memberships)
    parts_den = " + ".join(f"{m['mu']:.3f}" for m in memberships)

    print(f"\n   BƯỚC 4 — GIẢI MỜ (DEFUZZIFICATION - Centroid)")
    print(f"   Tử số  = {parts_num}")
    print(f"          = {numerator:.3f}")
    print(f"   Mẫu số = {parts_den}")
    print(f"          = {denominator:.3f}")
    print(
        f"   → CRISP = {numerator:.3f} / {denominator:.3f} = {crisp:.4f} (Thang 0-4)")

    if crisp < 0.5: label_idx = 0
    elif crisp < 1.5: label_idx = 1
    elif crisp < 2.5: label_idx = 2
    elif crisp < 3.5: label_idx = 3
    else: label_idx = 4

    label = ["Normal", "Mild", "Moderate",
             "Severe", "Extremely Severe"][label_idx]
    print(f"   → Kết luận: {label.upper()} (label_idx={label_idx})")

    return {
        "fuzzy_value": round(crisp, 4),
        "label_idx":   label_idx,
        "label":       label,
        "memberships": [{"label": m["label"], "mu": round(m["mu"], 4)} for m in memberships],
    }


# Bước 5: Forward Chaining

def _forward_chaining(d10: int, a10: int, s10: int) -> str:
    print(f"\n{'='*70}")
    print(f"{'BƯỚC 6 — FORWARD CHAINING':^70}")
    print(f"{'='*70}")
    print(f"   Fuzzy input (×10) : D={d10}  A={a10}  S={s10}")

    PRIORITY = [
        "maladaptive_crisis",
        "major_depression",
        "panic_disorder",
        "gad_stress_dominant",
        "social_anxiety",
        "low_risk",
    ]

    if PROLOG_AVAILABLE and _prolog_instance is not None:
        print("   Engine            : SWI-Prolog (pyswip)")
        with _prolog_lock:
            try:
                query = f"candidate_profile(Profile, {d10}, {a10}, {s10})"
                results = list(_prolog_instance.query(query))
                profiles_found = [str(r["Profile"]) for r in results]
                print(f"   Prolog candidates  : {profiles_found}")
                profile = next(
                    (p for p in PRIORITY if p in profiles_found),
                    "low_risk"
                )
                print(f"   → Hồ sơ nhận diện : {profile.upper()}")
                return profile
            except Exception as e:
                logger.warning(
                    f"[PROLOG] Forward chaining error: {e}. Using Python fallback.")

    print("   Engine            : Python fallback")
    if d10 >= 30 and a10 >= 30 and s10 >= 30:
        profile = "maladaptive_crisis"
    elif d10 >= 25:
        profile = "major_depression"
    elif a10 >= 12 and d10 <= 15 and s10 <= 20:   
        profile = "panic_disorder"
    elif s10 >= 20 and d10 <= 15 and a10 <= 15:   
        profile = "gad_stress_dominant"
    elif a10 >= 10 and s10 >= 15:             
        profile = "social_anxiety"
    elif d10 < 15 and a10 < 15 and s10 < 15:
        profile = "low_risk"
    else:
        profile = "low_risk"
    return profile


# Bước 6: Backward Chaining Verification

def _verify_diagnosis(profile: str, known_answers: Dict[str, Any]) -> bool:
    """
    Xác minh profile bằng Python logic (phản ánh đúng sơ đồ luồng).

    known_answers có thể chứa:
      - "a1": "yes"/"no"
      - "a3": ["a3_a", "a3_c", ...]   ← list các option được chọn
      - "n3": ["n3_a", "n3_b", ...]
      - "d4": ["d4_a", "d4_b", ...]
      - "n2": "yes"/"no"
      - v.v.
    """
    bw_flow = BACKWARD_FLOW.get(profile, [])
    if not bw_flow:
        return True

    if PROLOG_AVAILABLE and _prolog_instance is not None:
        with _prolog_lock:
            try:
                _retract_known()
                for q, ans in known_answers.items():
                    if isinstance(ans, list):
                        # multiselect: assert từng option được chọn
                        for opt in ans:
                            _prolog_instance.assertz(f"known({opt}, yes)")
                        # assert tổng đếm
                        _prolog_instance.assertz(
                            f"known({q}_count, {len(ans)})")
                    else:
                        _prolog_instance.assertz(f"known({q}, {ans})")

                results = list(_prolog_instance.query(
                    f"verify_diagnosis({profile})"))
                return len(results) > 0
            except Exception as e:
                logger.warning(
                    f"[PROLOG] Backward error: {e}. Using Python fallback.")
            finally:
                _retract_known()

    def yn(key: str) -> bool:
        return known_answers.get(key) == "yes"

    def multi_pass(key: str) -> bool:
        selected = known_answers.get(key, [])
        if not isinstance(selected, list):
            return False
        return _eval_multiselect(key, selected, known_answers)

    if profile == "major_depression":
        a1_or_a2 = yn("a1") or yn("a2")
        a3_ok = multi_pass("a3")
        a4_ok = yn("a4")
        return a1_or_a2 and a3_ok and a4_ok

    elif profile == "gad_stress_dominant":
        # N1 phải yes, N2 phải yes (thấy KHÓ kiểm soát = DSM-5 Criterion B), N3 multi ≥3, N4 yes
        return yn("n1") and yn("n2") and multi_pass("n3") and yn("n4")

    elif profile == "panic_disorder":
        # D1a, D1b, D2 đều yes, D4 multi ≥ 4
        return yn("d1a") and yn("d1b") and yn("d2") and multi_pass("d4")

    elif profile == "social_anxiety":
        # F1..F6 tất cả yes
        return all(yn(f"f{i}") for i in range(1, 7))

    return False


# Public API

def run_screening_phase(answers: Dict[int, int]) -> Dict[str, Any]:
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

    return {
        "phase": "screening_done",
        "screening": result,
        "questions_needed": sorted(set(questions_needed)),
    }


def run_fuzzy_phase(answers: Dict[int, int], screening_result: Dict) -> Dict[str, Any]:
    final = {}
    print(f"\n{'='*70}")
    print(f"{'HỆ CHUYÊN GIA ĐÁNH GIÁ SỨC KHỎE TÂM THẦN — DASS-42':^70}")
    print(f"{'='*70}")

    for dim in ["depression", "anxiety", "stress"]:
        s = screening_result["screening"][dim]
        scr = s["screening"]

        dim_label_map = {
            "depression": "TRẦM CẢM (Depression)",
            "anxiety":    "LO ÂU (Anxiety)",
            "stress":     "CĂNG THẲNG (Stress)",
        }
        print(f"\n[{dim_label_map[dim]}]")
        print(f"{'-'*70}")

        if scr["action"] == "skip":
            # Nội suy điểm từ 2 câu sàng lọc (có hiệu chỉnh theo correction factor)
            score_res  = _compute_score(dim, answers, "skip", scr["v1"], scr["v2"])
            print(f"\n BƯỚC 2: TÍNH ĐIỂM (Nội suy từ 2 câu sàng lọc)")
            print(f"   - Phương pháp : {score_res['method']}")
            print(f"   → ĐIỂM ƯỚC LƯỢNG: {score_res['total']} / 42")
            fuzzy_res = _fuzzy_evaluate(dim, score_res["total"])
            advice    = DIM_ADVICE[dim][fuzzy_res["label_idx"]]
            final[dim] = {
                "screening_action": "skip",
                "total_score":  score_res["total"],
                "fuzzy_value":  fuzzy_res["fuzzy_value"],
                "label_idx":    fuzzy_res["label_idx"],
                "label":        fuzzy_res["label"],
                "advice":       advice,
                "memberships":  fuzzy_res["memberships"],
            }
            continue

        score_res = _compute_score(
            dim, answers, scr["action"], scr["v1"], scr["v2"])
        print(f"\n BƯỚC 2: TÍNH ĐIỂM TỔNG")
        print(f"   - Phương pháp : {score_res['method']}")
        if score_res['detail']:
            items = [f"Q{q}={v}" for q, v in score_res['detail'].items()]
            # In theo hàng 7 câu
            for i in range(0, len(items), 7):
                prefix = "   - Chi tiết      : " if i == 0 else "                     "
                print(prefix + "  ".join(items[i:i+7]))
        print(f"   → ĐIỂM TỔNG   : {score_res['total']} / 42")
        fuzzy_res = _fuzzy_evaluate(dim, score_res["total"])
        advice = DIM_ADVICE[dim][fuzzy_res["label_idx"]]

        final[dim] = {
            "screening_action": scr["action"],
            "total_score":      score_res["total"],
            "fuzzy_value":      fuzzy_res["fuzzy_value"],
            "label_idx":        fuzzy_res["label_idx"],
            "label":            fuzzy_res["label"],
            "advice":           advice,
            "memberships":      fuzzy_res["memberships"],
        }

    d10 = round(final["depression"]["fuzzy_value"] * 10)
    a10 = round(final["anxiety"]["fuzzy_value"] * 10)
    s10 = round(final["stress"]["fuzzy_value"] * 10)
    profile = _forward_chaining(d10, a10, s10)

    bw_questions = build_backward_questions(profile)

    return {
        "phase": "fuzzy_done",
        "dimensions": final,
        "profile":    profile,
        "backward_questions": bw_questions,
        "needs_backward": len(bw_questions) > 0,
    }


def run_backward_phase(profile: str, known_answers: Dict[str, Any], fuzzy_result: Dict) -> Dict[str, Any]:
    print(f"\n{'='*70}")
    print(f"{'BƯỚC 7 — BACKWARD CHAINING':^70}")
    print(f"{'='*70}")
    print(f"   Profile nghi ngờ : {profile.upper()}")

    bw_flow = BACKWARD_FLOW.get(profile, [])

    if not bw_flow:
        print(
            f"   → Profile {profile.upper()} tự động xác nhận (không cần backward)")
        final_profile = profile
        verified = True
    else:
        print(f"\n   Câu trả lời backward:")
        for k in bw_flow:
            ans = known_answers.get(k, "—")
            q_text = BACKWARD_QUESTIONS.get(k, {}).get("text", k)
            q_type = BACKWARD_QUESTIONS.get(k, {}).get("type", "yesno")
            if q_type == "multiselect":
                selected = ans if isinstance(ans, list) else []
                min_c = BACKWARD_QUESTIONS[k].get("min_count", 0)
                mark = "✓" if len(selected) >= min_c else "✗"
                print(
                    f"   [{mark}] {k}: {len(selected)} triệu chứng chọn (cần ≥{min_c})")
                for s in selected:
                    print(f"        • {s}")
            else:
                mark = "✓" if ans == "yes" else "✗"
                print(f"   [{mark}] {k}: {ans}")

        verified = _verify_diagnosis(profile, known_answers)
        status = "ĐÃ XÁC NHẬN ✓" if verified else "CHƯA ĐỦ TIÊU CHÍ ✗"
        print(f"\n   → Kết quả xác minh: {status}")

        if verified:
            final_profile = profile
        else:
            dims = fuzzy_result.get("dimensions", {})
            any_severe = any(
                dims.get(d, {}).get("label_idx", 0) >= 3
                for d in ["depression", "anxiety", "stress"]
            )
            if any_severe:
                final_profile = profile
                print(
                    f"   → Safety net: điểm fuzzy cao (≥ Severe) → giữ profile {profile.upper()}")
            else:
                final_profile = "low_risk"
                print(f"   → Không đủ tiêu chí + điểm thấp → LOW_RISK")

    profile_adv = PROFILE_ADVICE.get(final_profile, PROFILE_ADVICE["low_risk"])

    print(f"\n{'='*70}")
    print(f"{'TỔNG KẾT CHẨN ĐOÁN':^70}")
    print(f"{'='*70}")
    dims = fuzzy_result.get("dimensions", {})
    dim_labels = {
        "depression": "Trầm cảm (Depression)",
        "anxiety":    "Lo âu (Anxiety)",
        "stress":     "Căng thẳng (Stress)",
    }
    print(f"  {'Chiều':<25} | {'Điểm':^6} | {'Fuzzy':^7} | Kết luận")
    print(f"  {'-'*65}")
    for dim, label in dim_labels.items():
        r = dims.get(dim, {})
        print(f"  {label:<25} | {r.get('total_score', 0):>3}/42 | {r.get('fuzzy_value', 0):.3f}  | {r.get('label', 'N/A').upper()}")
    print(f"\n  → Profile cuối    : {final_profile.upper()}")
    print(
        f"  → Xác nhận backward: {'CÓ' if verified else 'KHÔNG (safety net)'}")
    print(f"\n[KẾT LUẬN] {profile_adv}")
    print(f"{'='*70}")

    confirm_detail: List[Dict[str, Any]] = []
    confirm_score = 0

    for key in bw_flow:
        q = BACKWARD_QUESTIONS.get(key)
        if not q:
            continue
        ans = known_answers.get(key)
        if ans is None:
            continue

        q_type = q.get("type", "yesno")
        q_text = q.get("text", key)

        if q_type == "yesno":
            answer_str = str(ans)
            stop_if = q.get("stop_if")
            passed = (ans != stop_if) if stop_if else (ans == "yes")
        else:  # multiselect
            selected = ans if isinstance(ans, list) else []
            passed = _eval_multiselect(key, selected, known_answers)
            answer_str = "yes" if passed else "no"

        if passed:
            confirm_score += 1

        confirm_detail.append({
            "key":    key,
            "text":   q_text,
            "answer": answer_str,
        })

    confirm_total = len([k for k in bw_flow if BACKWARD_QUESTIONS.get(k)])

    return {
        "phase":            "complete",
        "profile":          final_profile,
        "profile_verified": verified,
        "profile_confirmed": verified,
        "profile_advice":   profile_adv,
        "dimensions":       dims,
        "confirm_detail":   confirm_detail,
        "confirm_score":    confirm_score,
        "confirm_total":    confirm_total,
    }
