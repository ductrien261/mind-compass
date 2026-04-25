export interface DassQuestion {
  id: number;
  text: string;
  dimension: "depression" | "anxiety" | "stress";
}

// Backward Question Types 

export type BackwardQuestionType = "yesno" | "multiselect";

export interface BackwardOption {
  value: string;
  label: string;
}

export interface BackwardQuestion {
  key: string;
  type: BackwardQuestionType;
  text: string;
  options?: BackwardOption[];   // chỉ có khi type = "multiselect"
  min_count?: number;           // ngưỡng để tính "pass"
  stop_if?: string;             // nếu trả lời = stop_if → dừng flow
  stop_reason?: string;
}

//  DASS-42

const DIM_MAP: Record<number, "depression" | "anxiety" | "stress"> = {
  3: "depression", 5: "depression", 10: "depression", 13: "depression",
  16: "depression", 17: "depression", 21: "depression", 24: "depression", 
  26: "depression", 31: "depression", 34: "depression", 37: "depression", 
  38: "depression", 42: "depression",
  2: "anxiety",  4: "anxiety",  7: "anxiety",  9: "anxiety",
  15: "anxiety", 19: "anxiety", 20: "anxiety", 23: "anxiety",
  25: "anxiety", 28: "anxiety", 30: "anxiety", 36: "anxiety",
  40: "anxiety", 41: "anxiety",
  1: "stress",  6: "stress",  8: "stress",  11: "stress",
  12: "stress", 14: "stress", 18: "stress", 22: "stress", 
  27: "stress", 29: "stress", 32: "stress", 33: "stress",
  35: "stress", 39: "stress",
};

export const DASS_QUESTIONS: DassQuestion[] = [
  { id: 1,  text: "Tôi thấy bản thân trở nên nhạy cảm quá mức trước những chuyện vặt vãnh, không đáng kể.",                   dimension: "stress"     },
  { id: 2,  text: "Tôi nhận thấy miệng mình bị khô.",                                                                         dimension: "anxiety"    },
  { id: 3,  text: "Tôi không cảm thấy có chút cảm xúc lạc quan, tích cực nào cả.",                                            dimension: "depression" },
  { id: 4,  text: "Tôi gặp tình trạng khó thở (như thở quá nhanh hoặc hụt hơi mà không do vận động thể chất).",               dimension: "anxiety"    },
  { id: 5,  text: "Tôi cứ thấy uể oải, không có chút động lực nào để bắt đầu.",                                               dimension: "depression" },
  { id: 6,  text: "Tôi có xu hướng phản ứng thái quá với các tình huống.",                                                    dimension: "stress"     },
  { id: 7,  text: "Tôi có cảm giác run rẩy (ví dụ: chân đứng không vững/sắp khuỵu xuống).",                                   dimension: "anxiety"    },
  { id: 8,  text: "Tôi thấy khó có thể thư giãn được.",                                                                       dimension: "stress"     },
  { id: 9,  text: "Tôi thấy lo lắng trong một số tình huống và chỉ thấy nhẹ người khi mọi chuyện xong xuôi.",                 dimension: "anxiety"    },
  { id: 10, text: "Tôi cảm thấy hiện tại mình chẳng còn điều gì để mong đợi hay chờ đón ở phía trước.",                       dimension: "depression" },
  { id: 11, text: "Tôi nhận thấy bản thân dễ bị kích động/buồn phiền hơn bình thường.",                                       dimension: "stress"     },
  { id: 12, text: "Tôi cảm thấy mình đang phải tiêu tốn quá nhiều sức lực để chống chọi với sự căng thẳng.",                  dimension: "stress"     },
  { id: 13, text: "Tôi cảm thấy buồn bã và chán nản.",                                                                        dimension: "depression" },
  { id: 14, text: "Tôi thấy mình dễ mất kiên nhẫn khi bị chậm trễ hoặc phải chờ đợi (ví dụ: chờ thang máy, đèn đỏ,....).",    dimension: "stress"     },
  { id: 15, text: "Tôi cảm thấy choáng váng, xây xẩm mặt mày, có cảm giác sắp ngất xỉu.",                                     dimension: "anxiety"    },
  { id: 16, text: "Tôi thấy mình không còn chút hứng thú nào với hầu hết mọi thứ.",                                           dimension: "depression" },
  { id: 17, text: "Tôi thấy mình là một người chẳng ra gì/không đáng giá.",                                                   dimension: "depression" },
  { id: 18, text: "Tôi cảm thấy mình khá là nhạy cảm/dễ tự ái.",                                                              dimension: "stress"     },
  { id: 19, text: "Tôi bị đổ mồ hôi bất thường (như đổ mồ hôi tay) mà không do tác động nhiệt hay gắng sức.",                 dimension: "anxiety"    },
  { id: 20, text: "Tôi cảm thấy sợ hãi mà không có lý do chính đáng nào.",                                                    dimension: "anxiety"    },
  { id: 21, text: "Tôi cảm thấy cuộc sống này không còn đáng sống nữa.",                                                      dimension: "depression" },
  { id: 22, text: "Tôi thấy khó thả lỏng mình sau khi làm việc/căng thẳng.",                                                  dimension: "stress"     },
  { id: 23, text: "Tôi cảm thấy bị nghẹn/vướng ở cổ họng khi nuốt.",                                                          dimension: "anxiety"    },
  { id: 24, text: "Tôi dường như không thể tìm thấy niềm vui trong những việc mình làm.",                                     dimension: "depression" },
  { id: 25, text: "Tôi nhận thấy nhịp tim bất thường dù không vận động nặng (ví dụ: tim đập nhanh, hẫng một nhịp).",          dimension: "anxiety"    },
  { id: 26, text: "Tôi thấy lòng nặng trĩu và u sầu.",                                                                        dimension: "depression" },
  { id: 27, text: "Tôi nhận thấy bản thân cực kỳ hay gắt gỏng.",                                                              dimension: "stress"     },
  { id: 28, text: "Tôi cảm thấy mình đã gần như hoảng loạn.",                                                                 dimension: "anxiety"    },
  { id: 29, text: "Tôi thấy khó lấy lại bình tĩnh sau khi gặp chuyện không vừa ý.",                                           dimension: "stress"     },
  { id: 30, text: "Tôi sợ bị mất phương hướng trước những việc nhỏ nhặt mà tôi chưa từng làm.",                               dimension: "anxiety"    },
  { id: 31, text: "Tôi không thể cảm thấy nhiệt tình hay hào hứng với bất cứ điều gì.",                                       dimension: "depression" },
  { id: 32, text: "Tôi thấy khó kiềm chế sự bực bội khi với việc bị ngắt quãng khi đang làm việc.",                           dimension: "stress"     },
  { id: 33, text: "Tôi luôn ở trong tình trạng căng thẳng thần kinh tột độ.",                                                 dimension: "stress"     },
  { id: 34, text: "Tôi thấy bản thân mình thật vô dụng.",                                                                     dimension: "depression" },
  { id: 35, text: "Tôi cảm thấy rất khó chịu với bất kỳ sự cản trở nào khiến tôi không thể hoàn thành việc mình đang làm.",   dimension: "stress"     },
  { id: 36, text: "Tôi có cảm giác kinh hãi/kinh hoàng.",                                                                     dimension: "anxiety"    },
  { id: 37, text: "Tôi cảm thấy tương lai mù mịt và không có chút hy vọng nào.",                                              dimension: "depression" },
  { id: 38, text: "Tôi cảm thấy cuộc đời mình hoàn toàn vô nghĩa.",                                                           dimension: "depression" },
  { id: 39, text: "Tôi nhận thấy mình dễ bị bồn chồn, đứng ngồi không yên.",                                                  dimension: "stress"     },
  { id: 40, text: "Tôi lo sợ mình sẽ mất bình tĩnh và hành xử ngớ ngẩn trong một số hoàn cảnh nhất định.",                    dimension: "anxiety"    },
  { id: 41, text: "Tôi thấy cơ thể bị run rẩy (ví dụ: run tay).",                                                             dimension: "anxiety"    },
  { id: 42, text: "Tôi thấy khó lòng thúc đẩy bản thân chủ động bắt tay vào làm việc gì đó.",                                 dimension: "depression" },
];

export const SCREENING_Q_IDS = [21, 10, 28, 7, 11, 8];

export const getScreeningQuestions = () =>
  DASS_QUESTIONS.filter(q => SCREENING_Q_IDS.includes(q.id))
    .sort((a, b) => SCREENING_Q_IDS.indexOf(a.id) - SCREENING_Q_IDS.indexOf(b.id));

export const getQuestionsByIds = (ids: number[]) =>
  DASS_QUESTIONS.filter(q => ids.includes(q.id))
    .sort((a, b) => a.id - b.id);

export const ANSWER_OPTIONS = [
  { value: 0, label: "Không bao giờ",    desc: "Không đúng với tôi chút nào",          key: "1" },
  { value: 1, label: "Thỉnh thoảng",     desc: "Đúng một phần, thỉnh thoảng xảy ra",  key: "2" },
  { value: 2, label: "Thường xuyên",     desc: "Đúng phần nhiều, phần lớn thời gian", key: "3" },
  { value: 3, label: "Rất thường xuyên", desc: "Hoàn toàn đúng, hầu hết thời gian",   key: "4" },
];

export const YESNO_OPTIONS = [
  { value: "yes", label: "Có",    desc: "Tôi gặp tình trạng này", key: "1" },
  { value: "no",  label: "Không", desc: "Tôi không thấy thế",     key: "2" },
];