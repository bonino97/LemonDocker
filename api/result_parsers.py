"""
Result parsers for different security tools
Extracts structured data from tool outputs
"""
import json
import re
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
from urllib.parse import urlparse


class BaseParser:
    """Base class for result parsers"""

    def __init__(self, tool_name: str):
        self.tool_name = tool_name

    def parse(self, output: str, output_file: str = None) -> List[Dict[str, Any]]:
        """Parse tool output and return structured results"""
        raise NotImplementedError


class SubdomainParser(BaseParser):
    """Parser for subdomain enumeration tools (Subfinder, Assetfinder, etc.)"""

    def parse(self, output: str, output_file: str = None) -> List[Dict[str, Any]]:
        results = []
        lines = output.strip().split('\n') if output else []

        # Try to read from file if provided
        if output_file:
            try:
                with open(output_file, 'r') as f:
                    lines = f.read().strip().split('\n')
            except:
                pass

        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                # Validate domain format
                if self._is_valid_domain(line):
                    results.append({
                        'result_type': 'subdomain',
                        'value': line,
                        'source_tool': self.tool_name,
                        'confidence': 0.9,
                        'metadata': {}
                    })

        return results

    def _is_valid_domain(self, domain: str) -> bool:
        """Validate domain format"""
        pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        return bool(re.match(pattern, domain))


class HttpxParser(BaseParser):
    """Parser for Httpx JSON output"""

    def parse(self, output: str, output_file: str = None) -> List[Dict[str, Any]]:
        results = []
        lines = output.strip().split('\n') if output else []

        # Try to read from file if provided
        if output_file:
            try:
                with open(output_file, 'r') as f:
                    lines = f.read().strip().split('\n')
            except:
                pass

        for line in lines:
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)
                result = {
                    'result_type': 'live_host',
                    'value': data.get('url', ''),
                    'source_tool': self.tool_name,
                    'confidence': 1.0,
                    'metadata': {
                        'status_code': data.get('status_code'),
                        'content_length': data.get('content_length'),
                        'content_type': data.get('content_type'),
                        'title': data.get('title'),
                        'webserver': data.get('webserver'),
                        'tech': data.get('tech', []),
                        'ip': data.get('host'),
                        'cdn': data.get('cdn'),
                        'asn': data.get('asn', {}).get('as_number') if isinstance(data.get('asn'), dict) else None,
                        'hash': data.get('hash', {}),
                        'jarm': data.get('jarm')
                    }
                }
                results.append(result)
            except json.JSONDecodeError:
                # Simple text format (just URL)
                if line.startswith('http'):
                    results.append({
                        'result_type': 'live_host',
                        'value': line,
                        'source_tool': self.tool_name,
                        'confidence': 0.95,
                        'metadata': {}
                    })

        return results


class NucleiParser(BaseParser):
    """Parser for Nuclei vulnerability scanner output"""

    def parse(self, output: str, output_file: str = None) -> List[Dict[str, Any]]:
        results = []
        lines = output.strip().split('\n') if output else []

        # Try to read from file
        if output_file:
            try:
                with open(output_file, 'r') as f:
                    lines = f.read().strip().split('\n')
            except:
                pass

        severity_map = {
            'critical': 1.0,
            'high': 0.9,
            'medium': 0.7,
            'low': 0.5,
            'info': 0.3
        }

        for line in lines:
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)
                severity = data.get('info', {}).get('severity', 'info').lower()

                result = {
                    'result_type': 'vulnerability',
                    'value': data.get('matched-at', data.get('host', '')),
                    'source_tool': self.tool_name,
                    'severity': severity,
                    'confidence': severity_map.get(severity, 0.5),
                    'metadata': {
                        'template_id': data.get('template-id'),
                        'template_name': data.get('info', {}).get('name'),
                        'type': data.get('type'),
                        'tags': data.get('info', {}).get('tags', []),
                        'description': data.get('info', {}).get('description'),
                        'reference': data.get('info', {}).get('reference'),
                        'cvss_score': data.get('info', {}).get('classification', {}).get('cvss-score'),
                        'cve_id': data.get('info', {}).get('classification', {}).get('cve-id'),
                        'matcher_name': data.get('matcher-name'),
                        'extracted_results': data.get('extracted-results', []),
                        'curl_command': data.get('curl-command')
                    }
                }
                results.append(result)
            except json.JSONDecodeError:
                continue

        return results


class PortScanParser(BaseParser):
    """Parser for Naabu/Masscan port scan output"""

    def parse(self, output: str, output_file: str = None) -> List[Dict[str, Any]]:
        results = []
        lines = output.strip().split('\n') if output else []

        # Try to read from file
        if output_file:
            try:
                with open(output_file, 'r') as f:
                    lines = f.read().strip().split('\n')
            except:
                pass

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Format: host:port or just port
            parts = line.split(':')
            if len(parts) == 2:
                host, port = parts
                results.append({
                    'result_type': 'open_port',
                    'value': line,
                    'source_tool': self.tool_name,
                    'confidence': 0.95,
                    'metadata': {
                        'host': host,
                        'port': int(port),
                        'protocol': 'tcp'
                    }
                })

        return results


class URLParser(BaseParser):
    """Parser for URL discovery tools (Katana, GAU, Waybackurls, etc.)"""

    def parse(self, output: str, output_file: str = None) -> List[Dict[str, Any]]:
        results = []
        lines = output.strip().split('\n') if output else []

        # Try to read from file
        if output_file:
            try:
                with open(output_file, 'r') as f:
                    lines = f.read().strip().split('\n')
            except:
                pass

        for line in lines:
            line = line.strip()
            if not line or not line.startswith('http'):
                continue

            # Extract URL components
            try:
                parsed = urlparse(line)

                # Categorize URL
                url_type = self._categorize_url(line, parsed)

                results.append({
                    'result_type': url_type,
                    'value': line,
                    'source_tool': self.tool_name,
                    'confidence': 0.9,
                    'metadata': {
                        'scheme': parsed.scheme,
                        'domain': parsed.netloc,
                        'path': parsed.path,
                        'query': parsed.query,
                        'params': parsed.params,
                        'extension': self._get_extension(parsed.path),
                        'has_params': bool(parsed.query)
                    }
                })
            except:
                continue

        return results

    def _categorize_url(self, url: str, parsed) -> str:
        """Categorize URL based on characteristics"""
        path = parsed.path.lower()

        # JavaScript files
        if path.endswith('.js'):
            return 'javascript_file'

        # API endpoints
        if '/api/' in path or parsed.path.startswith('/v1/') or parsed.path.startswith('/v2/'):
            return 'api_endpoint'

        # Admin panels
        if any(x in path for x in ['/admin', '/dashboard', '/panel', '/wp-admin']):
            return 'admin_url'

        # Static files
        if any(path.endswith(ext) for ext in ['.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.ttf']):
            return 'static_file'

        # URLs with parameters (potential injection points)
        if parsed.query:
            return 'parameterized_url'

        return 'url'

    def _get_extension(self, path: str) -> str:
        """Extract file extension from path"""
        if '.' in path:
            return path.split('.')[-1].lower()
        return ''


class DNSParser(BaseParser):
    """Parser for DNS resolution tools (Dnsx, MassDNS)"""

    def parse(self, output: str, output_file: str = None) -> List[Dict[str, Any]]:
        results = []
        lines = output.strip().split('\n') if output else []

        # Try to read from file
        if output_file:
            try:
                with open(output_file, 'r') as f:
                    lines = f.read().strip().split('\n')
            except:
                pass

        for line in lines:
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)
                result = {
                    'result_type': 'dns_record',
                    'value': data.get('host', ''),
                    'source_tool': self.tool_name,
                    'confidence': 1.0,
                    'metadata': {
                        'a': data.get('a', []),
                        'aaaa': data.get('aaaa', []),
                        'cname': data.get('cname', []),
                        'mx': data.get('mx', []),
                        'ns': data.get('ns', []),
                        'txt': data.get('txt', []),
                        'ptr': data.get('ptr', []),
                        'soa': data.get('soa', [])
                    }
                }
                results.append(result)
            except json.JSONDecodeError:
                # Simple format: domain IP
                parts = line.split()
                if len(parts) >= 2:
                    results.append({
                        'result_type': 'dns_record',
                        'value': parts[0],
                        'source_tool': self.tool_name,
                        'confidence': 0.9,
                        'metadata': {
                            'a': [parts[1]]
                        }
                    })

        return results


class TechnologyParser(BaseParser):
    """Parser for technology detection tools (WhatWeb, Webanalyze)"""

    def parse(self, output: str, output_file: str = None) -> List[Dict[str, Any]]:
        results = []

        # Try to read from file
        if output_file:
            try:
                with open(output_file, 'r') as f:
                    data = json.load(f)

                    # WhatWeb format (array of objects)
                    if isinstance(data, list):
                        for entry in data:
                            target = entry.get('target', '')
                            plugins = entry.get('plugins', {})

                            techs = []
                            for plugin_name, plugin_data in plugins.items():
                                if isinstance(plugin_data, dict):
                                    version = plugin_data.get('version', [''])[0] if isinstance(plugin_data.get('version'), list) else plugin_data.get('version', '')
                                    techs.append(f"{plugin_name}:{version}" if version else plugin_name)

                            results.append({
                                'result_type': 'technology',
                                'value': target,
                                'source_tool': self.tool_name,
                                'confidence': 0.85,
                                'metadata': {
                                    'technologies': techs,
                                    'http_status': entry.get('http_status'),
                                    'plugins': plugins
                                }
                            })
            except:
                pass

        return results


class TakeoverParser(BaseParser):
    """Parser for subdomain takeover detection (Subzy)"""

    def parse(self, output: str, output_file: str = None) -> List[Dict[str, Any]]:
        results = []
        lines = output.strip().split('\n') if output else []

        # Try to read from file
        if output_file:
            try:
                with open(output_file, 'r') as f:
                    lines = f.read().strip().split('\n')
            except:
                pass

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Subzy output format typically includes "Vulnerable:" or similar
            if 'vulnerable' in line.lower() or 'takeover' in line.lower():
                # Extract domain
                parts = line.split()
                domain = parts[0] if parts else line

                results.append({
                    'result_type': 'subdomain_takeover',
                    'value': domain,
                    'source_tool': self.tool_name,
                    'severity': 'high',
                    'confidence': 0.9,
                    'metadata': {
                        'details': line,
                        'vulnerable': True
                    }
                })

        return results


class CloudAssetsParser(BaseParser):
    """Parser for cloud asset discovery tools"""

    def parse(self, output: str, output_file: str = None) -> List[Dict[str, Any]]:
        results = []
        lines = output.strip().split('\n') if output else []

        # Try to read from file
        if output_file:
            try:
                with open(output_file, 'r') as f:
                    content = f.read()
                    try:
                        data = json.loads(content)
                        if isinstance(data, list):
                            for item in data:
                                results.append({
                                    'result_type': 'cloud_asset',
                                    'value': item.get('bucket', item.get('name', '')),
                                    'source_tool': self.tool_name,
                                    'confidence': 0.9,
                                    'metadata': item
                                })
                        return results
                    except:
                        lines = content.strip().split('\n')
            except:
                pass

        # Parse text format
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Look for S3 buckets, Azure storage, etc.
            if any(x in line.lower() for x in ['s3.amazonaws.com', 'blob.core.windows.net', 'storage.googleapis.com']):
                results.append({
                    'result_type': 'cloud_asset',
                    'value': line,
                    'source_tool': self.tool_name,
                    'confidence': 0.85,
                    'metadata': {
                        'raw_output': line
                    }
                })

        return results


# Parser factory
def get_parser(tool_name: str, category: str = None) -> BaseParser:
    """Get appropriate parser for tool"""

    # Map tools to parsers
    parser_map = {
        # Subdomain enumeration
        'Subfinder': SubdomainParser,
        'Assetfinder': SubdomainParser,
        'Amass': SubdomainParser,
        'Chaos': SubdomainParser,
        'Findomain': SubdomainParser,
        'Cero': SubdomainParser,
        'Sublist3r': SubdomainParser,
        'GithubSubdomains': SubdomainParser,
        'AlterX': SubdomainParser,

        # Active verification
        'Httpx': HttpxParser,
        'Httprobe': URLParser,
        'Dnsx': DNSParser,
        'MassDNS': DNSParser,

        # URLs and crawling
        'Katana': URLParser,
        'GAU': URLParser,
        'Gospider': URLParser,
        'Hakrawler': URLParser,
        'Waymore': URLParser,
        'Waybackurls': URLParser,

        # Port scanning
        'Naabu': PortScanParser,
        'Masscan': PortScanParser,

        # Vulnerabilities
        'Nuclei': NucleiParser,

        # Technology
        'WhatWeb': TechnologyParser,
        'Webanalyze': TechnologyParser,

        # Takeover
        'Subzy': TakeoverParser,

        # Cloud
        'CloudEnum': CloudAssetsParser,
        'S3Scanner': CloudAssetsParser,
    }

    parser_class = parser_map.get(tool_name, BaseParser)
    return parser_class(tool_name)
