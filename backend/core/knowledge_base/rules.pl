%% KNOWLEDGE BASE: DASS-42 & M.I.N.I (BACKWARD CHAINING)
:- dynamic known/2.


%% --- Hệ thống đặt câu hỏi  ---
ask_symptom(Question) :-
    (   known(Question, yes)  -> true
    ;   known(Question, no)   -> fail
    ;   ask_user(Question)
    ).

ask_user(Question) :-
    format(atom(Prompt), 'ASK:~w', [Question]),
    throw(need_input(Prompt)).

ask_symptom_no(Question) :-
    (   known(Question, no)  -> true
    ;   known(Question, yes) -> fail
    ;   ask_user(Question), known(Question, no)
    ).

%% --- Forward Chaining - Candidate Profile ---
%% Hồ sơ 1: Khủng hoảng toàn diện
candidate_profile(maladaptive_crisis, D10, A10, S10) :- D10 >= 30, A10 >= 30, S10 >= 30.

%% Hồ sơ 2: Trầm cảm
candidate_profile(major_depression, D10, A10, S10) :- D10 >= 25,
                                                   \+ candidate_profile(maladaptive_crisis, D10, A10, S10).

%% Hồ sơ 3: Panic
candidate_profile(panic_disorder, D10, A10, S10) :- A10 >= 12, D10 =< 15, S10 =< 20,
                                                 \+ candidate_profile(maladaptive_crisis, D10, A10, S10).

%% Hồ sơ 4: GAD
candidate_profile(gad_stress_dominant, D10, A10, S10) :- S10 >= 20, D10 =< 15, A10 =< 15,
                                                      \+ candidate_profile(maladaptive_crisis, D10, A10, S10),
                                                      \+ candidate_profile(panic_disorder, D10, A10, S10).

%% Hồ sơ 5: Social Anxiety
candidate_profile(social_anxiety, D10, A10, S10) :- A10 >= 10, S10 >= 15,
                                                 \+ candidate_profile(panic_disorder, D10, A10, S10),
                                                 \+ candidate_profile(major_depression, D10, A10, S10),
                                                 \+ candidate_profile(gad_stress_dominant, D10, A10, S10).

%% Hồ sơ 6: Low Risk — chỉ khi tất cả đều thấp
candidate_profile(low_risk, D10, A10, S10) :- D10 < 15, A10 < 15, S10 < 15.


%% --- Backward Chaining - Xác minh chuẩn đoán ---

%% --- MDD (Major Depressive Disorder) ---
ask_a1_or_a2 :- ask_symptom(a1), !.
ask_a1_or_a2 :- ask_symptom(a2).

verify_diagnosis(major_depression) :-
    ask_a1_or_a2,
    ask_symptom(a3),
    ask_symptom(a4).

%% --- GAD (Generalized Anxiety Disorder / gad_stress_dominant) ---
verify_diagnosis(gad_stress_dominant) :-
    ask_symptom(n1),
    ask_symptom_no(n2), 
    ask_symptom(n3),
    ask_symptom(n4).

%% --- Panic Disorder ---
verify_diagnosis(panic_disorder) :-
    ask_symptom(d1a),
    ask_symptom(d1b),
    ask_symptom(d2),
    ask_symptom(d4).

%% --- Social Anxiety ---
verify_diagnosis(social_anxiety) :-
    ask_symptom(f1),
    ask_symptom(f2),
    ask_symptom(f3),
    ask_symptom(f4),
    ask_symptom(f5),
    ask_symptom(f6).

verify_diagnosis(maladaptive_crisis)   :- true.
verify_diagnosis(low_risk)             :- true.


%% --- Lời khuyên theo từng nhóm Profile  ---
profile_advice(maladaptive_crisis, "MỨC ĐỘ NGUY HIỂM: Bạn đang kiệt sức hoàn toàn về mặt tâm lý. Xin đừng cố chịu đựng một mình, hãy liên hệ ngay với bác sĩ tâm lý hoặc đường dây hỗ trợ y tế khẩn cấp để được giúp đỡ.").

profile_advice(major_depression, "MỨC ĐỘ NẶNG (Trầm cảm nặng - MDD): Bạn đang đánh mất năng lượng và niềm vui sống. Hãy duy trì thời gian biểu sinh hoạt cố định, giữ kết nối với người thân và đi khám tâm lý để được hỗ trợ phương pháp trị liệu phù hợp.").

profile_advice(panic_disorder, "MỨC ĐỘ NẶNG (Hoảng sợ cấp tính): Cơ thể bạn đang phản ứng thái quá với sự lo âu. Khi cơn hoảng sợ đến, hãy tập hít thở sâu, chạm vào các đồ vật xung quanh để kéo tâm trí về hiện tại. Bạn nên gặp chuyên gia để học cách kiểm soát triệt để triệu chứng này.").

profile_advice(gad_stress_dominant, "MỨC ĐỘ VỪA - NẶNG (Lo âu & Căng thẳng kéo dài): Bạn đang bị quá tải và khó ngừng suy nghĩ. Hãy thử các bài tập kéo giãn cơ bắp, dành ra một 'khung giờ lo lắng' cố định thay vì lo âu cả ngày, và trò chuyện với tư vấn viên để giải tỏa.").

profile_advice(social_anxiety, "MỨC ĐỘ VỪA - NẶNG (Lo âu xã hội): Những nỗi sợ phán xét đang làm đảo lộn cuộc sống của bạn. Trị liệu hành vi nhận thức (CBT) đã được chứng minh là cực kỳ hiệu quả để giúp bạn lấy lại sự tự tin khi ra ngoài.").

profile_advice(low_risk, "MỨC ĐỘ AN TOÀN: Không có dấu hiệu nào đáng lo ngại. Sức khỏe tinh thần của bạn hiện tại rất ổn định. Hãy tiếp tục duy trì lối sống lành mạnh, ngủ đủ giấc và vận động thể chất đều đặn nhé.").