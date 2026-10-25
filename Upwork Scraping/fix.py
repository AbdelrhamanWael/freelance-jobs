import re

with open('e:/MY PROJECT/Machine Learning/Upwork Scraping/scrap.py', 'r', encoding='utf-8') as f:
    code = f.read()

start_idx = code.find('def scrape_jobs(page: ChromiumPage, seen_manager: SeenJobsManager) -> List[Dict]:')
end_idx = code.find('# GROQ AI EVALUATOR')

new_function = '''def scrape_jobs(page: ChromiumPage, seen_manager: SeenJobsManager) -> List[Dict]:
    all_jobs: List[Dict] = []
    seen_links: set = set()
    skipped_unverified = 0
    skipped_zero       = 0
    skipped_seen       = 0

    for kw_index, kw_query in enumerate(KEYWORDS):
        log.info(f"\\n[Scraping Group {kw_index+1}/{len(KEYWORDS)}]: {kw_query[:60]}...")
        encoded = urllib.parse.quote_plus(kw_query)
        base_url = f"https://www.upwork.com/nx/search/jobs/?q={encoded}&sort=recency"
        
        for page_num in range(1, MAX_PAGES + 1):
            url = f"{base_url}&page={page_num}"
            log.info(f"──► Page {page_num}: {url}")
            page.get(url)

            try:
                page.ele(".job-tile", timeout=15)
                time.sleep(2)
            except Exception:
                log.warning(f"  Timeout on page {page_num}.")
                time.sleep(3)

            soup = BeautifulSoup(page.html, "html.parser")
            cards = (
                soup.find_all("article", class_="job-tile")
                or soup.select("section.up-card-section")
                or soup.select("[data-test='job-tile']")
            )

            if not cards:
                log.info(f"  No cards on page {page_num} — moving to next query group.")
                break

            log.info(f"  {len(cards)} cards found.")

            for card in cards:
                title_elem = card.find("h2") or card.find("h3")
                if not title_elem:
                    continue
                for span in title_elem.find_all("span"):
                    span.unwrap()
                title = title_elem.get_text(strip=True)
                if not title:
                    continue

                link_tag = title_elem.find("a")
                if link_tag and "href" in link_tag.attrs:
                    link = "https://www.upwork.com" + link_tag["href"] if link_tag["href"].startswith("/") else link_tag["href"]
                else:
                    link = "No link"

                if link == "No link" or link in seen_links:
                    continue

                job_hash = SeenJobsManager.make_id(link)
                if seen_manager.is_seen(job_hash):
                    skipped_seen += 1
                    continue

                seen_links.add(link)

                client_info = extract_client_info(card)
                skip, reason = should_skip_client(client_info)
                if skip:
                    if reason == "payment_unverified":
                        skipped_unverified += 1
                        log.debug(f"  SKIP (unverified): {title[:60]}")
                    else:
                        skipped_zero += 1
                        log.debug(f"  SKIP ($0 spent): {title[:60]}")
                    continue

                desc_elem = (
                    card.find("span", {"data-test": "job-description-text"})
                    or card.find("div", class_="job-description-text")
                    or card.find("p", class_="mb-0")
                )
                description = (
                    desc_elem.get_text(strip=True) if desc_elem
                    else card.get_text(separator="\\n", strip=True)
                )

                budget_elem = (
                    card.find(attrs={"data-test": "job-type-label"})
                    or card.find(attrs={"data-test": "budget"})
                    or card.find(class_="job-type")
                )
                budget_raw = budget_elem.get_text(strip=True) if budget_elem else "N/A"

                skill_elems = (
                    card.select("[data-test='TokenClamp JobAttrs'] a")
                    or card.select(".air3-token")
                    or card.select("[data-test='attr-item']")
                )
                skills = ", ".join(s.get_text(strip=True) for s in skill_elems) or "N/A"

                exp_elem = card.find(attrs={"data-test": "experience-level"})
                experience_level = exp_elem.get_text(strip=True) if exp_elem else "N/A"

                time_elem = (
                    card.find("span", {"data-test": "posted-on"})
                    or card.find("small", {"data-test": "job-pubilshed-date"})
                )
                relative_time = time_elem.get_text(strip=True) if time_elem else "Just now"
                posted_date = convert_relative_time(relative_time)

                prop_elem = (
                    card.find(attrs={"data-test": "proposals-tier"})
                    or card.find(attrs={"data-test": "bid-count"})
                )
                proposals_count = prop_elem.get_text(strip=True) if prop_elem else "N/A"

                matched_keywords = get_matched_keywords(f"{title} {description} {skills}")
                relevance_flags  = get_relevance_flags(title, description, skills)
                category, category_group = infer_category(title, description)

                job_data = {
                    "job_id":          job_hash[:16],
                    "title":           title,
                    "link":            link,
                    "posted_date":     posted_date,
                    "description":     description,
                    "budget_raw":      budget_raw,
                    "skills":          skills,
                    "experience_level": experience_level,
                    "proposals_count": proposals_count,
                    "client_info":     client_info,
                    "matched_keywords": matched_keywords,
                    "relevance_flags": relevance_flags,
                    "category":        category,
                    "category_group":  category_group,
                    "_hash":           job_hash,
                }
                all_jobs.append(job_data)
                log.info(f"  [+] Extracted: {title[:60]}")

            log.info(
                f"  Running total: {len(all_jobs)} | "
                f"Skipped: unverified={skipped_unverified}, zero_spent={skipped_zero}, seen={skipped_seen}"
            )
            time.sleep(2)

    log.info("\\nScrape done.")
    log.info(f"Skipped: {skipped_unverified} unverified + {skipped_zero} $0-spent + {skipped_seen} already-seen.")
    return all_jobs


# ─────────────────────────────────────────────────────────────────────────────
'''

new_code = code[:start_idx] + new_function + code[end_idx:]

with open('e:/MY PROJECT/Machine Learning/Upwork Scraping/scrap.py', 'w', encoding='utf-8') as f:
    f.write(new_code)
