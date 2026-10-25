import json
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from mistralai.client import Mistral

api_key = "vnoE40E5UodRXTuHWEAL6PTIstYfiSLH"
client = Mistral(api_key=api_key)

SYSTEM_PROMPT = """
أنت خبير أكاديمي في تحليل الخطاب النقدي. حلل التغريدة التالية وأرجع JSON فقط بالمفاتيح المحددة.
القيود: الرد يجب أن يكون بصيغة JSON صالحة 100% فقط.
"""

user_message = """
التغريدة: الولايات المتحدة تقوم بتصنيف #أنصار_الله، المعروفين باسم #الحوثيين رسمياً كـ #منظمة_إرهابية_أجنبية.
الحساب: CENTCOMArabic
رابط: https://x.com/CENTCOMArabic/status/1896999436146110706
التفاعل: 5320

الرجاء ملء هذه المفاتيح فقط بصيغة JSON:
{
  "Hashtags": "هل يوجد وسوم؟ نعم/لا + الملاحظة",
  "Mentions": "هل يوجد إشارات؟ نعم/لا + الملاحظة",
  "Retweets_Quotes": "هل يوجد إعادة نشر؟ نعم/لا + الملاحظة",
  "Call_to_Action": "هل يوجد دعوة للمشاركة؟ نعم/لا + الملاحظة",
  "Official_Links": "هل يوجد روابط رسمية؟ نعم/لا + الملاحظة"
}
"""

response = client.chat.complete(
    model="mistral-large-latest",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ],
    response_format={"type": "json_object"}
)

result = response.choices[0].message.content
print("=== RAW JSON FROM MISTRAL ===")
print(result[:2000])
print()
parsed = json.loads(result)
print("=== KEYS RETURNED ===")
print(list(parsed.keys()))
print()
print("=== HASHTAGS VALUE ===")
print(type(parsed.get("Hashtags")), repr(parsed.get("Hashtags")))
