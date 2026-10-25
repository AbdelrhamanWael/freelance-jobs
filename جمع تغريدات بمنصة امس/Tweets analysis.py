import json
import os
import sys

# تأكد من أن مخرجات الكونسول تدعم اللغة العربية
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from docxtpl import DocxTemplate
from mistralai.client import Mistral

# ==========================================
# 1. الإعدادات الأساسية (Mistral API)
# ==========================================
# ضع مفتاح الـ API الخاص بـ Mistral هنا
api_key = "vnoE40E5UodRXTuHWEAL6PTIstYfiSLH"
client = Mistral(api_key=api_key)

# ضع الـ System Prompt النهائي هنا
SYSTEM_PROMPT = """
أنت الآن خبير أكاديمي متمرس في العلوم السياسية وتحليل الخطاب النقدي (Critical Discourse Analysis)، ومتخصص في الدبلوماسية الرقمية وتطبيقات نموذج "فان دايك" (Van Dijk). مهمتك هي تحليل تغريدات (منشورات منصة X) بناءً على الاستمارة الأكاديمية الصارمة المرفقة.

الهدف:
تحليل التغريدة المرفقة بدقة واحترافية واستخراج كافة البيانات المطلوبة وفقاً للأقسام الموضحة أدناه، مع الالتزام التام بأسلوب الكتابة الأكاديمية الرصينة، والابتعاد عن العبارات العامة، واستخدام "أمثلة نصية ومقتطفات مباشرة" من التغريدة لدعم كل حكم تحليلي.

--- النص المراد تحليله ---
[أدخل نص التغريدة هنا مع إحصائيات التفاعل إن وجدت]
--------------------------

--- هيكل الاستمارة المطلوب تعبئته بصيغة JSON فقط ---

أولاً: البيانات التعريفية للتغريدة والتمهيد
- "Date": تاريخ النشر
- "URL": رابط التغريدة
- "Language": اللغة
- "Occasion": المناسبة أو الحدث
- "Media_Type": نوع الوسائط (نص – صورة – فيديو – إنفوجرافيك)
- "Likes": عدد الإعجابات
- "Comments": عدد التعليقات
- "Retweets": عدد إعادة النشر
- "Intro_Paragraph": فقرة تمهيدية تصف التغريدة، وتوضح الفاعلين والنطاق والمفردات.

ثانياً: التحليل السياقي للخطاب
- "Target_Audience": الجمهور المستهدف (الجاليات/ جمهور دولي/ جمهور إحدى الدول/ صناع قرار/ وسائل اعلام/ اخرى)
- "Actors": الأطراف الفاعلة (رئيس الدولة/ وزير/ دبلوماسي/ منظمة دولية/ سفارة/ اخرى)
- "Geo_Scope": النطاق الجغرافي (إقليمي / دولي)
- "Comm_Goal": الهدف الاتصالي الظاهر (اعلام/ اقناع/ حوار/ بناء اجماع)
- "Regional_Context": السياق الإقليمي والدولي
- "Qualitative_Analysis_Space": مساحة التحليل الكيفي (كيف يحوّل النص المختصر إلى بنية إقناع).

ثالثاً: تحليل البنية النصية وفق نموذج فان دايك (المربع الأيديولوجي)
(لكل عنصر، حدد "الدرجة" ثم اكتب "التحليل")
- "Self_Positives_Score": 
- "Self_Positives_Analysis": 
- "Self_Negatives_Score": 
- "Self_Negatives_Analysis": 
- "Other_Negatives_Score": 
- "Other_Negatives_Analysis": 
- "Other_Positives_Score": 
- "Other_Positives_Analysis": 

رابعاً: تحليل استراتيجيات الدبلوماسية الرقمية

الاستراتيجية الأولى: الإعلام الرقمي (حدد "نعم/لا"، "الدرجة"، "الملاحظة")
- "Official_Info": (نشر معلومات أو بيانات رسمية)
- "Official_Statements": (نشر تصريحات المسؤولين)
- "Intl_Coop": (عرض مبادرات أو علاقات دولية)
- "Diplomatic_Visits": (الإعلان عن اللقاءات والزيارات الدبلوماسية)
- "Stats_Reports": (نشر التقارير والاحصاءات)

الاستراتيجية الثانية: الإقناع والتأثير
- "Intl_Sources": (الاستشهاد بمصادر دولية)
- "Human_Stories": (ابراز قصص انسانية)
- "National_Success": (إبراز النجاحات الوطنية)
- "State_Superiority": (ابراز تفوق او مكانة الدولة مقارنة بالدول الأخرى)
- "Solidarity": (التهنئة بالمناسبات او التضامن مع الدول في حالة الازمات او الكوارث)

الاستراتيجية الثالثة: بناء الصورة الذهنية والسمعة الدولية
- "Political_Values": (إبراز القيم السياسية أو الإنسانية)
- "Tech_Progress": (إبراز التقدم العلمي والتكنولوجي)
- "Intl_Leadership": (إبراز الدور القيادي الدولي)
- "Reliable_Partner": (تقديم الدولة كشريك موثوق)
- "Correct_Stereotypes": (تصحيح الصور النمطية السلبية)
- "Intl_Trust": (بناء الثقة الدولية)
- "Cultural_Appeal": (إبراز الجاذبية الحضارية والثقافية)

الاستراتيجية الرابعة: التفاعل والحضور الرقمي
- "Hashtags": (استخدام الوسوم)
- "Mentions": (استخدام الإشارات)
- "Retweets_Quotes": (إعادة نشر أو اقتباس التغريدات)
- "Call_to_Action": (دعوة الجمهور للمشاركة)
- "Official_Links": (توظيف روابط لمصادر رسمية)

الاستراتيجية الخامسة: نظرية الحوار
- "Comms_Channels": (توفير قنوات للتواصل وطلب المعلومات)
- "Reply_Audience": (الرد على تعليقات واستفسارات الجمهور)
- "Live_Sessions": (تنظيم جلسات أو لقاءات للحوار المباشر)
- "Encourage_Proposals": (تشجيع الجمهور على تقديم المقترحات)
- "Polls_Questions": (طرح الأسئلة واستطلاعات الرأي العام)

خامساً (أ): التكتيكات الخطابية (الإطار العاطفي)
(لكل تكتيك حدد "موجود/غير موجود"، ثم اذكر "الملاحظة" مدعومة بالنص)
- "Irony": السخرية
- "Celeb_Quotes": الاستشهاد بالشخصيات المشهورة
- "Disapproval": الاستهجان
- "Politeness": التلطف
- "Show_Power": استعراض القوة
- "Cultural_Symbols": استخدام الرموز الثقافية المألوفة
- "National_Praise": تمجيد الذات القومية
- "Endearment": التحبيب والاستحسان
- "Doubt": التشكيك والتكذيب
- "Linguistic_Styles": الأساليب اللغوية
- "Threats": التخويف والتهديد
- "Victimhood": لعب دور الضحية
- "Similarities": التأكيد على أوجه الشبه والتقارب
- "Challenge": التحدي
- "Slogans": الشعارات
- "Citizen_Opinions": الاستشهاد بآراء المواطنين
- "Categorization": التصنيف
- "Positives_Traits": الصفات الايجابية
- "Other_Negatives_Show": عرض سلبيات الآخر
- "Superlatives": استخدام صيغة التفضيل
- "Supportive_Power": القوة الداعمة

خامساً (ب): التكتيكات الخطابية (الإطار المنطقي)
- "Examples": التوضيح بالامثلة
- "Comparison": المقارنة
- "Proof": البرهنة
- "Justification": التبرير
- "Stats_Numbers": الأرقام والاحصاءات
- "Number_Game": لعبة الارقام
- "Religious_Frames": توظيف الأطر المرجعية الدينية

سادساً: تحليل ديناميكيات القوة الناعمة
(حدد: رئيسي/ثانوي/غائب، مع ملاحظة كيفية)
- "Soft_Pol_Power": القوة الناعمة السياسية
- "Soft_Cult_Power": القوة الناعمة الثقافية
- "Soft_Edu_Power": القوة الناعمة التعليمية والمعرفية
- "Soft_Econ_Power": القوة الناعمة الاقتصادية والتنموية
- "Soft_Tech_Power": القوة الناعمة العلمية والتكنولوجية
- "Soft_Human_Power": القوة الناعمة الإنسانية
- "Soft_Media_Power": القوة الناعمة الإعلامية

القيود الإلزامية:
- الرد يجب أن يكون بصيغة JSON صالحة 100% (Valid JSON) فقط، لا تكتب أي نص خارج الـ JSON.
- لا تهلوس (Do not hallucinate). لا تقم بتأليف استنتاجات لا يدعمها النص المرفق.
"""

# ==========================================
# 2. قراءة بيانات العينة (JSON)
# ==========================================
# الداتا اللي أنت سحبتها لأعلى 5 تغريدات تفاعلاً
tweets_json = r"""
{
  "total_high_engagement_tweets": 6315,
  "top_5": [
    {
      "الحساب": "USAbilAraby",
      "رابط التغريدة URL": "https://x.com/USAbilAraby/status/1898802249456890333",
      "التفاعل الكلي": 6368,
      "النص المرجعي": "وزير الخارجية ماركو روبيو: تدين الولايات المتحدة قيام إرهابيين إسلاميين متطرفين، وبما فيهم جهاديين أجانب، بعمليات قتل في غرب سوريا في الأيام الأخيرة. تقف الولايات المتحدة إلى جانب الأقليات الدينية والعرقية في سوريا، بما في ذلك الأقليات المسيحية والدرزية والعلوية والكردية، كما"
    },
    {
      "الحساب": "CENTCOMArabic",
      "رابط التغريدة URL": "https://x.com/CENTCOMArabic/status/2032495288305283561",
      "التفاعل الكلي": 5479,
      "النص المرجعي": "تأكيد وفاة جميع أفراد طاقم طائرة التزود بالوقود الأمريكية KC-135 التي سقطت في العراق \n  \nتامبا، فلوريدا – تم الآن تأكيد وفاة جميع أفراد الطاقم الستة الذين كانوا على متن طائرة التزود بالوقود الأمريكية طراز KC-135، والتي تحطمت في غرب العراق. فُقدت الطائرة أثناء تحليقها فوق مجال جوي"
    },
    {
      "الحساب": "CENTCOMArabic",
      "رابط التغريدة URL": "https://x.com/CENTCOMArabic/status/1901046061256302849",
      "التفاعل الكلي": 5476,
      "النص المرجعي": "العمليات التي تنفذها #القيادة_المركزية_الأمريكية (#سنتكوم) ضد الحوثيين المدعومين من إيران مستمرة... https://t.co/7SptJ1sEbB"
    },
    {
      "الحساب": "CENTCOMArabic",
      "رابط التغريدة URL": "https://x.com/CENTCOMArabic/status/1896999436146110706",
      "التفاعل الكلي": 5320,
      "النص المرجعي": "الولايات المتحدة تقوم بتصنيف #أنصار_الله، المعروفين باسم #الحوثيين رسمياً كــ #منظمة_إرهابية_أجنبية. https://t.co/ozSarfREy4"
    },
    {
      "الحساب": "CENTCOMArabic",
      "رابط التغريدة URL": "https://x.com/CENTCOMArabic/status/1901003270945988704",
      "التفاعل الكلي": 4702,
      "النص المرجعي": "قوات #القيادة_المركزية_الأمريكية (#سنتكوم) تشن عملية واسعة النطاق ضد الحوثيين المدعومين من إيران في اليمن\n\nفي 15 مارس/آذار، بدأت القيادة المركزية الأمريكية سلسلة من العمليات التي شملت ضربات دقيقة ضد أهداف الحوثيين المدعومين من إيران في مختلف أنحاء اليمن، وذلك للدفاع عن المصالح https://t.co/yOGASY5DYl"
    }
  ]
}
"""

data = json.loads(tweets_json)
top_tweets = data["top_5"]

# إنشاء مجلد لحفظ ملفات الوورد الناتجة
output_folder = "Mistral_CDA_Samples"
os.makedirs(output_folder, exist_ok=True)

print(f"تم العثور على {len(top_tweets)} تغريدات. جاري بدء التحليل...")

# ==========================================
# 3. حلقة الأتمتة (The Automation Loop)
# ==========================================
for index, tweet in enumerate(top_tweets):
    print(f"جاري تحليل التغريدة رقم {index + 1}...")
    
    tweet_text = tweet["النص المرجعي"]
    engagement = tweet["التفاعل الكلي"]
    account = tweet["الحساب"]
    url = tweet["رابط التغريدة URL"]
    
    user_message = f"""
    قم بتحليل التغريدة التالية:
    النص: {tweet_text}
    الحساب: {account}
    رابط التغريدة: {url}
    إجمالي التفاعل: {engagement}
    """

    try:
        # استدعاء نموذج Mistral
        # يفضل استخدام mistral-large-latest للمهام المعقدة
        response = client.chat.complete(
            model="mistral-large-latest",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            response_format={"type": "json_object"} # إجبار النموذج على إرجاع JSON
        )
        
        result_text = response.choices[0].message.content
        
        # تحويل النص إلى قاموس بايثون (Dictionary)
        raw_data = json.loads(result_text)
        
        # ==========================================
        # الفلتر السحري لتنظيف هلوسة الموديل (Recursive Extractor)
        # ==========================================
        # قائمة بكل المتغيرات المطلوبة في قالب الوورد
        known_keys = {
            "Date", "URL", "Language", "Occasion", "Media_Type", "Likes", "Comments", "Retweets", "Intro_Paragraph",
            "Target_Audience", "Actors", "Geo_Scope", "Comm_Goal", "Regional_Context", "Qualitative_Analysis_Space",
            "Self_Positives_Score", "Self_Positives_Analysis", "Self_Negatives_Score", "Self_Negatives_Analysis",
            "Other_Negatives_Score", "Other_Negatives_Analysis", "Other_Positives_Score", "Other_Positives_Analysis",
            "Official_Info", "Official_Statements", "Intl_Coop", "Diplomatic_Visits", "Stats_Reports",
            "Intl_Sources", "Human_Stories", "National_Success", "State_Superiority", "Solidarity",
            "Political_Values", "Tech_Progress", "Intl_Leadership", "Reliable_Partner", "Correct_Stereotypes", "Intl_Trust", "Cultural_Appeal",
            "Hashtags", "Mentions", "Retweets_Quotes", "Call_to_Action", "Official_Links",
            "Comms_Channels", "Reply_Audience", "Live_Sessions", "Encourage_Proposals", "Polls_Questions",
            "Irony", "Celeb_Quotes", "Disapproval", "Politeness", "Show_Power", "Cultural_Symbols", "National_Praise", "Endearment", "Doubt", "Linguistic_Styles", "Threats", "Victimhood", "Similarities", "Challenge", "Slogans", "Citizen_Opinions", "Categorization", "Positives_Traits", "Other_Negatives_Show", "Superlatives", "Supportive_Power",
            "Examples", "Comparison", "Proof", "Justification", "Stats_Numbers", "Number_Game", "Religious_Frames",
            "Soft_Pol_Power", "Soft_Cult_Power", "Soft_Edu_Power", "Soft_Econ_Power", "Soft_Tech_Power", "Soft_Human_Power", "Soft_Media_Power"
        }

        context_data = {k: "" for k in known_keys} # Initialize all to empty string to avoid missing tags
        
        def to_clean_string(node):
            if isinstance(node, dict):
                # Join dict values with " - "
                return " - ".join([to_clean_string(v) for v in node.values() if v is not None])
            elif isinstance(node, list):
                # Join list items with " | "
                return " | ".join([to_clean_string(item) for item in node if item is not None])
            elif node is None:
                return "غائب"
            else:
                return str(node)

        def extract_variables(d):
            if isinstance(d, dict):
                for k, v in d.items():
                    if k in known_keys:
                        context_data[k] = to_clean_string(v)
                    else:
                        # إذا لم يكن المتغير في القائمة، نبحث بداخله
                        extract_variables(v)
            elif isinstance(d, list):
                for item in d:
                    extract_variables(item)
                    
        extract_variables(raw_data)
        # ==========================================
        
        # إضافة المتغيرات اللي مش محتاجة ذكاء اصطناعي للقالب عشان الكود يملأها مباشرة
        context_data["Account_Name"] = account
        context_data["Tweet_URL"] = url
        context_data["Total_Engagement"] = engagement
        
        # فتح قالب الوورد المفرغ (تأكد من وجود ملف template.docx في نفس المسار)
        doc = DocxTemplate("template.docx")
        
        # حقن البيانات في القالب
        doc.render(context_data)
        
        # حفظ الملف باسم التغريدة
        output_filename = f"{output_folder}/Sample_Analysis_{index + 1}.docx"
        doc.save(output_filename)
        
        print(f"✅ تم الحفظ بنجاح: {output_filename}")
        
    except json.JSONDecodeError:
        print(f"❌ خطأ: النموذج لم يُرجع JSON صالح للتغريدة رقم {index + 1}.")
    except Exception as e:
        print(f"❌ حدث خطأ غير متوقع في التغريدة رقم {index + 1}: {e}")

print("🎉 اكتملت عملية توليد العينات الخمس بنجاح!")