"""
Seed database with reconnaissance tools and professional pipelines
Based on 2025 bug bounty best practices and modern recon methodologies
"""
from models import (
    init_db, get_session, Tool, Pipeline, PipelineStep, Configuration, PhaseCategory
)
import json

def seed_tools(session):
    """Populate database with all reconnaissance tools"""

    tools_data = [
        # ===== SUBDOMAIN ENUMERATION =====
        {
            "name": "Amass",
            "command": "amass",
            "description": "In-depth Attack Surface Mapping using OSINT and DNS sources",
            "category": PhaseCategory.SUBDOMAIN_ENUMERATION,
            "link": "https://github.com/OWASP/Amass",
            "requires_env": ["AMASS_CONFIG"],
            "output_format": "txt",
            "supports_list_input": False,
            "parallel_capable": True,
            "timeout_seconds": 7200
        },
        {
            "name": "Subfinder",
            "command": "subfinder",
            "description": "Fast passive subdomain enumeration using 50+ sources",
            "category": PhaseCategory.SUBDOMAIN_ENUMERATION,
            "link": "https://github.com/projectdiscovery/subfinder",
            "requires_env": ["SUBFINDER_CONFIG"],
            "output_format": "txt",
            "supports_list_input": False,
            "parallel_capable": True,
            "timeout_seconds": 1800
        },
        {
            "name": "ASNmap",
            "command": "asnmap",
            "description": "Map ASN and discover IP ranges for organizations",
            "category": PhaseCategory.SUBDOMAIN_ENUMERATION,
            "link": "https://github.com/projectdiscovery/asnmap",
            "output_format": "txt",
            "supports_list_input": False,
            "parallel_capable": True,
            "timeout_seconds": 600
        },
        {
            "name": "Assetfinder",
            "command": "assetfinder",
            "description": "Find domains and subdomains potentially related to a target",
            "category": PhaseCategory.SUBDOMAIN_ENUMERATION,
            "link": "https://github.com/tomnomnom/assetfinder",
            "output_format": "txt",
            "supports_list_input": False,
            "parallel_capable": True,
            "timeout_seconds": 900
        },
        {
            "name": "Chaos",
            "command": "chaos",
            "description": "ProjectDiscovery's public datasets for known subdomains",
            "category": PhaseCategory.SUBDOMAIN_ENUMERATION,
            "link": "https://github.com/projectdiscovery/chaos-client",
            "requires_env": ["CHAOS_KEY"],
            "output_format": "txt",
            "supports_list_input": False,
            "parallel_capable": True,
            "timeout_seconds": 300
        },
        {
            "name": "Cero",
            "command": "cero",
            "description": "Fast subdomain scraper using certificate transparency",
            "category": PhaseCategory.SUBDOMAIN_ENUMERATION,
            "link": "https://github.com/glebarez/cero",
            "output_format": "txt",
            "supports_list_input": False,
            "parallel_capable": True,
            "timeout_seconds": 600
        },
        {
            "name": "Sublist3r",
            "command": "python3 /opt/Sublist3r/sublist3r.py",
            "description": "Subdomain enumeration using search engines",
            "category": PhaseCategory.SUBDOMAIN_ENUMERATION,
            "link": "https://github.com/aboul3la/Sublist3r",
            "output_format": "txt",
            "supports_list_input": False,
            "parallel_capable": True,
            "timeout_seconds": 1200
        },
        {
            "name": "Findomain",
            "command": "findomain",
            "description": "Fast subdomain enumeration using APIs like Shodan, Virustotal",
            "category": PhaseCategory.SUBDOMAIN_ENUMERATION,
            "link": "https://github.com/Findomain/Findomain",
            "requires_env": ["FINDOMAIN_CONFIG"],
            "output_format": "txt",
            "supports_list_input": False,
            "parallel_capable": True,
            "timeout_seconds": 900
        },
        {
            "name": "AlterX",
            "command": "alterx",
            "description": "Fast subdomain permutation and alteration generation",
            "category": PhaseCategory.SUBDOMAIN_ENUMERATION,
            "link": "https://github.com/projectdiscovery/alterx",
            "output_format": "txt",
            "supports_list_input": True,
            "supports_stdin": True,
            "parallel_capable": True,
            "timeout_seconds": 600
        },
        {
            "name": "GithubSubdomains",
            "command": "github-subdomains",
            "description": "Find subdomains by searching GitHub repositories",
            "category": PhaseCategory.SUBDOMAIN_ENUMERATION,
            "link": "https://github.com/gwen001/github-subdomains",
            "requires_env": ["GITHUB_TOKEN"],
            "output_format": "txt",
            "supports_list_input": False,
            "parallel_capable": True,
            "timeout_seconds": 1800
        },

        # ===== ACTIVE VERIFICATION =====
        {
            "name": "Httpx",
            "command": "httpx",
            "description": "Fast HTTP toolkit for probing live hosts",
            "category": PhaseCategory.ACTIVE_VERIFICATION,
            "link": "https://github.com/projectdiscovery/httpx",
            "output_format": "json",
            "supports_list_input": True,
            "supports_stdin": True,
            "parallel_capable": True,
            "timeout_seconds": 1800
        },
        {
            "name": "Httprobe",
            "command": "httprobe",
            "description": "Take list of domains and probe for working HTTP/HTTPS servers",
            "category": PhaseCategory.ACTIVE_VERIFICATION,
            "link": "https://github.com/tomnomnom/httprobe",
            "output_format": "txt",
            "supports_list_input": True,
            "supports_stdin": True,
            "parallel_capable": True,
            "timeout_seconds": 900
        },
        {
            "name": "Dnsx",
            "command": "dnsx",
            "description": "Fast DNS toolkit for running various DNS queries",
            "category": PhaseCategory.ACTIVE_VERIFICATION,
            "link": "https://github.com/projectdiscovery/dnsx",
            "output_format": "json",
            "supports_list_input": True,
            "supports_stdin": True,
            "parallel_capable": True,
            "timeout_seconds": 1200
        },
        {
            "name": "MassDNS",
            "command": "massdns",
            "description": "High-performance DNS stub resolver for bulk lookups",
            "category": PhaseCategory.ACTIVE_VERIFICATION,
            "link": "https://github.com/blechschmidt/massdns",
            "output_format": "txt",
            "supports_list_input": True,
            "parallel_capable": True,
            "timeout_seconds": 1800
        },

        # ===== SPIDERING & CRAWLING =====
        {
            "name": "Gospider",
            "command": "gospider",
            "description": "Fast web spider written in Go",
            "category": PhaseCategory.SPIDERING,
            "link": "https://github.com/jaeles-project/gospider",
            "output_format": "txt",
            "supports_list_input": True,
            "parallel_capable": True,
            "timeout_seconds": 3600
        },
        {
            "name": "Hakrawler",
            "command": "hakrawler",
            "description": "Fast golang web crawler for gathering URLs and JavaScript files",
            "category": PhaseCategory.SPIDERING,
            "link": "https://github.com/hakluke/hakrawler",
            "output_format": "txt",
            "supports_list_input": True,
            "supports_stdin": True,
            "parallel_capable": True,
            "timeout_seconds": 2400
        },
        {
            "name": "Katana",
            "command": "katana",
            "description": "Next-generation crawling and spidering framework",
            "category": PhaseCategory.SPIDERING,
            "link": "https://github.com/projectdiscovery/katana",
            "output_format": "txt",
            "supports_list_input": True,
            "parallel_capable": True,
            "timeout_seconds": 3600
        },
        {
            "name": "GAU",
            "command": "gau",
            "description": "Fetch known URLs from AlienVault, Wayback Machine, Common Crawl, URLScan",
            "category": PhaseCategory.SPIDERING,
            "link": "https://github.com/lc/gau",
            "output_format": "txt",
            "supports_list_input": True,
            "supports_stdin": True,
            "parallel_capable": True,
            "timeout_seconds": 1800
        },
        {
            "name": "Waymore",
            "command": "waymore",
            "description": "Find even more links from the Wayback Machine",
            "category": PhaseCategory.SPIDERING,
            "link": "https://github.com/xnl-h4ck3r/waymore",
            "output_format": "txt",
            "supports_list_input": True,
            "parallel_capable": True,
            "timeout_seconds": 2400
        },
        {
            "name": "Waybackurls",
            "command": "waybackurls",
            "description": "Fetch all URLs that the Wayback Machine knows about",
            "category": PhaseCategory.SPIDERING,
            "link": "https://github.com/tomnomnom/waybackurls",
            "output_format": "txt",
            "supports_list_input": True,
            "supports_stdin": True,
            "parallel_capable": True,
            "timeout_seconds": 1200
        },

        # ===== PORT SCANNING =====
        {
            "name": "Naabu",
            "command": "naabu",
            "description": "Fast port scanner written in Go with focus on reliability",
            "category": PhaseCategory.PORT_SCANNING,
            "link": "https://github.com/projectdiscovery/naabu",
            "output_format": "txt",
            "supports_list_input": True,
            "parallel_capable": True,
            "timeout_seconds": 3600
        },
        {
            "name": "Masscan",
            "command": "masscan",
            "description": "TCP port scanner, spews SYN packets asynchronously",
            "category": PhaseCategory.PORT_SCANNING,
            "link": "https://github.com/robertdavidgraham/masscan",
            "output_format": "txt",
            "supports_list_input": False,
            "parallel_capable": False,
            "timeout_seconds": 1800
        },
        {
            "name": "Tlsx",
            "command": "tlsx",
            "description": "Fast TLS data scanning and grabbing",
            "category": PhaseCategory.PORT_SCANNING,
            "link": "https://github.com/projectdiscovery/tlsx",
            "output_format": "json",
            "supports_list_input": True,
            "parallel_capable": True,
            "timeout_seconds": 1800
        },
        {
            "name": "Nmap",
            "command": "nmap",
            "description": "Network exploration tool and security scanner",
            "category": PhaseCategory.PORT_SCANNING,
            "link": "https://nmap.org/",
            "output_format": "xml",
            "supports_list_input": False,
            "parallel_capable": False,
            "timeout_seconds": 3600
        },

        # ===== FINGERPRINTING =====
        {
            "name": "WhatWeb",
            "command": "whatweb",
            "description": "Web technology detection and fingerprinting",
            "category": PhaseCategory.FINGERPRINTING,
            "link": "https://github.com/urbanadventurer/WhatWeb",
            "output_format": "json",
            "supports_list_input": True,
            "parallel_capable": True,
            "timeout_seconds": 1800
        },
        {
            "name": "Webanalyze",
            "command": "webanalyze",
            "description": "Port of Wappalyzer for mass web technology detection",
            "category": PhaseCategory.FINGERPRINTING,
            "link": "https://github.com/rverton/webanalyze",
            "output_format": "json",
            "supports_list_input": True,
            "parallel_capable": True,
            "timeout_seconds": 1200
        },

        # ===== VULNERABILITY SCANNING =====
        {
            "name": "Nuclei",
            "command": "nuclei",
            "description": "Fast and customizable vulnerability scanner based on YAML templates",
            "category": PhaseCategory.VULNERABILITY_SCANNING,
            "link": "https://github.com/projectdiscovery/nuclei",
            "requires_env": ["NUCLEI_TEMPLATES_PATH"],
            "output_format": "json",
            "supports_list_input": True,
            "parallel_capable": True,
            "timeout_seconds": 7200
        },
        {
            "name": "CveMap",
            "command": "cvemap",
            "description": "Navigate the CVE database with ease",
            "category": PhaseCategory.VULNERABILITY_SCANNING,
            "link": "https://github.com/projectdiscovery/cvemap",
            "output_format": "json",
            "supports_list_input": True,
            "parallel_capable": True,
            "timeout_seconds": 600
        },
        {
            "name": "SQLMap",
            "command": "sqlmap",
            "description": "Automatic SQL injection and database takeover tool",
            "category": PhaseCategory.VULNERABILITY_SCANNING,
            "link": "https://github.com/sqlmapproject/sqlmap",
            "output_format": "txt",
            "supports_list_input": False,
            "parallel_capable": False,
            "timeout_seconds": 3600
        },
        {
            "name": "Ghauri",
            "command": "ghauri",
            "description": "Advanced cross-platform SQL injection detection tool",
            "category": PhaseCategory.VULNERABILITY_SCANNING,
            "link": "https://github.com/r0oth3x49/ghauri",
            "output_format": "txt",
            "supports_list_input": False,
            "parallel_capable": True,
            "timeout_seconds": 3600
        },
        {
            "name": "Nikto",
            "command": "nikto",
            "description": "Web server scanner for dangerous files and outdated software",
            "category": PhaseCategory.VULNERABILITY_SCANNING,
            "link": "https://github.com/sullo/nikto",
            "output_format": "txt",
            "supports_list_input": False,
            "parallel_capable": True,
            "timeout_seconds": 2400
        },
        {
            "name": "SSLyze",
            "command": "sslyze",
            "description": "Fast and powerful SSL/TLS scanning library",
            "category": PhaseCategory.VULNERABILITY_SCANNING,
            "link": "https://github.com/nabla-c0d3/sslyze",
            "output_format": "json",
            "supports_list_input": True,
            "parallel_capable": True,
            "timeout_seconds": 1800
        },

        # ===== SCREENSHOT =====
        {
            "name": "GoWitness",
            "command": "gowitness",
            "description": "Website screenshot utility using Chrome Headless",
            "category": PhaseCategory.SCREENSHOT,
            "link": "https://github.com/sensepost/gowitness",
            "output_format": "json",
            "supports_list_input": True,
            "parallel_capable": True,
            "timeout_seconds": 3600
        },
        {
            "name": "EyeWitness",
            "command": "eyewitness",
            "description": "Take screenshots of websites with server headers",
            "category": PhaseCategory.SCREENSHOT,
            "link": "https://github.com/FortyNorthSecurity/EyeWitness",
            "output_format": "txt",
            "supports_list_input": True,
            "parallel_capable": True,
            "timeout_seconds": 3600
        },

        # ===== BRUTEFORCING =====
        {
            "name": "FFUF",
            "command": "ffuf",
            "description": "Fast web fuzzer written in Go",
            "category": PhaseCategory.BRUTEFORCING,
            "link": "https://github.com/ffuf/ffuf",
            "output_format": "json",
            "supports_list_input": False,
            "parallel_capable": True,
            "timeout_seconds": 3600
        },
        {
            "name": "GoBuster",
            "command": "gobuster",
            "description": "Directory/file & DNS busting tool",
            "category": PhaseCategory.BRUTEFORCING,
            "link": "https://github.com/OJ/gobuster",
            "output_format": "txt",
            "supports_list_input": False,
            "parallel_capable": True,
            "timeout_seconds": 3600
        },
        {
            "name": "Dirsearch",
            "command": "python3 /opt/dirsearch/dirsearch.py",
            "description": "Web path scanner",
            "category": PhaseCategory.BRUTEFORCING,
            "link": "https://github.com/maurosoria/dirsearch",
            "output_format": "txt",
            "supports_list_input": False,
            "parallel_capable": True,
            "timeout_seconds": 3600
        },

        # ===== JAVASCRIPT ANALYSIS =====
        {
            "name": "JSFinder",
            "command": "jsfinder",
            "description": "Find JavaScript files and extract sensitive information",
            "category": PhaseCategory.JAVASCRIPT_ANALYSIS,
            "link": "https://github.com/kacakb/jsfinder",
            "output_format": "txt",
            "supports_list_input": True,
            "parallel_capable": True,
            "timeout_seconds": 1800
        },
        {
            "name": "LinkFinder",
            "command": "python3 /usr/local/bin/linkfinder",
            "description": "Discover endpoints and their parameters in JavaScript files",
            "category": PhaseCategory.JAVASCRIPT_ANALYSIS,
            "link": "https://github.com/GerbenJavado/LinkFinder",
            "output_format": "txt",
            "supports_list_input": True,
            "parallel_capable": True,
            "timeout_seconds": 1200
        },

        # ===== CLOUD DISCOVERY =====
        {
            "name": "CloudEnum",
            "command": "python3 /opt/cloud_enum/cloud_enum.py",
            "description": "Multi-cloud OSINT tool for finding cloud resources",
            "category": PhaseCategory.CLOUD_DISCOVERY,
            "link": "https://github.com/initstring/cloud_enum",
            "output_format": "txt",
            "supports_list_input": False,
            "parallel_capable": True,
            "timeout_seconds": 1800
        },
        {
            "name": "S3Scanner",
            "command": "s3scanner",
            "description": "Scan for open AWS S3 buckets",
            "category": PhaseCategory.CLOUD_DISCOVERY,
            "link": "https://github.com/sa7mon/s3scanner",
            "output_format": "json",
            "supports_list_input": True,
            "parallel_capable": True,
            "timeout_seconds": 1200
        },

        # ===== SUBDOMAIN TAKEOVER =====
        {
            "name": "Subzy",
            "command": "subzy",
            "description": "Subdomain takeover vulnerability checker",
            "category": PhaseCategory.SUBDOMAIN_TAKEOVER,
            "link": "https://github.com/PentestPad/subzy",
            "output_format": "txt",
            "supports_list_input": True,
            "supports_stdin": True,
            "parallel_capable": True,
            "timeout_seconds": 900
        },

        # ===== HOST DISCOVERY =====
        {
            "name": "Uncover",
            "command": "uncover",
            "description": "Quickly discover exposed hosts using multiple search engines",
            "category": PhaseCategory.HOST_DISCOVERY,
            "link": "https://github.com/projectdiscovery/uncover",
            "requires_env": ["UNCOVER_CONFIG"],
            "output_format": "json",
            "supports_list_input": False,
            "parallel_capable": True,
            "timeout_seconds": 600
        },

        # ===== UTILITY TOOLS =====
        {
            "name": "Anew",
            "command": "anew",
            "description": "Append lines from stdin to file, only unique",
            "category": PhaseCategory.UTILITY,
            "link": "https://github.com/tomnomnom/anew",
            "output_format": "txt",
            "supports_stdin": True,
            "parallel_capable": True,
            "timeout_seconds": 60
        },
        {
            "name": "Urless",
            "command": "urless",
            "description": "De-clutter URLs from list",
            "category": PhaseCategory.UTILITY,
            "link": "",
            "output_format": "txt",
            "supports_stdin": True,
            "parallel_capable": True,
            "timeout_seconds": 120
        },
        {
            "name": "GF",
            "command": "gf",
            "description": "Wrapper around grep for filtering output",
            "category": PhaseCategory.UTILITY,
            "link": "https://github.com/tomnomnom/gf",
            "output_format": "txt",
            "supports_stdin": True,
            "parallel_capable": True,
            "timeout_seconds": 60
        },
    ]

    for tool_data in tools_data:
        tool = session.query(Tool).filter_by(name=tool_data["name"]).first()
        if tool:
            # Update existing tool
            for key, value in tool_data.items():
                setattr(tool, key, value)
        else:
            # Create new tool
            tool = Tool(**tool_data)
            session.add(tool)

    session.commit()
    print(f"✓ Seeded {len(tools_data)} tools")


def seed_pipelines(session):
    """Create professional reconnaissance pipelines based on 2025 best practices"""

    # Clean existing pipelines
    session.query(Pipeline).delete()
    session.commit()

    pipelines_config = [
        # ===== PIPELINE 1: COMPLETE SUBDOMAIN DISCOVERY =====
        {
            "pipeline": {
                "name": "SUBDOMAIN_DISCOVERY_COMPLETE",
                "description": "Comprehensive subdomain enumeration using passive + active + bruteforce methods. Combines 10+ tools for maximum coverage.",
                "category": PhaseCategory.SUBDOMAIN_ENUMERATION,
                "parallel_execution": True,
                "estimated_duration_minutes": 45,
                "requires_env": ["SUBFINDER_CONFIG", "CHAOS_KEY", "GITHUB_TOKEN"]
            },
            "steps": [
                # PARALLEL GROUP 1: Passive enumeration (all run in parallel)
                {"order": 1, "tool": "Subfinder", "arguments": "-d {asset} -all -recursive -t 100 -silent -o {results_path}/subfinder.txt", "parallel_group": 1},
                {"order": 2, "tool": "Assetfinder", "arguments": "--subs-only {asset} | anew {results_path}/assetfinder.txt", "parallel_group": 1},
                {"order": 3, "tool": "Amass", "arguments": "enum -passive -d {asset} -o {results_path}/amass.txt", "parallel_group": 1},
                {"order": 4, "tool": "Chaos", "arguments": "-d {asset} -silent -o {results_path}/chaos.txt", "parallel_group": 1, "required": False},
                {"order": 5, "tool": "Findomain", "arguments": "-t {asset} -q -u {results_path}/findomain.txt", "parallel_group": 1, "required": False},
                {"order": 6, "tool": "Cero", "arguments": "{asset} | anew {results_path}/cero.txt", "parallel_group": 1},
                {"order": 7, "tool": "GithubSubdomains", "arguments": "-d {asset} -t $GITHUB_TOKEN -o {results_path}/github.txt", "parallel_group": 1, "required": False},

                # STEP 8: Combine all results
                {"order": 8, "tool": "Anew", "arguments": "{results_path}/all_subdomains.txt", "parallel_group": None,
                 "arguments": "cat {results_path}/*.txt 2>/dev/null | sort -u | anew {results_path}/all_subdomains.txt"},

                # PARALLEL GROUP 2: Active verification
                {"order": 9, "tool": "Httpx", "arguments": "-l {results_path}/all_subdomains.txt -silent -o {results_path}/live_subdomains.txt", "parallel_group": 2},
                {"order": 10, "tool": "Dnsx", "arguments": "-l {results_path}/all_subdomains.txt -silent -a -cname -resp -o {results_path}/dns_records.json -json", "parallel_group": 2},

                # STEP 11: Subdomain takeover check
                {"order": 11, "tool": "Subzy", "arguments": "run --targets {results_path}/all_subdomains.txt --output {results_path}/takeover.txt"},
            ]
        },

        # ===== PIPELINE 2: FULL RECONNAISSANCE =====
        {
            "pipeline": {
                "name": "FULL_RECON_PIPELINE",
                "description": "Complete reconnaissance from subdomain discovery to vulnerability scanning. Professional bug bounty workflow.",
                "category": PhaseCategory.SUBDOMAIN_ENUMERATION,
                "parallel_execution": True,
                "estimated_duration_minutes": 180,
                "requires_env": ["SUBFINDER_CONFIG", "NUCLEI_TEMPLATES_PATH"]
            },
            "steps": [
                # Phase 1: Subdomain enumeration (parallel)
                {"order": 1, "tool": "Subfinder", "arguments": "-d {asset} -all -silent -o {results_path}/subdomains.txt", "parallel_group": 1},
                {"order": 2, "tool": "Assetfinder", "arguments": "--subs-only {asset} | anew {results_path}/subdomains.txt", "parallel_group": 1},
                {"order": 3, "tool": "Amass", "arguments": "enum -passive -d {asset} -o {results_path}/amass_subs.txt", "parallel_group": 1},

                # Phase 2: Combine and verify
                {"order": 4, "tool": "Anew", "arguments": "cat {results_path}/subdomains.txt {results_path}/amass_subs.txt 2>/dev/null | sort -u | anew {results_path}/all_subs.txt"},
                {"order": 5, "tool": "Httpx", "arguments": "-l {results_path}/all_subs.txt -json -o {results_path}/httpx_detail.json -sc -cl -ct -location -title -tech-detect -hash md5 -jarm -asn"},
                {"order": 6, "tool": "Httpx", "arguments": "-l {results_path}/all_subs.txt -silent -o {results_path}/live_hosts.txt"},

                # Phase 3: Port scanning (parallel)
                {"order": 7, "tool": "Naabu", "arguments": "-l {results_path}/all_subs.txt -top-ports 1000 -c 50 -rate 10000 -silent -o {results_path}/open_ports.txt", "parallel_group": 3},
                {"order": 8, "tool": "Tlsx", "arguments": "-l {results_path}/live_hosts.txt -json -o {results_path}/tls_data.json", "parallel_group": 3},

                # Phase 4: Content discovery (parallel)
                {"order": 9, "tool": "Katana", "arguments": "-list {results_path}/live_hosts.txt -d 5 -jc -kf all -silent -o {results_path}/katana_urls.txt", "parallel_group": 4},
                {"order": 10, "tool": "GAU", "arguments": "--subs --threads 10 {asset} | anew {results_path}/gau_urls.txt", "parallel_group": 4},
                {"order": 11, "tool": "Waybackurls", "arguments": "{asset} | anew {results_path}/wayback_urls.txt", "parallel_group": 4},

                # Phase 5: Combine URLs
                {"order": 12, "tool": "Anew", "arguments": "cat {results_path}/*_urls.txt 2>/dev/null | sort -u | anew {results_path}/all_urls.txt"},

                # Phase 6: Technology fingerprinting
                {"order": 13, "tool": "WhatWeb", "arguments": "-i {results_path}/live_hosts.txt --log-json={results_path}/whatweb.json --aggression 3 --max-threads 50 --no-errors"},

                # Phase 7: Vulnerability scanning
                {"order": 14, "tool": "Nuclei", "arguments": "-l {results_path}/live_hosts.txt -t ~/nuclei-templates/ -severity critical,high,medium -c 50 -silent -json -o {results_path}/nuclei_vulns.json"},

                # Phase 8: Screenshot
                {"order": 15, "tool": "GoWitness", "arguments": "file -f {results_path}/live_hosts.txt -P {results_path}/screenshots --disable-logging"},
            ]
        },

        # ===== PIPELINE 3: CONTENT DISCOVERY DEEP =====
        {
            "pipeline": {
                "name": "CONTENT_DISCOVERY_DEEP",
                "description": "Deep content and endpoint discovery using multiple crawlers and archivers. Optimized for finding hidden paths.",
                "category": PhaseCategory.SPIDERING,
                "parallel_execution": True,
                "estimated_duration_minutes": 90,
            },
            "steps": [
                # Parallel crawling with multiple tools
                {"order": 1, "tool": "Katana", "arguments": "-list {input_file} -d 5 -jc -kf all -aff -ef woff,css,png,svg,jpg,woff2,jpeg,gif,svg -o {results_path}/katana.txt", "parallel_group": 1},
                {"order": 2, "tool": "Gospider", "arguments": "-S {input_file} -d 3 -c 20 -t 10 --sitemap --robots -o {results_path}/gospider", "parallel_group": 1},
                {"order": 3, "tool": "Hakrawler", "arguments": "-depth 3 -subs -u < {input_file} | anew {results_path}/hakrawler.txt", "parallel_group": 1},
                {"order": 4, "tool": "GAU", "arguments": "--threads 30 --subs < {input_file} | anew {results_path}/gau.txt", "parallel_group": 1},
                {"order": 5, "tool": "Waymore", "arguments": "-i {input_file} -mode U -oU {results_path}/waymore.txt", "parallel_group": 1},
                {"order": 6, "tool": "Waybackurls", "arguments": "< {input_file} | anew {results_path}/wayback.txt", "parallel_group": 1},

                # Combine and filter URLs
                {"order": 7, "tool": "Anew", "arguments": "cat {results_path}/*.txt 2>/dev/null | grep -E '^http' | urless | anew {results_path}/all_urls.txt"},

                # Categorize URLs using GF patterns (parallel)
                {"order": 8, "tool": "GF", "arguments": "xss < {results_path}/all_urls.txt | anew {results_path}/xss_urls.txt", "parallel_group": 2},
                {"order": 9, "tool": "GF", "arguments": "sqli < {results_path}/all_urls.txt | anew {results_path}/sqli_urls.txt", "parallel_group": 2},
                {"order": 10, "tool": "GF", "arguments": "ssrf < {results_path}/all_urls.txt | anew {results_path}/ssrf_urls.txt", "parallel_group": 2},
                {"order": 11, "tool": "GF", "arguments": "redirect < {results_path}/all_urls.txt | anew {results_path}/redirect_urls.txt", "parallel_group": 2},
                {"order": 12, "tool": "GF", "arguments": "lfi < {results_path}/all_urls.txt | anew {results_path}/lfi_urls.txt", "parallel_group": 2},

                # Extract JavaScript files
                {"order": 13, "tool": "JSFinder", "arguments": "-l {input_file} -silent -o {results_path}/js_files.txt"},
            ]
        },

        # ===== PIPELINE 4: VULNERABILITY SCAN COMPREHENSIVE =====
        {
            "pipeline": {
                "name": "VULNERABILITY_SCAN_COMPREHENSIVE",
                "description": "Multi-layered vulnerability scanning using Nuclei, SQL injection testing, and security checks.",
                "category": PhaseCategory.VULNERABILITY_SCANNING,
                "parallel_execution": True,
                "estimated_duration_minutes": 120,
                "requires_env": ["NUCLEI_TEMPLATES_PATH"]
            },
            "steps": [
                # Nuclei scanning with different severity levels (parallel)
                {"order": 1, "tool": "Nuclei", "arguments": "-l {input_file} -t ~/nuclei-templates/cves/ -severity critical,high -c 50 -silent -json -o {results_path}/nuclei_critical.json", "parallel_group": 1},
                {"order": 2, "tool": "Nuclei", "arguments": "-l {input_file} -t ~/nuclei-templates/vulnerabilities/ -severity medium,low -c 50 -silent -json -o {results_path}/nuclei_medium.json", "parallel_group": 1},
                {"order": 3, "tool": "Nuclei", "arguments": "-l {input_file} -t ~/nuclei-templates/misconfiguration/ -c 50 -silent -json -o {results_path}/nuclei_misconfig.json", "parallel_group": 1},

                # SSL/TLS scanning
                {"order": 4, "tool": "Tlsx", "arguments": "-l {input_file} -json -cn -san -hash sha256 -jarm -cipher -serial -o {results_path}/tls_scan.json", "parallel_group": 2},
                {"order": 5, "tool": "SSLyze", "arguments": "--targets_in={input_file} --json_out={results_path}/sslyze.json", "parallel_group": 2},

                # Web server scanning
                {"order": 6, "tool": "Nikto", "arguments": "-h {input_file} -o {results_path}/nikto.txt"},

                # Subdomain takeover
                {"order": 7, "tool": "Subzy", "arguments": "run --targets {input_file} --output {results_path}/takeover.txt"},
            ]
        },

        # ===== PIPELINE 5: PORT SCAN COMPLETE =====
        {
            "pipeline": {
                "name": "PORT_SCAN_COMPLETE",
                "description": "Comprehensive port scanning with service detection and TLS analysis.",
                "category": PhaseCategory.PORT_SCANNING,
                "parallel_execution": True,
                "estimated_duration_minutes": 60,
            },
            "steps": [
                # Fast top ports scan
                {"order": 1, "tool": "Naabu", "arguments": "-l {input_file} -top-ports 1000 -c 50 -rate 10000 -silent -verify -o {results_path}/top_ports.txt"},

                # Full port scan on discovered hosts
                {"order": 2, "tool": "Naabu", "arguments": "-l {input_file} -p - -c 50 -rate 7000 -silent -verify -o {results_path}/all_ports.txt"},

                # TLS analysis
                {"order": 3, "tool": "Tlsx", "arguments": "-l {input_file} -json -cn -san -hash sha256 -jarm -cipher -wc -smtp -ztls -o {results_path}/tls_analysis.json"},

                # Service detection with Nmap (on discovered ports)
                {"order": 4, "tool": "Nmap", "arguments": "-iL {input_file} -sV --top-ports 100 -T4 -oX {results_path}/nmap_services.xml"},
            ]
        },

        # ===== PIPELINE 6: JAVASCRIPT RECON =====
        {
            "pipeline": {
                "name": "JAVASCRIPT_RECON_PIPELINE",
                "description": "Deep JavaScript analysis to find endpoints, secrets, and API keys.",
                "category": PhaseCategory.JAVASCRIPT_ANALYSIS,
                "parallel_execution": True,
                "estimated_duration_minutes": 30,
            },
            "steps": [
                # Find all JS files (parallel)
                {"order": 1, "tool": "Katana", "arguments": "-list {input_file} -jc -kf all -em js -silent -o {results_path}/katana_js.txt", "parallel_group": 1},
                {"order": 2, "tool": "JSFinder", "arguments": "-l {input_file} -silent -o {results_path}/jsfinder.txt", "parallel_group": 1},
                {"order": 3, "tool": "GAU", "arguments": "--subs --threads 10 < {input_file} | grep '\\.js$' | anew {results_path}/gau_js.txt", "parallel_group": 1},

                # Combine JS files
                {"order": 4, "tool": "Anew", "arguments": "cat {results_path}/*_js.txt 2>/dev/null | sort -u | anew {results_path}/all_js_files.txt"},

                # Analyze JS files with LinkFinder
                {"order": 5, "tool": "LinkFinder", "arguments": "-i {results_path}/all_js_files.txt -o {results_path}/linkfinder_results.txt"},
            ]
        },

        # ===== PIPELINE 7: CLOUD ASSETS DISCOVERY =====
        {
            "pipeline": {
                "name": "CLOUD_ASSETS_DISCOVERY",
                "description": "Discover cloud resources across AWS, Azure, and GCP. Find exposed buckets and storage.",
                "category": PhaseCategory.CLOUD_DISCOVERY,
                "parallel_execution": True,
                "estimated_duration_minutes": 40,
            },
            "steps": [
                # Cloud enumeration
                {"order": 1, "tool": "CloudEnum", "arguments": "-k {asset} -l {results_path}/cloud_enum.txt"},

                # S3 bucket scanning
                {"order": 2, "tool": "S3Scanner", "arguments": "scan --buckets-file {input_file} --out-file {results_path}/s3_scan.json"},
            ]
        },

        # ===== PIPELINE 8: CONTINUOUS MONITORING =====
        {
            "pipeline": {
                "name": "CONTINUOUS_MONITORING",
                "description": "Lightweight continuous monitoring for new subdomains and changes. Optimized for frequent execution.",
                "category": PhaseCategory.SUBDOMAIN_ENUMERATION,
                "parallel_execution": True,
                "estimated_duration_minutes": 15,
            },
            "steps": [
                # Fast passive enumeration (parallel)
                {"order": 1, "tool": "Subfinder", "arguments": "-d {asset} -all -silent -o {results_path}/subfinder_new.txt", "parallel_group": 1},
                {"order": 2, "tool": "Chaos", "arguments": "-d {asset} -silent -o {results_path}/chaos_new.txt", "parallel_group": 1, "required": False},
                {"order": 3, "tool": "Cero", "arguments": "{asset} | anew {results_path}/cero_new.txt", "parallel_group": 1},

                # Combine and filter only new subdomains
                {"order": 4, "tool": "Anew", "arguments": "cat {results_path}/*_new.txt 2>/dev/null | anew {results_path}/all_subdomains_history.txt | tee {results_path}/newly_discovered.txt"},

                # Verify only new ones
                {"order": 5, "tool": "Httpx", "arguments": "-l {results_path}/newly_discovered.txt -json -o {results_path}/new_live_hosts.json -silent"},

                # Quick vulnerability check on new hosts
                {"order": 6, "tool": "Nuclei", "arguments": "-l {results_path}/newly_discovered.txt -t ~/nuclei-templates/ -severity critical,high -c 30 -silent -json -o {results_path}/new_vulns.json"},
            ]
        },

        # ===== PIPELINE 9: QUICK SCAN =====
        {
            "pipeline": {
                "name": "QUICK_SCAN",
                "description": "Fast reconnaissance for quick assessment. Subdomain enum + live check + basic vulns.",
                "category": PhaseCategory.SUBDOMAIN_ENUMERATION,
                "parallel_execution": True,
                "estimated_duration_minutes": 20,
            },
            "steps": [
                # Fast subdomain discovery
                {"order": 1, "tool": "Subfinder", "arguments": "-d {asset} -silent -o {results_path}/subdomains.txt", "parallel_group": 1},
                {"order": 2, "tool": "Assetfinder", "arguments": "--subs-only {asset} | anew {results_path}/subdomains.txt", "parallel_group": 1},

                # Quick verification
                {"order": 3, "tool": "Httpx", "arguments": "-l {results_path}/subdomains.txt -silent -o {results_path}/live.txt"},

                # Quick nuclei scan
                {"order": 4, "tool": "Nuclei", "arguments": "-l {results_path}/live.txt -t ~/nuclei-templates/ -severity critical -c 50 -silent -o {results_path}/critical_vulns.txt"},
            ]
        },
    ]

    # Create pipelines and steps
    for pipeline_config in pipelines_config:
        pipeline_data = pipeline_config["pipeline"]
        steps_data = pipeline_config["steps"]

        # Create pipeline
        pipeline = Pipeline(**pipeline_data)
        session.add(pipeline)
        session.flush()  # Get pipeline.id

        # Create steps
        for step_data in steps_data:
            tool_name = step_data.pop("tool")
            tool = session.query(Tool).filter_by(name=tool_name).first()
            if not tool:
                print(f"⚠ Warning: Tool '{tool_name}' not found for pipeline '{pipeline_data['name']}'")
                continue

            step = PipelineStep(
                pipeline_id=pipeline.id,
                tool_id=tool.id,
                **step_data
            )
            session.add(step)

        session.commit()
        print(f"✓ Created pipeline: {pipeline_data['name']} with {len(steps_data)} steps")

    print(f"\n✓ Created {len(pipelines_config)} professional pipelines")


def seed_configurations(session):
    """Seed default configurations"""

    configs = [
        {
            "key": "SUBFINDER_CONFIG",
            "description": "Path to Subfinder configuration file with API keys",
            "category": "api_keys",
            "required_for_tools": ["Subfinder"]
        },
        {
            "key": "CHAOS_KEY",
            "description": "ProjectDiscovery Chaos API key",
            "category": "api_keys",
            "is_sensitive": True,
            "required_for_tools": ["Chaos"]
        },
        {
            "key": "GITHUB_TOKEN",
            "description": "GitHub Personal Access Token for github-subdomains",
            "category": "api_keys",
            "is_sensitive": True,
            "required_for_tools": ["GithubSubdomains"]
        },
        {
            "key": "NUCLEI_TEMPLATES_PATH",
            "description": "Path to Nuclei templates directory",
            "value": "/root/nuclei-templates",
            "category": "tool_config",
            "required_for_tools": ["Nuclei"]
        },
        {
            "key": "RESULTS_BASE_PATH",
            "description": "Base path for storing results",
            "value": "/opt/results",
            "category": "system"
        },
        {
            "key": "MAX_PARALLEL_WORKERS",
            "description": "Maximum number of parallel Celery workers",
            "value": "10",
            "category": "system"
        },
        {
            "key": "DEFAULT_TIMEOUT",
            "description": "Default timeout for tool execution in seconds",
            "value": "3600",
            "category": "system"
        },
    ]

    for config_data in configs:
        config = session.query(Configuration).filter_by(key=config_data["key"]).first()
        if not config:
            config = Configuration(**config_data)
            session.add(config)

    session.commit()
    print(f"✓ Seeded {len(configs)} configurations")


def main():
    """Main seed function"""
    print("=" * 60)
    print("  LemonDocker - Seeding Database")
    print("  Professional Reconnaissance Pipelines 2025")
    print("=" * 60)
    print()

    # Initialize database
    print("Initializing database...")
    init_db()
    session = get_session()

    try:
        # Seed data
        seed_tools(session)
        seed_pipelines(session)
        seed_configurations(session)

        print()
        print("=" * 60)
        print("  ✓ Database seeded successfully!")
        print("=" * 60)
        print()

        # Print summary
        tool_count = session.query(Tool).count()
        pipeline_count = session.query(Pipeline).count()
        step_count = session.query(PipelineStep).count()

        print(f"Summary:")
        print(f"  • {tool_count} security tools")
        print(f"  • {pipeline_count} reconnaissance pipelines")
        print(f"  • {step_count} total pipeline steps")
        print()

    except Exception as e:
        print(f"\n✗ Error seeding database: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
