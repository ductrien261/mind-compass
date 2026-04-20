import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

LABEL_NAMES = ['Bình thường', 'Nhẹ', 'Vừa', 'Nặng', 'Rất Nặng']

class DASSFuzzySystem:
    def __init__(self):
        self.systems = {
            'depression': self._build('depression', [0,0,9,10],[9,10,13,14],[13,14,20,21],[20,21,27,28],[27,28,42,42]),
            'anxiety':    self._build('anxiety',    [0,0,7,8],[7,8,9,10],[9,10,14,15],[14,15,19,20],[19,20,42,42]),
            'stress':     self._build('stress',     [0,0,14,15],[14,15,18,19],[18,19,25,26],[25,26,33,34],[33,34,42,42]),
        }

    def _build(self, name, norm, mild, mod, sev, ext):
        score = ctrl.Antecedent(np.arange(0, 43, 1), f'{name}_score') # 0-42
        level = ctrl.Consequent(np.arange(0, 4.1, 0.1), f'{name}_level') # 0-4

        means = {
            #              Normal  Mild   Mod   Sev   ExtSev
            'depression': [ 0,     11,    17,   24,   35],
            'anxiety':    [ 0,      8,    12,   17,   31],
            'stress':     [ 0,     16,    22,   29,   38],
        }
        m = means[name]

        # Khai báo các hàm liên thuộc Gauss
        score['normal']           = fuzz.gaussmf(score.universe, m[0], 7)
        score['mild']             = fuzz.gaussmf(score.universe, m[1], 3)
        score['moderate']         = fuzz.gaussmf(score.universe, m[2], 3)
        score['severe']           = fuzz.gaussmf(score.universe, m[3], 3)
        score['extremely_severe'] = fuzz.gaussmf(score.universe, m[4], 7)

        level['normal']           = fuzz.gaussmf(level.universe, 0.0, 0.5)
        level['mild']             = fuzz.gaussmf(level.universe, 1.0, 0.5)
        level['moderate']         = fuzz.gaussmf(level.universe, 2.0, 0.5)
        level['severe']           = fuzz.gaussmf(level.universe, 3.0, 0.5)
        level['extremely_severe'] = fuzz.gaussmf(level.universe, 4.0, 0.5)

        rules = [
            ctrl.Rule(score['normal'],           level['normal']),
            ctrl.Rule(score['mild'],             level['mild']),
            ctrl.Rule(score['moderate'],         level['moderate']),
            ctrl.Rule(score['severe'],           level['severe']),
            ctrl.Rule(score['extremely_severe'], level['extremely_severe']),
            ctrl.Rule(score['mild']     & score['moderate'], level['moderate']),
            ctrl.Rule(score['moderate'] & score['severe'],   level['severe']),
            ctrl.Rule(score['severe']   & score['extremely_severe'], level['extremely_severe']),
        ]

        sim = ctrl.ControlSystemSimulation(ctrl.ControlSystem(rules))
        return {'sim': sim, 'score_var': score, 'level_var': level}

    def evaluate(self, name, score_val):
        sim = self.systems[name]['sim']
        sim.input[f'{name}_score'] = score_val
        sim.compute()
        crisp = sim.output[f'{name}_level']

        if   crisp < 0.5: label_idx = 0
        elif crisp < 1.5: label_idx = 1
        elif crisp < 2.5: label_idx = 2
        elif crisp < 3.5: label_idx = 3
        else:             label_idx = 4

        return {
            'score': score_val,
            'fuzzy_value': round(float(crisp), 3),
            'label_idx': label_idx,
            'label': LABEL_NAMES[label_idx],
        }

    def analyze_all(self, d_score, a_score, s_score):
        """Hàm bọc lại để gọi API cho lẹ"""
        return {
            "depression": self.evaluate('depression', d_score),
            "anxiety": self.evaluate('anxiety', a_score),
            "stress": self.evaluate('stress', s_score)
        }

fuzzy_analyzer = DASSFuzzySystem()