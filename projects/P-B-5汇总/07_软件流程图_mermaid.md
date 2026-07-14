# 软件流程图（Mermaid 版）

## 图一：主程序流程 (main)

```mermaid
flowchart TD
    A([开始]) --> B[SystemInit]
    B --> C[Timer0Init]
    C --> D{g_tick2ms != 0?}
    D -- 是 --> E[g_tick2ms--]
    E --> F[SystemTick2ms]
    F --> G{g_oledDue != 0?}
    D -- 否 --> G
    G -- 是 --> H[g_oledDue = 0]
    H --> I[OLED_UpdateScreen]
    I --> D
    G -- 否 --> D
```

---

## 图二：系统 2ms 时基处理 (SystemTick2ms)

```mermaid
flowchart TD
    A([进入 SystemTick2ms]) --> B[g_keyTicks++]
    B --> C{keyTicks >= 5?}
    C -- 是 --> D[keys = KeyScan]
    D --> E{keys != 0?}
    E -- 是 --> F[HandleKeys keys]
    E -- 否 --> G{g_night?}
    F --> G
    C -- 否 --> G
    G -- 是 --> H[g_flashTicks++]
    H --> I{flashTicks >= 250?}
    I -- 是 --> J[g_flashOn 翻转]
    I -- 否 --> K{!emergency && !night?}
    J --> K
    G -- 否 --> K
    K -- 是 --> L[g_secondTicks++]
    L --> M{secondTicks >= 500?}
    M -- 是 --> N[phaseSec--]
    N --> O{phaseSec == 0?}
    O -- 是 --> P[AdvancePhase]
    O -- 否 --> Q[g_oledDue = 1]
    P --> Q
    M -- 否 --> Q
    K -- 否 --> Q
    Q --> R[g_oledTicks++]
    R --> S{oledTicks >= 250?}
    S -- 是 --> T[g_oledDue = 1]
    S -- 否 --> U[ApplyLights]
    T --> U
    U --> V[UpdateDisplay]
    V --> W([返回])
```

---

## 图三：按键处理 (HandleKeys)

```mermaid
flowchart TD
    A([进入 HandleKeys]) --> B{NS_CAR / EW_CAR?}
    B -- 是 --> C[RegisterVehicle 方向]
    B -- 否 --> D{紧急按键按下?}
    C --> D
    D -- 是 --> E[g_emergency 翻转]
    E --> F{g_emergency == 1?}
    F -- 是 --> G[SelectEmergencyDirection]
    F -- 否 --> H[StartPhase NS_GREEN]
    G --> I[g_oledDue = 1]
    H --> I
    I --> J{g_emergency?}
    J -- 是 --> K([返回])
    J -- 否 --> L{夜间按键按下?}
    L -- 是 --> M[g_night 翻转]
    M --> N{g_night == 1?}
    N -- 是 --> K
    N -- 否 --> O[StartPhase NS_GREEN]
    O --> K
    L -- 否 --> K
```

---

## 图四：定时器 0 中断服务 (Timer0ISR)

```mermaid
flowchart TD
    A([中断入口]) --> B[TH0=0xF8 TL0=0xCD]
    B --> C[关闭所有位选]
    C --> D[P0 = g_dispBuf idx]
    D --> E{g_digitIndex?}
    E -- 0 --> F[DIG_NS_TENS = 0]
    E -- 1 --> G[DIG_NS_ONES = 0]
    E -- 2 --> H[DIG_EW_TENS = 0]
    E -- 3 --> I[DIG_EW_ONES = 0]
    F --> J[g_digitIndex++]
    G --> J
    H --> J
    I --> J
    J --> K{idx >= 4?}
    K -- 是 --> L[idx = 0]
    K -- 否 --> M[g_tick2ms++]
    L --> M
    M --> N([中断返回])
```

---

## 图五：交通灯状态机

```mermaid
stateDiagram-v2
    [*] --> NS_GREEN: 上电启动
    NS_GREEN --> NS_YELLOW: 倒计时归零
    NS_YELLOW --> EW_GREEN: 3s到期
    EW_GREEN --> EW_YELLOW: 倒计时归零
    EW_YELLOW --> NS_GREEN: 3s到期

    NS_GREEN --> EMERGENCY: 紧急键
    NS_YELLOW --> EMERGENCY: 紧急键
    EW_GREEN --> EMERGENCY: 紧急键
    EW_YELLOW --> EMERGENCY: 紧急键

    NS_GREEN --> NIGHT: 夜间键
    NS_YELLOW --> NIGHT: 夜间键
    EW_GREEN --> NIGHT: 夜间键
    EW_YELLOW --> NIGHT: 夜间键

    EMERGENCY --> NS_GREEN: 再按紧急键
    NIGHT --> NS_GREEN: 再按夜间键
```

---

## 图六：智能绿灯时间计算 (CalcGreenTime)

```mermaid
flowchart TD
    A([进入 CalcGreenTime]) --> B{ownCnt > 6?}
    B -- 是 --> C[ownCnt = 6]
    B -- 否 --> D[sec = 12 + ownCnt * 2]
    C --> D
    D --> E{ownCnt > otherCnt+1?}
    E -- 是 --> F[sec += 3]
    E -- 否 --> G{pedReq == 1?}
    F --> G
    G -- 是 --> H[sec += 3]
    G -- 否 --> I{sec > 25?}
    H --> I
    I -- 是 --> J[sec = 25]
    I -- 否 --> K{sec < 8?}
    J --> K
    K -- 是 --> L[sec = 8]
    K -- 否 --> M([返回 sec])
    L --> M
```

---

## 图七：按键消抖流程

```mermaid
flowchart TD
    A([进入 KeyScan]) --> B[读取 raw = KeyReadRaw]
    B --> C[i = 0]
    C --> D{cur == prev?}
    D -- 是 --> E[debounce++]
    E --> F{debounce >= 3?}
    F -- 是 --> G[stable = cur]
    F -- 否 --> H[cur = raw bit i]
    G --> H
    D -- 否 --> I[debounce = 0]
    I --> H
    H --> J{prev==0 且 stable!=0?}
    J -- 是 --> K[edge |= mask]
    J -- 否 --> L{i++}
    K --> L
    L --> M{i < 6?}
    M -- 是 --> D
    M -- 否 --> N([返回 edge])
```
