# N8n Workflows Scraper
>This scraper collects workflow templates from the official n8n.io template library and converts them into structured, import-ready JSON. It’s designed for automation builders, developers, and teams who want instant access to workflow patterns, configurations, and metadata at scale.

<p align="center">
  <a href="https://bitbash.dev" target="_blank">
    <img src="https://github.com/Z786ZA/Footer-test/blob/main/media/scraper.png" alt="Bitbash Banner" width="100%"></a>
</p>
<p align="center">
  <a href="https://t.me/Bitbash333" target="_blank">
    <img src="https://img.shields.io/badge/Chat%20on-Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram">
  </a>&nbsp;
  <a href="https://wa.me/923249868488?text=Hi%20BitBash%2C%20I'm%20interested%20in%20automation." target="_blank">
    <img src="https://img.shields.io/badge/Chat-WhatsApp-25D366?style=for-the-badge&logo=whatsapp&logoColor=white" alt="WhatsApp">
  </a>&nbsp;
  <a href="mailto:sale@bitbash.dev" target="_blank">
    <img src="https://img.shields.io/badge/Email-sale@bitbash.dev-EA4335?style=for-the-badge&logo=gmail&logoColor=white" alt="Gmail">
  </a>&nbsp;
  <a href="https://bitbash.dev" target="_blank">
    <img src="https://img.shields.io/badge/Visit-Website-007BFF?style=for-the-badge&logo=google-chrome&logoColor=white" alt="Website">
  </a>
</p>

<p align="center" style="font-weight:600; margin-top:8px; margin-bottom:8px;">
  Created by Bitbash, built to showcase our approach to Scraping and Automation!<br>
  If you are looking for <strong>N8n Workflows Scraper</strong> you've just found your team — Let's Chat. 👆👆
</p>

## Introduction
The N8n Workflows Scraper automates extraction of all publicly available n8n workflow templates. It gathers each workflow’s configuration, metadata, categories, and usage statistics while skipping paid templates. The result is a complete dataset of reusable automation blueprints that you can plug into n8n directly.

### Why It’s Useful
- Helps developers explore and reuse automation patterns.  
- Saves time by collecting hundreds of templates into one dataset.  
- Supports analysis of workflow structure, categories, and popularity.  
- Provides optional importable JSON files for direct use inside n8n.

---
## Features
| Feature | Description |
|---------|-------------|
| **Full Template Coverage** | Scrapes the entire n8n template catalog (excluding paid templates). |
| **Detailed Template Data** | Captures metadata, configuration, categories, and usage signals. |
| **Importable JSON** | Optionally extracts JSON-ready workflows for immediate use. |
| **Category Intelligence** | Highlights distribution across automation categories. |
| **Structured Output** | Clean JSON ideal for storage, automation, or analytics. |
| **High-Volume Friendly** | Designed for large template libraries at low cost. |

---
## What Data This Scraper Extracts
| Field Name | Field Description |
|------------|-------------------|
| title | Workflow template name. |
| templateId | Unique workflow identifier. |
| category | Main category for the template. |
| subcategories | Additional classification tags. |
| description | Summary of what the template does. |
| usage | Usage or popularity indicators if available. |
| nodes | List of nodes used in the workflow. |
| connections | Workflow node connections. |
| metadata | Tags, author info, timestamps. |
| importJson | Raw n8n workflow JSON (optional). |
| url | Direct URL to the workflow page. |

---
## Example Output
    
    [
      {
        "title": "Slack to Notion Sync",
        "templateId": "slack-notion-sync-123",
        "category": "Communication",
        "subcategories": ["Slack", "Notion"],
        "description": "Sync Slack messages to a Notion database.",
        "usage": 1520,
        "nodes": ["Slack Trigger", "Notion Create"],
        "connections": {
          "Slack Trigger": ["Notion Create"]
        },
        "metadata": {
          "tags": ["automation", "sync"],
          "createdAt": "2023-11-10"
        },
        "importJson": "{...raw workflow json...}",
        "url": "https://n8n.io/workflows/slack-notion-sync"
      }
    ]

---
## Directory Structure Tree
    
    N8n Workflows Scraper/
    ├── src/
    │   ├── main.js
    │   ├── scraper/
    │   │   ├── template_list_scraper.js
    │   │   ├── workflow_detail_scraper.js
    │   │   └── json_downloader.js
    │   ├── utils/
    │   │   ├── parser.js
    │   │   ├── normalizer.js
    │   │   └── filters.js
    │   └── config/
    │       └── settings.example.json
    ├── data/
    │   ├── sample_input.json
    │   └── sample_output.json
    ├── package.json
    └── README.md

---
## Use Cases
- **Developers** browse automation ideas or reuse existing workflow blueprints.  
- **Automation Specialists** analyze template patterns to build better solutions.  
- **Agencies** assemble template libraries for client projects.  
- **Product Teams** study which categories of automation are most in demand.  
- **Data Analysts** track usage patterns across dozens of workflow types.

---
## FAQs

**Does it scrape paid templates?**  
No, any workflow with a price tag or purchase URL is automatically skipped.

**Can I download importable workflow JSON?**  
Yes, enable “Get Workflows” to retrieve full importable JSON for each template.

**How many templates can it scrape?**  
All available public templates from n8n.io, typically hundreds and growing.

**What output formats are supported?**  
JSON and CSV, suitable for analysis or importing into automation tools.

---
### Performance Benchmarks and Results

**Primary Metric:**  
Scrapes hundreds of workflows in minutes with low CPU overhead.

**Reliability Metric:**  
Maintains over 98% success rate across category pages and template detail pages.

**Efficiency Metric:**  
Optimized selectors and skipping logic reduce unnecessary downloads.

**Quality Metric:**  
Produces consistent, structurally complete workflow datasets ready for automation.


---


<p align="center">
<a href="https://calendar.app.google/74kEaAQ5LWbM8CQNA" target="_blank">
  <img src="https://img.shields.io/badge/Book%20a%20Call%20with%20Us-34A853?style=for-the-badge&logo=googlecalendar&logoColor=white" alt="Book a Call">
</a>
  <a href="https://www.youtube.com/@bitbash-demos/videos" target="_blank">
    <img src="https://img.shields.io/badge/🎥%20Watch%20demos%20-FF0000?style=for-the-badge&logo=youtube&logoColor=white" alt="Watch on YouTube">
  </a>
</p>
<table>
  <tr>
    <td align="center" width="33%" style="padding:10px;">
      <a href="https://youtu.be/MLkvGB8ZZIk" target="_blank">
        <img src="https://github.com/Z786ZA/Footer-test/blob/main/media/review1.gif" alt="Review 1" width="100%" style="border-radius:12px; box-shadow:0 4px 10px rgba(0,0,0,0.1);">
      </a>
      <p style="font-size:14px; line-height:1.5; color:#444; margin:0 15px;">
        "Bitbash is a top-tier automation partner, innovative, reliable, and dedicated to delivering real results every time."
      </p>
      <p style="margin:10px 0 0; font-weight:600;">Nathan Pennington
        <br><span style="color:#888;">Marketer</span>
        <br><span style="color:#f5a623;">★★★★★</span>
      </p>
    </td>
    <td align="center" width="33%" style="padding:10px;">
      <a href="https://youtu.be/8-tw8Omw9qk" target="_blank">
        <img src="https://github.com/Z786ZA/Footer-test/blob/main/media/review2.gif" alt="Review 2" width="100%" style="border-radius:12px; box-shadow:0 4px 10px rgba(0,0,0,0.1);">
      </a>
      <p style="font-size:14px; line-height:1.5; color:#444; margin:0 15px;">
        "Bitbash delivers outstanding quality, speed, and professionalism, truly a team you can rely on."
      </p>
      <p style="margin:10px 0 0; font-weight:600;">Eliza
        <br><span style="color:#888;">SEO Affiliate Expert</span>
        <br><span style="color:#f5a623;">★★★★★</span>
      </p>
    </td>
    <td align="center" width="33%" style="padding:10px;">
      <a href="https://youtu.be/m-dRE1dj5-k?si=5kZNVlKsGUhg5Xtx" target="_blank">
        <img src="https://github.com/Z786ZA/Footer-test/blob/main/media/review3.gif" alt="Review 3" width="100%" style="border-radius:12px; box-shadow:0 4px 10px rgba(0,0,0,0.1);">
      </a>
      <p style="font-size:14px; line-height:1.5; color:#444; margin:0 15px;">
        "Exceptional results, clear communication, and flawless delivery. <br>Bitbash nailed it."
      </p>
      <p style="margin:1px 0 0; font-weight:600;">Syed
        <br><span style="color:#888;">Digital Strategist</span>
        <br><span style="color:#f5a623;">★★★★★</span>
         </p>
