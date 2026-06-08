#!/usr/bin/env python3
"""
FOC PI参数自动整定工具
根据电机基本参数计算电流环/速度环 PI 初始参数

用法：
  python foc_pi_tuner.py --R 1.23 --L 5.6e-3 --poles 8 --J 1e-3
  python foc_pi_tuner.py --mode interactive
  python foc_pi_tuner.py --R 2.1 --L 8e-3 --poles 6 --J 2e-3 --target_bw 150
"""

import argparse
import math
import sys

try:
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    HAS_PLOT = True
except ImportError:
    HAS_PLOT = False


def tune_current_loop(R, L, target_bw_hz=None, bandwidth_factor=0.5):
    """
    电流环 PI 整定

    目标：闭环带宽 ωbw = R/L × bandwidth_factor（典型 0.3~0.6）
    对于离散系统，还需考虑采样频率的影响

    参数:
        R: 相电阻 (Ω)
        L: 相电感 (H)
        target_bw_hz: 目标带宽 Hz（None=自动计算）
        bandwidth_factor: 带宽因子（默认0.5，即 ωbw≈R/(2L)）

    返回:
        dict: Kp, Ki, 带宽, 推荐采样频率
    """
    if target_bw_hz:
        omega_bw = 2 * math.pi * target_bw_hz
    else:
        omega_bw = R / L * bandwidth_factor

    # 连续域 PI 参数（直接综合）
    # 电流环传递函数：Gc(s) = Kp*(1 + 1/(Ki*s)) / (L*s + R)
    # 简化整定：使系统近似为一阶系统
    Kp = L * omega_bw          # 电感决定比例增益
    Ki = R / L                  # 电阻决定积分增益

    # 推荐采样频率（香农：>2倍信号带宽，建议 >10倍）
    f_sw_min = target_bw_hz * 20 if target_bw_hz else R / L * bandwidth_factor / math.pi * 5
    f_sw_rec = max(f_sw_min, 8000)  # 最低 8kHz

    # 离散化修正（双线性变换，Tustin）
    # 若实际采样频率已知，做后处理修正
    return {
        'Kp': Kp,
        'Ki': Ki,
        'omega_bw_rad_s': omega_bw,
        'bandwidth_hz': omega_bw / (2 * math.pi),
        'recommended_switching_freq_hz': f_sw_rec,
        'R_ohm': R,
        'L_H': L,
    }


def tune_speed_loop(J, Kt, current_bw_hz, target_speed_bw_hz=None, friction_Nm=0.0):
    """
    速度环 PI 整定

    目标：速度环带宽 ≈ 电流环带宽 / (5~20)，典型 10~30Hz
    经验公式：Kp_speed ≈ J * ωbw_speed，Ki_speed ≈ Kt * ωbw_speed / (J * ωe)

    参数:
        J: 转动惯量 (kg·m²)
        Kt: 转矩常数 (Nm/A)
        current_bw_hz: 电流环带宽 Hz
        target_speed_bw_hz: 目标速度环带宽 Hz（None=自动）
        friction_Nm: 摩擦转矩 (Nm)
    """
    # 速度环带宽建议为电流环的 1/10
    if target_speed_bw_hz is None:
        omega_cs = 2 * math.pi * current_bw_hz
        omega_ss = omega_cs / 10  # 速度环约为电流环1/10
        target_speed_bw_hz = omega_ss / (2 * math.pi)
    else:
        omega_ss = 2 * math.pi * target_speed_bw_hz

    # PI 参数
    Kp_speed = J * omega_ss
    # 积分时间常数 ≈ 机械时间常数 Tm = J*R / Kt^2（简化）
    # Ki_speed = Kp_speed / Tm（工程整定法）
    # 这里用经验法：Ki ≈ J / (5 * Tm) 近似
    Tm_estimate = J * 10 / Kt if Kt > 0.001 else 1.0  # 粗估机械时间常数 s
    Ki_speed = Kp_speed / (Tm_estimate * 5) if Tm_estimate > 0 else 0.01

    return {
        'Kp_speed': Kp_speed,
        'Ki_speed': Ki_speed,
        'speed_bw_hz': target_speed_bw_hz,
        'Tm_estimate_s': Tm_estimate,
        'J_kg_m2': J,
        'Kt_Nm_A': Kt,
    }


def discrete_correction(Kp, Ki, Ts, method='tustin'):
    """
    离散化 PI 参数修正

    参数:
        Kp, Ki: 连续域 PI 参数
        Ts: 采样周期 (s)
        method: 'tustin'（默认）, 'euler', 'backward'

    离散 PI 公式（位置式）：
      u[k] = u[k-1] + Kp*(e[k]-e[k-1]) + Ki*Ts*e[k]

    返回:
        dict: 离散化后的等效参数
    """
    if method == 'tustin':
        # Tustin 双线性变换
        Kp_d = Kp
        Ki_d = Ki * Ts / 2
    elif method == 'euler':
        # 前向 Euler（少用，稳定性差）
        Kp_d = Kp
        Ki_d = Ki * Ts
    else:
        # 后向 Euler
        Kp_d = Kp
        Ki_d = Ki * Ts

    return {
        'Kp_discrete': Kp_d,
        'Ki_discrete': Ki_d,
        'method': method,
        'Ts_s': Ts,
    }


def plot_bode(Kp, Ki, R, L, current_bw_hz, filename='foc_pi_bode.png'):
    """绘制电流环开环 Bode 图（近似）"""
    if not HAS_PLOT:
        return

    omega = np.logspace(0, 5, 500)  # 0.1 ~ 100k rad/s
    s = 1j * omega

    # PI 控制器
    Gc = Kp * (1 + 1 / (Ki * s))

    # 被控对象
    Gp = 1 / (L * s + R)

    # 开环传递函数
    Go = Gc * Gp

    mag = 20 * np.log10(np.abs(Go))
    phase = np.angle(Go, deg=True)

    plt.figure(figsize=(12, 8))

    # 幅值图
    plt.subplot(2, 1, 1)
    plt.semilogx(omega, mag, 'b-', linewidth=2)
    omega_bw = 2 * math.pi * current_bw_hz
    plt.axvline(x=omega_bw, color='r', linestyle='--', label=f'BW={current_bw_hz:.0f}Hz')
    plt.axhline(y=0, color='k', linewidth=0.5)
    plt.xlabel('Frequency (rad/s)')
    plt.ylabel('Magnitude (dB)')
    plt.title('Current Loop Open-Loop Bode Plot')
    plt.grid(True, which='both', alpha=0.3)
    plt.legend()

    # 相位图
    plt.subplot(2, 1, 2)
    plt.semilogx(omega, phase, 'b-', linewidth=2)
    plt.axvline(x=omega_bw, color='r', linestyle='--', label=f'BW={current_bw_hz:.0f}Hz')
    plt.xlabel('Frequency (rad/s)')
    plt.ylabel('Phase (deg)')
    plt.title('Phase Plot')
    plt.grid(True, which='both', alpha=0.3)
    plt.legend()

    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    print(f"[INFO] Bode图已保存: {filename}")


def format_output(cur, spd, dsc=None):
    out = f"""
{'='*60}
           FOC PI 参数整定结果
{'='*60}
【电机参数】
  相电阻 R      = {cur['R_ohm']:.4f} Ω
  相电感 L      = {cur['L_H']*1000:.2f} mH
  电流环带宽    = {cur['bandwidth_hz']:.1f} Hz
  推荐开关频率  = {cur['recommended_switching_freq_hz']:.0f} Hz

【电流环 PI 参数（连续域）】
  Kp_id = Kp_iq = {cur['Kp']:.6f}
  Ki_id = Ki_iq = {cur['Ki']:.2f}

  ※ 整定依据：ωbw = R/L × 0.5 = {cur['omega_bw_rad_s']:.1f} rad/s
  ※ 离散化后参数（见下）需根据实际采样周期 Ts 修正

【速度环 PI 参数（连续域）】
  目标速度带宽  = {spd['speed_bw_hz']:.1f} Hz
  机械时间常数  ≈ {spd['Tm_estimate_s']:.4f} s

  Kp_speed      = {spd['Kp_speed']:.6f}
  Ki_speed      = {spd['Ki_speed']:.6f}

{'='*60}
【使用指南】
  1. 初始加载以上参数
  2. 阶跃响应测试：超调 < 20% 为宜，过大则减小 Kp
  3. 稳态误差：观察静差，积分 Ki 不足则加大
  4. 电流振荡：带宽过高，减小 Kp 20%~50%
  5. 实际采样频率 > 10× 带宽频率
"""
    if dsc:
        out += f"""
【离散 PI 参数（{dsc['method']} 方法, Ts={dsc['Ts_s']*1e6:.0f}μs）】
  Kp_discrete = {dsc['Kp_discrete']:.6f}
  Ki_discrete = {dsc['Ki_discrete']:.6f}

  ※ 位置式离散 PI 实现：
    integral += Ki_discrete * error
    output   = Kp_discrete * error + integral
    (需做积分限幅，防止windup)
"""
    return out


def interactive_mode():
    print("\n" + "="*60)
    print("      FOC PI 参数整定工具（交互模式）")
    print("="*60)

    try:
        R = float(input("相电阻 R (Ω): ") or "1.23")
        L_mH = float(input("相电感 L (mH): ") or "5.6")
        L = L_mH / 1000
        poles = int(input("极数 (8): ") or "8")
        J = float(input("转动惯量 J (kg·m²): ") or "0.001")
        Kt = float(input("转矩常数 Kt (Nm/A): ") or "0.15")
        bw_extra = input("目标电流带宽 Hz（直接回车=自动）: ").strip()
        target_bw = float(bw_extra) if bw_extra else None
        Ts_us = input("采样周期 μs（直接回车=自动）: ").strip()
        Ts = float(Ts_us) * 1e-6 if Ts_us else 1 / 16000

        cur = tune_current_loop(R, L, target_bw)
        spd = tune_speed_loop(J, Kt, cur['bandwidth_hz'])
        dsc = discrete_correction(cur['Kp'], cur['Ki'], Ts)

        print(format_output(cur, spd, dsc))

        if HAS_PLOT:
            plot_bode(cur['Kp'], cur['Ki'], R, L, cur['bandwidth_hz'])

    except KeyboardInterrupt:
        print("\n已退出")


def main():
    parser = argparse.ArgumentParser(description='FOC PI 参数自动整定工具')
    parser.add_argument('--R', type=float, help='相电阻 Ω')
    parser.add_argument('--L', type=float, help='相电感 H（支持 5.6e-3 格式）')
    parser.add_argument('--L_mH', type=float, help='相电感 mH（与 --L 二选一）')
    parser.add_argument('--poles', type=int, default=8, help='极数')
    parser.add_argument('--J', type=float, default=1e-3, help='转动惯量 kg·m²')
    parser.add_argument('--Kt', type=float, default=0.15, help='转矩常数 Nm/A')
    parser.add_argument('--target_bw', type=float, help='目标电流环带宽 Hz')
    parser.add_argument('--speed_bw', type=float, help='目标速度环带宽 Hz')
    parser.add_argument('--Ts', type=float, help='采样周期 s')
    parser.add_argument('--Ts_us', type=float, help='采样周期 μs')
    parser.add_argument('--mode', default='calc', choices=['calc', 'interactive'])
    parser.add_argument('--plot', action='store_true', help='绘制Bode图')
    parser.add_argument('--output', type=str, help='输出文件前缀')

    args = parser.parse_args()

    if args.mode == 'interactive':
        interactive_mode()
        return

    # Auto-calculate L from mH if needed
    L = args.L
    if L is None and args.L_mH:
        L = args.L_mH / 1000

    if L is None:
        print("[ERROR] 必须提供 --L 或 --L_mH")
        sys.exit(1)

    R = args.R or 1.23
    Ts = args.Ts
    if Ts is None and args.Ts_us:
        Ts = args.Ts_us * 1e-6

    cur = tune_current_loop(R, L, args.target_bw)
    spd = tune_speed_loop(J=args.J, Kt=args.Kt,
                          current_bw_hz=cur['bandwidth_hz'],
                          target_speed_bw_hz=args.speed_bw)
    dsc = None
    if Ts:
        dsc = discrete_correction(cur['Kp'], cur['Ki'], Ts)

    print(format_output(cur, spd, dsc))

    if args.plot and HAS_PLOT:
        filename = args.output + '_bode.png' if args.output else 'foc_pi_bode.png'
        plot_bode(cur['Kp'], cur['Ki'], R, L, cur['bandwidth_hz'], filename)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        interactive_mode()
    else:
        main()
