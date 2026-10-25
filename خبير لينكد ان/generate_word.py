import docx

data = [
    ["محمد الحسيني", "أخصائي مبيعات أول", "رواء (Rewaa)", "https://www.linkedin.com/in/ACwAAEEmrzYBBnf2Gaz2Gf0Tp2p3gYcfPImXBZ8", "+سنتين", ""],
    ["علي الضحيان", "مدير مبيعات", "شركة الممتلكات الأفضل", "https://www.linkedin.com/in/ACwAAAq6PUIBuAzy2qqFCKirlOJyhcmBMslAuRc", "+سنتين", ""],
    ["حمد النقيدان", "مدير أول للمبيعات والتسويق", "MEFSCO", "https://www.linkedin.com/in/ACwAACHQqGMBRwICkf7R5fJY_CxMvwBKXyFkpKk", "+سنتين", ""],
    ["محمد مجدي", "مدير مبيعات إقليمي", "Gulf Polyester Powder Coating", "https://www.linkedin.com/in/ACwAAAn1_JwBwXeUcrWtn-vcYqbMPw3l3quS33c", "+سنتين", ""],
    ["شريف التلت", "مدير التسويق والتدريب", "شركة آدم الطبية", "https://www.linkedin.com/in/ACwAAC7wgj8BclfpGOOeYjJJKmVmaynCHUOGemY", "+سنتين", ""],
    ["هيثم الشاعر", "مدير مبيعات", "فيوليا لتقنية المياه", "https://www.linkedin.com/in/ACwAABvYeAsB483OAIyWIEPI8euCAn8qtKcshjs", "+سنتين", ""],
    ["فيصل عبد العزيز دجم", "مدير تسويق", "الرومانسية", "https://www.linkedin.com/in/ACwAADmXZiMB9Kw69uRYujyA_jKnYuqca75-Jqk", "+سنتين", ""],
    ["مشاعل بن جبرين", "مديرة تسويق أولى", "شركة حسم للتطوير العقاري", "https://www.linkedin.com/in/ACwAACR-zLABXhglJc-1MpfssPmQbB0DJXfftWI", "+سنتين", ""],
    ["مهنا أ.", "مدير مبيعات B2B", "الصافي دانون", "https://www.linkedin.com/in/ACwAACX6AdUB8D9mt-qtuZiGt9iR1LJ2BGTZX0Q", "+سنتين", ""],
    ["محمود يلدريم", "مدير مبيعات وتطوير الأعمال", "Sampa Automotive", "https://www.linkedin.com/in/ACwAACTFsXsBW-S-3VNL7WqC6ygfLQwtlfT28Gs", "+سنتين", ""],
    ["سامر غلاييني", "مدير تسويق", "Unimix SA", "https://www.linkedin.com/in/ACwAAA5300ABZ_YhqLj1MfihC91O4OesICVtWf4", "+سنتين", ""],
    ["أواب أحمد", "مدير مبيعات", "لوازم", "https://www.linkedin.com/in/ACwAABnsuasBFlw3MjZB_tQuL1E26ppKXqIQHIo", "+سنتين", ""],
    ["حسام السمري", "رئيس المبيعات", "Cleanplus International", "https://www.linkedin.com/in/ACwAAAXRdQ8BABMj_2-NDm-ZOMCJFo128kX31T0", "+سنتين", ""],
    ["سالم باطوق", "مدير مبيعات", "مقاهي", "https://www.linkedin.com/in/ACwAAC-Ks9sBAzSRE7Hkz-LtdH-kyNyrQwOSR6s", "+سنتين", ""],
    ["كريم داود", "مدير أول مبيعات حلول الشركات", "Advansys", "https://www.linkedin.com/in/ACwAAAVm-9sBsZXPp7uPSakwCGmykwhob-shQ8g", "+سنتين", ""],
    ["خالد ربيع", "أخصائي مبيعات", "ركاز", "https://www.linkedin.com/in/ACwAACevi1cBNcMd56APUFdXjI8OmkJXyNUPRng", "+سنتين", ""],
    ["خالد الزهراني", "مدير تطوير المبيعات", "FlyAkeed", "https://www.linkedin.com/in/ACwAABKnkQsBYxyTaLrTrW61De5HfduS9AQ1OLg", "+سنتين", ""],
    ["ظفر شمس الدينوف", "مدير مبيعات الشركات", "Rubrik", "https://www.linkedin.com/in/ACwAAAPzrxIBh5t_yVvAETT5lEn47GidIT7vJVM", "+سنتين", ""],
    ["يوسف محمود", "مدير مبيعات تقنية أول", "Bayzat", "https://www.linkedin.com/in/ACwAAFSfHxcBjEp4CUu4gwi4MN_6_W4cybH-p5I", "+سنتين", ""],
    ["شريف درويش", "مدير تسويق", "الدهام", "https://www.linkedin.com/in/ACwAAAZyFsgBehCyzQS4Jo0LSACFyVPG2dELmGk", "+سنتين", ""],
    ["إبراهيم القدومي", "مدير مبيعات إقليمي", "Planar International", "https://www.linkedin.com/in/ACwAAAPPLgYBbkkl45mXAZQz0mbi6yp3bJj2xZc", "+سنتين", ""],
    ["مهند حيدر", "خبير مبيعات وتطوير أعمال", "معين لتوظيف المواهب", "https://www.linkedin.com/in/ACwAACKNlpwBde8iQBMM7rzF-i8XbSiRDNnrBsU", "+سنتين", ""],
    ["وسام ز.", "مدير مبيعات الشركات", "الفالح للرياضة", "https://www.linkedin.com/in/ACwAACn3_zYB1FVna8JWHgBdm1f5rQwlSF7fq4w", "+سنتين", ""],
    ["محمود س.", "مدير النمو", "دفاتر", "https://www.linkedin.com/in/ACwAABVLwE4B848mQ9ej__IAAiqo5bxu0UOlptU", "+سنتين", ""],
    ["عبد القادر الزبيدي", "مدير مشاريع التسويق", "دار الأميرات", "https://www.linkedin.com/in/ACwAADQwsBUBi-cAjKGc10RfQ7iHCAWkyBDlhTM", "+سنتين", ""],
    ["محمد أبو رمشان", "مدير مبيعات المملكة", "Hira Industries", "https://www.linkedin.com/in/ACwAABfnx54BSS7XoKKT_ccF-HedI0uZfafnL2I", "+سنتين", ""],
    ["محمد طه", "مدير مبيعات إقليمي", "سري (Confidential)", "https://www.linkedin.com/in/ACwAAAy0tsIBZANyurHJCK-rZcrG8Qcf3CLyMGY", "+سنتين", ""],
    ["حسين شنير", "مدير مبيعات وتطوير الأعمال", "سيمنز", "https://www.linkedin.com/in/ACwAAA-uu_8Bm_LoC8fO8n9Ag33hUlgHYgJtxOQ", "+سنتين", ""],
    ["ضياء عبد العظيم", "مدير مبيعات B2B", "مجموعة العايد", "https://www.linkedin.com/in/ACwAABuKKZ8B1pUIaXTdttVG9pzXUGtUm6jKFrg", "+سنتين", ""],
    ["محمد رفاعي", "مدير مبيعات", "TSAB LLC", "https://www.linkedin.com/in/ACwAABV0i7UBpIMEd7VxZGG5RwgW95q5OXCk178", "+سنتين", ""],
    ["مرام أ.", "مديرة تسويق أولى", "سري (Confidential)", "https://www.linkedin.com/in/ACwAACUG_ocBiddAwbRXq5EyiUmQw5Qe-cL-92M", "+سنتين", ""],
    ["رائد الزهراني", "مدير مبيعات أول", "سلام", "https://www.linkedin.com/in/ACwAACn1nnEBjoSbfkEDLBfO94iT7FYRZZ8SsF4", "+سنتين", ""],
    ["محمد الثبيتي", "مدير مبيعات إقليمي", "AVIS السعودية", "https://www.linkedin.com/in/ACwAAAOvnb4B5s80bwjgFwnK6dBM-suuqQ3NFFY", "+سنتين", ""],
    ["شريف عطية", "مدير مبيعات إقليمي", "دهانات الجزيرة", "https://www.linkedin.com/in/ACwAAAleCikBgyCGDg2QTIBnhxjik_gAD-ABEYw", "+سنتين", ""],
    ["عمر القاضي", "مدير مبيعات المملكة", "DDN", "https://www.linkedin.com/in/ACwAAAXshCYBKMJ47RD9LxAgiKG84LP8ip0xW7E", "+سنتين", ""],
    ["موفق نجم", "مدير مبيعات B2B أول", "سامسونج", "https://www.linkedin.com/in/ACwAACDA7ocBdUC2ttMpLUbjmOO9mhUxiMZiNBM", "+سنتين", ""],
    ["محمد عبد العزيز", "مدير مبيعات إقليمي", "مجموعة العمودي", "https://www.linkedin.com/in/ACwAABO890MBw7lCR0uqombQKUwPPPh6GAEuQJQ", "+سنتين", ""],
    ["محمد كايد", "رئيس المبيعات وتطوير الأعمال", "شركة منافذ", "https://www.linkedin.com/in/ACwAACI56NwBFiNY8viPNMzn_AUeAerZV85L1a4", "+سنتين", ""],
    ["السيد عامر", "مدير تسويق", "سبيماكو", "https://www.linkedin.com/in/ACwAAA2Pu7sBe3y5_mrSHZka3l-L6lvaIoZU0Bo", "+سنتين", ""],
    ["مهند تاتان", "مدير التجزئة", "هواوي", "https://www.linkedin.com/in/ACwAABClN1kBkJ3mt-eQukkgHBQ-IZgYwCza1tY", "+سنتين", ""],
    ["أسماء القحطاني", "أخصائية مبيعات B2B", "شركة معارض الرياض", "https://www.linkedin.com/in/ACwAAER5FokB5qdXNuI15ri4MzyECTYWFryQRkk", "+سنتين", ""],
    ["مروان زيدان", "مدير مبيعات وتطوير الأعمال", "غرس", "https://www.linkedin.com/in/ACwAAC7oYI4B5wRZgBkH5U8xAl27BQLUqVagQnM", "+سنتين", ""],
    ["سعود السدحان", "مدير مبيعات B2B", "stc", "https://www.linkedin.com/in/ACwAADJYUwsBx1ab6DYwtDZVDSO_vYCaf7X-rbk", "+سنتين", ""],
    ["بول كابريليان", "مدير المبيعات وتطوير الأعمال", "SPAN Group", "https://www.linkedin.com/in/ACwAABba9rkBbLicmJW40GWeIUxPmV-xaIfNPow", "+سنتين", ""],
    ["أحمد مرسلة", "مدير مبيعات", "Value Plus", "https://www.linkedin.com/in/ACwAAATjlK0Bz0iUu1wtp-fFmGL0CqegXUslWsg", "+سنتين", ""],
    ["أحمد سمير", "مدير مبيعات إقليمي", "مجموعة باشا الطبية", "https://www.linkedin.com/in/ACwAACFnu3EB-XxfRub4yNJGPUS742Xpq_dRMJY", "+سنتين", ""],
    ["عاصم القصاص", "مدير مبيعات", "Tempesta Hospitality", "https://www.linkedin.com/in/ACwAACAXpsQBh3zaKjRsTito78qZTUVldC0_YPw", "+سنتين", ""],
    ["عبد الله عبد الملك", "مدير تسويق", "متجر دار السلام", "https://www.linkedin.com/in/ACwAADttS2MBuUSO-4bHZGPxxYD_-GqpJkDJz1s", "+سنتين", ""],
    ["أسامة عوض", "مدير مبيعات المملكة", "شركة تطوير الطرق", "https://www.linkedin.com/in/ACwAAANbU3wB5VPeHS8hs0x0nqXQUljkCOh2Pkw", "+سنتين", ""],
    ["عامر العوض", "أخصائي مبيعات وتطوير أعمال", "وايدا", "https://www.linkedin.com/in/ACwAACJvrWUBkcWYfUNMP0kzKfgd_k2RwzH16Vs", "+سنتين", ""]
]

template_path = r"e:\MY PROJECT\Freelance Jobs\خبير لينكد ان\مرشحين-مبيعات-وتسويق.docx"
output_path = r"e:\MY PROJECT\Freelance Jobs\خبير لينكد ان\مرشحين-مبيعات-وتسويق-جاهز.docx"

doc = docx.Document(template_path)
table = doc.tables[0]

# remove empty rows (except header) if any
while len(table.rows) > 1:
    row = table.rows[-1]
    table._tbl.remove(row._tr)

for row_data in data:
    row = table.add_row()
    for idx, cell_text in enumerate(row_data):
        row.cells[idx].text = cell_text

doc.save(output_path)
print("Done! File saved as:", output_path)
