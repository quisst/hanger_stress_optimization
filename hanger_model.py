import numpy as np

# Hanger의 형상에 맞는 D 계산 함수
def calculate_D(r, b, h, V):
    pi = np.pi
    
    # D^2 = 4V / (pi * (2b + h + (pi-2)r))
    numerator = 4 * V
    denominator = pi * ((2 * b) + h + (pi - 2) * r)
    
    if denominator <= 0:
        return None # 물리적으로 불가능
        
    D = np.sqrt(numerator / denominator)
    return D

# 제조 한계인 r = D/2 가 되는 지점의 r 값을 찾는 함수
def find_r_min_boundary(b, h, V):
    # V = (pi/4)D^2 * [2b + h + (pi-2)r] 모델에서 D=2r을 대입하여
    # pi*(pi-2)*r^3 + pi*(2b+h)*r^2 - V = 0 의 양의 실근을 찾기
    pi = np.pi
    
    # 3차 방정식의 계수
    a = pi * (pi - 2)
    b_coeff = pi * (2 * b + h)
    c = 0.0
    d = -V  # r=D/2 공식
    
    coefficients = [a, b_coeff, c, d]
    roots = np.roots(coefficients)
    
    real_roots = roots[np.isreal(roots)].real
    positive_real_root = real_roots[real_roots > 0]
    
    if len(positive_real_root) == 1:
        return positive_real_root[0]
    else:
        return None