"""
Metadata Configuration for GovInsight

This module provides manual metadata configuration for PDF documents.
All metadata is explicitly defined here rather than extracted from PDF content,
ensuring consistent and reliable metadata for the RAG pipeline.

To add a new PDF document:
1. Add an entry to DOCUMENT_METADATA with the filename (without path) as key
2. Fill in all required fields: year, ministry, scheme, budget_category
3. Re-run the indexing pipeline

The metadata schema ensures every chunk stored in the vector database
has complete and consistent metadata, preventing query failures.
"""

from typing import Dict, Optional, List


# Default metadata schema with required fields and their default values
DEFAULT_METADATA_SCHEMA = {
    "year": "Unknown",
    "ministry": "Unknown",
    "scheme": "General",
    "budget_category": "General",
    "state": "Central",  # For future state budget extension
    "document_type": "Budget Document"
}


# Manual metadata configuration for each PDF document
# Key: PDF filename (without path, case-sensitive)
# Value: Dictionary with metadata fields
DOCUMENT_METADATA: Dict[str, Dict[str, str]] = {
    # Example entries - customize these for your actual PDF files
    #
    # "Budget_2023-24_Expenditure.pdf": {
    #     "year": "2023-24",
    #     "ministry": "Ministry of Finance",
    #     "scheme": "General",
    #     "budget_category": "Expenditure Budget",
    #     "state": "Central",
    #     "document_type": "Expenditure Budget"
    # },
    #
    # "MoRTH_Demands_2024-25.pdf": {
    #     "year": "2024-25",
    #     "ministry": "Ministry of Road Transport & Highways",
    #     "scheme": "Bharatmala Pariyojana",
    #     "budget_category": "Demands for Grants",
    #     "state": "Central",
    #     "document_type": "Demands for Grants"
    # },
    #
    # Add your actual PDF files below:
    "Annual Report 2024-25 (English).pdf": {
        "document_name": "Annual Report 2024-25 (English).pdf",
        "year": "2024-25",
        "ministry": "NITI Aayog",
        "scheme": "General",
        "budget_category": "Annual Report",
        "state": "Central",
        "document_type": "NITI Aayog Annual Report"
    },
    "Annual_Report_2021_2022_(English).pdf": {
        "document_name": "Annual_Report_2021_2022_(English).pdf",
        "year": "2021-22",
        "ministry": "Ministry of Finance",
        "scheme": "General",
        "budget_category": "Annual Report",
        "state": "Central",
        "document_type": "Annual Report"
    },
    "Annual-Report-2022-2023-(English).pdf": {
        "document_name": "Annual-Report-2022-2023-(English).pdf",
        "year": "2022-23",
        "ministry": "Ministry of Finance",
        "scheme": "General",
        "budget_category": "Annual Report",
        "state": "Central",
        "document_type": "Annual Report"
    },
    "Annual-Report2020-2021-(English).pdf": {
        "document_name": "Annual-Report2020-2021-(English).pdf",
        "year": "2020-21",
        "ministry": "Ministry of Finance",
        "scheme": "General",
        "budget_category": "Annual Report",
        "state": "Central",
        "document_type": "Annual Report"
    },
    "beti bacho.pdf": {
        "document_name": "beti bacho.pdf",
        "year": "2024-25",
        "ministry": "Ministry of Women and Child Development",
        "scheme": "Beti Bachao Beti Padhao",
        "budget_category": "Scheme",
        "state": "Central",
        "document_type": "Scheme Document"
    },
    "budget_at_a_glance(2024-2025).pdf": {
        "document_name": "budget_at_a_glance(2024-2025).pdf",
        "year": "2024-25",
        "ministry": "Ministry of Finance",
        "scheme": "General",
        "budget_category": "Budget Overview",
        "state": "Central",
        "document_type": "Budget at a Glance"
    },
    "Budget_Speech(2021-2022).pdf": {
        "document_name": "Budget_Speech(2021-2022).pdf",
        "year": "2021-22",
        "ministry": "Ministry of Finance",
        "scheme": "General",
        "budget_category": "Budget Speech",
        "state": "Central",
        "document_type": "Budget Speech"
    },
    "budget_speech(2023-2024).pdf": {
        "document_name": "budget_speech(2023-2024).pdf",
        "year": "2023-24",
        "ministry": "Ministry of Finance",
        "scheme": "General",
        "budget_category": "Budget Speech",
        "state": "Central",
        "document_type": "Budget Speech"
    },
    "budget_speech(2025-2026).pdf": {
        "document_name": "budget_speech(2025-2026).pdf",
        "year": "2025-26",
        "ministry": "Ministry of Finance",
        "scheme": "General",
        "budget_category": "Budget Speech",
        "state": "Central",
        "document_type": "Budget Speech"
    },
    "child welfare focus.pdf": {
        "document_name": "child welfare focus.pdf",
        "year": "2024-25",
        "ministry": "Ministry of Women and Child Development",
        "scheme": "Child Welfare",  
        "budget_category": "Scheme",
        "state": "Central", 
        "document_type": "Scheme Document"
    },
    "constitution.pdf": {
        "document_name": "constitiution.pdf",
        "year": "2024-25",
        "ministry": "Ministry of Law and Justice",
        "scheme": "General",
        "budget_category": "Legal Document",
        "state": "Central",
        "document_type": "Constitution of India"
    },
    "Fiscal_Health_Index_24012025_Final.pdf": {
        "document_name": "Fiscal_Health_Index_24012025_Final.pdf",
        "year": "2024-25",
        "ministry": "Ministry of Finance",
        "scheme": "General",
        "budget_category": "Fiscal Health Index",   
        "state": "Central",
        "document_type": "Fiscal Health Index Report"
    },
    "lok sabha debates.pdf": {
        "document_name": "lok sabha debates.pdf",
        "year": "2024-25",
        "ministry": "Lok Sabha",
        "scheme": "General",
        "budget_category": "Parliamentary Debates",
        "state": "Central",
        "document_type": "Lok Sabha Debates"
    },
    "Naari Shakthi.pdf": {
        "document_name": "Naari Shakthi.pdf",
        "year": "2024-25",
        "ministry": "Ministry of Women and Child Development",
        "scheme": "Naari Shakthi",
        "budget_category": "Scheme",
        "state": "Central",
        "document_type": "Scheme Document"
    },
    "National-Multidimentional-Poverty-Index-2023-Final-17th-July.pdf": {
        "document_name": "National-Multidimentional-Poverty-Index-2023-Final-17th-July.pdf",
        "year": "2023",
        "ministry": "NITI Aayog",
        "scheme": "Poverty Alleviation",
        "budget_category": "Policy Report",
        "state": "Central",
        "document_type": "NITI Aayog Report"
    
    },
    "prs (child and women development).pdf": {
        "document_name": "prs (child and women development).pdf",
        "year": "2024-25",
        "ministry": "Ministry of Women and Child Development",
        "scheme": "General",
        "budget_category": "PRS Report",
        "state": "Central",
        "document_type": "PRS Report"
    },
    "rajya sabha.pdf": {
        "document_name": "rajya sabha.pdf",
        "year": "2024-25",
        "ministry": "Rajya Sabha",
        "scheme": "General",
        "budget_category": "Parliamentary Debates",
        "state": "Central",
        "document_type": "Rajya Sabha Debates"
    },
    "SDG_India_Index_2023-24.pdf": {
        "document_name": "SDG_India_Index_2023-24.pdf",
        "year": "2023-24",
        "ministry": "NITI Aayog",
        "scheme": "Sustainable Development Goals",
        "budget_category": "Policy Report",
        "state": "Central",

        "document_type": "SDG India Index Report"
    },
    "SDG-NER-Report(2023-2024).pdf": {
        "document_name": "SDG-NER-Report(2023-2024).pdf",
        "year": "2023-24",
        "ministry": "NITI Aayog",
        "scheme": "Sustainable Development Goals",
        "budget_category": "Policy Report",
        "state": "Central",
        "document_type": "SDG NER Report"
    },
    "transport(2024-2025).pdf": {
        "document_name": "transport(2024-2025).pdf",
        "year": "2024-25",
        "ministry": "Ministry of Road Transport & Highways",
        "scheme": "Bharatmala Pariyojana",
        "budget_category": "Demands for Grants",
        "state": "Central",
        "document_type": "Demands for Grants"
    },
    "women and child development (annual report).pdf": {
        "document_name": "women and child development (annual report).pdf",
        "year": "2024-25",
        "ministry": "Ministry of Women and Child Development",
        "scheme": "General",
        "budget_category": "Annual Report",
        "state": "Central",
        "document_type": "Annual Report"
    },
    "women and child development-expenditure.pdf": {
        "document_name": "women and child development-expenditure.pdf",
        "year": "2024-25",
        "ministry": "Ministry of Women and Child Development",
        "scheme": "General",
        "budget_category": "Expenditure",
        "state": "Central",
        "document_type": "Expenditure Report"
    }
}
def get_metadata_for_document(filename: str) -> Dict[str, str]:
    """
    Get metadata for a specific PDF document.
    
    If the document is not found in DOCUMENT_METADATA, returns default metadata
    to ensure every chunk has complete metadata schema.
    
    Args:
        filename: PDF filename (without path)
        
    Returns:
        Complete metadata dictionary with all required fields
    """
    # Start with default schema
    metadata = DEFAULT_METADATA_SCHEMA.copy()
    
    # Override with document-specific metadata if available
    if filename in DOCUMENT_METADATA:
        doc_metadata = DOCUMENT_METADATA[filename]
        metadata.update(doc_metadata)
    else:
        # Document not in configuration - use defaults but log a warning
        print(f"  ⚠️  WARNING: No metadata configured for '{filename}'. Using defaults.")
        print(f"     Add this file to DOCUMENT_METADATA in metadata_config.py for accurate metadata.")
    
    return metadata


def validate_metadata(metadata: Dict[str, str]) -> Dict[str, str]:
    """
    Validate and normalize metadata to ensure all required fields are present.
    
    This function guarantees that every metadata dictionary has all required
    fields with valid string values, preventing KeyError during queries.
    
    Args:
        metadata: Metadata dictionary to validate
        
    Returns:
        Validated metadata with all required fields
    """
    validated = DEFAULT_METADATA_SCHEMA.copy()
    
    for key, default_value in DEFAULT_METADATA_SCHEMA.items():
        if key in metadata and metadata[key] is not None:
            # Ensure value is a non-empty string
            value = str(metadata[key]).strip()
            validated[key] = value if value else default_value
        else:
            validated[key] = default_value
    
    return validated


def get_all_configured_documents() -> List[str]:
    """
    Get list of all documents that have metadata configured.
    
    Returns:
        List of configured document filenames
    """
    return list(DOCUMENT_METADATA.keys())


def add_document_metadata(filename: str, metadata: Dict[str, str]) -> None:
    """
    Programmatically add metadata for a document.
    
    This can be used to add metadata at runtime before indexing.
    
    Args:
        filename: PDF filename (without path)
        metadata: Metadata dictionary for the document
    """
    DOCUMENT_METADATA[filename] = validate_metadata(metadata)
    print(f"  Added metadata for: {filename}")


def bulk_add_metadata(metadata_list: List[Dict[str, str]]) -> None:
    """
    Add metadata for multiple documents at once.
    
    Each entry in metadata_list must have a 'filename' key plus the metadata fields.
    
    Args:
        metadata_list: List of dictionaries with 'filename' and metadata fields
        
    Example:
        bulk_add_metadata([
            {
                "filename": "Budget_2023-24.pdf",
                "year": "2023-24",
                "ministry": "Ministry of Finance",
                "scheme": "General",
                "budget_category": "Union Budget"
            },
            ...
        ])
    """
    for entry in metadata_list:
        filename = entry.pop("filename", None)
        if filename:
            add_document_metadata(filename, entry)
        else:
            print("  ⚠️  WARNING: Entry missing 'filename' field, skipping.")


# Sample configuration for common budget document types
SAMPLE_CONFIGURATIONS = """
# Copy and customize these examples for your PDF files:

DOCUMENT_METADATA = {
    # Union Budget - Expenditure
    "Expenditure_Budget_Vol1_2024-25.pdf": {
        "year": "2024-25",
        "ministry": "Ministry of Finance",
        "scheme": "General",
        "budget_category": "Expenditure Budget",
        "state": "Central",
        "document_type": "Expenditure Budget Volume I"
    },
    
    # Ministry of Road Transport & Highways
    "MoRTH_Demands_2024-25.pdf": {
        "year": "2024-25",
        "ministry": "Ministry of Road Transport & Highways",
        "scheme": "Bharatmala Pariyojana",
        "budget_category": "Demands for Grants",
        "state": "Central",
        "document_type": "Demands for Grants"
    },
    
    # Budget at a Glance
    "Budget_at_Glance_2023-24.pdf": {
        "year": "2023-24",
        "ministry": "Ministry of Finance",
        "scheme": "General",
        "budget_category": "Budget Overview",
        "state": "Central",
        "document_type": "Budget at a Glance"
    },
    
    # NITI Aayog Report
    "NITI_Infrastructure_Report_2023.pdf": {
        "year": "2023",
        "ministry": "NITI Aayog",
        "scheme": "Infrastructure Development",
        "budget_category": "Policy Report",
        "state": "Central",
        "document_type": "NITI Aayog Report"
    },
    
    # PMGSY Scheme Document
    "PMGSY_Allocation_2024-25.pdf": {
        "year": "2024-25",
        "ministry": "Ministry of Rural Development",
        "scheme": "PMGSY",
        "budget_category": "Scheme Allocation",
        "state": "Central",
        "document_type": "Scheme Document"
    }
}
"""
