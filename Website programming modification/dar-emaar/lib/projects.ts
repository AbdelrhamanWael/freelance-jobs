/**
 * Static project data — replace content with real projects.
 * To add a project: duplicate one entry, change the slug, and
 * drop the PDF in /public/files/<slug>.pdf and images in /public/images/<slug>-*.jpg
 */

export type Project = {
  slug: string;
  title: string;
  category: string;
  location: string;
  client: string;
  duration: string;
  area: string;
  floors: string;
  year: string;
  description: string;
  scope: string[];
  images: string[]; // paths inside /public/
  thumbnailIndex: number; // which image to use as grid thumbnail
  attachmentFile: string | null; // path inside /public/ — null if no file
  attachmentLabel: string;
};

export const projects: Project[] = [
  {
    slug: "commercial-complex-riyadh",
    title: "مجمع مكاتب الواجهة التجارية",
    category: "مباني تجارية",
    location: "الرياض — حي العليا",
    client: "شركة الديار للتطوير",
    duration: "18 شهر",
    area: "4,500 م²",
    floors: "6 طوابق",
    year: "2023",
    description:
      "تصميم وبناء مجمع مكاتب من 6 طوابق بمساحة إجمالية تتجاوز 4,500 م²، شمل أعمال الهيكل الإنشائي الكامل والتشطيبات الداخلية الفاخرة وأنظمة الكهرباء والتكييف والسباكة وشبكات الإنترنت والأمن. تم التسليم في الموعد المحدد وبتكلفة ضمن الميزانية المتفق عليها.",
    scope: [
      "أعمال الهيكل الإنشائي الخرساني",
      "التشطيبات الداخلية والخارجية",
      "أنظمة التكييف المركزي",
      "أنظمة الكهرباء وإنارة LED",
      "شبكات السباكة والصرف الصحي",
      "أنظمة الأمن والمراقبة",
      "مواقف سيارات بطابقين",
    ],
    images: [
      "/images/project-1.jpg",
      "/images/project-2.jpg",
      "/images/project-3.jpg",
    ],
    thumbnailIndex: 0,
    attachmentFile: "/files/commercial-complex-riyadh.pdf",
    attachmentLabel: "تحميل ملف المشروع (PDF)",
  },
  {
    slug: "luxury-villa-jeddah",
    title: "فيلا سكنية فاخرة",
    category: "مباني سكنية",
    location: "جدة — حي الشاطئ",
    client: "عميل خاص",
    duration: "14 شهر",
    area: "1,200 م²",
    floors: "3 طوابق",
    year: "2024",
    description:
      "تصميم وتنفيذ فيلا سكنية فاخرة بطراز معماري عصري، تشمل حديقة خارجية ومسبح ومجلس مستقل وغرف نوم فاخرة مع تشطيبات راقية من الرخام الإيطالي والخشب الطبيعي.",
    scope: [
      "التصميم المعماري والداخلي",
      "أعمال البناء والمقاولات",
      "تشطيبات رخام إيطالي",
      "أنظمة المنزل الذكي",
      "تنسيق الحدائق الخارجية",
      "إنشاء المسبح والملحقات",
    ],
    images: [
      "/images/project-2.jpg",
      "/images/project-4.jpg",
    ],
    thumbnailIndex: 0,
    attachmentFile: "/files/luxury-villa-jeddah.pdf",
    attachmentLabel: "تحميل ملف المشروع (PDF)",
  },
  {
    slug: "infrastructure-madinah",
    title: "مشروع بنية تحتية",
    category: "بنية تحتية",
    location: "المدينة المنورة",
    client: "أمانة المدينة المنورة",
    duration: "24 شهر",
    area: "12,000 م²",
    floors: "—",
    year: "2022",
    description:
      "تنفيذ مشروع بنية تحتية شامل يتضمن شبكات الصرف الصحي والمياه والكهرباء وتمهيد الطرق وتركيب إنارة الشوارع لمنطقة سكنية جديدة.",
    scope: [
      "أعمال الحفر والردم",
      "شبكات الصرف الصحي",
      "خطوط المياه والري",
      "كابلات الكهرباء الأرضية",
      "تمهيد وأسفلت الطرق",
      "إنارة الشوارع",
    ],
    images: [
      "/images/project-3.jpg",
      "/images/project-5.jpg",
    ],
    thumbnailIndex: 0,
    attachmentFile: null,
    attachmentLabel: "",
  },
  {
    slug: "interior-finishing-compound",
    title: "تشطيبات كمبوند سكني",
    category: "تشطيبات داخلية",
    location: "الرياض — حي قرطبة",
    client: "شركة إتقان للتطوير",
    duration: "10 أشهر",
    area: "8,000 م²",
    floors: "—",
    year: "2024",
    description:
      "تشطيب داخلي كامل لـ 40 وحدة سكنية في كمبوند سكني متكامل، يشمل الدهانات والأسقف الجبسية والأرضيات والحمامات والمطابخ وجميع التمديدات الكهربائية والصحية.",
    scope: [
      "40 وحدة سكنية كاملة",
      "أسقف جبسية بتصاميم متنوعة",
      "دهانات عازلة للحرارة والرطوبة",
      "أرضيات بورسلان وخشب",
      "تجهيز الحمامات والمطابخ",
      "تمديدات كهربائية وصحية",
    ],
    images: [
      "/images/project-4.jpg",
      "/images/project-6.jpg",
    ],
    thumbnailIndex: 0,
    attachmentFile: "/files/interior-finishing-compound.pdf",
    attachmentLabel: "تحميل كتالوج التشطيبات",
  },
  {
    slug: "project-management-tower",
    title: "إدارة مشروع برج سكني",
    category: "إدارة مشاريع",
    location: "جدة — كورنيش",
    client: "مجموعة المملكة هولدينج",
    duration: "36 شهر",
    area: "22,000 م²",
    floors: "22 طابق",
    year: "2023",
    description:
      "تولي إدارة مشروع برج سكني فاخر من 22 طابقاً بالكامل، من مرحلة التخطيط والتصميم حتى التسليم النهائي، مع الإشراف على جميع المقاولين من الباطن وإدارة الجداول الزمنية والميزانية.",
    scope: [
      "إدارة المشروع من الألف إلى الياء",
      "تنسيق وإشراف على 12 مقاولاً",
      "إدارة الجدول الزمني والميزانية",
      "تقارير دورية أسبوعية وشهرية",
      "ضمان جودة المخرجات",
      "التسليم النهائي والتوثيق",
    ],
    images: [
      "/images/project-5.jpg",
      "/images/project-1.jpg",
    ],
    thumbnailIndex: 0,
    attachmentFile: null,
    attachmentLabel: "",
  },
  {
    slug: "solar-energy-factory",
    title: "تركيب طاقة شمسية لمصنع",
    category: "طاقة متجددة",
    location: "الرياض — المنطقة الصناعية الثانية",
    client: "شركة KWIN الصناعية",
    duration: "4 أشهر",
    area: "3,000 م² أسطح",
    floors: "—",
    year: "2024",
    description:
      "تركيب منظومة طاقة شمسية متكاملة على أسطح مصنع بمساحة 3,000 م² بقدرة إنتاجية 500 كيلوواط، مما يوفر 70% من استهلاك الكهرباء ويخفض التكاليف التشغيلية.",
    scope: [
      "تركيب 1,200 لوح شمسي",
      "أنظمة العواكس والتخزين",
      "ربط بالشبكة الكهربائية",
      "نظام مراقبة ذكي عن بعد",
      "صيانة دورية لمدة عام",
    ],
    images: [
      "/images/project-6.jpg",
      "/images/project-3.jpg",
    ],
    thumbnailIndex: 0,
    attachmentFile: "/files/solar-energy-factory.pdf",
    attachmentLabel: "تحميل تقرير الطاقة الشمسية",
  },
];

export function getProjectBySlug(slug: string): Project | undefined {
  return projects.find((p) => p.slug === slug);
}
