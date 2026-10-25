import pandas as pd
from datetime import datetime

# All job data from LinkedIn searches
all_jobs = []

# Search 1: Embedded AI Intern PhD 2027
all_jobs.extend([
    {"title": "Embedded Machine Learning & Radar Processing Intern - Summer 2027", "company": "NXP Semiconductors", "location": "San Jose, CA", "time": "2 days ago", "url": "https://www.linkedin.com/jobs/view/embedded-machine-learning-radar-processing-intern-summer-2027-at-nxp-semiconductors-4464090607", "search_term": "Embedded AI Intern PhD 2027"},
    {"title": "Radar Sensing AI Research Intern", "company": "Bosch USA", "location": "Pittsburgh, PA", "time": "2 days ago", "url": "https://www.linkedin.com/jobs/view/radar-sensing-ai-research-intern-at-bosch-usa-4471206010", "search_term": "Embedded AI Intern PhD 2027"},
    {"title": "AI Perception Intern (PICO) - 2027 Start (PhD)", "company": "ByteDance", "location": "San Jose, CA", "time": "3 hours ago", "url": "https://www.linkedin.com/jobs/view/ai-perception-intern-pico-2027-start-phd-at-bytedance-4473974856", "search_term": "Embedded AI Intern PhD 2027"},
    {"title": "PhD Research Intern, Generalist Embodied Agents Research - 2027", "company": "NVIDIA", "location": "Santa Clara, CA", "time": "1 week ago", "url": "https://www.linkedin.com/jobs/view/phd-research-intern-generalist-embodied-agents-research-2027-at-nvidia-4467819359", "search_term": "Embedded AI Intern PhD 2027"},
    {"title": "PhD Research Intern, Autonomous Systems and Physical AI Research - 2027", "company": "NVIDIA", "location": "Santa Clara, CA", "time": "2 weeks ago", "url": "https://www.linkedin.com/jobs/view/phd-research-intern-autonomous-systems-and-physical-ai-research-2027-at-nvidia-4465702327", "search_term": "Embedded AI Intern PhD 2027"},
    {"title": "Software Algorithm Embedded Intern", "company": "STMicroelectronics", "location": "Santa Clara, CA", "time": "1 day ago", "url": "https://www.linkedin.com/jobs/view/software-algorithm-embedded-intern-at-stmicroelectronics-4473568575", "search_term": "Embedded AI Intern PhD 2027"},
    {"title": "Embedded AI Firmware Co-Op", "company": "Schneider Electric", "location": "Andover, MA", "time": "1 week ago", "url": "https://www.linkedin.com/jobs/view/embedded-ai-firmware-co-op-at-schneider-electric-4467874984", "search_term": "Embedded AI Intern PhD 2027"},
    {"title": "Autonomous Driving Applications Research Intern", "company": "Nissan Motor Corporation", "location": "N/A", "time": "1 day ago", "url": "https://www.linkedin.com/jobs/view/autonomous-driving-applications-research-intern-at-nissan-motor-corporation-4418153214", "search_term": "Embedded AI Intern PhD 2027"},
    {"title": "Machine Learning & Artificial Intelligence Engineering Internship – Summer 2027", "company": "Qualcomm", "location": "N/A", "time": "1 week ago", "url": "https://www.linkedin.com/jobs/view/machine-learning-artificial-intelligence-engineering-internship-summer-2027-at-qualcomm-4468095266", "search_term": "Embedded AI Intern PhD 2027"},
    {"title": "2027 Internship – Engineering/Science – Tailored Autonomous Systems", "company": "Johns Hopkins Applied Physics Laboratory", "location": "N/A", "time": "2 weeks ago", "url": "https://www.linkedin.com/jobs/view/2027-internship-engineering-science-tailored-autonomous-systems-at-johns-hopkins-applied-physics-laboratory-4463934414", "search_term": "Embedded AI Intern PhD 2027"},
    {"title": "Algorithm Engineer Intern", "company": "VisLab (an Ambarella Inc. company)", "location": "N/A", "time": "1 month ago", "url": "https://www.linkedin.com/jobs/view/algorithm-engineer-intern-at-vislab-an-ambarella-inc-company-4459840393", "search_term": "Embedded AI Intern PhD 2027"},
    {"title": "Audio AI Engineering Intern-Summer 2027", "company": "Skyworks Solutions, Inc.", "location": "N/A", "time": "1 month ago", "url": "https://www.linkedin.com/jobs/view/audio-ai-engineering-intern-summer-2027-at-skyworks-solutions-inc-4454837251", "search_term": "Embedded AI Intern PhD 2027"},
    {"title": "AI Vision Research Scientist Intern - Global Frontier Tech Recruitment Program - 2027 Start (PHD)", "company": "ByteDance", "location": "N/A", "time": "1 day ago", "url": "https://www.linkedin.com/jobs/view/ai-vision-research-scientist-intern-global-frontier-tech-recruitment-program-2027-start-phd-at-bytedance-4435836915", "search_term": "Embedded AI Intern PhD 2027"},
    {"title": "2027 Summer Intern, PhD, Machine Learning, Computer Vision", "company": "Waymo", "location": "N/A", "time": "2 weeks ago", "url": "https://www.linkedin.com/jobs/view/2027-summer-intern-phd-machine-learning-computer-vision-at-waymo-4464832342", "search_term": "Embedded AI Intern PhD 2027"},
    {"title": "Intern - Engineering ADAS Perception Features", "company": "Magna International", "location": "N/A", "time": "2 weeks ago", "url": "https://www.linkedin.com/jobs/view/intern-engineering-adas-perception-features-at-magna-international-4466557740", "search_term": "Embedded AI Intern PhD 2027"},
    {"title": "Summer 2027 - Software Engineer Intern", "company": "Shield AI", "location": "N/A", "time": "2 weeks ago", "url": "https://www.linkedin.com/jobs/view/summer-2027-software-engineer-intern-at-shield-ai-4465604643", "search_term": "Embedded AI Intern PhD 2027"},
    {"title": "AI Intern", "company": "Oshkosh Corporation", "location": "N/A", "time": "2 weeks ago", "url": "https://www.linkedin.com/jobs/view/ai-intern-at-oshkosh-corporation-4465420039", "search_term": "Embedded AI Intern PhD 2027"},
    {"title": "Autonomy Engineering Intern", "company": "JLG Industries", "location": "N/A", "time": "2 weeks ago", "url": "https://www.linkedin.com/jobs/view/autonomy-engineering-intern-at-jlg-industries-4465598332", "search_term": "Embedded AI Intern PhD 2027"},
    {"title": "2027 Summer Intern, MS/PhD, Software Engineer, Sys Intel & Machine Learning", "company": "Waymo", "location": "N/A", "time": "5 days ago", "url": "https://www.linkedin.com/jobs/view/2027-summer-intern-ms-phd-software-engineer-sys-intel-machine-learning-at-waymo-4470720097", "search_term": "Embedded AI Intern PhD 2027"},
    {"title": "Software Engineering Intern", "company": "Shure", "location": "N/A", "time": "6 days ago", "url": "https://www.linkedin.com/jobs/view/software-engineering-intern-at-shure-4461391646", "search_term": "Embedded AI Intern PhD 2027"},
    {"title": "2027 PhD ML System Engineering Intern/Co-op", "company": "AMD", "location": "N/A", "time": "2 weeks ago", "url": "https://www.linkedin.com/jobs/view/2027-phd-ml-system-engineering-intern-co-op-at-amd-4464240966", "search_term": "Embedded AI Intern PhD 2027"}
])

# Search 2: TinyML Intern 2027 (unique jobs)
all_jobs.extend([
    {"title": "Engineering Intern (Spring 2027)", "company": "SRC", "location": "N/A", "time": "2 weeks ago", "url": "https://www.linkedin.com/jobs/view/engineering-intern-spring-2027-at-src-4457281278", "search_term": "TinyML Intern 2027"},
    {"title": "NVIDIA 2027 Internships: Autonomous Vehicles and Robotics", "company": "NVIDIA", "location": "N/A", "time": "2 weeks ago", "url": "https://www.linkedin.com/jobs/view/nvidia-2027-internships-autonomous-vehicles-and-robotics-at-nvidia-4455473273", "search_term": "TinyML Intern 2027"},
    {"title": "Software Development Engineer Intern", "company": "VisLab (an Ambarella Inc. company)", "location": "N/A", "time": "1 month ago", "url": "https://www.linkedin.com/jobs/view/software-development-engineer-intern-at-vislab-an-ambarella-inc-company-4459834459", "search_term": "TinyML Intern 2027"},
    {"title": "Engineering Intern (Summer 2027)", "company": "SRC", "location": "N/A", "time": "1 week ago", "url": "https://www.linkedin.com/jobs/view/engineering-intern-summer-2027-at-src-4459534762", "search_term": "TinyML Intern 2027"},
    {"title": "Software Engineering Intern, Connectivity (Summer 2027)", "company": "HP IQ", "location": "N/A", "time": "6 days ago", "url": "https://www.linkedin.com/jobs/view/software-engineering-intern-connectivity-summer-2027-at-hp-iq-4462075245", "search_term": "TinyML Intern 2027"},
    {"title": "NVIDIA 2027 Internships: Deep Learning", "company": "NVIDIA", "location": "N/A", "time": "2 weeks ago", "url": "https://www.linkedin.com/jobs/view/nvidia-2027-internships-deep-learning-at-nvidia-4455493097", "search_term": "TinyML Intern 2027"}
])

# Search 3: Edge AI Intern PhD 2027 (unique jobs)
all_jobs.extend([
    {"title": "PhD Research Intern, Fundamental Generative AI - 2027", "company": "NVIDIA", "location": "N/A", "time": "2 weeks ago", "url": "https://www.linkedin.com/jobs/view/phd-research-intern-fundamental-generative-ai-2027-at-nvidia-4466588638", "search_term": "Edge AI Intern PhD 2027"},
    {"title": "PhD Research Intern, Physical AI - Foundation Models - 2027", "company": "NVIDIA", "location": "N/A", "time": "2 weeks ago", "url": "https://www.linkedin.com/jobs/view/phd-research-intern-physical-ai-foundation-models-2027-at-nvidia-4466805414", "search_term": "Edge AI Intern PhD 2027"},
    {"title": "Ph.D. Intern - AI/ML & Design Automation", "company": "Marvell Technology", "location": "N/A", "time": "2 weeks ago", "url": "https://www.linkedin.com/jobs/view/ph-d-intern-ai-ml-design-automation-at-marvell-technology-4463928066", "search_term": "Edge AI Intern PhD 2027"},
    {"title": "2027 PhD AI Model Optimization & Software Engineer Intern/Co-op", "company": "AMD", "location": "N/A", "time": "2 weeks ago", "url": "https://www.linkedin.com/jobs/view/2027-phd-ai-model-optimization-software-engineer-intern-co-op-at-amd-4466224533", "search_term": "Edge AI Intern PhD 2027"},
    {"title": "Research Intern, PhD (AI, Robotics)", "company": "Dexmate", "location": "N/A", "time": "2 weeks ago", "url": "https://www.linkedin.com/jobs/view/research-intern-phd-ai-robotics-at-dexmate-4375109645", "search_term": "Edge AI Intern PhD 2027"}
])

# Search 4: Firmware Engineer Intern PhD 2027 (unique jobs)
all_jobs.extend([
    {"title": "SSD Firmware Development Engineer Intern", "company": "SK hynix memory solutions America Inc.", "location": "N/A", "time": "1 week ago", "url": "https://www.linkedin.com/jobs/view/ssd-firmware-development-engineer-intern-at-sk-hynix-memory-solutions-america-inc-4461225859", "search_term": "Firmware Engineer Intern PhD 2027"},
    {"title": "Embedded Software Engineer Intern - Fall 2026", "company": "Castelion", "location": "N/A", "time": "3 weeks ago", "url": "https://www.linkedin.com/jobs/view/embedded-software-engineer-intern-fall-2026-at-castelion-4468299424", "search_term": "Firmware Engineer Intern PhD 2027"},
    {"title": "Embedded Systems Firmware Engineering Intern (Graduates & U.S. Persons Only)", "company": "ELDAEON INC.", "location": "N/A", "time": "2 weeks ago", "url": "https://www.linkedin.com/jobs/view/embedded-systems-firmware-engineering-intern-graduates-u-s-persons-only-at-eldaeon-inc-4466163775", "search_term": "Firmware Engineer Intern PhD 2027"},
    {"title": "Software and Electronics Engineering Intern (Summer 2027) - Group 76", "company": "MIT Lincoln Laboratory", "location": "N/A", "time": "1 week ago", "url": "https://www.linkedin.com/jobs/view/software-and-electronics-engineering-intern-summer-2027-group-76-at-mit-lincoln-laboratory-4469227159", "search_term": "Firmware Engineer Intern PhD 2027"},
    {"title": "2027 Masters Firmware Engineering Intern/Co-op", "company": "AMD", "location": "N/A", "time": "1 month ago", "url": "https://www.linkedin.com/jobs/view/2027-masters-firmware-engineering-intern-co-op-at-amd-4454168242", "search_term": "Firmware Engineer Intern PhD 2027"},
    {"title": "Embedded Security Intern - Electronics Prototype", "company": "MITRE", "location": "N/A", "time": "3 weeks ago", "url": "https://www.linkedin.com/jobs/view/embedded-security-intern-electronics-prototype-at-mitre-4461245037", "search_term": "Firmware Engineer Intern PhD 2027"},
    {"title": "Firmware Engineer Intern", "company": "Hewlett Packard Enterprise", "location": "N/A", "time": "1 month ago", "url": "https://www.linkedin.com/jobs/view/firmware-engineer-intern-at-hewlett-packard-enterprise-4460538251", "search_term": "Firmware Engineer Intern PhD 2027"},
    {"title": "NVIDIA 2027 Internships: Systems Software Engineering", "company": "NVIDIA", "location": "N/A", "time": "2 weeks ago", "url": "https://www.linkedin.com/jobs/view/nvidia-2027-internships-systems-software-engineering-at-nvidia-4455474236", "search_term": "Firmware Engineer Intern PhD 2027"},
    {"title": "Software-Firmware Engineering Intern", "company": "Qorvo, Inc.", "location": "N/A", "time": "1 month ago", "url": "https://www.linkedin.com/jobs/view/software-firmware-engineering-intern-at-qorvo-inc-4461049622", "search_term": "Firmware Engineer Intern PhD 2027"},
    {"title": "Firmware Engineer Intern (Graduate Level) (Summer 2027)", "company": "Vertiv", "location": "N/A", "time": "1 week ago", "url": "https://www.linkedin.com/jobs/view/firmware-engineer-intern-graduate-level-summer-2027-at-vertiv-4459602356", "search_term": "Firmware Engineer Intern PhD 2027"},
    {"title": "Embedded Engineering Internship - Summer 2027", "company": "Qualcomm", "location": "N/A", "time": "1 week ago", "url": "https://www.linkedin.com/jobs/view/embedded-engineering-internship-summer-2027-at-qualcomm-4468407022", "search_term": "Firmware Engineer Intern PhD 2027"},
    {"title": "Intern - Firmware Engineer - Fall 2026", "company": "Advanced Energy", "location": "N/A", "time": "1 week ago", "url": "https://www.linkedin.com/jobs/view/intern-firmware-engineer-fall-2026-at-advanced-energy-4469048992", "search_term": "Firmware Engineer Intern PhD 2027"}
])

# Search 5: Signal Processing Intern PhD 2027 (unique jobs)
all_jobs.extend([
    {"title": "Audio DSP Engineering Intern", "company": "Shure", "location": "N/A", "time": "6 days ago", "url": "https://www.linkedin.com/jobs/view/audio-dsp-engineering-intern-at-shure-4461374890", "search_term": "Signal Processing Intern PhD 2027"},
    {"title": "2027 Communication Systems and Signal Processing Graduate Intern", "company": "The Aerospace Corporation", "location": "N/A", "time": "2 weeks ago", "url": "https://www.linkedin.com/jobs/view/2027-communication-systems-and-signal-processing-graduate-intern-at-the-aerospace-corporation-4465273074", "search_term": "Signal Processing Intern PhD 2027"},
    {"title": "Digital Signal Processing Intern", "company": "Shure", "location": "N/A", "time": "6 days ago", "url": "https://www.linkedin.com/jobs/view/digital-signal-processing-intern-at-shure-4461393538", "search_term": "Signal Processing Intern PhD 2027"},
    {"title": "Summer 2027 Masters Digital Signal Processing Engineer Intern", "company": "AMD", "location": "N/A", "time": "1 week ago", "url": "https://www.linkedin.com/jobs/view/summer-2027-masters-digital-signal-processing-engineer-intern-at-amd-4471180495", "search_term": "Signal Processing Intern PhD 2027"},
    {"title": "2027 Internship – Sensor & Phenomenology Engineering Intern", "company": "Johns Hopkins Applied Physics Laboratory", "location": "N/A", "time": "4 weeks ago", "url": "https://www.linkedin.com/jobs/view/2027-internship-sensor-phenomenology-engineering-intern-at-johns-hopkins-applied-physics-laboratory-4459561037", "search_term": "Signal Processing Intern PhD 2027"},
    {"title": "Acoustic and Vibration Technologies Co-op", "company": "Draper", "location": "N/A", "time": "2 days ago", "url": "https://www.linkedin.com/jobs/view/acoustic-and-vibration-technologies-co-op-at-draper-4443196174", "search_term": "Signal Processing Intern PhD 2027"},
    {"title": "Strategic & Long-Range Communications Intern (Summer 2027) - Group 61", "company": "MIT Lincoln Laboratory", "location": "N/A", "time": "1 day ago", "url": "https://www.linkedin.com/jobs/view/strategic-long-range-communications-intern-summer-2027-group-61-at-mit-lincoln-laboratory-4473574631", "search_term": "Signal Processing Intern PhD 2027"},
    {"title": "2027 Internship – Algorithm, Software, or RF Systems Engineering", "company": "Johns Hopkins Applied Physics Laboratory", "location": "N/A", "time": "4 days ago", "url": "https://www.linkedin.com/jobs/view/2027-internship-algorithm-software-or-rf-systems-engineering-at-johns-hopkins-applied-physics-laboratory-4470528998", "search_term": "Signal Processing Intern PhD 2027"},
    {"title": "Summer Research Intern 2027 - Edge communications processing with AI accelerators", "company": "IBM", "location": "N/A", "time": "5 days ago", "url": "https://www.linkedin.com/jobs/view/summer-research-intern-2027-edge-communications-processing-with-ai-accelerators-at-ibm-4470181929", "search_term": "Signal Processing Intern PhD 2027"},
    {"title": "Radar Digital Signal Processing (DSP) Intern/Co-Op", "company": "SoloPulse", "location": "N/A", "time": "3 months ago", "url": "https://www.linkedin.com/jobs/view/radar-digital-signal-processing-dsp-intern-co-op-at-solopulse-4422704255", "search_term": "Signal Processing Intern PhD 2027"},
    {"title": "Research Intern (PhD students)", "company": "Keysight Technologies", "location": "N/A", "time": "1 month ago", "url": "https://www.linkedin.com/jobs/view/research-intern-phd-students-at-keysight-technologies-4451281634", "search_term": "Signal Processing Intern PhD 2027"},
    {"title": "Summer 2027 Internship in Digital Signal Processing & Machine Learning - Top Secret/SCI Clearance Required - R149", "company": "Expedition Technology", "location": "N/A", "time": "1 week ago", "url": "https://www.linkedin.com/jobs/view/summer-2027-internship-in-digital-signal-processing-machine-learning-top-secret-sci-clearance-required-r149-at-expedition-technology-4468198043", "search_term": "Signal Processing Intern PhD 2027"}
])

# Remove duplicates based on URL
unique_jobs = {}
for job in all_jobs:
    if job['url'] not in unique_jobs:
        unique_jobs[job['url']] = job

unique_jobs_list = list(unique_jobs.values())

# Convert to Excel format
EXCEL_COLUMNS = [
    "Employer",
    "Internship / program",
    "Priority",
    "Location",
    "Timing",
    "Listing type",
    "Why it fits your CV",
    "Eligibility / next step",
    "Employer sponsorship policy",
    "Listed deadline",
    "Application status",
    "Requisition / ID",
    "Application / source"
]

excel_jobs = []
for job in unique_jobs_list:
    excel_jobs.append({
        "Employer": job["company"],
        "Internship / program": job["title"],
        "Priority": "To be evaluated",
        "Location": job["location"],
        "Timing": "2027",
        "Listing type": f"LinkedIn - {job['search_term']}",
        "Why it fits your CV": "Keyword match from search",
        "Eligibility / next step": "Check eligibility requirements",
        "Employer sponsorship policy": "To be verified",
        "Listed deadline": None,
        "Application status": "Not applied",
        "Requisition / ID": "N/A",
        "Application / source": job["url"]
    })

# Create DataFrame - ensure proper column alignment
df = pd.DataFrame(excel_jobs)
df = df[EXCEL_COLUMNS]  # Ensure columns are in the correct order

# Add header info rows (matching existing format)
header_data = [
    ["Comprehensive Job Search Results - Embedded AI/ML/Signal Processing Internships"] + [None] * 12,
    [f"Generated on {datetime.now().strftime('%B %d, %Y')} using LinkedIn search with multiple keywords"] + [None] * 12,
    [f"Total unique jobs found: {len(excel_jobs)}"] + [None] * 12,
    ["Search keywords used: Embedded AI Intern PhD 2027, TinyML Intern 2027, Edge AI Intern PhD 2027, Firmware Engineer Intern PhD 2027, Signal Processing Intern PhD 2027"] + [None] * 12,
    ["Note: Results from LinkedIn Jobs. Google Jobs showed no results for the search terms. Company career pages (TI, etc.) require direct navigation."] + [None] * 12,
    [None] * 13,
    EXCEL_COLUMNS
]

header_df = pd.DataFrame(header_data)

# Ensure both have the same number of columns
header_df = header_df.iloc[:, :len(EXCEL_COLUMNS)]
df = df.iloc[:, :len(EXCEL_COLUMNS)]

final_df = pd.concat([header_df, df], ignore_index=True)

# Save to Excel
output_file = "JobSearchResults_Comprehensive.xlsx"
final_df.to_excel(output_file, index=False, header=False)
print(f"Saved {len(excel_jobs)} unique jobs to {output_file}")
print(f"\nCompanies found: {len(set(job['company'] for job in unique_jobs_list))}")
print(f"Search terms used: {len(set(job['search_term'] for job in unique_jobs_list))}")
