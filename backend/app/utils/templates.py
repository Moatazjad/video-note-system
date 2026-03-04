from typing import Callable, Dict, Tuple

TEMPLATE_TYPES = {"educational", "business", "research"}
SUPPORTED_LANGUAGES = {"en", "ar"}


# =========================
# EDUCATIONAL
# =========================

def get_educational_template_en() -> str:
    return """Create structured, high-clarity learning notes from the transcript.

Rules:
- No filler.
- No repetition.
- Focus on clarity and depth.
- Use precise explanations.
- Do not invent information.

Structure:

# Clear, Specific Title

## Core Idea
Explain the central concept in 3–5 strong sentences.

## Key Principles
- Principle — short explanation
- Principle — short explanation
- Principle — short explanation

## Deep Explanation
Break the topic into logical sections.
Use clear headings.
Explain mechanisms, reasoning, and cause-effect relationships.

## Examples (If Present)
Summarize practical examples mentioned in the transcript.

## Practical Insights
Actionable understanding someone can apply immediately.

## Summary in 5 Bullet Points
- ...
- ...
- ...
- ...
- ...
"""


def get_educational_template_ar() -> str:
    return """أنشئ ملاحظات تعليمية واضحة وعميقة من النص.

القواعد:
- بدون حشو.
- بدون تكرار.
- وضوح ودقة.
- لا تخترع معلومات غير موجودة.

البنية:

# عنوان واضح ومحدد

## الفكرة الأساسية
اشرح المفهوم الرئيسي في 3–5 جمل قوية.

## المبادئ الرئيسية
- مبدأ — شرح مختصر
- مبدأ — شرح مختصر
- مبدأ — شرح مختصر

## شرح متعمق
قسّم الموضوع إلى أقسام منطقية.
استخدم عناوين واضحة.
اشرح الآليات والعلاقات السببية.

## أمثلة (إن وجدت)
لخّص الأمثلة العملية المذكورة.

## تطبيق عملي
كيف يمكن الاستفادة من المعلومات مباشرة؟

## ملخص في 5 نقاط
- ...
- ...
- ...
- ...
- ...
"""


# =========================
# BUSINESS
# =========================

def get_business_template_en() -> str:
    return """Create strategic business notes from the transcript.

Rules:
- Executive clarity.
- Decision-focused.
- No generic summaries.
- Extract real value.

Structure:

# Strategic Overview
Concise summary of what matters.

## Core Problems Identified
- Problem
- Problem
- Problem

## Opportunities
- Opportunity
- Opportunity

## Key Decisions
- Decision + reasoning

## Action Plan
- Immediate actions
- Short-term actions
- Long-term actions

## Risks
Main risks or constraints discussed.

## Strategic Insight
One paragraph explaining the big-picture implication.
"""


def get_business_template_ar() -> str:
    return """أنشئ ملاحظات أعمال استراتيجية من النص.

القواعد:
- وضوح تنفيذي.
- تركيز على القرارات.
- لا تلخص بشكل سطحي.

البنية:

# النظرة الاستراتيجية
ملخص مختصر لما هو مهم.

## المشكلات الأساسية
- مشكلة
- مشكلة

## الفرص
- فرصة
- فرصة

## القرارات الرئيسية
- قرار + سبب

## خطة العمل
- إجراءات فورية
- إجراءات قصيرة المدى
- إجراءات طويلة المدى

## المخاطر
المخاطر أو القيود المذكورة.

## الرؤية الاستراتيجية
فقرة تشرح الأثر العام.
"""


# =========================
# RESEARCH
# =========================

def get_research_template_en() -> str:
    return """Create analytical research notes from the transcript.

Rules:
- Analytical tone.
- Evidence-based.
- Structured reasoning.
- No invented citations.

Structure:

# Research Focus

## Central Question
What problem is being explored?

## Argument or Hypothesis
Core claim being made.

## Supporting Evidence
- Evidence
- Evidence
- Evidence

## Logical Breakdown
Explain how the argument develops step by step.

## Implications
Why this matters.

## Limitations (If Mentioned)
Constraints or uncertainties discussed.

## Open Questions
Unresolved areas or future directions.
"""


def get_research_template_ar() -> str:
    return """أنشئ ملاحظات بحثية تحليلية من النص.

القواعد:
- نبرة تحليلية.
- قائمة على الأدلة.
- لا تضف مصادر غير موجودة.

البنية:

# محور البحث

## السؤال المركزي
ما المشكلة التي يتم بحثها؟

## الفرضية أو الطرح
الادعاء الأساسي.

## الأدلة الداعمة
- دليل
- دليل
- دليل

## التحليل المنطقي
اشرح تسلسل الحجة خطوة بخطوة.

## الأثر
لماذا هذا مهم؟

## القيود (إن وجدت)
القيود أو الشكوك المذكورة.

## أسئلة مفتوحة
نقاط تحتاج إلى بحث إضافي.
"""


# =========================
# TEMPLATE ROUTER
# =========================

def get_template(template_type: str, language: str = "en") -> str:
    if template_type not in TEMPLATE_TYPES:
        raise ValueError(
            f"Invalid template_type '{template_type}'. "
            f"Allowed: {', '.join(TEMPLATE_TYPES)}"
        )

    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Invalid language '{language}'. "
            f"Allowed: {', '.join(SUPPORTED_LANGUAGES)}"
        )

    template_map: Dict[Tuple[str, str], Callable[[], str]] = {
        ("educational", "en"): get_educational_template_en,
        ("educational", "ar"): get_educational_template_ar,
        ("business", "en"): get_business_template_en,
        ("business", "ar"): get_business_template_ar,
        ("research", "en"): get_research_template_en,
        ("research", "ar"): get_research_template_ar,
    }

    return template_map[(template_type, language)]()