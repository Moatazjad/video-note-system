from typing import Callable, Dict, Tuple

TEMPLATE_TYPES = {"educational", "business", "research"}
SUPPORTED_LANGUAGES = {"en", "ar"}


# =========================
# SECTION-SCOPED TEMPLATES
#
# Used per topic-section rather than for the whole document -- a separate
# assembly step supplies the "## <section title>" heading, so these
# instructions must make the model start directly with body content and
# never echo a heading/label of its own (a real bug found in testing: an
# earlier version of this instruction showed a literal "## Section Title"
# example, and the model echoed that literal placeholder back as output).
# =========================

def get_educational_section_template_en() -> str:
    return """Write the detailed notes for THIS transcript section only. A
separate assembly step will place your output under its own section
heading, so start directly with the body content -- do not output any
heading, title, or label of your own (no "#", "##", or similar) anywhere
in your response.

Rules:
- No filler, no repetition, no invented information.
- Write in clear, precise Markdown paragraphs and bullet lists.
- Explain the core idea(s) of this section, key principles, and any
  concrete examples mentioned.
- End with 1–3 short "Key takeaway" bullet points scoped to this section.
"""


def get_educational_section_template_ar() -> str:
    return """اكتب الملاحظات التفصيلية لهذا الجزء من النص فقط. خطوة تجميع
منفصلة ستضع ناتجك تحت عنوان القسم الخاص بها، فابدأ مباشرة بالمحتوى نفسه —
لا تكتب أي عنوان أو تصنيف خاص بك (لا تستخدم رمز # أو ## أو ما شابه) في أي
مكان من إجابتك.

القواعد:
- بدون حشو، بدون تكرار، بدون معلومات مختلقة.
- اكتب بأسلوب عربي طبيعي وسليم لغويًا، لا كأنه ترجمة حرفية عن الإنجليزية.
- اشرح الفكرة أو الأفكار الأساسية في هذا الجزء، والمبادئ المهمة، وأي أمثلة
  عملية وردت فيه.
- أنهِ بـ 1 إلى 3 نقاط قصيرة بعنوان "أهم ما يجب تذكره" خاصة بهذا الجزء فقط.
"""


def get_business_section_template_en() -> str:
    return """Write the strategic business notes for THIS transcript section
only. A separate assembly step will place your output under its own
section heading, so start directly with the body content -- do not output
any heading, title, or label of your own (no "#", "##", or similar)
anywhere in your response.

Rules:
- Executive clarity, decision-focused, no generic summaries.
- Cover the problems/opportunities/decisions/risks actually discussed in
  this section.
- End with 1–3 short "Action items" bullets scoped to this section.
"""


def get_business_section_template_ar() -> str:
    return """اكتب ملاحظات الأعمال الاستراتيجية لهذا الجزء من النص فقط. خطوة
تجميع منفصلة ستضع ناتجك تحت عنوان القسم الخاص بها، فابدأ مباشرة بالمحتوى
نفسه — لا تكتب أي عنوان أو تصنيف خاص بك (لا تستخدم رمز # أو ## أو ما شابه)
في أي مكان من إجابتك.

القواعد:
- وضوح تنفيذي، تركيز على القرارات، بدون تلخيص سطحي.
- اكتب بأسلوب عربي طبيعي وسليم، لا ترجمة حرفية.
- غطِّ المشكلات والفرص والقرارات والمخاطر التي ورد ذكرها فعليًا في هذا الجزء.
- أنهِ بـ 1 إلى 3 نقاط قصيرة بعنوان "إجراءات مقترحة" خاصة بهذا الجزء.
"""


def get_research_section_template_en() -> str:
    return """Write the analytical research notes for THIS transcript section
only. A separate assembly step will place your output under its own
section heading, so start directly with the body content -- do not output
any heading, title, or label of your own (no "#", "##", or similar)
anywhere in your response.

Rules:
- Analytical tone, evidence-based, no invented citations.
- Cover the question/argument/evidence actually discussed in this section.
- End with 1–3 short "Open questions" bullets scoped to this section, if any.
"""


def get_research_section_template_ar() -> str:
    return """اكتب الملاحظات البحثية التحليلية لهذا الجزء من النص فقط. خطوة
تجميع منفصلة ستضع ناتجك تحت عنوان القسم الخاص بها، فابدأ مباشرة بالمحتوى
نفسه — لا تكتب أي عنوان أو تصنيف خاص بك (لا تستخدم رمز # أو ## أو ما شابه)
في أي مكان من إجابتك.

القواعد:
- نبرة تحليلية، قائمة على الأدلة، بدون مصادر مختلقة.
- اكتب بأسلوب عربي طبيعي وسليم، لا ترجمة حرفية.
- غطِّ السؤال أو الحجة أو الأدلة التي ورد ذكرها فعليًا في هذا الجزء.
- أنهِ بـ 1 إلى 3 نقاط قصيرة بعنوان "أسئلة مفتوحة" إن وُجدت، خاصة بهذا الجزء.
"""


def get_section_template(template_type: str, language: str = "en") -> str:
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

    section_template_map: Dict[Tuple[str, str], Callable[[], str]] = {
        ("educational", "en"): get_educational_section_template_en,
        ("educational", "ar"): get_educational_section_template_ar,
        ("business", "en"): get_business_section_template_en,
        ("business", "ar"): get_business_section_template_ar,
        ("research", "en"): get_research_section_template_en,
        ("research", "ar"): get_research_section_template_ar,
    }

    return section_template_map[(template_type, language)]()


def get_overview_template(language: str = "en") -> str:
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Invalid language '{language}'. "
            f"Allowed: {', '.join(SUPPORTED_LANGUAGES)}"
        )

    if language == "ar":
        return """اكتب فقرة تمهيدية قصيرة (3 إلى 6 جمل) تلخص محتوى الفيديو بالكامل،
بالاعتماد فقط على عناوين الأقسام المُعطاة لك. اكتبها بأسلوب عربي طبيعي
وسليم، بدون حشو، وبدون تكرار حرفي لعناوين الأقسام."""

    return """Write a short overview paragraph (3–6 sentences) summarizing the
video as a whole, based only on the given section titles. Natural prose,
no filler, don't just restate the section titles verbatim."""
