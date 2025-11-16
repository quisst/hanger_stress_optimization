import matplotlib.pyplot as plt

def plot_results(results, mass_kg, b_const, h_const, best_r, best_D, best_stress):
    # GSS 시뮬레이션 결과를 Matplotlib 그래프로 시각화
    print("")
    print("결과 그래프를 생성합니다...")
    
    r_plot = [res[0] for res in results]
    d_plot = [res[1] for res in results]
    stress_plot = [res[2] for res in results]
    
    fig, ax1 = plt.subplots(figsize=(12, 7))

    # 1. 응력 그래프 (Stress) - Y축1
    color = 'tab:red'
    ax1.set_xlabel('r (mm)', fontsize=14)
    ax1.set_ylabel('Max Stress (MPa)', color=color, fontsize=14)
    ax1.plot(r_plot, stress_plot, 'o-', color=color, label='Max Stress (MPa)')
    ax1.tick_params(axis='y', labelcolor=color, labelsize=12)
    ax1.tick_params(axis='x', labelsize=12)
    
    # 2. 직경 그래프 (Diameter) - Y축2
    ax2 = ax1.twinx() # Y축 공유
    color = 'tab:blue'
    ax2.set_ylabel('D (mm)', color=color, fontsize=14)
    ax2.plot(r_plot, d_plot, 's--', color=color, label='Diameter (mm)')
    ax2.tick_params(axis='y', labelcolor=color, labelsize=12)
    
    # 3. 최적점 표시 및 텍스트 출력
    # 마커 찍기
    ax1.plot(best_r, best_stress, 'D', color='magenta', markersize=12, label='Optimal Point')
    
    # 마커 옆에 텍스트 달기
    info_text = f' Optimal Point\n r = {best_r:.2f} mm\n D = {best_D:.2f} mm\n Stress = {best_stress:.2f} MPa'
    
    ax1.annotate(info_text, 
                 xy=(best_r, best_stress),
                 xytext=(0, 40),
                 textcoords='offset points',
                 fontsize=12,
                 color='black',
                 fontweight='bold',
                 bbox=dict(boxstyle="round,pad=0.5", fc="white", ec="magenta", alpha=0.9),
                 arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0", color='magenta'))
    
    # 제목 및 범례
    fig.suptitle(f'GSS Optimization Results (m={mass_kg}kg, b={b_const}mm, h={h_const}mm)', fontsize=16)
    fig.tight_layout()
    
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper right', fontsize=12)
    
    plt.grid(True)
    plt.show()