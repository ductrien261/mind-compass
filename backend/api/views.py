# backend/api/views.py
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.engine.fuzzy_engine import fuzzy_analyzer
from core.engine.prolog_engine import (
    run_screening_phase,
    run_fuzzy_phase,
    run_backward_phase,
    BACKWARD_QUESTIONS,
    BACKWARD_FLOW,
)

logger = logging.getLogger(__name__)


class ScreeningView(APIView):
    """
    POST /api/screening/
    Nhận 6 câu sàng lọc → quyết định câu nào cần hỏi thêm.

    Body: { "answers": { "21": 2, "10": 1, "28": 3, "7": 0, "11": 1, "8": 2 } }
    """
    def post(self, request):
        try:
            raw = request.data.get("answers", {})
            # key có thể là string từ JSON → convert sang int
            answers = {int(k): int(v) for k, v in raw.items()}

            logger.info(f"[SCREENING] Nhận {len(answers)} câu trả lời: {answers}")

            result = run_screening_phase(answers)
            return Response({"status": "success", "data": result}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception(f"[SCREENING ERROR] {e}")
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class FuzzyAnalysisView(APIView):
    """
    POST /api/fuzzy-analysis/
    Nhận đủ câu trả lời + screening_result → chạy Fuzzy + Forward Chaining.

    Body: {
        "answers": { "1": 0, "2": 2, ..., "42": 1 },   // tất cả câu đã trả lời
        "screening": { ... }                             // kết quả từ /api/screening/
    }
    """
    def post(self, request):
        try:
            raw      = request.data.get("answers", {})
            screening = request.data.get("screening", {})

            answers = {int(k): int(v) for k, v in raw.items()}

            logger.info(f"[FUZZY] Nhận {len(answers)} câu trả lời, chạy Fuzzy engine...")

            result = run_fuzzy_phase(answers, screening)
            return Response({"status": "success", "data": result}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception(f"[FUZZY ERROR] {e}")
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class BackwardChainingView(APIView):
    """
    POST /api/backward-chaining/
    Nhận câu trả lời backward chaining → xác nhận profile → trả kết quả cuối.

    Body: {
        "profile": "gad_stress_dominant",
        "known_answers": { "n1": "yes", "n2": "no", "n3": "yes", "n4": "yes" },
        "fuzzy_result": { ... }   // kết quả từ /api/fuzzy-analysis/
    }
    """
    def post(self, request):
        try:
            profile       = request.data.get("profile", "low_risk")
            known_answers = request.data.get("known_answers", {})
            fuzzy_result  = request.data.get("fuzzy_result", {})

            logger.info(f"[BACKWARD] Profile={profile}, answers={known_answers}")

            result = run_backward_phase(profile, known_answers, fuzzy_result)
            return Response({"status": "success", "data": result}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception(f"[BACKWARD ERROR] {e}")
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DassAnalysisView(APIView):
    def post(self, request):
        data = request.data
        try:
            d_score = float(data.get('depression_score', 0))
            a_score = float(data.get('anxiety_score', 0))
            s_score = float(data.get('stress_score', 0))
            result = fuzzy_analyzer.analyze_all(d_score, a_score, s_score)
            return Response({"status": "success", "data": result}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)