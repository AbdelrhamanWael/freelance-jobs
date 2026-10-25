# =============================================================================
#  category_dictionary.py — قاموس مطابقة التصنيفات للمنصات الثلاث
# =============================================================================

# خرائط مطابقة تصنيفات متجر "قطاف الطبيعة" لأمازون، نون، وترينديول

CATEGORY_MAP = {
    "عسل": {
        "amazon": {
            "browse_node": "16402371031",
            "item_type": "honey",
            "product_type": "GROCERY",
            "path_en": "Grocery & Gourmet Food > Cooking & Baking Supplies > Syrups, Sugars & Sweeteners > Honeys",
            "path_ar": "البقالة والأغذية الفاخرة > لوازم الطبخ والخبز > عسل",
        },
        "noon": {
            "category_code": "honey_and_spreads",
            "category_name_ar": "بقالة ومستلزمات > عسل ومحليات طبيعية",
            "family_code": "NOON_HONEY",
        },
        "trendyol": {
            "category_id": "103856",
            "category_name": "Süpermarket > Bal ve Reçel",
            "category_name_ar": "سوبرماركت > عسل ومربى",
        },
    },
    "اعشاب": {
        "amazon": {
            "browse_node": "16402364031",
            "item_type": "herbs-and-spices",
            "product_type": "GROCERY",
            "path_en": "Grocery & Gourmet Food > Herbs, Spices & Seasonings > Whole Herbs",
            "path_ar": "البقالة والأغذية الفاخرة > أعشاب وتوابل وبهارات",
        },
        "noon": {
            "category_code": "herbs_and_spices",
            "category_name_ar": "بقالة ومستلزمات > أعشاب وبهارات طبيعية",
            "family_code": "NOON_HERBS",
        },
        "trendyol": {
            "category_id": "103854",
            "category_name": "Süpermarket > Baharat ve Şifalı Bitkiler",
            "category_name_ar": "سوبرماركت > أعشاب ونباتات طبية",
        },
    },
    "بهارات": {
        "amazon": {
            "browse_node": "16402364031",
            "item_type": "seasoning-and-spices",
            "product_type": "GROCERY",
            "path_en": "Grocery & Gourmet Food > Herbs, Spices & Seasonings",
            "path_ar": "البقالة والأغذية الفاخرة > بهارات وتوابل",
        },
        "noon": {
            "category_code": "cooking_essentials_spices",
            "category_name_ar": "بقالة ومستلزمات > بهارات وتوابل الطبخ",
            "family_code": "NOON_SPICES",
        },
        "trendyol": {
            "category_id": "103854",
            "category_name": "Süpermarket > Baharat ve Çeşniler",
            "category_name_ar": "سوبرماركت > بهارات وتتبيلات",
        },
    },
    "العناية الشخصية": {
        "amazon": {
            "browse_node": "16400030031",
            "item_type": "hair-coloring-agent",
            "product_type": "BEAUTY",
            "path_en": "Beauty & Personal Care > Hair Care > Henna & Hair Treatments",
            "path_ar": "الجمال والعناية الشخصية > العناية بالشعر > حناء وعلاجات طبيعية",
        },
        "noon": {
            "category_code": "personal_care_hair_skin",
            "category_name_ar": "جمال وصحة > عناية شخصية وطبيعية",
            "family_code": "NOON_BEAUTY",
        },
        "trendyol": {
            "category_id": "104128",
            "category_name": "Kozmetik & Kişisel Bakım > Saç Bakımı",
            "category_name_ar": "مستحضرات تجميل > عناية بالشعر والجسم",
        },
    },
    "زيوت": {
        "amazon": {
            "browse_node": "16402366031",
            "item_type": "cooking-oil",
            "product_type": "GROCERY",
            "path_en": "Grocery & Gourmet Food > Cooking Oils, Vinegars & Sprays > Oils",
            "path_ar": "البقالة والأغذية الفاخرة > زيوت ومياه طبيعية",
        },
        "noon": {
            "category_code": "cooking_oils_ghee",
            "category_name_ar": "بقالة ومستلزمات > زيوت طبيعية للطبخ والعناية",
            "family_code": "NOON_OILS",
        },
        "trendyol": {
            "category_id": "103858",
            "category_name": "Süpermarket > Sıvı Yağlar",
            "category_name_ar": "سوبرماركت > زيوت طبيعية",
        },
    },
    "مشروبات": {
        "amazon": {
            "browse_node": "16402353031",
            "item_type": "tea",
            "product_type": "GROCERY",
            "path_en": "Grocery & Gourmet Food > Beverages > Coffee, Tea & Cocoa > Tea",
            "path_ar": "البقالة والأغذية الفاخرة > مشروبات > شاي ومشروبات عشبية",
        },
        "noon": {
            "category_code": "tea_and_herbal_drinks",
            "category_name_ar": "بقالة ومستلزمات > شاي ومشروبات ساخنة",
            "family_code": "NOON_TEA",
        },
        "trendyol": {
            "category_id": "103860",
            "category_name": "Süpermarket > Çay ve İçecekler",
            "category_name_ar": "سوبرماركت > شاي ومشروبات صحية",
        },
    },
    "عضوي": {
        "amazon": {
            "browse_node": "16402376031",
            "item_type": "organic-food-pantry",
            "product_type": "GROCERY",
            "path_en": "Grocery & Gourmet Food > Pantry Staples > Organic Foods",
            "path_ar": "البقالة والأغذية الفاخرة > منتجات عضوية",
        },
        "noon": {
            "category_code": "organic_health_foods",
            "category_name_ar": "بقالة ومستلزمات > منتجات عضوية وصحية",
            "family_code": "NOON_ORGANIC",
        },
        "trendyol": {
            "category_id": "103850",
            "category_name": "Süpermarket > Organik Gıda",
            "category_name_ar": "سوبرماركت > أغذية عضوية",
        },
    },
    "كيتو": {
        "amazon": {
            "browse_node": "16402376031",
            "item_type": "dietary-food",
            "product_type": "GROCERY",
            "path_en": "Grocery & Gourmet Food > Diet & Nutrition Foods > Keto Friendly",
            "path_ar": "البقالة والأغذية الفاخرة > منتجات الكيتو والحميات",
        },
        "noon": {
            "category_code": "keto_diet_foods",
            "category_name_ar": "بقالة ومستلزمات > أغذية حمية كيتو",
            "family_code": "NOON_KETO",
        },
        "trendyol": {
            "category_id": "103850",
            "category_name": "Süpermarket > Diyet ve Sağlıklı Yaşam",
            "category_name_ar": "سوبرماركت > أغذية حمية وصحة",
        },
    },
}

DEFAULT_CATEGORY_INFO = {
    "amazon": {
        "browse_node": "16402344031",
        "item_type": "pantry-staples",
        "product_type": "GROCERY",
        "path_en": "Grocery & Gourmet Food > Pantry Staples",
        "path_ar": "البقالة والأغذية الفاخرة > منتجات المونة والمطبخ",
    },
    "noon": {
        "category_code": "pantry_staples_general",
        "category_name_ar": "بقالة ومستلزمات > أطعمة وتموين",
        "family_code": "NOON_PANTRY",
    },
    "trendyol": {
        "category_id": "103850",
        "category_name": "Süpermarket > Temel Gıda",
        "category_name_ar": "سوبرماركت > منتجات المونة الغذائية",
    },
}


def match_category(salla_cat: str, product_name: str, platform: str) -> dict:
    """
    تطابق اسم التصنيف في سلة (مع فحص اسم المنتج عند الضرورة)
    وتعيد بيانات التصنيف الدقيقة للمنصة المستهدفة.
    """
    text_to_search = f"{salla_cat} {product_name}".lower()

    # أولوية المطابقة بالكلمات المفتاحية
    priority_keys = [
        ("عسل", "عسل"),
        ("بهارات", "بهارات"),
        ("توابل", "بهارات"),
        ("شاي", "مشروبات"),
        ("ماتشا", "مشروبات"),
        ("حناء", "العناية الشخصية"),
        ("سدر", "العناية الشخصية"),
        ("زيت", "زيوت"),
        ("مياه", "زيوت"),
        ("اعشاب", "اعشاب"),
        ("كيتو", "كيتو"),
        ("عضوي", "عضوي"),
        ("عناية", "العناية الشخصية"),
    ]

    for keyword, target_key in priority_keys:
        if keyword in text_to_search:
            return CATEGORY_MAP[target_key].get(platform, DEFAULT_CATEGORY_INFO[platform])

    return DEFAULT_CATEGORY_INFO.get(platform, {})
