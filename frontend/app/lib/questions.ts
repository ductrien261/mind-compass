export interface DassQuestion {
  id: number;       
  text: string;
  dimension: "depression" | "anxiety" | "stress";
}

const DIM_MAP: Record<number, "depression" | "anxiety" | "stress"> = {
  // Depression
  3: "depression", 5: "depression", 10: "depression", 13: "depression",
  16: "depression", 17: "depression", 21: "depression", 24: "depression",
  26: "depression", 31: "depression", 34: "depression", 37: "depression",
  38: "depression", 42: "depression",
  // Anxiety
  2: "anxiety", 4: "anxiety",  7: "anxiety",  9: "anxiety",
  15: "anxiety", 19: "anxiety", 20: "anxiety", 23: "anxiety",
  25: "anxiety", 28: "anxiety", 30: "anxiety", 36: "anxiety",
  40: "anxiety", 41: "anxiety",
  // Stress
  1: "stress",  6: "stress",  8: "stress", 11: "stress",
  12: "stress", 14: "stress", 18: "stress", 22: "stress",
  27: "stress", 29: "stress", 32: "stress", 33: "stress",
  35: "stress", 39: "stress",
};

export const DASS_QUESTIONS: DassQuestion[] = [
  { id: 1,  text: "Tôi thấy bản thân khó có thể thư giãn được.",                                                       dimension: "stress"     },
  { id: 2,  text: "Tôi bị khô miệng.",                                                                                dimension: "anxiety"    },
  { id: 3,  text: "Tôi dường như không có cảm xúc tích cực nào cả.",                                                   dimension: "depression" },
  { id: 4,  text: "Tôi bị rối loạn nhịp thở (thở nhanh, khó thở dù không vận động).",                                dimension: "anxiety"    },
  { id: 5,  text: "Tôi thấy thật khó để bắt tay vào công việc.",                                                      dimension: "depression" },
  { id: 6,  text: "Tôi có xu hướng phản ứng thái quá với các tình huống.",                                             dimension: "stress"     },
  { id: 7,  text: "Tôi cảm thấy tay hoặc chân run rẩy.",                                                              dimension: "anxiety"    },
  { id: 8,  text: "Tôi cảm thấy mình đang tiêu hao rất nhiều sức lực, căng thẳng thần kinh.",                         dimension: "stress"     },
  { id: 9,  text: "Tôi lo lắng về những tình huống có thể khiến tôi hoảng sợ hoặc trở thành trò cười.",               dimension: "anxiety"    },
  { id: 10, text: "Tôi cảm thấy không có gì để mong đợi.",                                                            dimension: "depression" },
  { id: 11, text: "Tôi thấy bản thân dễ bị kích động.",                                                               dimension: "stress"     },
  { id: 12, text: "Tôi thấy khó thư giãn được.",                                                                      dimension: "stress"     },
  { id: 13, text: "Tôi cảm thấy chán nản, thất vọng.",                                                                dimension: "depression" },
  { id: 14, text: "Tôi không thể chịu đựng được bất cứ điều gì cản trở tôi hoàn thành việc đang làm.",               dimension: "stress"     },
  { id: 15, text: "Tôi cảm thấy sắp bị hoảng loạn.",                                                                  dimension: "anxiety"    },
  { id: 16, text: "Tôi không thể tìm thấy hứng thú, nhiệt tình với bất cứ điều gì.",                                  dimension: "depression" },
  { id: 17, text: "Tôi cảm thấy mình chẳng có giá trị gì với tư cách là một con người.",                              dimension: "depression" },
  { id: 18, text: "Tôi cảm thấy bản thân dễ bị tổn thương, dễ tức giận.",                                             dimension: "stress"     },
  { id: 19, text: "Tôi nhận thấy tim mình đập nhanh dù không vận động mạnh.",                                         dimension: "anxiety"    },
  { id: 20, text: "Tôi cảm thấy sợ hãi mà không có lý do rõ ràng.",                                                  dimension: "anxiety"    },
  { id: 21, text: "Tôi cảm thấy cuộc sống vô nghĩa.",                                                                 dimension: "depression" },
  { id: 22, text: "Tôi thấy bản thân khó có thể bình tĩnh lại sau khi gặp điều gì đó làm mình khó chịu.",            dimension: "stress"     },
  { id: 23, text: "Tôi bị đổ mồ hôi nhiều (ví dụ: tay đẫm mồ hôi) dù không nóng hay vận động.",                     dimension: "anxiety"    },
  { id: 24, text: "Tôi không thấy hứng thú, vui vẻ với bất cứ điều gì mình làm.",                                     dimension: "depression" },
  { id: 25, text: "Tôi cảm thấy bồn chồn, lo lắng.",                                                                  dimension: "anxiety"    },
  { id: 26, text: "Tôi cảm thấy không có giá trị gì.",                                                                dimension: "depression" },
  { id: 27, text: "Tôi cảm thấy rất khó chịu khi bị gián đoạn công việc.",                                            dimension: "stress"     },
  { id: 28, text: "Tôi cảm thấy sắp hoảng loạn.",                                                                     dimension: "anxiety"    },
  { id: 29, text: "Tôi thấy khó bình tĩnh lại sau khi gặp điều gì đó làm mình buồn.",                                dimension: "stress"     },
  { id: 30, text: "Tôi sợ rằng mình có thể bị 'tê liệt' bởi sự hoảng loạn.",                                         dimension: "anxiety"    },
  { id: 31, text: "Tôi không thể cảm thấy nhiệt tình với bất cứ điều gì.",                                            dimension: "depression" },
  { id: 32, text: "Tôi thấy khó chịu đựng sự gián đoạn.",                                                             dimension: "stress"     },
  { id: 33, text: "Tôi đang trong trạng thái căng thẳng thần kinh.",                                                   dimension: "stress"     },
  { id: 34, text: "Tôi cảm thấy mình chẳng có gì đáng mong đợi trong tương lai.",                                    dimension: "depression" },
  { id: 35, text: "Tôi thấy bản thân dễ bị kích động, cáu kỉnh.",                                                    dimension: "stress"     },
  { id: 36, text: "Tôi cảm thấy tim đập mạnh hoặc loạn nhịp.",                                                        dimension: "anxiety"    },
  { id: 37, text: "Tôi cảm thấy buồn và chán nản.",                                                                   dimension: "depression" },
  { id: 38, text: "Tôi thấy khó có thể tập trung.",                                                                   dimension: "depression" },
  { id: 39, text: "Tôi cảm thấy tức giận khi bị cản trở.",                                                            dimension: "stress"     },
  { id: 40, text: "Tôi cảm thấy lo lắng và bất an.",                                                                  dimension: "anxiety"    },
  { id: 41, text: "Tôi cảm thấy cuộc sống thật vô nghĩa và trống rỗng.",                                              dimension: "anxiety"    },
  { id: 42, text: "Tôi không thể cảm thấy nhiệt tình hoặc hứng khởi với bất cứ điều gì.",                            dimension: "depression" },
];

// Câu hỏi sàng lọc (6 câu đầu tiên được hỏi)
export const SCREENING_Q_IDS = [21, 10, 28, 7, 11, 8];

export const getScreeningQuestions = () =>
  DASS_QUESTIONS.filter(q => SCREENING_Q_IDS.includes(q.id))
    .sort((a, b) => SCREENING_Q_IDS.indexOf(a.id) - SCREENING_Q_IDS.indexOf(b.id));

export const getQuestionsByIds = (ids: number[]) =>
  DASS_QUESTIONS.filter(q => ids.includes(q.id))
    .sort((a, b) => a.id - b.id);

export const ANSWER_OPTIONS = [
  { value: 0, label: "Không bao giờ",       desc: "Không đúng với tôi chút nào",          key: "1" },
  { value: 1, label: "Thỉnh thoảng",        desc: "Đúng một phần, thỉnh thoảng xảy ra",  key: "2" },
  { value: 2, label: "Thường xuyên",        desc: "Đúng phần nhiều, phần lớn thời gian", key: "3" },
  { value: 3, label: "Rất thường xuyên",    desc: "Hoàn toàn đúng, hầu hết thời gian",   key: "4" },
];

export const YESNO_OPTIONS = [
  { value: "yes", label: "Có",   desc: "Tôi gặp tình trạng này",   key: "1" },
  { value: "no",  label: "Không", desc: "Tôi không thấy thế",       key: "2" },
];