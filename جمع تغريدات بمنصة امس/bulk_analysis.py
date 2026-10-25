import json
import os
import sys
import time
import pandas as pd
from mistralai.client import Mistral

# تأكد من أن مخرجات الكونسول تدعم اللغة العربية
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# ==========================================
# 1. الإعدادات الأساسية (Mistral API)
# ==========================================
api_key = "vnoE40E5UodRXTuHWEAL6PTIstYfiSLH"
client = Mistral(api_key=api_key)

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

known_keys = [
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
]

def to_clean_string(node):
    if isinstance(node, dict):
        return " - ".join([to_clean_string(v) for v in node.values() if v is not None])
    elif isinstance(node, list):
        return " | ".join([to_clean_string(item) for item in node if item is not None])
    elif node is None:
        return "غائب"
    else:
        return str(node).strip()

def process_tweet(row):
    tweet_text = row.get("النص المرجعي", "")
    account = row.get("الحساب", "")
    url = row.get("رابط التغريدة URL", "")
    
    engagement = 0
    try:
        engagement = int(row.get('عدد الإعجابات', 0)) + int(row.get('عدد التعليقات', 0)) + int(row.get('عدد إعادة النشر', 0))
    except:
        pass

    user_message = f"""
    قم بتحليل التغريدة التالية:
    النص: {tweet_text}
    الحساب: {account}
    رابط التغريدة: {url}
    إجمالي التفاعل: {engagement}
    """
    
    # Try multiple times to handle temporary API errors
    for attempt in range(3):
        try:
            response = client.chat.complete(
                model="mistral-large-latest",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content
            raw_data = json.loads(result_text)
            
            # Extract variables
            context_data = {k: "" for k in known_keys}
            def extract_variables(d):
                if isinstance(d, dict):
                    for k, v in d.items():
                        if k in known_keys:
                            context_data[k] = to_clean_string(v)
                        else:
                            extract_variables(v)
                elif isinstance(d, list):
                    for item in d:
                        extract_variables(item)
                        
            extract_variables(raw_data)
            
            return context_data
            
        except json.JSONDecodeError:
            print(f"   [!] Error: Invalid JSON from Mistral for URL: {url}. Retrying ({attempt+1}/3)...")
            time.append(2)
        except Exception as e:
            print(f"   [!] API Error: {str(e)}. Retrying ({attempt+1}/3)...")
            time.sleep(5)
            
    print(f"   [X] Failed to process URL: {url} after 3 attempts.")
    return None

def main(test_mode=False):
    input_file = "Filtered_Sample_1245_Tweets_Cleaned.xlsx"
    output_file = "Analyzed_Tweets_Results.csv"
    
    print(f"--- بدء التحليل الشامل (Bulk Analysis) ---")
    print(f"الملف المدخل: {input_file}")
    print(f"طريقة الحفظ: CSV تزايدي (للحماية من التوقف) -> {output_file}")
    
    try:
        df = pd.read_excel(input_file)
    except Exception as e:
        print(f"لا يمكن قراءة ملف الإدخال: {e}")
        return
        
    print(f"إجمالي التغريدات في الملف: {len(df)}")
    
    if test_mode:
        print(f"*** وضع الاختبار مفعل (سيتم تحليل 20 تغريدة فقط) ***")
        df = df.head(20)
        
    # Check already processed tweets to resume
    processed_urls = set()
    if os.path.exists(output_file):
        try:
            df_existing = pd.read_csv(output_file)
            if 'Tweet_URL' in df_existing.columns:
                processed_urls = set(df_existing['Tweet_URL'].astype(str).tolist())
            print(f"تم العثور على ملف حفظ سابق يحتوي على {len(processed_urls)} تغريدة محللة.")
        except Exception as e:
            print(f"تحذير: لا يمكن قراءة ملف الحفظ السابق: {e}")
    else:
        # Create the CSV with headers if it doesn't exist
        headers = ["Account_Name", "Tweet_URL", "Original_Text"] + known_keys
        pd.DataFrame(columns=headers).to_csv(output_file, index=False, encoding='utf-8-sig')
        print("تم إنشاء ملف النتائج الجديد.")

    # Start processing loop
    success_count = 0
    for index, row in df.iterrows():
        url = str(row.get("رابط التغريدة URL", ""))
        account = str(row.get("الحساب", ""))
        text = str(row.get("النص المرجعي", ""))
        
        if url in processed_urls:
            continue
            
        print(f"[{index+1}/{len(df)}] جاري تحليل تغريدة {account}...")
        
        analysis_data = process_tweet(row)
        if analysis_data:
            # Add basic info
            row_data = {
                "Account_Name": account,
                "Tweet_URL": url,
                "Original_Text": text
            }
            row_data.update(analysis_data)
            
            # Save to CSV immediately
            pd.DataFrame([row_data]).to_csv(output_file, mode='a', header=False, index=False, encoding='utf-8-sig')
            processed_urls.add(url)
            success_count += 1
            print(f"   [✓] تم التحليل والحفظ بنجاح.")
            
        # Avoid hitting API rate limits
        time.sleep(1)
        
    print(f"\n--- اكتملت العملية! تم تحليل {success_count} تغريدة جديدة. ---")
    print(f"يمكنك فتح الملف {output_file} في برنامج الإكسل.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', action='store_true', help='Run in test mode (only 3 tweets)')
    args = parser.parse_args()
    
    main(test_mode=args.test)
