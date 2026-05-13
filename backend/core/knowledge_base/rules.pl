:- dynamic known/2.


%% ------------------------------------------------------------
%% PHẦN 0 — NGưỡng SÀNG LỌC (Screening Thresholds)
%% ------------------------------------------------------------
screening_threshold(depression, q21, q10, 1.5).
screening_threshold(anxiety,    q28, q7,  1.5).
screening_threshold(stress,     q11, q8,  1.5).


%% ------------------------------------------------------------
%% PHẦN 1 — HỆ THỐNG ĐẶT CÂU HỎI (Backward Chaining)
%% ------------------------------------------------------------

%% ask_symptom/1: pass nếu triệu chứng HIỆN DIỆN (known = yes)
ask_symptom(Question) :-
    (   known(Question, yes)  -> true
    ;   known(Question, no)   -> fail
    ;   ask_user(Question)
    ).

ask_user(Question) :-
    format(atom(Prompt), 'ASK:~w', [Question]),
    throw(need_input(Prompt)).

%% ask_symptom_no/1: pass nếu triệu chứng VẮNG MẶT (known = no)
ask_symptom_no(Question) :-
    (   known(Question, no)  -> true
    ;   known(Question, yes) -> fail
    ;   ask_user(Question), known(Question, no)
    ).


%% ------------------------------------------------------------
%% PHẦN 2 — FORWARD CHAINING: candidate_profile/4
%% ------------------------------------------------------------

%% Hồ sơ 1: Khủng hoảng toàn diện — cả 3 chiều đều nghiêm trọng
candidate_profile(maladaptive_crisis, D10, A10, S10) :-
    D10 >= 30, A10 >= 30, S10 >= 30.

%% Hồ sơ 2: Trầm cảm nặng (MDD) — D rất cao, chưa đến crisis
candidate_profile(major_depression, D10, A10, S10) :-
    D10 >= 25,
    \+ candidate_profile(maladaptive_crisis, D10, A10, S10).

%% Hồ sơ 3: Rối loạn Hoảng sợ — A cao, D và S thấp
candidate_profile(panic_disorder, D10, A10, S10) :-
    A10 >= 12, D10 =< 15, S10 =< 20,
    \+ candidate_profile(maladaptive_crisis, D10, A10, S10).

%% Hồ sơ 4: Lo âu Lan tỏa / GAD — S cao, D và A thấp
candidate_profile(gad_stress_dominant, D10, A10, S10) :-
    S10 >= 20, D10 =< 15, A10 =< 15,
    \+ candidate_profile(maladaptive_crisis, D10, A10, S10),
    \+ candidate_profile(panic_disorder, D10, A10, S10).

%% Hồ sơ 5: Lo âu Xã hội — A và S cùng tăng
candidate_profile(social_anxiety, D10, A10, S10) :-
    A10 >= 10, S10 >= 15,
    \+ candidate_profile(panic_disorder,      D10, A10, S10),
    \+ candidate_profile(major_depression,    D10, A10, S10),
    \+ candidate_profile(gad_stress_dominant, D10, A10, S10).

%% Hồ sơ 6: Không có nguy cơ — tất cả đều trong phạm vi an toàn
candidate_profile(low_risk, D10, A10, S10) :-
    D10 < 15, A10 < 15, S10 < 15.


%% ------------------------------------------------------------
%% PHẦN 3 — BACKWARD CHAINING: verify_diagnosis/1
%% ------------------------------------------------------------

%% --- MDD (Major Depressive Disorder) ---
%% Tiêu chí A (DSM-5): (A1 HOẶC A2) VÀ A3 (≥5/9 triệu chứng) VÀ A4 (suy giảm chức năng)
ask_a1_or_a2 :- ask_symptom(a1), !.
ask_a1_or_a2 :- ask_symptom(a2).

verify_diagnosis(major_depression) :-
    ask_a1_or_a2,
    ask_symptom(a3),
    ask_symptom(a4).

%% --- GAD (Generalized Anxiety Disorder / gad_stress_dominant) ---
%% Tiêu chí (DSM-5): lo lắng quá mức ≥6 tháng (N1) + thấy KHÓ kiểm soát (N2=yes)
%%                   + ≥3 triệu chứng thể chất (N3) + suy giảm chức năng (N4)
verify_diagnosis(gad_stress_dominant) :-
    ask_symptom(n1),
    ask_symptom(n2),     
    ask_symptom(n3),
    ask_symptom(n4).

%% --- Panic Disorder ---
%% Tiêu chí (DSM-5): cơn hoảng sợ tái diễn (D1a) + đỉnh trong 10 phút (D1b)
%%                   + ít nhất 1 cơn bất ngờ (D2) + ≥4 triệu chứng thực thể (D4)
verify_diagnosis(panic_disorder) :-
    ask_symptom(d1a),
    ask_symptom(d1b),
    ask_symptom(d2),
    ask_symptom(d4).

%% --- Social Anxiety Disorder ---
%% Tiêu chí (DSM-5): sợ hãi rõ rệt trong tình huống xã hội (F1–F6 đều dương tính)
verify_diagnosis(social_anxiety) :-
    ask_symptom(f1),
    ask_symptom(f2),
    ask_symptom(f3),
    ask_symptom(f4),
    ask_symptom(f5),
    ask_symptom(f6).

%% --- Các hồ sơ tự xác nhận ---
verify_diagnosis(maladaptive_crisis) :- true.
verify_diagnosis(low_risk)           :- true.
