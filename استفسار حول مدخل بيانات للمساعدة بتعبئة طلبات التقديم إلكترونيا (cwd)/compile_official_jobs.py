import pandas as pd
from datetime import datetime

# Official company internship opportunities found from web search
official_jobs = [
    # Texas Instruments
    {
        'Employer': 'Texas Instruments',
        'Internship / program': 'Analog IC Design Engineering Intern - MS/PhD',
        'Priority': 'High',
        'Location': 'Dallas, TX or Tucson, AZ',
        'Timing': 'Summer 2027',
        'Listing type': 'Official Company Page',
        'Why it fits your CV': 'MS/PhD level, matches electrical engineering background',
        'Eligibility / next step': 'Apply via careers.ti.com, requires 3.0+ GPA',
        'Employer sponsorship policy': 'CPT/OPT welcome (check specific role)',
        'Listed deadline': 'Rolling - apply early',
        'Application status': 'Not applied',
        'Requisition / ID': '25017544',
        'Application / source': 'https://careers.ti.com/en/sites/CX/job/25017544'
    },
    {
        'Employer': 'Texas Instruments',
        'Internship / program': 'Systems Engineering Intern – MS/PhD',
        'Priority': 'High',
        'Location': 'United States (multiple locations)',
        'Timing': 'Summer 2027',
        'Listing type': 'Official Company Page',
        'Why it fits your CV': 'MS/PhD level, systems engineering focus',
        'Eligibility / next step': 'Apply via careers.ti.com',
        'Employer sponsorship policy': 'CPT/OPT welcome (check specific role)',
        'Listed deadline': 'Rolling - apply early',
        'Application status': 'Not applied',
        'Requisition / ID': 'Various',
        'Application / source': 'https://careers.ti.com/en/sites/CX/jobs?keyword=intern'
    },

    # NVIDIA
    {
        'Employer': 'NVIDIA',
        'Internship / program': 'PhD Research Intern, Autonomous Systems and Physical AI Research - 2027',
        'Priority': 'High',
        'Location': 'United States',
        'Timing': 'Summer 2027',
        'Listing type': 'Official Company Page',
        'Why it fits your CV': 'PhD Research Intern, autonomous systems and AI',
        'Eligibility / next step': 'Apply via jobs.nvidia.com, PhD required',
        'Employer sponsorship policy': 'Check specific role',
        'Listed deadline': 'Rolling',
        'Application status': 'Not applied',
        'Requisition / ID': '893397266856',
        'Application / source': 'https://jobs.nvidia.com/careers/job/893397266856'
    },
    {
        'Employer': 'NVIDIA',
        'Internship / program': 'PhD Research Intern, Electronic Design Automation - 2027',
        'Priority': 'High',
        'Location': 'Santa Clara, CA',
        'Timing': 'Summer 2027',
        'Listing type': 'Official Company Page',
        'Why it fits your CV': 'PhD Research Intern, AI for EDA',
        'Eligibility / next step': 'Apply via jobs.nvidia.com, PhD required',
        'Employer sponsorship policy': 'Check specific role',
        'Listed deadline': 'At least until September 27, 2026',
        'Application status': 'Not applied',
        'Requisition / ID': 'JR2026471',
        'Application / source': 'https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/job/PhD-Research-Intern--Electronic-Design-Automation---2027_JR2026471'
    },
    {
        'Employer': 'NVIDIA',
        'Internship / program': 'PhD Research Intern, Fundamental Generative AI - 2027',
        'Priority': 'High',
        'Location': 'United States',
        'Timing': 'Summer 2027',
        'Listing type': 'Official Company Page',
        'Why it fits your CV': 'PhD Research Intern, generative AI',
        'Eligibility / next step': 'Apply via jobs.nvidia.com, PhD required',
        'Employer sponsorship policy': 'Check specific role',
        'Listed deadline': 'At least until September 20, 2026',
        'Application status': 'Not applied',
        'Requisition / ID': '893397633487',
        'Application / source': 'https://jobs.nvidia.com/careers/job/893397633487'
    },
    {
        'Employer': 'NVIDIA',
        'Internship / program': 'NVIDIA 2027 Internships: Ph.D. Research Computer Architecture and Systems',
        'Priority': 'High',
        'Location': 'United States',
        'Timing': 'Summer 2027',
        'Listing type': 'Official Company Page',
        'Why it fits your CV': 'PhD Research Intern, computer architecture',
        'Eligibility / next step': 'Apply via jobs.nvidia.com, PhD required',
        'Employer sponsorship policy': 'Check specific role',
        'Listed deadline': 'Rolling',
        'Application status': 'Not applied',
        'Requisition / ID': '893397112671',
        'Application / source': 'https://jobs.nvidia.com/careers/job/893397112671'
    },
    {
        'Employer': 'NVIDIA',
        'Internship / program': 'NVIDIA 2027 Internships: Ph.D. Research Hardware',
        'Priority': 'High',
        'Location': 'United States',
        'Timing': 'Summer 2027',
        'Listing type': 'Official Company Page',
        'Why it fits your CV': 'PhD Research Intern, hardware',
        'Eligibility / next step': 'Apply via jobs.nvidia.com, PhD required',
        'Employer sponsorship policy': 'Check specific role',
        'Listed deadline': 'Rolling',
        'Application status': 'Not applied',
        'Requisition / ID': '893397112663',
        'Application / source': 'https://jobs.nvidia.com/careers/job/893397112663'
    },

    # Qualcomm
    {
        'Employer': 'Qualcomm',
        'Internship / program': 'Embedded Engineering Internship - Summer 2027',
        'Priority': 'High',
        'Location': 'San Diego, Santa Clara, Austin, Boulder, Boxborough, etc.',
        'Timing': 'Summer 2027 (May-September)',
        'Listing type': 'Official Company Page',
        'Why it fits your CV': 'Embedded engineering, C/C++/Python',
        'Eligibility / next step': 'Apply via Qualcomm careers, BS/MS required',
        'Employer sponsorship policy': 'Check specific role',
        'Listed deadline': 'Rolling',
        'Application status': 'Not applied',
        'Requisition / ID': 'Various',
        'Application / source': 'https://careers.qualcomm.com/jobs'
    },

    # Medtronic
    {
        'Employer': 'Medtronic',
        'Internship / program': 'Software Engineering Intern – Summer 2027',
        'Priority': 'High',
        'Location': 'United States (multiple locations)',
        'Timing': 'Summer 2027 (June-August)',
        'Listing type': 'Official Company Page',
        'Why it fits your CV': 'Software engineering, embedded systems focus',
        'Eligibility / next step': 'Apply via medtronic.wd1.myworkdayjobs.com',
        'Employer sponsorship policy': 'Does NOT sponsor for internships',
        'Listed deadline': 'October 16, 2026',
        'Application status': 'Not applied',
        'Requisition / ID': 'R73630-1',
        'Application / source': 'https://medtronic.wd1.myworkdayjobs.com/en-US/MedtronicCareers/job/Software-Engineering-Intern---Summer-2027_R73630-1'
    },
    {
        'Employer': 'Medtronic',
        'Internship / program': 'Engineering Intern Summer 2027',
        'Priority': 'High',
        'Location': 'Minnesota, California, Colorado, Connecticut, Massachusetts',
        'Timing': 'Summer 2027 (June-August)',
        'Listing type': 'Official Company Page',
        'Why it fits your CV': 'Engineering intern, biomedical devices',
        'Eligibility / next step': 'Apply via medtronic.wd1.myworkdayjobs.com',
        'Employer sponsorship policy': 'Does NOT sponsor for internships',
        'Listed deadline': 'Various (October-November 2026)',
        'Application status': 'Not applied',
        'Requisition / ID': 'Various',
        'Application / source': 'https://medtronic.wd1.myworkdayjobs.com/en-US/MedtronicCareers'
    },

    # Garmin
    {
        'Employer': 'Garmin',
        'Internship / program': 'Software Engineering Intern - Summer 2027',
        'Priority': 'Medium',
        'Location': 'Olathe, KS or Chandler, AZ',
        'Timing': 'Summer 2027',
        'Listing type': 'Official Company Page',
        'Why it fits your CV': 'Embedded software, C/C++',
        'Eligibility / next step': 'Apply via careers.garmin.com',
        'Employer sponsorship policy': 'Check specific role',
        'Listed deadline': 'October 11, 2026',
        'Application status': 'Not applied',
        'Requisition / ID': 'Various',
        'Application / source': 'https://careers.garmin.com/jobs'
    },

    # Bosch
    {
        'Employer': 'Bosch',
        'Internship / program': 'Software Engineering Intern (8 months/40hrs per week)',
        'Priority': 'Medium',
        'Location': 'Farmington Hills, Michigan',
        'Timing': 'January-August 2027 or May-December 2027',
        'Listing type': 'Official Company Page',
        'Why it fits your CV': 'Embedded Linux, cloud, Go, Rust, Python',
        'Eligibility / next step': 'Apply via Bosch careers',
        'Employer sponsorship policy': 'Check specific role',
        'Listed deadline': 'Rolling',
        'Application status': 'Not applied',
        'Requisition / ID': 'Various',
        'Application / source': 'https://jobs.bosch.com'
    },
    {
        'Employer': 'Bosch',
        'Internship / program': 'Mandatory Internship in Automation of Process Development with Agentic AI',
        'Priority': 'Medium',
        'Location': 'Renningen, Germany',
        'Timing': '6 months, start by agreement',
        'Listing type': 'Official Company Page',
        'Why it fits your CV': 'AI, data engineering, Python',
        'Eligibility / next step': 'Apply via jobs.bosch.de',
        'Employer sponsorship policy': 'EU work permit required',
        'Listed deadline': 'Rolling',
        'Application status': 'Not applied',
        'Requisition / ID': 'REF289080A',
        'Application / source': 'https://jobs.bosch.de/en/job/Mandatory-Internship-in-Automation-of-Process-Development-with-Agentic-AI-in-Manufacturing-Renningen?id=9a974d7c-bdf8-48d7-b6a5-62aa08e9a410'
    },

    # Honeywell
    {
        'Employer': 'Honeywell',
        'Internship / program': 'Embedded Engineer - Summer 2027 Intern',
        'Priority': 'High',
        'Location': 'Multiple US locations',
        'Timing': 'Summer 2027',
        'Listing type': 'Official Company Page',
        'Why it fits your CV': 'Embedded systems, C/C++',
        'Eligibility / next step': 'Apply via Honeywell careers',
        'Employer sponsorship policy': 'Unable to consider applicants requiring sponsorship',
        'Listed deadline': 'March 31, 2027',
        'Application status': 'Not applied',
        'Requisition / ID': 'Various',
        'Application / source': 'https://careers.honeywell.com'
    },

    # Analog Devices
    {
        'Employer': 'Analog Devices',
        'Internship / program': 'FY27 Intern Opportunities',
        'Priority': 'High',
        'Location': 'Multiple global locations',
        'Timing': '2027 Co-op/Intern',
        'Listing type': 'Official Company Page',
        'Why it fits your CV': 'Embedded software, AI/ML, signal processing',
        'Eligibility / next step': 'Apply via analogdevices.wd1.myworkdayjobs.com',
        'Employer sponsorship policy': 'Check specific role',
        'Listed deadline': 'Rolling from August/September 2026',
        'Application status': 'Not applied',
        'Requisition / ID': 'R265819',
        'Application / source': 'https://analogdevices.wd1.myworkdayjobs.com/en-US/External/job/FY27-Intern-Opportunities_R265819'
    },
    {
        'Employer': 'Analog Devices',
        'Internship / program': 'Embedded Software Engineer Intern',
        'Priority': 'High',
        'Location': 'Multiple global locations',
        'Timing': '2027',
        'Listing type': 'Official Company Page',
        'Why it fits your CV': 'Embedded software, RTOS, embedded Linux',
        'Eligibility / next step': 'Apply via analogdevices.wd1.myworkdayjobs.com',
        'Employer sponsorship policy': 'Check specific role',
        'Listed deadline': 'Rolling',
        'Application status': 'Not applied',
        'Requisition / ID': 'R266132',
        'Application / source': 'https://analogdevices.wd1.myworkdayjobs.com/en-US/External/job/Embedded-Software-Engineer-Intern_R266132'
    },
    {
        'Employer': 'Analog Devices',
        'Internship / program': 'Algorithm Development Engineer Intern',
        'Priority': 'High',
        'Location': 'Wilmington, MA',
        'Timing': '2027',
        'Listing type': 'Official Company Page',
        'Why it fits your CV': 'Machine learning, signal processing, C/C++/Python',
        'Eligibility / next step': 'Apply via analogdevices.wd1.myworkdayjobs.com',
        'Employer sponsorship policy': 'Check specific role',
        'Listed deadline': 'Rolling',
        'Application status': 'Not applied',
        'Requisition / ID': 'R265306-1',
        'Application / source': 'https://analogdevices.wd1.myworkdayjobs.com/en-US/External/job/US-MA-Wilmington/Algorithm-Development-Engineer-Intern_R265306-1'
    },

    # Infineon
    {
        'Employer': 'Infineon',
        'Internship / program': 'Internship Embedded AI Application Engineering',
        'Priority': 'High',
        'Location': 'Singapore',
        'Timing': '2027',
        'Listing type': 'Official Company Page',
        'Why it fits your CV': 'Embedded AI, application engineering',
        'Eligibility / next step': 'Apply via jobs.infineon.com',
        'Employer sponsorship policy': 'Check specific role',
        'Listed deadline': 'Rolling',
        'Application status': 'Not applied',
        'Requisition / ID': '563808971490142',
        'Application / source': 'https://jobs.infineon.com/careers/job/563808971490142-internship-embedded-ai-application-engineering-singapore?domain=infineon.com'
    },
    {
        'Employer': 'Infineon',
        'Internship / program': 'Internship Embedded Systems Engineer',
        'Priority': 'High',
        'Location': 'San Jose, CA or Austin, TX',
        'Timing': '2027',
        'Listing type': 'Official Company Page',
        'Why it fits your CV': 'Embedded systems, firmware, USB-PD',
        'Eligibility / next step': 'Apply via jobs.infineon.com',
        'Employer sponsorship policy': 'Check specific role',
        'Listed deadline': 'February 2027',
        'Application status': 'Not applied',
        'Requisition / ID': 'Various',
        'Application / source': 'https://jobs.infineon.com/careers'
    },

    # Microchip
    {
        'Employer': 'Microchip',
        'Internship / program': 'Engineering Summer Intern 2026/2027',
        'Priority': 'Medium',
        'Location': 'Chandler, AZ or other locations',
        'Timing': 'November 2026 - February 2027',
        'Listing type': 'Official Company Page',
        'Why it fits your CV': 'GNSS, embedded, RF, automation',
        'Eligibility / next step': 'Apply via microchiphr.wd5.myworkdayjobs.com',
        'Employer sponsorship policy': 'Check specific role',
        'Listed deadline': 'Rolling',
        'Application status': 'Not applied',
        'Requisition / ID': 'R3567-26',
        'Application / source': 'https://microchiphr.wd5.myworkdayjobs.com/en-US/External/job/Engineering-Summer-Intern-2026-2027--12-week-Internship-_R3567-26'
    },
    {
        'Employer': 'Microchip',
        'Internship / program': 'Intern - Engineering (Applications)',
        'Priority': 'Medium',
        'Location': 'Chandler, AZ',
        'Timing': '2027',
        'Listing type': 'Official Company Page',
        'Why it fits your CV': 'Applications engineering, embedded firmware',
        'Eligibility / next step': 'Apply via microchiphr.wd5.myworkdayjobs.com',
        'Employer sponsorship policy': 'Check specific role',
        'Listed deadline': 'Rolling',
        'Application status': 'Not applied',
        'Requisition / ID': 'R3880-26',
        'Application / source': 'https://microchiphr.wd5.myworkdayjobs.com/en-US/External/job/Intern---Engineering--Applications-_R3880-26'
    },
    {
        'Employer': 'Microchip',
        'Internship / program': 'Intern- Engineering (Verification)',
        'Priority': 'Medium',
        'Location': 'Chandler, AZ',
        'Timing': '2027',
        'Listing type': 'Official Company Page',
        'Why it fits your CV': 'Verification, AI tools',
        'Eligibility / next step': 'Apply via microchiphr.wd5.myworkdayjobs.com',
        'Employer sponsorship policy': 'Check specific role',
        'Listed deadline': 'Rolling',
        'Application status': 'Not applied',
        'Requisition / ID': 'R3700-26',
        'Application / source': 'https://microchiphr.wd5.myworkdayjobs.com/en-US/External/job/Intern--Engineering--Verification-_R3700-26'
    },

    # ARM
    {
        'Employer': 'ARM',
        'Internship / program': 'Hardware Designer Intern - Solutions Engineering',
        'Priority': 'Medium',
        'Location': 'Budapest, Hungary',
        'Timing': '2027 (6 months)',
        'Listing type': 'Official Company Page',
        'Why it fits your CV': 'Hardware design, solutions engineering',
        'Eligibility / next step': 'Apply via careers.arm.com',
        'Employer sponsorship policy': 'Unable to provide visa sponsorship',
        'Listed deadline': 'Rolling',
        'Application status': 'Not applied',
        'Requisition / ID': '2026-19558',
        'Application / source': 'https://careers.arm.com/job/budapest/hardware-designer-intern-solutions-engineering/33099/101386258464'
    },
    {
        'Employer': 'ARM',
        'Internship / program': 'FPGA Intern',
        'Priority': 'Medium',
        'Location': 'Trondheim, Norway',
        'Timing': 'June 2027 (10 weeks)',
        'Listing type': 'Official Company Page',
        'Why it fits your CV': 'FPGA, hardware engineering',
        'Eligibility / next step': 'Apply via careers.arm.com',
        'Employer sponsorship policy': 'Unable to provide visa sponsorship',
        'Listed deadline': 'Rolling',
        'Application status': 'Not applied',
        'Requisition / ID': '2026-18905',
        'Application / source': 'https://careers.arm.com/job/trondheim/fpga-intern/33099/101434822768'
    },
    {
        'Employer': 'ARM',
        'Internship / program': 'Graphics Software Intern, Direct3D',
        'Priority': 'Medium',
        'Location': 'Trondheim, Norway',
        'Timing': 'June 2027 (10 weeks)',
        'Listing type': 'Official Company Page',
        'Why it fits your CV': 'Graphics software, Direct3D',
        'Eligibility / next step': 'Apply via careers.arm.com',
        'Employer sponsorship policy': 'Unable to provide visa sponsorship',
        'Listed deadline': 'Rolling',
        'Application status': 'Not applied',
        'Requisition / ID': '2026-19436',
        'Application / source': 'https://careers.arm.com/en/job/trondheim/graphics-software-intern-direct3d/33099/100604944256'
    },

    # STMicroelectronics
    {
        'Employer': 'STMicroelectronics',
        'Internship / program': 'Intern – AI Agent Developer',
        'Priority': 'Medium',
        'Location': 'Cornaredo, Italy',
        'Timing': '2027',
        'Listing type': 'Official Company Page',
        'Why it fits your CV': 'AI agent development',
        'Eligibility / next step': 'Apply via stmicroelectronics.eightfold.ai',
        'Employer sponsorship policy': 'EU work permit required',
        'Listed deadline': 'Rolling',
        'Application status': 'Not applied',
        'Requisition / ID': '563637171891879',
        'Application / source': 'https://stmicroelectronics.eightfold.ai/careers/job/563637171891879-intern-%E2%80%93-ai-agent-developer-cornaredo-italy?domain=stmicroelectronics.com'
    },
    {
        'Employer': 'STMicroelectronics',
        'Internship / program': 'Internship - Secure Sw Designer',
        'Priority': 'Medium',
        'Location': 'Marcianise, Italy',
        'Timing': '2027',
        'Listing type': 'Official Company Page',
        'Why it fits your CV': 'Secure software design',
        'Eligibility / next step': 'Apply via stmicroelectronics.eightfold.ai',
        'Employer sponsorship policy': 'EU work permit required',
        'Listed deadline': 'Rolling',
        'Application status': 'Not applied',
        'Requisition / ID': '563637169409367',
        'Application / source': 'https://stmicroelectronics.eightfold.ai/careers/job/563637169409367-internship-secure-sw-designer-marcianise-italy?domain=stmicroelectronics.com'
    },
]

# Create DataFrame
df = pd.DataFrame(official_jobs)

# Save to Excel
output_file = 'JobSearchResults_Official_Company_Pages.xlsx'
df.to_excel(output_file, index=False, engine='openpyxl')

print(f"Successfully created {output_file} with {len(df)} official company internship opportunities")
print(f"\nSummary:")
print(f"- Total jobs: {len(df)}")
print(f"- Companies: {df['Employer'].nunique()}")
print(f"- High priority: {len(df[df['Priority'] == 'High'])}")
print(f"- Medium priority: {len(df[df['Priority'] == 'Medium'])}")
print(f"\nBreakdown by company:")
print(df.groupby('Employer').size().sort_values(ascending=False))
