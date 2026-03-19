#!/usr/bin/env python3
"""
LinkedIn Link Extractor and Verifier

Extracts shortened LinkedIn URLs (lnkd.in) from text, resolves them to actual
destinations, fetches page titles, and generates summaries.
"""

import re
import sys
import json
import time
import argparse
import os
from dataclasses import dataclass, asdict
from typing import Optional
from urllib.parse import urlparse

try:
    import requests
    from bs4 import BeautifulSoup
    import certifi
except ImportError:
    print("Missing required dependencies. Install them with:")
    print("  pip install requests beautifulsoup4 certifi")
    sys.exit(1)


@dataclass
class LinkResult:
    """Result of processing a single link."""
    index: int
    original_url: str
    resolved_url: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    status: str = "pending"
    category: Optional[str] = None
    original_label: Optional[str] = None
    error: Optional[str] = None


class LinkedInLinkExtractor:
    """Extract and resolve LinkedIn shortened URLs."""
    
    LINKEDIN_SHORT_PATTERN = r'https?://lnkd\.in/[a-zA-Z0-9_-]+'
    
    USER_AGENT = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    
    def __init__(self, timeout: int = 10, delay: float = 0.5, verify_ssl: bool = True):
        self.timeout = timeout
        self.delay = delay
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        })
        
        if verify_ssl:
            ca_bundle = os.environ.get('REQUESTS_CA_BUNDLE') or os.environ.get('SSL_CERT_FILE')
            if ca_bundle and os.path.exists(ca_bundle):
                self.session.verify = ca_bundle
            else:
                self.session.verify = certifi.where()
        else:
            self.session.verify = False
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    def extract_urls(self, text: str) -> list[LinkResult]:
        """Extract LinkedIn shortened URLs from text with context."""
        results = []
        seen_urls = set()
        current_category = None
        
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if self._is_category_header(line):
                current_category = line.rstrip(':').strip()
                continue
            
            urls = re.findall(self.LINKEDIN_SHORT_PATTERN, line)
            
            for url in urls:
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                
                label = self._extract_label(line, url)
                
                results.append(LinkResult(
                    index=len(results) + 1,
                    original_url=url,
                    category=current_category,
                    original_label=label,
                ))
        
        return results
    
    def _is_category_header(self, line: str) -> bool:
        """Check if a line is a category header (e.g., VIDEOS, REPOS)."""
        clean = line.rstrip(':').strip()
        return (
            clean.isupper() and 
            len(clean.split()) <= 3 and 
            not re.search(self.LINKEDIN_SHORT_PATTERN, line)
        )
    
    def _extract_label(self, line: str, url: str) -> Optional[str]:
        """Extract the label/name associated with a URL in a line."""
        pattern = r'^\d+\.\s*(.+?):\s*' + re.escape(url)
        match = re.search(pattern, line)
        if match:
            return match.group(1).strip()
        
        before_url = line.split(url)[0].strip()
        before_url = re.sub(r'^\d+\.\s*', '', before_url)
        before_url = before_url.rstrip(':').strip()
        if before_url:
            return before_url
        
        return None
    
    def resolve_url(self, url: str) -> tuple[Optional[str], Optional[str]]:
        """Resolve a shortened URL to its final destination."""
        resolved, error = self._resolve_with_curl(url)
        if resolved:
            return resolved, None
        
        try:
            response = self.session.head(
                url, 
                allow_redirects=True, 
                timeout=self.timeout
            )
            return response.url, None
        except requests.exceptions.TooManyRedirects:
            try:
                response = self.session.get(
                    url, 
                    allow_redirects=True, 
                    timeout=self.timeout
                )
                return response.url, None
            except Exception as e:
                return None, str(e)
        except Exception as e:
            return None, str(e)
    
    def _resolve_with_curl(self, url: str) -> tuple[Optional[str], Optional[str]]:
        """Use curl to resolve URL (more reliable with corporate proxies)."""
        import subprocess
        try:
            result = subprocess.run(
                ['curl', '-Ls', '-o', '/dev/null', '-w', '%{url_effective}', url],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            if result.returncode == 0 and result.stdout:
                resolved = result.stdout.strip()
                if 'lnkd.in' in resolved:
                    actual_url = self._extract_from_linkedin_interstitial(url)
                    if actual_url:
                        return actual_url, None
                return resolved, None
            return None, result.stderr
        except subprocess.TimeoutExpired:
            return None, "Timeout"
        except Exception as e:
            return None, str(e)
    
    def _extract_from_linkedin_interstitial(self, url: str) -> Optional[str]:
        """Extract actual URL from LinkedIn's interstitial warning page."""
        import subprocess
        try:
            result = subprocess.run(
                ['curl', '-Ls', '-A', self.USER_AGENT, url],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            if result.returncode == 0 and result.stdout:
                match = re.search(r'data-tracking-will-navigate\s+href="([^"]+)"', result.stdout)
                if match:
                    return match.group(1)
                match = re.search(r'href="(https?://(?!linkedin\.com|lnkd\.in)[^"]+)"', result.stdout)
                if match:
                    return match.group(1)
            return None
        except Exception:
            return None
    
    def fetch_page_info(self, url: str) -> tuple[Optional[str], Optional[str], Optional[str]]:
        """Fetch page title and generate summary from URL."""
        html_content = self._fetch_with_curl(url)
        if not html_content:
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                html_content = response.text
            except Exception as e:
                return None, None, str(e)
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            title = None
            og_title = soup.find('meta', property='og:title')
            if og_title and og_title.get('content'):
                title = og_title['content'].strip()
            elif soup.title:
                title = soup.title.string.strip() if soup.title.string else None
            
            description = None
            og_desc = soup.find('meta', property='og:description')
            if og_desc and og_desc.get('content'):
                description = og_desc['content'].strip()
            else:
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc and meta_desc.get('content'):
                    description = meta_desc['content'].strip()
            
            summary = self._generate_summary(title, description, url)
            
            return title, summary, None
            
        except Exception as e:
            return None, None, str(e)
    
    def _fetch_with_curl(self, url: str) -> Optional[str]:
        """Use curl to fetch page content (more reliable with corporate proxies)."""
        import subprocess
        try:
            result = subprocess.run(
                ['curl', '-Ls', '-A', self.USER_AGENT, url],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0 and result.stdout:
                return result.stdout
            return None
        except Exception:
            return None
    
    def _generate_summary(self, title: Optional[str], description: Optional[str], url: str) -> str:
        """Generate a one-line summary from available info."""
        domain = urlparse(url).netloc.replace('www.', '')
        
        if description:
            summary = description[:150]
            if len(description) > 150:
                summary = summary.rsplit(' ', 1)[0] + '...'
            return summary
        
        if title:
            return f"Resource titled '{title}' on {domain}"
        
        return f"Content hosted on {domain}"
    
    def process_link(self, result: LinkResult, verbose: bool = False) -> LinkResult:
        """Process a single link: resolve, fetch info, and update result."""
        if verbose:
            print(f"  [{result.index}] Resolving {result.original_url}...", end=" ", flush=True)
        
        resolved_url, error = self.resolve_url(result.original_url)
        
        if error or not resolved_url:
            result.status = "failed"
            result.error = error or "Could not resolve URL"
            if verbose:
                print("❌")
            return result
        
        result.resolved_url = resolved_url
        
        if verbose:
            print("✓", flush=True)
            print(f"      Fetching page info...", end=" ", flush=True)
        
        title, summary, fetch_error = self.fetch_page_info(resolved_url)
        
        if fetch_error:
            result.status = "partial"
            result.error = fetch_error
            result.title = result.original_label or self._extract_domain(resolved_url)
            result.summary = f"Content at {self._extract_domain(resolved_url)} (could not fetch details)"
            if verbose:
                print("⚠️")
        else:
            result.status = "success"
            result.title = title or result.original_label or self._extract_domain(resolved_url)
            result.summary = summary
            if verbose:
                print("✓")
        
        return result
    
    def _extract_domain(self, url: str) -> str:
        """Extract clean domain from URL."""
        return urlparse(url).netloc.replace('www.', '')
    
    def process_all(self, text: str, verbose: bool = True) -> list[LinkResult]:
        """Extract and process all links from text."""
        results = self.extract_urls(text)
        
        if not results:
            print("No LinkedIn shortened URLs (lnkd.in) found in the input.")
            return []
        
        if verbose:
            print(f"\nFound {len(results)} unique LinkedIn link(s). Processing...\n")
        
        for i, result in enumerate(results):
            self.process_link(result, verbose=verbose)
            if i < len(results) - 1:
                time.sleep(self.delay)
        
        return results
    
    def format_markdown_table(self, results: list[LinkResult]) -> str:
        """Format results as a markdown table."""
        if not results:
            return "No links found."
        
        lines = []
        current_category = None
        
        for result in results:
            if result.category and result.category != current_category:
                if current_category is not None:
                    lines.append("")
                lines.append(f"### {result.category}")
                lines.append("")
                lines.append("| # | Status | Title | Resolved URL | Summary |")
                lines.append("|---|--------|-------|--------------|---------|")
                current_category = result.category
            elif current_category is None and not any(r.category for r in results):
                lines.append("| # | Status | Title | Resolved URL | Summary |")
                lines.append("|---|--------|-------|--------------|---------|")
                current_category = "__none__"
            
            status_icon = {
                "success": "✅",
                "partial": "⚠️",
                "failed": "❌",
                "pending": "⏳"
            }.get(result.status, "?")
            
            title = (result.title or "Unknown")[:50]
            resolved = result.resolved_url or result.original_url
            summary = (result.summary or result.error or "N/A")[:100]
            
            lines.append(f"| {result.index} | {status_icon} | {title} | {resolved} | {summary} |")
        
        return "\n".join(lines)
    
    def format_json(self, results: list[LinkResult]) -> str:
        """Format results as JSON."""
        return json.dumps([asdict(r) for r in results], indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Extract and verify LinkedIn shortened URLs"
    )
    parser.add_argument(
        "--json", 
        action="store_true", 
        help="Output results as JSON"
    )
    parser.add_argument(
        "--timeout", 
        type=int, 
        default=10, 
        help="Timeout per URL in seconds (default: 10)"
    )
    parser.add_argument(
        "--delay", 
        type=float, 
        default=0.5, 
        help="Delay between requests in seconds (default: 0.5)"
    )
    parser.add_argument(
        "--quiet", 
        action="store_true", 
        help="Suppress progress output"
    )
    parser.add_argument(
        "--no-verify-ssl",
        action="store_true",
        help="Disable SSL certificate verification (for corporate proxies)"
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        help="Input file (reads from stdin if not provided)"
    )
    
    args = parser.parse_args()
    
    if args.input_file:
        with open(args.input_file, 'r') as f:
            text = f.read()
    else:
        print("Paste LinkedIn post content (press Ctrl+D or Ctrl+Z when done):")
        print("-" * 50)
        try:
            text = sys.stdin.read()
        except KeyboardInterrupt:
            print("\nCancelled.")
            sys.exit(0)
    
    extractor = LinkedInLinkExtractor(
        timeout=args.timeout, 
        delay=args.delay,
        verify_ssl=not args.no_verify_ssl
    )
    results = extractor.process_all(text, verbose=not args.quiet)
    
    if not results:
        sys.exit(0)
    
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60 + "\n")
    
    if args.json:
        print(extractor.format_json(results))
    else:
        print(extractor.format_markdown_table(results))
    
    success = sum(1 for r in results if r.status == "success")
    partial = sum(1 for r in results if r.status == "partial")
    failed = sum(1 for r in results if r.status == "failed")
    
    print(f"\n\nSummary: {success} ✅ | {partial} ⚠️ | {failed} ❌ | Total: {len(results)}")


if __name__ == "__main__":
    main()
