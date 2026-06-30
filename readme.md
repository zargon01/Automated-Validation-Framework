# 🧠 Multi-Region Content Validation Framework

A scalable, reusable, and configuration-driven automation framework for validating web page content across multiple regions and languages.

---

## 🚀 Overview

This framework is designed to validate UI content across different regions (e.g., localized Microsoft pages) with high reliability and minimal flakiness.

It supports:

* 🌍 Multi-region execution
* 🌐 Automatic language detection & translation
* 🧠 Semantic text validation using transformer models
* 📊 Excel-based input/output
* 🧩 Plug-and-play checks
* ⚙️ Fully configuration-driven architecture

---

## 🏗️ Architecture

```
framework/
│
├── core/                    # Execution engine
│   ├── runner.py
│   ├── page_engine.py
│   ├── check_executor.py
│
├── services/                # Shared services
│   ├── browser_service.py
│   ├── translation_service.py
│   ├── semantic_service.py
│   ├── language_service.py
│
├── utils/                   # Helper utilities
│   ├── excel_utils.py
│   ├── highlight_utils.py
│   ├── retry_utils.py
│   ├── logger.py
│
├── checks/                  # Validation logic
│   ├── base_check.py
│   ├── content_check.py
│   ├── visibility_check.py
│   ├── custom_checks/
│
├── registry/                # Mapping layer
│   ├── check_registry.py
│   ├── page_registry.py
│
├── configs/                 # Config-driven system
│   ├── pages.yaml
│   ├── checks.yaml
│
├── data/                    # Input data
│   ├── regions_checks.xlsx
│
├── reports/
│   ├── screenshots/
│
└── main.py
```

---

## 🔄 Execution Flow

```
Excel Input
   ↓
Load Configs (pages + checks)
   ↓
Initialize Services
   ↓
For each region:
   ↓
   Open Page
   ↓
   Detect Language
   ↓
   For each check:
       ↓
       Locate element(s)
       ↓
       Extract text
       ↓
       Translate (if not English)
       ↓
       Run validation:
           - Exact match
           - Semantic match (fallback)
       ↓
       Highlight result
       ↓
       Store result
   ↓
   Capture screenshot
   ↓
Write results to Excel
```

---

## 🧩 Core Concepts

### 1. Configuration-Driven Design

No hardcoding. Pages and checks are defined in YAML files.

### 2. Pluggable Checks

Checks are modular and reusable across pages.

### 3. Service-Based Architecture

Independent services handle:

* Browser automation
* Translation
* Semantic matching
* Language detection

### 4. Page-Agnostic Engine

Same engine works for:

* PDP pages
* Homepages
* Pricing pages
* Any future pages

---

## ⚙️ Configuration

### 📄 `pages.yaml`

Defines pages and associated checks:

```yaml
PDP:
  url: "https://www.microsoft.com/{region}/microsoft-365/..."
  checks:
    - promo_text
    - accordion_ai
```

---

### 📄 `checks.yaml`

Defines reusable checks:

```yaml
promo_text:
  type: content
  locator: '[data-automation-test-id^="buy-box-promo"] p'
  expected: "Subscription automatically renews"
  match_type: hybrid
  threshold: 0.6
  translate: true

accordion_ai:
  type: content
  locator: 'li:first-child div.collapse.show div.accordion-body p:nth-child(2)'
  expected: "Microsoft 365 Family plan lets you share"
  match_type: hybrid
  threshold: 0.6
  translate: true
```

---

## 🧪 Check Types

| Type       | Description                       |
| ---------- | --------------------------------- |
| content    | Validates text content            |
| visibility | Checks if element is visible      |
| attribute  | Validates attributes (href, etc.) |
| count      | Validates number of elements      |

---

## 🧠 Matching Strategy

Each check follows a hybrid approach:

1. ✅ Exact Match (fast, reliable)
2. 🧠 Semantic Match (fallback using transformer model)

Threshold-based acceptance ensures flexibility across localized content.

---

## 🌐 Translation Strategy

To reduce flakiness:

### ✅ Default Behavior

* Translate **element text only**

### ⚠️ Fallback

* Page-level translation only if necessary

### 💡 Benefits

* Faster execution
* Less dependency on browser UI
* More stable results

---

## 📊 Excel Integration

### Input

* Region list
* Optional test metadata

### Output

* Actual text
* PASS / FAIL result
* Highlighted validation results

---

## 🎯 Result Format

Each check produces a structured result:

```json
{
  "check_id": "promo_text",
  "status": "PASS",
  "expected": "...",
  "actual": "...",
  "score": 0.78,
  "match_type": "semantic",
  "error": null
}
```

---

## 🧱 Key Design Principles

* ✅ Separation of concerns
* ✅ Reusability over duplication
* ✅ Config over code
* ✅ Stability over speed
* ✅ Graceful failure handling

---

## ⚠️ Anti-Patterns to Avoid

* ❌ Hardcoding locators in logic
* ❌ Using `time.sleep()`
* ❌ Translating entire page unnecessarily
* ❌ Mixing services with checks
* ❌ Tight coupling with Excel format

---

## 🚀 Future Enhancements

* Parallel execution (multi-region)
* HTML/Allure reporting
* CI/CD integration
* Visual regression testing
* API-based validations
* Caching for embeddings & translations

---

## ▶️ Getting Started

1. Install dependencies
2. Configure `pages.yaml` and `checks.yaml`
3. Add regions in Excel file
4. Run:

```
python main.py
```

---

## 🧠 Final Thought

This framework is not just a script—it's a **validation engine**.

Design it once, and reuse it across:

* Pages
* Products
* Regions
* Languages

---

## 🤝 Contribution

Feel free to extend:

* New check types
* New services
* New page configurations

Keep the core engine untouched for maximum stability and scalability.

---
