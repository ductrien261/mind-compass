from django.urls import path
from .views import (
    ScreeningView,
    FuzzyAnalysisView,
    BackwardChainingView,
    DassAnalysisView,
)

urlpatterns = [
    # ─── Main expert system flow (called by frontend) ───────────────────
    path('screening/', ScreeningView.as_view(), name='screening'),
    path('fuzzy-analysis/', FuzzyAnalysisView.as_view(), name='fuzzy_analysis'),
    path('backward-chaining/', BackwardChainingView.as_view(), name='backward_chaining'),
    # ─── Legacy / utility endpoint ──────────────────────────────────────
    path('analyze-dass/', DassAnalysisView.as_view(), name='analyze_dass'),
]