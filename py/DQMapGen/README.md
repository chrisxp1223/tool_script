# 🧰 DQMapGen

**DQMapGen** is a Python-based automation tool designed to convert DRAM DQ Mapping tables from BAE checklists (Excel or CSV format) into C-style header files (`.h`) for use in APCB firmware integration.

This tool is ideal for BIOS/UEFI engineers who need to streamline and validate pin mapping in a structured and consistent manner.

---

## 📌 Features

- ✅ Supports input from `.xlsx` or `.csv` formats
- 🧠 Automatically generates `#define` macros for DQ to CPU pin mapping
- 🔧 Output header files ready for APCB integration
- 🛠 Built with Python 3 using `pandas` and `openpyxl`
- 📈 Reduces manual errors and boosts efficiency

---

## 📥 Input & 📤 Output Rules

### 📥 Input Rule

The tool accepts **Excel (.xlsx)** or **CSV (.csv)** files as input, typically exported from the **BAE checklist**. To ensure proper parsing and generation, please follow these rules:

- File naming convention:
  - Use `dqmap_<platform>.xlsx` or `dqmap_<platform>.csv`
  - Examples:
    - `dqmap_mdn.xlsx` → Mendocino
    - `dqmap_rmb.xlsx` → Rembrandt
    - `dqmap_phx.xlsx` → Phoenix
    - `dqmap_stx.xlsx` → Strix Point
    - `dqmap_krk.xlsx` → Krackan

---

### 📤 Output Rule

The output is a **C-style Header File (.h)** with `#define` macros that map each DQ pin to its corresponding CPU pin. Output naming and structure follow these rules:

- Output file must be specified via `--output` argument
- Each mapping will be exported as:
  ```c
  {
    // MAA/MAB
    { MEM_MX_DATA_08, MEM_MX_DATA_09, MEM_MX_DATA_10, MEM_MX_DATA_11, MEM_MX_DATA_12, MEM_MX_DATA_13, MEM_MX_DATA_14, MEM_MX_DATA_15 },
    { MEM_MX_DATA_00, MEM_MX_DATA_01, MEM_MX_DATA_02, MEM_MX_DATA_03, MEM_MX_DATA_04, MEM_MX_DATA_05, MEM_MX_DATA_06, MEM_MX_DATA_07 },
    { MEM_MX_DATA_16, MEM_MX_DATA_17, MEM_MX_DATA_18, MEM_MX_DATA_19, MEM_MX_DATA_20, MEM_MX_DATA_21, MEM_MX_DATA_22, MEM_MX_DATA_23 },
    { MEM_MX_DATA_24, MEM_MX_DATA_25, MEM_MX_DATA_26, MEM_MX_DATA_27, MEM_MX_DATA_28, MEM_MX_DATA_29, MEM_MX_DATA_30, MEM_MX_DATA_31 },
    // MBA/MBB
  ```
- If any row contains missing or invalid pins, that line will be **skipped** with a warning
- Output file name convention: `dqmap_<platform>.h`

---

### 🧪 Example

#### Input (`dqmap_mdn.xlsx`):

#### Output (`dqmap_mdn.h`):

```c
    { MEM_MX_DATA_08, MEM_MX_DATA_09, MEM_MX_DATA_10, MEM_MX_DATA_11, MEM_MX_DATA_12, MEM_MX_DATA_13, MEM_MX_DATA_14, MEM_MX_DATA_15 },
    { MEM_MX_DATA_00, MEM_MX_DATA_01, MEM_MX_DATA_02, MEM_MX_DATA_03, MEM_MX_DATA_04, MEM_MX_DATA_05, MEM_MX_DATA_06, MEM_MX_DATA_07 },
```

---
