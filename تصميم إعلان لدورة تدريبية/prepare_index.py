import base64

# Read bg_4.jpg
with open('bg_4.jpg', 'rb') as f:
    bg4_b64 = f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode('utf-8')}"

with open('styles.css', 'r', encoding='utf-8') as f:
    css_content = f.read()

# Replace background with bg_4.jpg embedded base64
import re
css_content = re.sub(
    r"background:\s*linear-gradient\([^)]+\),\s*url\('[^']+'\)[^;]*;",
    f"background: linear-gradient(rgba(23, 39, 54, 0.25), rgba(23, 39, 54, 0.25)), url('{bg4_b64}') no-repeat center center fixed;",
    css_content
)

top_bar_and_edit_css = """
/* Floating Action Bar */
.top-bar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: rgba(15, 23, 42, 0.90);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.12);
    z-index: 9999;
    padding: 12px 24px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    font-family: 'Cairo', 'Tajawal', sans-serif;
}
.top-bar-content {
    max-width: 950px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
}
.top-bar-info {
    color: #e2e8f0;
    font-size: 0.95rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 10px;
}
.top-bar-info i {
    color: #38bdf8;
    font-size: 1.1rem;
}
.top-bar-actions {
    display: flex;
    align-items: center;
    gap: 10px;
}
.btn {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 9px 20px;
    border-radius: 50px;
    font-size: 0.92rem;
    font-weight: 800;
    cursor: pointer;
    border: none;
    transition: all 0.25s ease;
    font-family: inherit;
    text-decoration: none;
}
.btn-primary {
    background: linear-gradient(135deg, #0d9488, #059669);
    color: white;
    box-shadow: 0 4px 14px rgba(5, 150, 105, 0.4);
}
.btn-primary:hover {
    background: linear-gradient(135deg, #14b8a6, #10b981);
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(5, 150, 105, 0.5);
}
.btn-secondary {
    background: rgba(255, 255, 255, 0.12);
    color: #f1f5f9;
    border: 1px solid rgba(255, 255, 255, 0.25);
}
.btn-secondary:hover {
    background: rgba(255, 255, 255, 0.22);
}

/* Edit Mode styling */
body {
    padding-top: 85px !important;
}

[contenteditable="true"] {
    outline: none;
    cursor: text;
    transition: all 0.2s ease;
    border-radius: 4px;
}
[contenteditable="true"]:hover {
    background-color: rgba(61, 164, 166, 0.08);
}
[contenteditable="true"]:focus {
    background-color: rgba(61, 164, 166, 0.14);
    box-shadow: 0 0 0 2px rgba(61, 164, 166, 0.45);
}

/* Print optimizations */
@media print {
    .top-bar {
        display: none !important;
    }
    body {
        padding-top: 0 !important;
    }
}
"""

full_css = css_content + "\n" + top_bar_and_edit_css

html_template = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>إعلان دورة القدرات - معهد مئة وثمانون درجة</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- مكتبات تصدير PDF بجودة فائقة -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <style>
{full_css}
    </style>
</head>
<body>

    <!-- شريط التحكم العلوي لتحميل PDF واستعادة الأصل -->
    <div class="top-bar" data-html2canvas-ignore="true">
        <div class="top-bar-content">
            <div class="top-bar-info">
                <i class="fa-solid fa-pen-to-square"></i>
                <span>انقر على أي نص لتعديله مباشرة</span>
            </div>
            <div class="top-bar-actions">
                <button id="reset-btn" onclick="resetContent()" class="btn btn-secondary" title="استعادة النصوص الأساسية">
                    <i class="fa-solid fa-rotate-left"></i> <span>استعادة الأصل</span>
                </button>
                <button id="download-pdf-btn" onclick="downloadPDF(true)" class="btn btn-primary" title="تصدير الإعلان بالخلفية كملف PDF">
                    <i class="fa-solid fa-file-pdf"></i> <span id="download-text">تحميل الإعلان (PDF)</span>
                </button>
            </div>
        </div>
    </div>

    <!-- بطاقة الإعلان الأساسية المطابقة 100% لتصميم index.html -->
    <div class="flyer-container" id="flyer-card">
        <!-- Decorative circles matching the printed flyer -->
        <div class="blob blob-1"></div>
        <div class="blob blob-2"></div>
        <div class="blob blob-3"></div>
        
        <!-- Header -->
        <header class="header">
            <h2 class="institute-name" contenteditable="true" title="انقر للتعديل">معهد مئة وثمانون درجة العالي للتدريب</h2>
            <h1 class="course-title" contenteditable="true" title="انقر للتعديل">دورة التأسيس لاختبار القدرات</h1>
            <h3 class="course-subtitle" contenteditable="true" title="انقر للتعديل">(كمي ولفظي)</h3>
            <div class="badge-comprehensive" contenteditable="true" title="انقر للتعديل">دورة شاملة</div>
        </header>

        <!-- Features -->
        <section class="features-section">
            <ul class="features-list">
                <li><i class="fa-solid fa-circle-check" aria-hidden="true"></i><span contenteditable="true" title="انقر للتعديل">إتقان الكمي واللفظي من الصفر</span></li>
                <li><i class="fa-solid fa-circle-check" aria-hidden="true"></i><span contenteditable="true" title="انقر للتعديل">أسرار الحل السريع بدون تعقيد</span></li>
                <li><i class="fa-solid fa-circle-check" aria-hidden="true"></i><span contenteditable="true" title="انقر للتعديل">محاكاة واقعية لاختبار قياس</span></li>
                <li><i class="fa-solid fa-circle-check" aria-hidden="true"></i><span contenteditable="true" title="انقر للتعديل">تحليل أداء وتطوير نقاط الضعف</span></li>
                <li><i class="fa-solid fa-circle-check" aria-hidden="true"></i><span contenteditable="true" title="انقر للتعديل">إدارة وقت ذكية تحت الضغط</span></li>
                <li><i class="fa-solid fa-circle-check" aria-hidden="true"></i><span contenteditable="true" title="انقر للتعديل">مهارات تركيز واختيار الإجابة</span></li>
            </ul>
        </section>

        <!-- Trainers -->
        <section class="trainers-section">
            <div class="trainers-group">
                <h3 class="section-title"><i class="fa-solid fa-user-tie"></i> <span contenteditable="true" title="انقر للتعديل">قسم الطلاب (المدربين)</span></h3>
                <div class="trainers-cards">
                    <div class="trainer-card trainer-red">
                        <h4 class="trainer-name" contenteditable="true" title="انقر للتعديل">د. فهد الزماي</h4>
                    </div>
                    <div class="trainer-card trainer-teal">
                        <h4 class="trainer-name" contenteditable="true" title="انقر للتعديل">أ. سعد اللويش</h4>
                    </div>
                    <div class="trainer-card trainer-red">
                        <h4 class="trainer-name" contenteditable="true" title="انقر للتعديل">أ. مشاري العديم</h4>
                    </div>
                </div>
            </div>

            <div class="trainers-group">
                <h3 class="section-title"><i class="fa-solid fa-user-graduate"></i> <span contenteditable="true" title="انقر للتعديل">قسم الطالبات (المدربات)</span></h3>
                <div class="trainers-cards">
                    <div class="trainer-card trainer-teal">
                        <h4 class="trainer-name" contenteditable="true" title="انقر للتعديل">أ. موضي الشمري</h4>
                    </div>
                    <div class="trainer-card trainer-red">
                        <h4 class="trainer-name" contenteditable="true" title="انقر للتعديل">أ. نوف الشمري</h4>
                    </div>
                </div>
            </div>
        </section>

        <!-- Schedule & Details -->
        <section class="details-section">
            <div class="detail-box date-box">
                <div class="icon"><i class="fa-regular fa-calendar-days"></i></div>
                <div class="content" contenteditable="true" title="انقر للتعديل">
                    الانطلاق يوم الاحد تاريخ <strong>9 / 4 / 1448 هـ</strong>
                </div>
            </div>
            
            <div class="detail-box duration-box">
                <div class="icon"><i class="fa-solid fa-hourglass-half"></i></div>
                <div class="content" contenteditable="true" title="انقر للتعديل">
                    <strong>خمسة أسابيع</strong>
                </div>
            </div>

            <div class="detail-box time-box">
                <div class="icon"><i class="fa-regular fa-clock"></i></div>
                <div class="content" contenteditable="true" title="انقر للتعديل">
                    30 ساعة تدريبية - ثلاثة أيام بالأسبوع - <strong>4:30 عصرا إلى 6:30 مساءً</strong>
                </div>
            </div>
        </section>

        <!-- Pricing -->
        <section class="pricing-section">
            <div class="price-normal" contenteditable="true" title="انقر للتعديل">السعر: 949 ريال</div>
            <div class="price-early" contenteditable="true" title="انقر للتعديل">التسجيل المبكر: <span>749 ريال</span></div>
        </section>

        <!-- Contact & Footer -->
        <footer class="footer">
            <div class="registration">
                <span class="label" contenteditable="true" title="انقر للتعديل">للتسجيل:</span>
                <span class="number" dir="ltr" contenteditable="true" title="انقر للتعديل">055 381 1717</span>
            </div>
            <p class="slogan" contenteditable="true" title="انقر للتعديل">معاً نحو قدرات أعلى .. ومستقبل أوسع</p>
        </footer>
    </div>

    <!-- كود الجافاسكربت للتعديل وتصدير PDF بالخلفية bg_4.jpg المطلوبة -->
    <script>
        const BG_IMAGE_DATA = "{bg4_b64}";
        let initialFlyerHTML = '';
        
        window.addEventListener('DOMContentLoaded', () => {{
            const flyer = document.getElementById('flyer-card');
            if (flyer) {{
                initialFlyerHTML = flyer.innerHTML;
            }}
        }});

        function resetContent() {{
            const flyer = document.getElementById('flyer-card');
            if (flyer && initialFlyerHTML) {{
                flyer.innerHTML = initialFlyerHTML;
            }}
        }}

        async function downloadPDF(withBackground = true) {{
            const btn = document.getElementById('download-pdf-btn');
            const textSpan = document.getElementById('download-text');
            const originalText = textSpan.innerText;
            
            // إزالة أي تحديد أو مؤشر كتابة نشط
            if (document.activeElement) {{
                document.activeElement.blur();
            }}
            if (window.getSelection) {{
                window.getSelection().removeAllRanges();
            }}

            textSpan.innerText = 'جاري التصدير...';
            btn.style.opacity = '0.7';
            btn.style.pointerEvents = 'none';

            try {{
                const flyer = document.getElementById('flyer-card');
                let targetElement;
                let removeWrapper = false;
                
                if (withBackground) {{
                    // إنشاء حاوية لتصدير الإعلان بكامل الخلفية bg_4.jpg بدقة فائقة
                    const flyerClone = flyer.cloneNode(true);
                    flyerClone.querySelectorAll('[contenteditable]').forEach(el => {{
                        el.removeAttribute('contenteditable');
                    }});
                    
                    const wrapper = document.createElement('div');
                    wrapper.id = 'export-bg-wrapper';
                    wrapper.style.position = 'fixed';
                    wrapper.style.left = '-9999px';
                    wrapper.style.top = '0';
                    wrapper.style.width = '1080px';
                    wrapper.style.minHeight = '1450px';
                    wrapper.style.display = 'flex';
                    wrapper.style.justifyContent = 'center';
                    wrapper.style.alignItems = 'center';
                    wrapper.style.padding = '40px 30px';
                    wrapper.style.backgroundImage = 'linear-gradient(rgba(23, 39, 54, 0.25), rgba(23, 39, 54, 0.25)), url("' + BG_IMAGE_DATA + '")';
                    wrapper.style.backgroundRepeat = 'no-repeat';
                    wrapper.style.backgroundPosition = 'center center';
                    wrapper.style.backgroundSize = 'cover';
                    
                    wrapper.appendChild(flyerClone);
                    document.body.appendChild(wrapper);
                    
                    targetElement = wrapper;
                    removeWrapper = true;
                }} else {{
                    targetElement = flyer;
                }}

                // تحويل التصميم إلى Canvas بجودة مضاعفة
                const canvas = await html2canvas(targetElement, {{
                    scale: 2,
                    useCORS: true,
                    logging: false
                }});

                if (removeWrapper && targetElement.parentNode) {{
                    document.body.removeChild(targetElement);
                }}

                const imgData = canvas.toDataURL('image/jpeg', 0.95);
                const {{ jsPDF }} = window.jspdf;

                // إنشاء ملف PDF من صفحة واحدة
                const pdf = new jsPDF({{
                    orientation: 'portrait',
                    unit: 'px',
                    format: [canvas.width / 2, canvas.height / 2]
                }});

                pdf.addImage(imgData, 'JPEG', 0, 0, canvas.width / 2, canvas.height / 2);
                pdf.save('إعلان_دورة_القدرات.pdf');
            }} catch (err) {{
                console.error('PDF export error:', err);
                alert('حدث خطأ أثناء تحميل ملف الـ PDF، يرجى المحاولة مجدداً.');
            }} finally {{
                textSpan.innerText = originalText;
                btn.style.opacity = '1';
                btn.style.pointerEvents = 'auto';
            }}
        }}
    </script>
</body>
</html>
"""

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

with open('final_client_app.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

print("SUCCESS: index.html and final_client_app.html created with bg_4.jpg embedded!")
