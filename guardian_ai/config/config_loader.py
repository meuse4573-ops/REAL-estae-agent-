"""
Config Loader — Dynamic configuration for multi-region support

File: guardian_ai/config/config_loader.py

Loads YAML configuration files per region, supports Florida (initial),
Texas, California, and other regions. Provides access to contract templates,
disclosure requirements, and timeline defaults.
"""

import os
import yaml
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

BASE_CONFIG_DIR = Path(__file__).parent.parent / "config"
SUPPORTED_REGIONS = ["florida", "texas", "california", "new_york", "arizona", "nevada", "colorado"]

_cache: Dict[str, Dict[str, Any]] = {}


def _get_config_path(region_code: str, filename: str) -> Path:
    region_dir = BASE_CONFIG_DIR / region_code
    return region_dir / filename


def validate_region_config(region: str) -> Dict[str, Any]:
    region_lower = region.lower()
    required_files = ["config.yaml", "contracts.yaml", "disclosures.yaml", "timelines.yaml"]

    region_dir = BASE_CONFIG_DIR / region_lower
    missing_files = []

    if not region_dir.exists():
        return {
            "valid": False,
            "error": f"Region directory does not exist: {region_dir}",
            "missing_files": required_files
        }

    for filename in required_files:
        config_path = region_dir / filename
        if not config_path.exists():
            missing_files.append(filename)

    if missing_files:
        return {
            "valid": False,
            "error": f"Missing required config files: {missing_files}",
            "missing_files": missing_files
        }

    return {
        "valid": True,
        "region": region_lower,
        "files_found": required_files
    }


def load_region_config(region_code: str, force_reload: bool = False) -> Dict[str, Any]:
    region_lower = region_code.lower()

    if region_lower in _cache and not force_reload:
        logger.debug(f"Returning cached config for region: {region_lower}")
        return _cache[region_lower]

    validation = validate_region_config(region_lower)
    if not validation["valid"]:
        logger.warning(f"Region {region_lower} validation failed: {validation['error']}")

        if region_lower == "florida":
            return _load_legacy_florida_config()
        else:
            raise FileNotFoundError(
                f"Configuration files not found for region: {region_lower}. "
                f"Required files: {validation.get('missing_files', [])}"
            )

    config = {}

    for filename in ["config.yaml", "contracts.yaml", "disclosures.yaml", "timelines.yaml"]:
        config_path = _get_config_path(region_lower, filename)
        try:
            with open(config_path, 'r') as f:
                data = yaml.safe_load(f)
                config_key = filename.replace('.yaml', '')
                config[config_key] = data
        except Exception as e:
            logger.error(f"Error loading {filename} for region {region_lower}: {e}")
            config[config_key] = {}

    _cache[region_lower] = config
    logger.info(f"Loaded configuration for region: {region_lower}")

    return config


def _load_legacy_florida_config() -> Dict[str, Any]:
    logger.info("Loading legacy Florida config from root config directory")

    config_path = BASE_CONFIG_DIR / "florida_config.yaml"
    if not config_path.exists():
        return {
            "error": "Legacy Florida config not found",
            "config": {}
        }

    try:
        with open(config_path, 'r') as f:
            florida_config = yaml.safe_load(f)

        return {
            "config": florida_config,
            "contracts": florida_config.get("florida", {}),
            "disclosures": florida_config.get("florida", {}).get("disclosures", []),
            "timelines": florida_config.get("florida", {}).get("timelines", {})
        }
    except Exception as e:
        logger.error(f"Error loading legacy Florida config: {e}")
        return {"error": str(e), "config": {}}


def get_current_region(tenant_id: str) -> str:
    try:
        from guardian_ai.core.tenant_guard import get_tenant_settings
        settings = get_tenant_settings(tenant_id)

        region = settings.get("region", "florida")
        logger.debug(f"Region for tenant {tenant_id}: {region}")
        return region

    except Exception as e:
        logger.warning(f"Could not get region from tenant settings, defaulting to florida: {e}")
        return "florida"


def get_contract_template(region: str, template_name: str) -> Optional[Dict[str, Any]]:
    config = load_region_config(region)

    contracts = config.get("contracts", {})

    contract_types = contracts.get("contract_types", []) if isinstance(contracts, dict) else []

    for contract in contract_types:
        if contract.get("name") == template_name or contract.get("abbrev") == template_name:
            logger.info(f"Found contract template: {template_name} for region: {region}")
            return contract

    logger.warning(f"Contract template '{template_name}' not found in region {region}")
    return None


def get_disclosure_requirements(region: str) -> List[Dict[str, Any]]:
    config = load_region_config(region)

    disclosures = config.get("disclosures", {})

    if isinstance(disclosures, dict):
        disclosure_list = disclosures.get("disclosures", [])
    else:
        disclosure_list = disclosures if isinstance(disclosures, list) else []

    logger.info(f"Retrieved {len(disclosure_list)} disclosure requirements for region: {region}")

    return disclosure_list


def get_timeline_defaults(region: str) -> Dict[str, Any]:
    config = load_region_config(region)

    timelines = config.get("timelines", {})

    if isinstance(timelines, dict):
        timeline_defaults = timelines.get("timelines", {}) if "timelines" in timelines else timelines
    else:
        timeline_defaults = {
            "inspection_contingency": 15,
            "financing_contingency": 30,
            "closing_financed": 45,
            "closing_cash": 30
        }

    logger.info(f"Retrieved timeline defaults for region: {region}")

    return timeline_defaults


def get_region_config(region: str) -> Dict[str, Any]:
    return load_region_config(region)


def clear_cache(region: Optional[str] = None) -> None:
    global _cache
    if region:
        region_lower = region.lower()
        if region_lower in _cache:
            del _cache[region_lower]
            logger.info(f"Cleared cache for region: {region_lower}")
    else:
        _cache.clear()
        logger.info("Cleared all cached configurations")


def list_supported_regions() -> List[str]:
    regions = []
    if BASE_CONFIG_DIR.exists():
        for item in BASE_CONFIG_DIR.iterdir():
            if item.is_dir() and (item / "config.yaml").exists():
                regions.append(item.name)

    for legacy in SUPPORTED_REGIONS:
        if legacy not in regions:
            legacy_path = BASE_CONFIG_DIR / f"{legacy}_config.yaml"
            if legacy_path.exists():
                regions.append(legacy)

    return sorted(set(regions))


def get_florida_config() -> Dict[str, Any]:
    return load_region_config("florida")


def get_county_requirements(region: str, county: str) -> List[str]:
    config = load_region_config(region)

    if isinstance(config.get("config"), dict):
        counties = config["config"].get("florida", {}).get("counties", {}).get("high_volume", [])
    else:
        counties = config.get("counties", {}).get("high_volume", [])

    for county_config in counties:
        if county_config.get("name", "").lower() == county.lower():
            return county_config.get("requirements", [])

    return []


def get_frec_regulations(region: str) -> Dict[str, Any]:
    config = load_region_config(region)

    if isinstance(config.get("config"), dict):
        regulations = config["config"].get("florida", {}).get("regulations", {})
    else:
        regulations = config.get("regulations", {})

    return regulations


def get_wind_mitigation_requirements(region: str) -> Dict[str, Any]:
    config = load_region_config(region)

    if isinstance(config.get("config"), dict):
        wind_mitigation = config["config"].get("florida", {}).get("wind_mitigation", {})
    else:
        wind_mitigation = config.get("wind_mitigation", {})

    return wind_mitigation


def get_disaster_disclosure_triggers(region: str) -> Dict[str, Any]:
    config = load_region_config(region)

    if isinstance(config.get("config"), dict):
        triggers = config["config"].get("florida", {}).get("disaster_disclosure", {})
    else:
        triggers = config.get("disaster_disclosure", {})

    return triggers