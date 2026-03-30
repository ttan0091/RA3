---
name: protocol-freeze-change-log
description: Protokolün (PICO, kriterler, analiz planı) dondurulması ve değişikliklerin audit edilebilir şekilde loglanması SOP'u.
---

# Protocol Freeze + Change Log SOP

## Amaç

Meta-analiz sürecinde **analiz öncesi** kararların sabitlenmesi (protocol freeze) ve sonradan yapılan değişikliklerin şeffaf şekilde raporlanması.

## Önerilen dosyalar

- `protocol/PROTOCOL.md` (SSOT)
- `logs/protocol_changes.csv` (değişiklik kaydı)

## protocol_changes.csv şeması

```csv
timestamp,changed_by,section,old_value,new_value,reason,impact_assessment,approved_by
2026-01-31T14:00:00Z,agent,Eligibility.Criteria,"...","...","...","risk of bias reduction","PI"
```

## SOP

1. Freeze noktası: arama stratejisi + inclusion/exclusion + primary outcomes + effect measure + model (random/fixed) + subgroup planı.
2. Freeze sonrası her değişiklik:
   - neden
   - etkisi (bias riski, kapsam değişimi)
   - onay
3. PRISMA raporunda “protocol deviations” olarak özetle.
