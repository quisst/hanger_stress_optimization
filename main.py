import numpy as np
import pandas as pd

from hanger_model import calculate_D, find_r_min_boundary
from plotter import plot_results

# 사용자에게 Fusion 360 시뮬레이션 값을 입력받는 함수
def get_simulation_stress(r, D):
    print("-" * 40)
    print(f"다음 값으로 Fusion 360 시뮬레이션을 진행하세요: ")
    print(f"r = {r:.4f} mm")
    print(f"D = {D:.4f} mm")

    while True:
        try:
            # 폰 미세스 응력의 최대값을 입력
            stress = float(input(f"-> 시뮬레이션 결과(최대 폰 미세스 응력, MPa)를 입력하세요: "))
            return stress
        except ValueError:
            print("숫자를 입력해야 합니다.")
            print("다시 입력해주세요.")

# 새로운 점 추가 전 중복 확인
def add_result(results, r_val, D_val, stress_val):
    if not any(np.isclose(r_val, r, atol=1e-6) for r, _, _ in results):
        results.append((r_val, D_val, stress_val))

# 메인 실행 코드 (GGS 사용)
def main():
    # 1. 기본 파라미터 설정
    # (단위: mm, kg, N, MPa 기준)
    print("--- 1. 기본 고정값 입력 ---")
    b_const = float(input("고정할 b (수평 팔 길이, mm) 값을 입력하세요: "))
    h_const = float(input("고정할 h (수직 팔 길이, mm) 값을 입력하세요: "))
    mass_kg = float(input("고정할 m (총 질량, kg) 값을 입력하세요: "))

    # 밀도는 재료(구조용 강)에 따라 고정
    density_kg_mm3 = 7.85e-6  # 구조용 강의 밀도 (kg/mm^3)
    V_const = mass_kg / density_kg_mm3  # 총 부피 (mm^3)

    print(f"b={b_const} mm, h={h_const} mm")
    print(f"m={mass_kg} kg (V={V_const:.4f} mm^3)")

    # --- 2. GSS 검색 범위 설정 ---
    print("")
    print("--- 2. GSS 탐색 범위 계산 ---")

    # r=D/2가 되는 지점을 최소 경계로 사용
    r_min_boundary = find_r_min_boundary(b_const, h_const, V_const)

    # r=h/2가 되는 지점을 최대 경계로 사용
    r_max_boundary = h_const / 2

    if r_max_boundary is None or r_max_boundary <= r_min_boundary:
        print("r=h/2가 되는 지점을 찾을 수 없거나 r_min_boundary보다 작습니다.")
        print("b, h, V 값을 확인하고 다시 시도하세요.")
        return

    print(f"GSS 검색 범위: r = [{r_min_boundary:.4f} mm] ~ [{r_max_boundary:.4f} mm]")

    a = r_min_boundary
    b = r_max_boundary

    # --- 3. GSS 알고리즘 초기화 ---
    print("")
    print("--- 3. GSS 초기값 계산 (2회 시뮬레이션 필요) ---")
    phi = (1 + np.sqrt(5)) / 2

    # 초기 두 테스트 지점 (d, c) 계산
    # a---d---c---b
    d = b - (b - a) / phi
    c = a + (b - a) / phi

    # 두 지점의 D 값 계산
    D_c = calculate_D(c, b_const, h_const, V_const)
    D_d = calculate_D(d, b_const, h_const, V_const)

    # 두 지점의 시뮬레이션 값 입력받기
    stress_c = get_simulation_stress(c, D_c)
    stress_d = get_simulation_stress(d, D_d)

    # 결과 저장을 위한 리스트
    results = [(c, D_c, stress_c), (d, D_d, stress_d)]

    # --- 4. 자동 종료 조건 설정 ---
    tolerance = 50.0  # 임의의 값
    print("")
    print(f"GSS 자동 종료 r 구간 너비(tolerance)를 {tolerance:.2f} mm로 설정합니다.")

    print("")
    print(f"--- 4. GSS 메인 루프 시작 (구간 너비가 {tolerance} 보다 작아질 때까지 반복) ---")

    iteration_count = 0

    while (b - a) > tolerance:
        iteration_count += 1
        print(f"--- Iteration {iteration_count} (현재 구간 너비: {(b-a):.4f}) ---")

        # d = 왼쪽 점, c = 오른쪽 점
        # stress_c = f(c) (오른쪽 값), stress_d = f(d) (왼쪽 값)

        if stress_c < stress_d:
            # f(오른쪽) < f(왼쪽) -> 최적점은 오른쪽 구간 [d, b]에 있음
            # 새 구간의 왼쪽 경계(a)를 d로 업데이트
            a = d
            # 기존의 오른쪽 점(c)이 새 구간의 왼쪽 점(d)이 됨
            d = c
            stress_d = stress_c
            # 새 구간 [d, b]의 오른쪽 점(c)을 새로 계산
            c = a + (b - a) / phi
            # 새로 계산한 c만 시뮬레이션
            D_c = calculate_D(c, b_const, h_const, V_const)
            stress_c = get_simulation_stress(c, D_c)
            add_result(results, c, D_c, stress_c)

        else:
            # f(오른쪽) >= f(왼쪽) -> 최적점은 왼쪽 구간 [a, c]에 있음
            # 새 구간의 오른쪽 경계(b)를 c로 업데이트
            b = c
            # 기존의 왼쪽 점(d)이 새 구간의 오른쪽 점(c)이 됨
            c = d
            stress_c = stress_d
            # 새 구간 [a, c]의 왼쪽 점(d)을 새로 계산
            d = b - (b - a) / phi
            # 새로 계산한 d만 시뮬레이션
            D_d = calculate_D(d, b_const, h_const, V_const)
            stress_d = get_simulation_stress(d, D_d)
            add_result(results, d, D_d, stress_d)

        print(f"현재 탐색 구간: r = [{a:.4f}] ~ [{b:.4f}]")

    print("=" * 40)
    print("GSS 탐색 완료")

    # --- 5. 결과 행렬식 출력 ---
    print("")
    print("--- 시뮬레이션 결과 행렬 (r 오름차순 정렬) ---")

    # 결과를 r 기준으로 정렬
    results.sort(key=lambda x: x[0])
    print(f"{'#':<4} | {'r (mm)':>12} | {'D (mm)':>12} | {'Stress (MPa)':>15}")
    print("-" * 49)
    for i, (r_val, d_val, stress_val) in enumerate(results):
        print(f"{i+1:<4} | {r_val:>12.4f} | {d_val:>12.4f} | {stress_val:>15.4f}")

    # --- 6. 최종 결과 분석 ---
    # 모든 results 중에서 가장 낮은 응력 찾기
    best_result = min(results, key=lambda x: x[2])
    best_r, best_D, best_stress = best_result

    print("")
    print("--- 최종 최적점 ---")
    print(f"[질량 {mass_kg} kg] 기준,")
    print(f"최적의 r = {best_r:.4f} mm")
    print(f"최적의 D = {best_D:.4f} mm")
    print(f"최소 응력 = {best_stress:.4f} MPa")

    # --- 7. 결과 plot ---
    plot_results(results, mass_kg, b_const, h_const, best_r, best_D, best_stress)

    # --- 8. 결과 파일로 저장 ---
    try:
        # 파일 이름 만들기
        filename = f'gss_results_m{mass_kg}kg_b{b_const}mm_h{h_const}mm.csv'
        
        # pandas DataFrame으로 변환
        df = pd.DataFrame(results, columns=['r (mm)', 'D (mm)', 'Stress (MPa)'])
        
        # CSV 파일로 저장
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n결과가 {filename} 에 저장되었습니다.")
        
    except Exception as e:
        print(f"\nCSV 파일 저장에 실패했습니다: {e}")
        print("pandas 라이브러리가 설치되어 있는지 확인하세요. (pip install pandas)")


if __name__ == "__main__":
    main()