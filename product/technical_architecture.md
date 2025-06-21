# Technical Architecture: Persona Experience & Brand Audit Tool

**Status: ✅ IMPLEMENTED - YAML-Driven, Persona-Aware Architecture**

## 1. Introduction

This document provides the technical architecture for the completed audit tool. The system is now fully implemented with 100% YAML-driven configuration and complete persona awareness, eliminating all hardcoded values.

## 2. System Design Philosophy

The architecture is based on **Separation of Concerns** and **Configuration-Driven Design** principles:

- **YAML Configuration**: All methodology, scoring criteria, and rules defined in `methodology.yaml`
- **Persona-Aware Processing**: Every analysis tailored to specific persona attributes
- **Template-Based Output**: Configurable prompts and report templates
- **Robust Path Resolution**: Works from any directory structure
- **Comprehensive Testing**: Full test suite with 5 test components

Data flows unidirectionally from collection → processing → reporting, with all business logic externalized to configuration files.

## 3. Current Architecture Overview

```mermaid
classDiagram
    direction LR

    class MainApp {
        +main()
        +run_audit()
    }

    class Scraper {
        +fetch_page(url: str) : PageData
        +url_to_filename(url: str) : str
        -_get_cache_path()
        -_save_to_cache()
        -_load_from_cache()
    }

    class AIInterface {
        +generate_experience_report() : str
        +generate_hygiene_scorecard() : str
        +get_subjective_score() : float
        +generate_strategic_summary() : str
        -_load_prompt_template()
        -_get_system_message()
        -_format_persona_attributes()
        -_find_project_root()
    }

    class MethodologyParser {
        +parse() : Methodology
        +get_scoring_descriptors() : dict
        +get_gating_rules() : dict
        +get_brand_messaging() : dict
        -_parse_onsite_tiers()
        -_parse_offsite_channels()
        -_parse_tier_criteria()
    }

    class PersonaParser {
        +extract_attributes(file_path: str) : PersonaAttributes
        +extract_attributes_from_content(content: str) : PersonaAttributes
        -_extract_name()
        -_extract_role()
        -_extract_priorities()
        -_extract_pain_points()
    }

    class ReportGenerator {
        +save_hygiene_scorecard()
        +save_experience_report()
        +extract_score_from_report()
    }

    class StrategicSummaryGenerator {
        +generate_full_report() : tuple
        -_get_criterion_weight_from_yaml()
        -_get_brand_criteria_from_yaml()
        -_get_gating_rule_thresholds_from_yaml()
        -_get_classification_triggers_from_yaml()
        -_get_scoring_config_from_yaml()
    }

    class PageData {
        <<Dataclass>>
        +url: str
        +raw_text: str
        +is_404: bool
        +objective_findings: dict
    }

    class PersonaAttributes {
        <<Dataclass>>
        +name: str
        +role: str
        +industry: str
        +geographic_scope: str
        +key_priorities: List[str]
        +business_context: str
        +communication_style: str
        +pain_points: List[str]
        +decision_factors: List[str]
    }

    class Methodology {
        <<Dataclass>>
        +tiers: List[Tier]
        +offsite_channels: List[OffsiteChannel]
        +metadata: dict
        +scoring_config: dict
        +gating_rules: dict
        +brand_messaging: dict
    }

    MainApp --> Scraper
    MainApp --> MethodologyParser
    MainApp --> PersonaParser
    MainApp --> AIInterface
    MainApp --> ReportGenerator
    MainApp --> StrategicSummaryGenerator

    AIInterface --> PersonaParser
    StrategicSummaryGenerator --> MethodologyParser

    Scraper ..> PageData : creates
    MethodologyParser ..> Methodology : creates
    PersonaParser ..> PersonaAttributes : creates
```

## 4. Component Deep Dive

### 4.1. Data Models (`models.py`)

Enhanced dataclasses for type-safe data transfer:

- **`PageData`**: Scraped page data with objective findings
- **`PersonaAttributes`**: Structured persona information extracted from markdown files
- **`Methodology`**: Complete scoring framework loaded from YAML
- **`Tier`/`OffsiteChannel`**: Scoring contexts with brand/performance percentages
- **`Criterion`**: Individual scoring rules with weights, categories, and requirements
- **`Scorecard`**: Structured audit results with evidence and penalties

### 4.2. YAML Configuration System (`methodology.yaml`)

**542-line configuration file** containing:

- **Scoring Framework**: All criteria, weights, and descriptors
- **Classification Rules**: Page tier assignment triggers
- **Gating Rules**: Non-negotiable quality thresholds
- **Brand Messaging**: Corporate hierarchy and approved value propositions
- **Quality Penalties**: Automatic deductions for common issues
- **Evidence Requirements**: Mandatory documentation standards

### 4.3. Persona-Aware Processing (`PersonaParser`)

**Structured attribute extraction** from persona markdown files:

- Parses role, industry, geographic scope, priorities, pain points
- Formats attributes for template substitution
- Supports both file-based and content-based parsing
- Handles complex persona documents (11-16KB files)

### 4.4. Configurable AI Interface (`AIInterface`)

**Template-driven AI interactions**:

- Loads prompt templates from `audit_inputs/prompts/`
- Dynamic persona attribute substitution
- Robust path resolution for any working directory
- Separate system messages and main prompts
- Comprehensive error handling and retries

### 4.5. YAML-Driven Generators (`StrategicSummaryGenerator`)

**100% configuration-driven scoring**:

- Retrieves all weights from YAML methodology
- Classifies pages using YAML triggers
- Applies gating rules from configuration
- Uses YAML scoring descriptors for health status
- No hardcoded values anywhere in the pipeline

### 4.6. Test Infrastructure (`audit_tool/tests/`)

**Comprehensive test suite**:

- **YAML Configuration Test**: Verifies methodology loading
- **Persona Parsing Test**: Tests attribute extraction
- **Web Scraper Test**: Validates page fetching and caching
- **AI Interface Test**: Checks template loading and formatting
- **Full Pipeline Test**: End-to-end audit execution

## 5. Current Data Flow

```mermaid
graph TD
    A[main.py starts] --> B[Parse Arguments]
    B --> C[Load YAML Methodology]
    C --> D[Initialize Components]

    subgraph "URL Processing Loop"
        E[For each URL] --> F[Scrape Page with Caching]
        F --> G[Parse Persona Attributes]
        G --> H[Load Prompt Templates]
        H --> I[Generate Experience Report]
        I --> J[Generate Hygiene Scorecard]
        J --> K[Save Reports to Disk]
    end

    D --> E

    subgraph "Strategic Summary Generation"
        L[Load All Reports] --> M[Apply YAML Methodology]
        M --> N[Calculate Weighted Scores]
        N --> O[Generate Strategic Summary]
        O --> P[Save Summary and Data]
    end

    K --> L
    P --> Q[Complete - All Reports Generated]
```

## 6. Key Architectural Improvements

### 6.1. Configuration Externalization

- **Before**: 50+ hardcoded references throughout codebase
- **After**: 0% hardcoded values - everything in YAML

### 6.2. Persona Awareness

- **Before**: Fixed C-suite/Benelux assumptions
- **After**: Dynamic persona-driven analysis for any role/industry

### 6.3. Template System

- **Before**: String concatenation and hardcoded prompts
- **After**: Configurable templates with variable substitution

### 6.4. Robust Architecture

- **Before**: Fragile path dependencies
- **After**: Works from any directory with automatic project root detection

### 6.5. Comprehensive Testing

- **Before**: Manual testing only
- **After**: Automated test suite covering all components

## 7. Production Readiness

The audit tool is now **production ready** with:

- ✅ **Zero hardcoded values** - fully configurable
- ✅ **Complete persona awareness** - role-specific analysis
- ✅ **Robust error handling** - comprehensive exception management
- ✅ **Automated testing** - 5-component test suite
- ✅ **Professional UI** - Streamlit dashboard for non-technical users
- ✅ **Caching system** - Efficient re-processing of content
- ✅ **Modular design** - Easy to extend and maintain

**Ready for deployment and further enhancement.**
