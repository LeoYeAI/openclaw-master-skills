---
name: motor-foc-control
description: FOC磁场定向控制深度指南 | 深入讲解FOC原理、SVPWM、MTPA、弱磁控制、龙贝格观测器，配合实测案例、C代码和PI整定脚本
version: 2.1.0
tags: [foc, motor-control, svpwm, mtpa, flux-weakening, smo, pmsm, pmsm-control]
category: motor-engineering
---

# FOC 磁场定向控制深度指南 v2.1

面向电机工程实践，系统讲解 FOC 磁场定向控制的原理、实现、调参要点。
**新增：PI自动整定脚本、弱磁深度控制、故障诊断完整流程。**

## 目录

1. [FOC 基本原理](#foc-基本原理)
2. [SVPWM 原理与实现](#svpwm-原理与实现)
3. [MTPA（最大转矩电流比）控制](#mtpa最大转矩电流比控制)
4. [弱磁控制](#弱磁控制)
5. [磁链观测器](#磁链观测器)
6. [PI 参数整定指南](#pi-参数整定指南)
7. [工程参数速查](#工程参数速查)
8. [常见问题排查](#常见问题排查)
9. [参考资源](#参考资源)

---

## FOC 基本原理

### 坐标变换

```
三相静止坐标系 (ABC)
        ↓ Clarke 变换
两相静止坐标系 (α, β)
        ↓ Park 变换  
两相旋转坐标系 (d, q)

关键公式：
Clarke:  Iα = Ia
         Iβ = (Ia + 2Ib)/√3

Park:    Id = Iα·cos(θ) + Iβ·sin(θ)
         Iq = -Iα·sin(θ) + Iβ·cos(θ)

逆变换：
Iα = Id·cos(θ) - Iq·sin(θ)
Iβ = Id·sin(θ) + Iq·cos(θ)

三相重构：
Ia = Iα
Ib = -Iα/2 + Iβ·√3/2
Ic = -Iα/2 - Iβ·√3/2
```

### FOC 控制框图

```
        ┌──────────────────────────────────────────┐
        │                                          │
Iq_ref ──→ ┌────┐    ┌────┐    ┌────┐    ┌─────┐ │
           │ PI │───→│ SVPWM │──→│ 逆变器 │──→│ 电机 │ │
           └────┘    └────┘    └─────┘    │     │ │
           ↑ PI      ↑            ↑             │     │
Id_ref ───→┌────┐    │            │             ↓     ↓
           │ PI │────┘            │        ┌────────┐ │
           └────┘                 │        │ 三相输出 │ │
           ↑                      │        └────────┘ │
        0 ───→┌────┐             │             ↑       │
           ┌─→│ −ωLqIq │←───────┘             │       │
           │  └────┘                          │       │
      ┌────┐│                                 │       │
 θe ←│ PLL│←─────────────────────────────────┘       │
      └────┘                                          │
      (磁链观测器)                                      │
                                                     │
     ←←←←←← 转速环 ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
```

---

## SVPWM 原理与实现

### 空间矢量定义

```c
// 8个基本空间矢量（6个非零 + 2个零矢量）
// U0(000): 000, U1(100): 100, U2(110): 110, ...
// U3(010): 010, U4(011): 011, U5(001): 001
// U6(101): 101, U7(111): 111

typedef struct {
    float alpha;
    float beta;
} SpaceVector;

// 合成任意方向电压矢量
SpaceVector sv_ref = {
    .alpha = Uref * cos(theta_e),
    .beta  = Uref * sin(theta_e)
};
```

### SVPWM 扇区判断

```c
// 判断参考电压矢量所在扇区
int sv_sector(SpaceVector *sv) {
    float a = sv->beta;
    float b = sv->alpha * 0.866 - sv->beta * 0.5;
    float c = -sv->alpha * 0.866 - sv->beta * 0.5;

    int N = 0;
    if (a > 0) N |= 1;
    if (b > 0) N |= 2;
    if (c > 0) N |= 4;

    // N → 扇区号 (1~6)
    const int sector_table[8] = {0, 2, 6, 1, 4, 3, 5, 0};
    return sector_table[N];
}
```

### SVPWM 时间计算

```c
// 在扇区 k 中，计算相邻矢量作用时间
// T0 = (T - Ta - Tb) / 2
// Ta, Tb 根据扇区查表

typedef struct {
    float Ualpha;
    float Ubeta;
    float T;        // PWM周期
    float Udc;      // 母线电压
} SVPWM_Handle;

void svpwm_calc(SVPWM_Handle *h, float *Ta, float *Tb) {
    float X = h->Ubeta;
    float Y = h->Ualpha * 0.866 + h->Ubeta * 0.5;
    float Z = -h->Ualpha * 0.866 + h->Ubeta * 0.5;

    int sector = sv_sector((SpaceVector*)h);

    switch(sector) {
        case 1: *Ta = Z; *Tb = Y; break;
        case 2: *Ta = Y; *Tb = -X; break;
        case 3: *Ta = -Z; *Tb = X; break;
        case 4: *Ta = -X; *Tb = Z; break;
        case 5: *Ta = X; *Tb = -Y; break;
        case 6: *Ta = -Y; *Tb = -Z; break;
    }

    // 过调制处理
    float T_sum = *Ta + *Tb;
    if (T_sum > h->T) {
        *Ta = *Ta * h->T / T_sum;
        *Tb = *Tb * h->T / T_sum;
    }

    // 零矢量分配（7段式对称PWM）
    float T0 = (h->T - *Ta - *Tb) / 2;
    float T7 = T0;

    // 计算三相占空比
    // DPA, DPB, DPC 存入比较寄存器
}
```

### 占空比计算（7段式对称SVPWM）

```c
// 各扇区占空比计算
// Tcm1, Tcm2, Tcm3 → 对应 ABC 三相比较值

void svpwm_duty(SVPWM_Handle *h, float *Tcm) {
    float Ta, Tb;
    svpwm_calc(h, &Ta, &Tb);
    float T0 = (h->T - Ta - Tb) / 2;

    int sector = sv_sector((SpaceVector*)h);

    switch(sector) {
        case 1:  // U4(100), U6(110), U0(000)
            Tcm[0] = (h->T + Ta + Tb) / 2;  // A: 先断后通
            Tcm[1] = (h->T - Ta + Tb) / 2;  // B
            Tcm[2] = (h->T - Ta - Tb) / 2;  // C
            break;
        case 2:  // U6(110), U2(010), U0(000)
            Tcm[0] = (h->T - Ta + Tb) / 2;
            Tcm[1] = (h->T + Ta + Tb) / 2;
            Tcm[2] = (h->T - Ta - Tb) / 2;
            break;
        case 3:  // U2(010), U3(011), U0(000)
            Tcm[0] = (h->T - Ta - Tb) / 2;
            Tcm[1] = (h->T + Ta + Tb) / 2;
            Tcm[2] = (h->T + Ta - Tb) / 2;
            break;
        case 4:  // U3(011), U1(001), U0(000)
            Tcm[0] = (h->T - Ta - Tb) / 2;
            Tcm[1] = (h->T - Ta + Tb) / 2;
            Tcm[2] = (h->T + Ta + Tb) / 2;
            break;
        case 5:  // U1(001), U5(101), U0(000)
            Tcm[0] = (h->T + Ta - Tb) / 2;
            Tcm[1] = (h->T - Ta - Tb) / 2;
            Tcm[2] = (h->T + Ta + Tb) / 2;
            break;
        case 6:  // U5(101), U4(100), U0(000)
            Tcm[0] = (h->T + Ta + Tb) / 2;
            Tcm[1] = (h->T - Ta - Tb) / 2;
            Tcm[2] = (h->T + Ta - Tb) / 2;
            break;
    }
}
```

---

## MTPA（最大转矩电流比）控制

### 原理

对于内嵌式 PMSM（IPMSM），存在 d轴磁阻转矩，利用 MTPA 可在相同电流下获得更大转矩。

```
电磁转矩方程：
T = 1.5 × np × [Ψm × Iq + (Ld - Lq) × Id × Iq]

定义电流幅值：
|I| = √(Id² + Iq²)

MTPA 轨迹：固定 |I|，寻找使 T 最大的 (Id, Iq) 组合
```

### MTPA 数学推导

```
令 ∂T/∂Id = 0，约束条件 |I| = constant

拉格朗日函数：L = T - λ(√(Id²+Iq²) - I_ref)

∂L/∂Id = 1.5×np×[(Ld-Lq)×Iq] - λ×Id/|I| = 0
∂L/∂Iq = 1.5×np×[Ψm + (Ld-Lq)×Id] - λ×Iq/|I| = 0

联立求解（化简后）：

Id_MTPA = -(Ψm / (2×ΔL)) + √[(Ψm/(2ΔL))² + Iq²]

其中 ΔL = Lq - Ld > 0

当 ΔL 很小时（表贴式），Id_MTPA ≈ 0 → 退化为 Id=0 控制
```

### MTPA 实现

```c
// MTPA 查表法（实时性最好）
// 预计算 MTPA 曲线，运行时查表 + 线性插值

static const float mtpa_table_Iq[] = {
    0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 15.0, 18.0, 20.0
};
static const float mtpa_table_Id[] = {
    0.0, -0.5, -1.1, -1.8, -2.5, -3.2, -4.0, -5.3, -6.6, -7.8
};

float mtpa_interpolate(float Iq) {
    int n = sizeof(mtpa_table_Iq) / sizeof(mtpa_table_Iq[0]);
    // 边界
    if (Iq <= mtpa_table_Iq[0]) return mtpa_table_Id[0];
    if (Iq >= mtpa_table_Iq[n-1]) return mtpa_table_Id[n-1];
    // 查表
    for (int i = 0; i < n-1; i++) {
        if (Iq >= mtpa_table_Iq[i] && Iq < mtpa_table_Iq[i+1]) {
            float t = (Iq - mtpa_table_Iq[i]) /
                       (mtpa_table_Iq[i+1] - mtpa_table_Iq[i]);
            return mtpa_table_Id[i] + t * (mtpa_table_Id[i+1] - mtpa_table_Id[i]);
        }
    }
    return 0;
}

// MTPA 解析公式法（适合在线计算）
float mtpa_Id_formula(float Iq, float Psi_m, float Ld, float Lq) {
    float delta_L = Lq - Ld;
    if (delta_L < 1e-6) return 0;  // 表贴式，无 MTPA 效益

    float k = Psi_m / (2.0f * delta_L);
    float Id = -k + sqrtf(k * k + Iq * Iq);
    return -Id;  // Id 必须为负（去磁）
}
```

---

## 弱磁控制

### 原理

当转速超过基速时，反电动势 E > Vdc，电压饱和。弱磁通过增加 Id（去磁电流）来降低有效磁链，从而在恒功率区扩展转速。

```
电压极限椭圆（d-q 平面）：
Vd² + Vq² ≤ Vdc² / 2   （SVPWM线性调制区最大输出）

反电动势约束：
V = ω_e × (Ψm - Ld×Id)  ≈ ω_e × Ψm_eff

弱磁的本质：在电压极限椭圆内重新分配 Id、Iq
```

### 弱磁深度等级

| 等级 | Id 比例 | 适用转速范围 | 特性 |
|------|---------|------------|------|
| 轻度弱磁 | -0.3×Imax | 1~1.5× 基速 | 转矩下降少 |
| 中度弱磁 | -0.5×Imax | 1.5~2× 基速 | 恒功率区主力 |
| 深度弱磁 | -0.7×Imax | 2~3× 基速 | 转矩大幅下降 |
| 六步方波 | 全部去磁 | >3× 基速 | 最大转速，扭矩波动大 |

### 弱磁控制器实现

```c
typedef enum {
    MTPA_MODE,         // 最大转矩电流比
    FW_MODE,            // 弱磁模式
    SIXSTEP_MODE        // 六步方波
} FluxMode;

typedef struct {
    float Vdc;          // 母线电压
    float V_lim;        // 电压极限（Vdc/sqrt(2)）
    float V_th;         // 弱磁启动阈值（建议 0.9×V_lim）
    float Id_fw_min;    // 最大去磁电流（负值）
    float gamma;         // 弱磁PI积分系数
    float Kp_fw;        // 弱磁比例增益
    float Ki_fw;        // 弱磁积分增益
} FluxWeaken_Handle;

void flux_weaken_update(FluxWeaken_Handle *h,
                        float V_mag, float Id_ref,
                        float *Id_fw_out) {
    // V_mag = sqrt(Vd² + Vq²)
    // Id_ref = MTPA 给定的 Id

    static float integral = 0;
    float error = V_mag - h->V_lim * 0.95;  // 提前 5% 介入

    if (error > 0) {
        // 电压饱和，启动弱磁
        integral += h->gamma * error;
        integral = fminf(integral, 0);  // Id_fw 为负，积分限幅
        *Id_fw_out = h->Id_fw_min;       // 直接给最大去磁
    } else {
        // 电压裕量足够，逐渐减小弱磁
        integral *= 0.95;  // 缓慢衰减
        *Id_fw_out = Id_ref + integral;
    }

    // 与 MTPA 叠加
    *Id_fw_out = fmaxf(*Id_fw_out, h->Id_fw_min);
}
```

### 弱磁调度逻辑

```c
float select_Id_ref(float Id_MTPA, float Id_FW, float V_mag,
                    float V_lim, float speed) {
    float Id_ref;

    if (V_mag < V_lim * 0.85) {
        // 电压充裕，MTPA 控制
        Id_ref = Id_MTPA;
    } else if (V_mag < V_lim * 0.95) {
        // 电压接近饱和，过渡区
        float alpha = (V_mag - V_lim * 0.85) / (V_lim * 0.1);
        Id_ref = Id_MTPA + alpha * (Id_FW - Id_MTPA);
    } else {
        // 深度弱磁
        Id_ref = Id_FW;
    }

    return Id_ref;
}
```

---

## 磁链观测器

### 滑模观测器（SMO）估测转子位置

```c
typedef struct {
    float I_alpha;
    float I_beta;
    float Ia;
    float Ib;
    float Ic;
    float R;
    float L;
    float emf_alpha;
    float emf_beta;
    float angle;
    float speed;
    float prev_angle;
    float k_gain;       // 滑模增益
    float filter_bw;     // 低通截止频率 rad/s
} SMO_Handle;

// sign 函数（连续近似，避免抖振）
float sign_f(float x, float delta) {
    if (x > delta)  return 1.0f;
    if (x < -delta) return -1.0f;
    return x / delta;  // |x|<delta: 线性近似
}

#define K_SMO 0.5f    // 滑模增益（过大=抖振，过小=延迟）

void smo_update(SMO_Handle *smo, float V_alpha, float V_beta,
               float Ia, float Ib, float Ic, float dt) {

    float e_alpha = smo->I_alpha - Ia;
    float e_beta  = smo->I_beta  - Ib;

    // 滑模控制量
    float z_alpha = smo->k_gain * sign_f(e_alpha, 0.05f);
    float z_beta  = smo->k_gain * sign_f(e_beta,  0.05f);

    // 电流更新（欧拉法）
    smo->I_alpha += dt * (-smo->R * Ia + V_alpha - z_alpha) / smo->L;
    smo->I_beta  += dt * (-smo->R * Ib + V_beta  - z_beta ) / smo->L;

    // 反电动势提取（低通滤波）
    float alpha_lpf = 2.0f * M_PI * smo->filter_bw;
    smo->emf_alpha += dt * alpha_lpf * (z_alpha - smo->emf_alpha);
    smo->emf_beta  += dt * alpha_lpf * (z_beta  - smo->emf_beta);

    // 角度提取
    smo->angle = atan2f(smo->emf_alpha, -smo->emf_beta);

    // 速度计算（微分）
    float d_angle = smo->angle - smo->prev_angle;
    // 角度归一化（处理 -π 到 +π 跳变）
    if (d_angle > M_PI)  d_angle -= 2.0f * M_PI;
    if (d_angle < -M_PI) d_angle += 2.0f * M_PI;
    smo->speed = d_angle / dt;
    smo->prev_angle = smo->angle;
}
```

### PLL（锁相环）角度提取

```c
// 对 SMO 估算的反电动势做 PLL
// emf_d = -ω_e × Ψm × sin(Δθ) ≈ -ω_e × Ψm × Δθ（小角度时）
// emf_q =  ω_e × Ψm × cos(Δθ) ≈  ω_e × Ψm

typedef struct {
    float Kp;
    float Ki;
    float integral;
    float angle;
    float speed;
    float lock_threshold;  // 锁定阈值 rad/s
    int   locked;         // 锁定标志
} PLL_Handle;

void pll_update(PLL_Handle *pll, float emf_d, float emf_q, float dt) {
    // d轴反电动势应接近0（正确对齐时）
    // q轴反电动势 = ω_e × Ψm

    float error = emf_d;  // PLL 误差

    // PI 积分
    pll->integral += pll->Ki * error * dt;
    // 积分限幅
    pll->integral = fmaxf(fminf(pll->integral, 1000.0f), -1000.0f);

    pll->speed = pll->Kp * error + pll->integral;
    pll->angle += pll->speed * dt;

    // 角度归一化 0~2π
    while (pll->angle < 0)      pll->angle += 2.0f * M_PI;
    while (pll->angle > 2.0f*M_PI) pll->angle -= 2.0f * M_PI;

    // 锁定判断
    if (fabsf(error) < pll->lock_threshold && fabsf(pll->speed) > 10.0f) {
        pll->locked = 1;
    }
}
```

---

## PI 参数整定指南

### 自动整定脚本

```bash
# 自动计算 PI 参数
python scripts/foc_pi_tuner.py --R 1.23 --L 5.6e-3 --J 1e-3 --Kt 0.15

# 交互模式（引导输入）
python scripts/foc_pi_tuner.py --mode interactive

# 指定目标带宽
python scripts/foc_pi_tuner.py --R 2.1 --L 8e-3 --target_bw 150

# 指定采样周期 + 生成Bode图
python scripts/foc_pi_tuner.py --R 1.23 --L 5.6e-3 --Ts_us 62.5 --plot
```

### 电流环整定

```
目标：带宽 ωbw = R/L × 0.5（典型因子 0.3~0.6）

Kp = L × ωbw
Ki = R / L

示例：
R = 1.23Ω, L = 5.6mH, ωbw = 1.23/0.0056 × 0.5 ≈ 110 rad/s
Kp = 0.0056 × 110 ≈ 0.616
Ki = 1.23/0.0056 ≈ 220 (需根据 Ts 离散化修正)
```

### 速度环整定

```
目标：带宽 ≈ 电流环带宽 / 10

Kp_speed ≈ J × ωbw_speed
Ki_speed ≈ Kp_speed / Tm

示例：
J = 0.001 kg·m²
ωbw_speed = 11 rad/s (电流环1/10)
Kp_speed = 0.001 × 11 = 0.011
Tm = J × R / Kt² = 0.001 × 1.23 / 0.15² ≈ 0.055 s
Ki_speed = 0.011 / 0.055 ≈ 0.2
```

### 离散化修正（Tustin 方法）

```
给定采样周期 Ts：
Kp_d = Kp
Ki_d = Ki × Ts / 2

示例：Ts = 62.5μs (16kHz)
Ki_d = 220 × 31.25e-6 = 0.006875

实现（位置式）：
  integral += Ki_d × error
  output   = Kp_d × error + integral
  限幅：output ∈ [-Vmax, Vmax]
```

---

## 工程参数速查

> 详见 `references/foc-quick-ref.md`

| 参数 | 典型值 | 说明 |
|------|--------|------|
| 电流环带宽 | 100~500 Hz | 转速决定上限 |
| 速度环带宽 | 10~50 Hz | 电流环的1/5~1/10 |
| 开关频率 | 8~25 kHz | 载波比 >100 |
| 死区时间 | 200~800 ns | 电压越高，死区越大 |
| 电流采样延迟 | ≤1×Ts | 影响带宽 |
| 编码器分辨率 | ≥2500线 | 直接影响角度精度 |
| PWM分辨率 | ≥11-bit | 决定电流精度 |

---

## 常见问题排查

| 现象 | 原因 | 解决 |
|------|------|------|
| 启动抖动 | 初始角度错误/Hall错位 | 检查初始角校准程序 |
| 高速失步 | 弱磁不足/电压裕量不足 | 增强弱磁，提高Vdc |
| 低速蠕动 | 编码器分辨率低/速度环带宽低 | 提高速度环带宽，更换编码器 |
| 电流振荡 | 电流环带宽过高/采样延迟大 | 减小 Kp，减小 Ts |
| 温升快 | 铜损过高/换向重叠角小 | 检查开关死区，降低电流 |
| 振动噪音 | PWM载波比低/共振频率激发 | 提高PWM频率，加陷波滤波 |
| 反电动势波形畸变 | 磁钢充磁不均/磁饱和 | Maxwell仿真确认 |
| 启动转速超调 | 速度环积分Windup | 加积分清零/抗积分饱和 |
| 换向时有台阶 | Hall传感器滞后/角度误差 | 检查Hall安装相位 |

### 调试流程图

```
启动抖动？
├─ 初始角度问题 → 重新做初始角辨识（脉冲法/预定位）
├─ Hall错位 → 校正Hall安装位置
└─ 电流环带宽不足 → 提高电流环 Kp

高速失步？
├─ 弱磁不足 → 增强 Id_fw，验证 V_mag > 0.95×V_lim
├─ 母线电压不足 → 提高 Vdc 或加升压
└─ 反电动势估算错误 → 检查速度观测器

振动噪音？
├─ 开关频率共振 → 提高PWM频率或加RC吸收
├─ 机械共振 → 加陷波滤波器
└─ 电流纹波大 → 提高开关频率或加电感
```

---

## 参考资源

- `scripts/foc_pi_tuner.py` - **PI参数自动整定脚本**（推荐优先使用）
- `references/foc-quick-ref.md` - **FOC工程参数速查卡**（典型值、阈值速查）
- `references/pm-materials.md` - 永磁体牌号参数表（可选扩展）

### 快速使用 PI 整定

```bash
# 完整参数计算（自动输出离散PI参数）
python scripts/foc_pi_tuner.py --R 1.23 --L 5.6e-3 --poles 8 --J 1e-3 --Kt 0.15 --Ts_us 62.5

# 绘制 Bode 图（验证稳定性）
python scripts/foc_pi_tuner.py --R 1.23 --L 5.6e-3 --plot

# 对比不同带宽参数
python scripts/foc_pi_tuner.py --R 2.1 --L 8e-3 --target_bw 80
python scripts/foc_pi_tuner.py --R 2.1 --L 8e-3 --target_bw 200
```

> **注意**：脚本输出为理论初始值，实际需在电机上微调。调试顺序：电流环→速度环→位置环，逐级验证带宽和稳定性。
