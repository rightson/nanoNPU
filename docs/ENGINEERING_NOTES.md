# V0 工程判斷紀錄

完整執行結果與限制以 [VALIDATION.md](VALIDATION.md) 為準。這份筆記整理
從實際 failure 推到修正的理由。

## 1. 先定位錯誤發生的時間，再改算術

原版 4×4 system test 有 28 個 word 通過、8 個失敗。先把 testbench 的
shift 欄位放到實際使用它的 fused CONV 指令上，結果仍是 28/8。
因此單靠修改指令編碼不能解決問題。

追蹤顯示第一組四列輸出正確，但 CU 又啟動一次 CONV，第二組輸出覆寫了
結果。CONV 子狀態機已返回 idle，主狀態機卻仍在 EXECUTE 等待 fused
datapath 尾端完成；以 EXECUTE 的 level 作為啟動條件會重複觸發。

[CU.SV](../Backend/openlane/RTL/CU.SV) 加入 `exec_pulse` 條件，讓每條
指令只啟動一次。testbench 同時檢查一次 launch、四列 write，以及有效
資料期間的 shift 值。Golden 算術未改，兩個 seed 共 72/72 通過。
這類 control invariant 可以比最終數值比對更早指出錯誤來源。

## 2. 負 slack 必須先對照 clock-domain 假設

第一次 standalone post-route STA 報告 UART 輸入 hold slack 為
−0.273445 ns。最初嘗試全域增加 hold 餘裕，帶來數千個額外 buffer。
之後追到 routed netlist，才確認 endpoint 是 UART 的第一級 `rx_sync1`。

[uart_rx.v](../Backend/openlane/RTL/uart_rx.v) 已有兩級同步器。
外部 UART 與 `clk` 沒有固定相位關係；用一般同步 I/O 的 min delay
要求第一級 D pin，並不符合這個介面的 clock-domain 模型。

[UART SDC](../constraints/uart_async.sdc) 只排除外部 pin 到第一級 D pin
的同步 timing path。它從保留的 RTL net name 找到 register，避免寫死
綜合產生的 instance 編號；找不到預期結構就報錯。

驗證使用原 routed ODB 與 SPEF：例外前重現負 slack，例外後該 input
path 不再被同步分析，第一級到第二級的 setup／hold path 仍存在且通過。
這個修正需要 clock-domain 與實際 fanout 的證據，不能把任意失敗路徑
設為 false path。它也沒有完成 synchronizer placement、CDC 或 MTBF 驗證。

## 3. 設定值不等於工具最後實現的結果

Upstream 設了 `FP_CORE_UTIL=20`，同時使用固定 die 與 DEF template。
實際 global placement 報告 utilization 為 76.223%。放大成
1,750 × 1,750 µm standalone floorplan 後，報告為 22.218%。

兩者 synthesis netlist hash、50,042 cells 與 576,764.4128 µm² cell area
一致，讓 floorplan 比較有共同邏輯基準。原尺寸流程在詳細繞線時異常終止，
根因未確認；不能只憑這次比較就宣稱 die 太小是唯一原因。

Standalone 犧牲原 OpenFrame slot 的尺寸相容性。這是明確的 integration
取捨，必須隨 GDS 一起交代。

## 驗收邊界

RTL simulation、setup/hold STA、electrical limit checks、DRC、LVS 和 CDC
各自回答不同問題。LibreLane 3.0.5 預設會對部分 max-slew／max-cap 結果
給 warning；flow exit 0 不能單獨證明所有電氣限制都已收斂。
因此 repo 同時保留 execution receipt、輸入 hash、產物 hash 與實際違例數。
