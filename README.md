<div align="center">

# 🧭 MindCompass

### Hệ Chuyên Gia Đánh Giá Sức Khỏe Tâm Thần

*Dựa trên thang đo DASS-42 · Logic Mờ · Prolog Backward Chaining*

<br/>

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.x-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![Next.js](https://img.shields.io/badge/Next.js-15-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)](https://nextjs.org)
[![SWI-Prolog](https://img.shields.io/badge/SWI--Prolog-10.0-E61E29?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZD0iTTEyIDJMMiA3bDEwIDUgMTAtNUwxMiAyem0wIDE1bC0xMC01djUuNWwxMCA1IDEwLTVWMTJsMC0wIDAtMHoiIGZpbGw9IndoaXRlIi8+PC9zdmc+)](https://www.swi-prolog.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

<br/>

> **MindCompass** là một hệ chuyên gia tương tác giúp người dùng tự đánh giá sức khỏe tâm thần thông qua
> bộ câu hỏi DASS-42 (Depression · Anxiety · Stress Scale). Hệ thống kết hợp ba kỹ thuật AI cổ điển:
> **Fuzzy Logic** (để định lượng mức độ), **Forward Chaining** và **Backward Chaining** (để suy diễn hồ sơ tâm lý).

</div>

---

## ✨ Tính năng nổi bật

| Tính năng | Mô tả |
|-----------|-------|
| 🔍 **Sàng lọc thông minh** | Chỉ hỏi 6 câu ban đầu, tự động bỏ qua chiều nào không có nguy cơ |
| 🌀 **Fuzzy Logic** | Gaussian Membership Function + Centroid Defuzzification - tính mức độ liên tục thay vì rời rạc |
| 🔗 **Forward Chaining (Prolog)** | Từ điểm số Fuzzy → suy diễn hồ sơ tâm lý nghi ngờ |
| ↩️ **Backward Chaining (Prolog)** | SWI-Prolog `verify_diagnosis/1` xác nhận hoặc bác bỏ hồ sơ bằng luật tri thức |
| 🇻🇳 **Giao diện tiếng Việt** | Câu hỏi, kết quả và lời khuyên hoàn toàn bằng tiếng Việt |
| 📡 **REST API** | Django REST Framework - dễ tích hợp |
| ⚡ **Real-time UX** | Next.js 15 + animations mượt mà, 7 bước đánh giá có progress bar |

---

## 🏗️ Kiến trúc hệ thống

```
┌─────────────────────────────────────────────────────────────────────┐
│                         MindCompass                                  │
│                                                                      │
│   ┌──────────────┐    REST API     ┌──────────────────────────────┐  │
│   │   Frontend   │◄───────────────►│         Backend              │  │
│   │  (Next.js)   │                 │         (Django)             │  │
│   │              │                 │                              │  │
│   │  Landing     │  POST /screen-  │  ┌────────────────────────┐  │  │
│   │  ↓           │  ing/           │  │   prolog_engine.py     │  │  │
│   │  Assess      │◄───────────────►│  │                        │  │  │
│   │  (7 phases)  │  POST /fuzzy-   │  │  ① Prolog Screening    │  │  │
│   │  ↓           │  analysis/      │  │  ② Scoring (DASS-42)   │  │  │
│   │  Result      │◄───────────────►│  │  ③ Fuzzy Logic         │  │  │
│   │              │  POST /back-    │  │  ④ Forward Chaining    │  │  │
│   │              │  ward-chaining/ │  │  ⑤ Backward Chaining   │  │  │
│   └──────────────┘◄───────────────►│  └────────────┬───────────┘  │  │
│                                    │               │               │  │
│                                    │  ┌────────────▼───────────┐  │  │
│                                    │  │   rules.pl (SWI-Prolog) │  │  │
│                                    │  │   candidate_profile/4   │  │  │
│                                    │  │   verify_diagnosis/1    │  │  │
│                                    │  └────────────────────────┘  │  │
│                                    └──────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔬 Luồng hoạt động

Hệ thống hoạt động theo **3 giai đoạn** liên tiếp:

### Giai đoạn 1 — Sàng lọc (Screening)

```
User trả lời 6 câu (2 câu × 3 chiều: D / A / S)
        │
        ▼
   ┌────────────────────────────────────────────┐
   │  Với mỗi chiều (Depression / Anxiety / Stress):│
   │                                            │
   │  if score[q1] ≤ 1.5 AND score[q2] ≤ 1.5   │
   │      → SKIP chiều này                      │
   │  else                                      │
   │      → ASK_MORE (hỏi 14 câu đầy đủ)        │
   └────────────────────────────────────────────┘
```

### Giai đoạn 2 — Fuzzy Logic + Forward Chaining

```
Với mỗi chiều cần đánh giá:

  Tổng điểm (0–42)
      │
      ▼
  Gaussian MF: μ = exp(-(x - mean)² / (2σ²))
      │         cho 5 tập mờ: Normal / Mild / Moderate / Severe / Extremely Severe
      ▼
  Centroid Defuzzification: crisp = Σ(μᵢ × idxᵢ) / Σ(μᵢ)    [thang 0–4]
      │
      ▼
  D×10, A×10, S×10  ──→  SWI-Prolog: candidate_profile(Profile, D10, A10, S10)
                                           │
                                           ▼
                                     Profile nghi ngờ
```

### Giai đoạn 3 — Backward Chaining (Xác minh Prolog)

```
Frontend hỏi N câu Yes/No tương ứng với profile
      │
      ▼
Backend nhận toàn bộ câu trả lời
      │
      ▼
  Prolog: assertz(known(QuestionKey, yes/no))   ← cho từng câu trả lời
      │
      ▼
  Prolog: verify_diagnosis(Profile)
      │    ← đọc luật ask_symptom/1 và ask_symptom_no/1 từ rules.pl
      │
      ├── Thành công → Profile được XÁC NHẬN
      └── Thất bại   → Kết luận: low_risk
```

---

## 📂 Cấu trúc dự án

```
mindcompass/
├── backend/                        # Django REST API
│   ├── api/
│   │   ├── views.py                # ScreeningView, FuzzyAnalysisView, BackwardChainingView
│   │   └── urls.py                 # URL routing
│   ├── core/
│   │   ├── engine/
│   │   │   ├── prolog_engine.py    # ⭐ Engine chính: Fuzzy + Prolog integration
│   │   │   └── fuzzy_engine.py     # Scikit-fuzzy helper
│   │   └── knowledge_base/
│   │       └── rules.pl            # ⭐ Luật tri thức SWI-Prolog
│   ├── config/
│   │   └── settings.py
│   ├── test_pipeline.py            # Script test end-to-end
│   └── manage.py
│
└── frontend/                       # Next.js 15
    └── app/
        ├── page.tsx                # Landing page
        ├── assess/page.tsx         # Trang đánh giá
        ├── result/page.tsx         # Trang kết quả
        ├── components/
        │   ├── AssessmentFlow.tsx  # ⭐ State machine 7 bước
        │   ├── ResultDashboard.tsx # Dashboard kết quả
        │   ├── AnalysisScreen.tsx  # Màn hình đang xử lý
        │   └── RadarChart.tsx      # Biểu đồ radar D/A/S
        └── lib/
            ├── api.ts              # Giao tiếp với backend
            └── questions.ts        # Ngân hàng câu hỏi DASS-42
```

---

## 🚀 Cài đặt & Chạy

### Yêu cầu

- **Python** 3.11+
- **Node.js** 18+
- **SWI-Prolog** 10.x — [Tải tại đây](https://www.swi-prolog.org/download/stable) (bắt buộc để chạy Backward Chaining thực)

### Backend (Django)

```bash
cd backend

# 1. Tạo virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

# 2. Cài dependencies
pip install django djangorestframework django-cors-headers pyswip

# 3. Chạy migrations
python manage.py migrate

# 4. Khởi động server
python manage.py runserver
# → http://localhost:8000
```

> **Lưu ý:** `pyswip` tự động giao tiếp với SWI-Prolog đã cài. Nếu SWI-Prolog chưa được thêm vào `PATH`, hãy [xem hướng dẫn](https://www.swi-prolog.org/FAQ/FindSWIProlog.html).

### Frontend (Next.js)

```bash
cd frontend

# 1. Cài dependencies
npm install

# 2. Khởi động dev server
npm run dev
# → http://localhost:3000
```

### Chạy test pipeline

```bash
cd backend
python test_pipeline.py
```

Output mẫu:

```
PROLOG_AVAILABLE: True

# TEST: MDD Anxious Distress (D=3, A=3 cao đồng thời)
  → Engine: SWI-Prolog — xác minh verify_diagnosis(mdd_anxious_distress)
  → Prolog → ĐÃ XÁC NHẬN ✓
>> RESULT: PASS ✓ | Profile: MDD_ANXIOUS_DISTRESS

# TEST: GAD Stress Dominant
  → Prolog → ĐÃ XÁC NHẬN ✓
>> RESULT: PASS ✓ | Profile: GAD_STRESS_DOMINANT

# TEST: GAD bị từ chối (lo âu có nguồn gốc cụ thể)
  → Prolog → CHƯA ĐỦ TIÊU CHÍ ✗
>> RESULT: WARN (unverified) | Profile: LOW_RISK
```

---

## 🔌 API Reference

Base URL: `http://localhost:8000/api/`

### `POST /api/screening/`

Nhận 6 câu sàng lọc và trả về danh sách câu hỏi cần hỏi tiếp.

**Request:**
```json
{
  "answers": {
    "21": 2,
    "10": 1,
    "28": 3,
    "7": 0,
    "11": 1,
    "8": 2
  }
}
```

**Response:**
```json
{
  "phase": "screening_done",
  "screening": {
    "depression": { "screening": { "action": "ask_more", "q1": 21, "q2": 10 }, "needs_full_questions": true },
    "anxiety":    { "screening": { "action": "skip",     "q1": 28, "q2": 7 },  "needs_full_questions": false },
    "stress":     { "screening": { "action": "skip",     "q1": 11, "q2": 8 },  "needs_full_questions": false }
  },
  "questions_needed": [3, 5, 13, 16, 17, 24, 26, 31, 34, 37, 38, 42]
}
```

---

### `POST /api/fuzzy-analysis/`

Nhận toàn bộ câu trả lời, chạy Fuzzy Logic + Forward Chaining.

**Request:**
```json
{
  "answers": { "3": 2, "5": 3, "10": 2, "21": 3 },
  "screening": { ... }
}
```

**Response:**
```json
{
  "phase": "fuzzy_done",
  "profile": "pure_depression",
  "dimensions": {
    "depression": {
      "total_score": 24,
      "fuzzy_value": 2.87,
      "label": "Severe",
      "advice": "Trầm cảm: Mức độ nặng..."
    },
    "anxiety": { "label": "Normal", "fuzzy_value": 0.0 },
    "stress":  { "label": "Normal", "fuzzy_value": 0.0 }
  },
  "backward_questions": [
    { "key": "a1", "text": "Bạn có cảm thấy buồn, trống rỗng..." },
    { "key": "a2", "text": "Bạn có mất hứng thú..." }
  ],
  "needs_backward": true
}
```

---

### `POST /api/backward-chaining/`

Nhận câu trả lời Yes/No, chạy Backward Chaining (SWI-Prolog) để xác nhận.

**Request:**
```json
{
  "profile": "pure_depression",
  "answers": {
    "a1": "yes",
    "a2": "no",
    "a3": "yes",
    "a4": "yes"
  },
  "fuzzy_result": { ... }
}
```

**Response:**
```json
{
  "phase": "complete",
  "profile": "pure_depression",
  "profile_verified": true,
  "confirm_score": 3,
  "confirm_total": 4,
  "profile_advice": "MỨC ĐỘ NẶNG (Trầm cảm): Bạn đang đánh mất năng lượng...",
  "dimensions": { ... }
}
```

---

## 🧠 Knowledge Base (Prolog)

File: `backend/core/knowledge_base/rules.pl`

### Forward Chaining — `candidate_profile/4`

```prolog
%% Khủng hoảng toàn diện (D + A + S đều ≥ 30)
candidate_profile(maladaptive_crisis, D10, A10, S10) :-
    D10 >= 30, A10 >= 30, S10 >= 30.

%% Trầm cảm kèm lo âu (D ≥ 25 VÀ A ≥ 25)
candidate_profile(mdd_anxious_distress, D10, A10, S10) :-
    D10 >= 25, A10 >= 25,
    \+ candidate_profile(maladaptive_crisis, D10, A10, S10).

%% GAD / Lo âu lan tỏa (S cao, D/A thấp)
candidate_profile(gad_stress_dominant, D10, A10, S10) :-
    S10 >= 25, D10 =< 15, A10 =< 15, ...
```

### Backward Chaining — `verify_diagnosis/1`

```prolog
%% GAD: n2 phải là "no" (lo âu KHÔNG có nguồn cụ thể)
verify_diagnosis(gad_stress_dominant) :-
    ask_symptom(n1),
    ask_symptom_no(n2),    %← key: lo âu không từ sự kiện cụ thể
    ask_symptom(n3),
    ask_symptom(n4).

%% MDD: (a1 HOẶC a2) VÀ a3 VÀ a4
ask_a1_or_a2 :- ask_symptom(a1), !.
ask_a1_or_a2 :- ask_symptom(a2).
verify_diagnosis(pure_depression) :-
    ask_a1_or_a2,
    ask_symptom(a3),
    ask_symptom(a4).
```

---

## 📊 Các hồ sơ tâm lý được nhận diện

| Profile | Tên đầy đủ | Điều kiện Forward Chaining |
|---------|-----------|---------------------------|
| `maladaptive_crisis` | Khủng hoảng toàn diện | D ≥ 30 **và** A ≥ 30 **và** S ≥ 30 |
| `mdd_anxious_distress` | Trầm cảm kèm lo âu | D ≥ 25 **và** A ≥ 25 |
| `panic_disorder` | Rối loạn hoảng sợ | A ≥ 25, D ≤ 15, S ≤ 20 |
| `gad_stress_dominant` | Lo âu lan tỏa / GAD | S ≥ 25, D ≤ 15, A ≤ 15 |
| `pure_depression` | Trầm cảm thuần | D ≥ 25, A < 25, S < 25 |
| `social_anxiety` | Lo âu xã hội | A ≥ 20 **và** S ≥ 20 |
| `low_risk` | Không có nguy cơ | D < 15 **và** A < 15 **và** S < 15 |

---

## 📸 Giao diện

<table>
  <tr>
    <td align="center"><b>Landing Page</b></td>
    <td align="center"><b>Sàng lọc</b></td>
    <td align="center"><b>Kết quả</b></td>
  </tr>
  <tr>
    <td>Trang chủ với thiết kế tối, gradient hiện đại</td>
    <td>7 bước đánh giá có progress bar và animation</td>
    <td>Dashboard với Radar Chart D/A/S và lời khuyên</td>
  </tr>
</table>

---

## 🛠️ Tech Stack

### Backend
| Công nghệ | Mô tả |
|-----------|-------|
| **Python 3.11** | Ngôn ngữ chính |
| **Django 4.x** | Web framework |
| **Django REST Framework** | REST API |
| **SWI-Prolog 10** | Engine suy diễn logic |
| **pyswip 0.3.3** | Python bridge → SWI-Prolog |
| **scikit-fuzzy** | Hỗ trợ tính toán Fuzzy (bổ sung) |

### Frontend
| Công nghệ | Mô tả |
|-----------|-------|
| **Next.js 15** | React framework |
| **TypeScript** | Type safety |
| **Geist Font** | Font hỗ trợ tiếng Việt |
| **CSS Animations** | Micro-interactions |

