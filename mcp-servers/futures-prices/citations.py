"""
Citation metadata helpers for North MCP.
"""

from datetime import datetime
from typing import Dict, Any, Optional


def create_citation_metadata(
    title: str,
    source_url: str = "https://energy-trader.local/futures-prices",
    author_name: str = "Energy Trader Database",
    last_updated: Optional[datetime] = None,
    page_number: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create citation metadata following North MCP format.
    
    Args:
        title: Title of the data source
        source_url: URL or identifier for the source
        author_name: Name of the data source/author
        last_updated: Timestamp of last update (defaults to now)
        page_number: Optional page number
        
    Returns:
        Dictionary with _north_metadata structure
    """
    if last_updated is None:
        last_updated = datetime.utcnow()
    
    metadata = {
        "title": title,
        "url": source_url,
        "author_name": author_name,
        "last_updated": last_updated.isoformat() + "Z"
    }
    
    if page_number:
        metadata["page_number"] = page_number
    
    return {
        "_north_metadata": metadata
    }


def format_price_response(text: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format tool response with text and citation metadata.
    
    Args:
        text: Response text content
        metadata: Citation metadata dictionary
        
    Returns:
        Formatted response dictionary
    """
    return {
        "text": text,
        **metadata
    }

