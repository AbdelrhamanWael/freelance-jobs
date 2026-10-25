import json
import pandas as pd
from datetime import datetime

# Job data extracted from LinkedIn
jobs_data = [
    {
        "title": "Embedded Machine Learning & Radar Processing Intern - Summer 2027",
        "company": "NXP Semiconductors",
        "location": "San Jose, CA",
        "time": "2 days ago",
        "url": "https://www.linkedin.com/jobs/view/embedded-machine-learning-radar-processing-intern-summer-2027-at-nxp-semiconductors-4464090607"
    },
    {
        "title": "Radar Sensing AI Research Intern",
        "company": "Bosch USA",
        "location": "Pittsburgh, PA",
        "time": "2 days ago",
        "url": "https://www.linkedin.com/jobs/view/radar-sensing-ai-research-intern-at-bosch-usa-4471206010"
    },
    {
        "title": "AI Perception Intern (PICO) - 2027 Start (PhD)",
        "company": "ByteDance",
        "location": "San Jose, CA",
        "time": "3 hours ago",
        "url": "https://www.linkedin.com/jobs/view/ai-perception-intern-pico-2027-start-phd-at-bytedance-4473974856"
    },
    {
        "title": "PhD Research Intern, Generalist Embodied Agents Research - 2027",
        "company": "NVIDIA",
        "location": "Santa Clara, CA",
        "time": "1 week ago",
        "url": "https://www.linkedin.com/jobs/view/phd-research-intern-generalist-embodied-agents-research-2027-at-nvidia-4467819359"
    },
    {
        "title": "PhD Research Intern, Autonomous Systems and Physical AI Research - 2027",
        "company": "NVIDIA",
        "location": "Santa Clara, CA",
        "time": "2 weeks ago",
        "url": "https://www.linkedin.com/jobs/view/phd-research-intern-autonomous-systems-and-physical-ai-research-2027-at-nvidia-4465702327"
    },
    {
        "title": "Software Algorithm Embedded Intern",
        "company": "STMicroelectronics",
        "location": "Santa Clara, CA",
        "time": "1 day ago",
        "url": "https://www.linkedin.com/jobs/view/software-algorithm-embedded-intern-at-stmicroelectronics-4473568575"
    },
    {
        "title": "Embedded AI Firmware Co-Op",
        "company": "Schneider Electric",
        "location": "Andover, MA",
        "time": "1 week ago",
        "url": "https://www.linkedin.com/jobs/view/embedded-ai-firmware-co-op-at-schneider-electric-4467874984"
    },
    {
        "title": "Autonomous Driving Applications Research Intern",
        "company": "Nissan Motor Corporation",
        "location": "N/A",
        "time": "1 day ago",
        "url": "https://www.linkedin.com/jobs/view/autonomous-driving-applications-research-intern-at-nissan-motor-corporation-4418153214"
    },
    {
        "title": "Machine Learning & Artificial Intelligence Engineering Internship – Summer 2027",
        "company": "Qualcomm",
        "location": "N/A",
        "time": "1 week ago",
        "url": "https://www.linkedin.com/jobs/view/machine-learning-artificial-intelligence-engineering-internship-summer-2027-at-qualcomm-4468095266"
    },
    {
        "title": "2027 Internship – Engineering/Science – Tailored Autonomous Systems",
        "company": "Johns Hopkins Applied Physics Laboratory",
        "location": "N/A",
        "time": "2 weeks ago",
        "url": "https://www.linkedin.com/jobs/view/2027-internship-engineering-science-tailored-autonomous-systems-at-johns-hopkins-applied-physics-laboratory-4463934414"
    },
    {
        "title": "Algorithm Engineer Intern",
        "company": "VisLab (an Ambarella Inc. company)",
        "location": "N/A",
        "time": "1 month ago",
        "url": "https://www.linkedin.com/jobs/view/algorithm-engineer-intern-at-vislab-an-ambarella-inc-company-4459840393"
    },
    {
        "title": "Audio AI Engineering Intern-Summer 2027",
        "company": "Skyworks Solutions, Inc.",
        "location": "N/A",
        "time": "1 month ago",
        "url": "https://www.linkedin.com/jobs/view/audio-ai-engineering-intern-summer-2027-at-skyworks-solutions-inc-4454837251"
    },
    {
        "title": "AI Vision Research Scientist Intern - Global Frontier Tech Recruitment Program - 2027 Start (PHD)",
        "company": "ByteDance",
        "location": "N/A",
        "time": "1 day ago",
        "url": "https://www.linkedin.com/jobs/view/ai-vision-research-scientist-intern-global-frontier-tech-recruitment-program-2027-start-phd-at-bytedance-4435836915"
    },
    {
        "title": "2027 Summer Intern, PhD, Machine Learning, Computer Vision",
        "company": "Waymo",
        "location": "N/A",
        "time": "2 weeks ago",
        "url": "https://www.linkedin.com/jobs/view/2027-summer-intern-phd-machine-learning-computer-vision-at-waymo-4464832342"
    },
    {
        "title": "Intern - Engineering ADAS Perception Features",
        "company": "Magna International",
        "location": "N/A",
        "time": "2 weeks ago",
        "url": "https://www.linkedin.com/jobs/view/intern-engineering-adas-perception-features-at-magna-international-4466557740"
    },
    {
        "title": "Summer 2027 - Software Engineer Intern",
        "company": "Shield AI",
        "location": "N/A",
        "time": "2 weeks ago",
        "url": "https://www.linkedin.com/jobs/view/summer-2027-software-engineer-intern-at-shield-ai-4465604643"
    },
    {
        "title": "AI Intern",
        "company": "Oshkosh Corporation",
        "location": "N/A",
        "time": "2 weeks ago",
        "url": "https://www.linkedin.com/jobs/view/ai-intern-at-oshkosh-corporation-4465420039"
    },
    {
        "title": "Autonomy Engineering Intern",
        "company": "JLG Industries",
        "location": "N/A",
        "time": "2 weeks ago",
        "url": "https://www.linkedin.com/jobs/view/autonomy-engineering-intern-at-jlg-industries-4465598332"
    },
    {
        "title": "2027 Summer Intern, MS/PhD, Software Engineer, Sys Intel & Machine Learning",
        "company": "Waymo",
        "location": "N/A",
        "time": "5 days ago",
        "url": "https://www.linkedin.com/jobs/view/2027-summer-intern-ms-phd-software-engineer-sys-intel-machine-learning-at-waymo-4470720097"
    },
    {
        "title": "Software Engineering Intern",
        "company": "Shure",
        "location": "N/A",
        "time": "6 days ago",
        "url": "https://www.linkedin.com/jobs/view/software-engineering-intern-at-shure-4461391646"
    },
    {
        "title": "2027 PhD ML System Engineering Intern/Co-op",
        "company": "AMD",
        "location": "N/A",
        "time": "2 weeks ago",
        "url": "https://www.linkedin.com/jobs/view/2027-phd-ml-system-engineering-intern-co-op-at-amd-4464240966"
    }
]

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
for job in jobs_data:
    excel_jobs.append({
        "Employer": job["company"],
        "Internship / program": job["title"],
        "Priority": "To be evaluated",
        "Location": job["location"],
        "Timing": "2027",
        "Listing type": "LinkedIn",
        "Why it fits your CV": "Keyword match from search",
        "Eligibility / next step": "Check eligibility requirements",
        "Employer sponsorship policy": "To be verified",
        "Listed deadline": None,
        "Application status": "Not applied",
        "Requisition / ID": "N/A",
        "Application / source": job["url"]
    })

# Create DataFrame
df = pd.DataFrame(excel_jobs, columns=EXCEL_COLUMNS)

# Add header info rows (matching existing format)
header_data = [
    ["Job Search Results - Embedded AI/ML Internships", None, None, None, None, None, None, None, None, None, None, None, None],
    [f"Generated on {datetime.now().strftime('%B %d, %Y')} using LinkedIn search", None, None, None, None, None, None, None, None, None, None, None, None],
    [f"Total jobs found: {len(excel_jobs)}", None, None, None, None, None, None, None, None, None, None, None, None],
    ["Search keywords: Embedded AI Intern, PhD Intern, TinyML, Edge AI, Firmware Engineer, Signal Processing", None, None, None, None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None, None, None, None, None],
    EXCEL_COLUMNS
]

header_df = pd.DataFrame(header_data)
final_df = pd.concat([header_df, df], ignore_index=True)

# Save to Excel
output_file = "JobSearchResults_Linkedin.xlsx"
final_df.to_excel(output_file, index=False, header=False)
print(f"Saved {len(excel_jobs)} jobs to {output_file}")
