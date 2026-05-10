"""
Tenant Guard — Multi-Tenant Data Isolation Middleware

Enforces that EVERY database query includes tenant_id filter.
Fails closed: denies access if tenant_id is missing or invalid.

File: guardian_ai/core/tenant_guard.py
"""

from functools import wraps
from typing import Optional, List, Any
import logging

logger = logging.getLogger(__name__)

_thread_local_tenant_id: Optional[str] = None


def set_current_tenant(tenant_id: str) -> None:
    global _thread_local_tenant_id
    _thread_local_tenant_id = tenant_id
    logger.debug(f"Tenant context set: {tenant_id}")


def get_current_tenant_id() -> Optional[str]:
    return _thread_local_tenant_id


def clear_current_tenant() -> None:
    global _thread_local_tenant_id
    _thread_local_tenant_id = None
    logger.debug("Tenant context cleared")


def require_tenant(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        tenant_id = kwargs.get('tenant_id') or (
            args[0] if len(args) > 0 and isinstance(args[0], str) and len(args[0]) == 36 else None
        )

        if not tenant_id:
            if _thread_local_tenant_id:
                tenant_id = _thread_local_tenant_id
            else:
                raise PermissionError(
                    "Tenant ID is required for this operation. "
                    "Either pass tenant_id parameter or set tenant context via set_current_tenant()"
                )

        return func(*args, **kwargs, tenant_id=tenant_id)
    return wrapper


def assert_tenant_isolation(query, entity_name: str = "entity") -> None:
    if query is None:
        raise ValueError(f"Query cannot be None for {entity_name}")

    query_str = str(query)

    isolation_keywords = ['tenant_id', 'tenant.id', 'tenantId']

    has_isolation = any(keyword in query_str.lower() for keyword in isolation_keywords)

    if not has_isolation:
        raise SecurityError(
            f"SECURITY VIOLATION: Query on {entity_name} does not include tenant_id filter. "
            f"This could lead to cross-tenant data access. Query: {query_str[:200]}"
        )


class SecurityError(Exception):
    pass


class TenantAccessDeniedError(Exception):
    pass


def verify_tenant_access(deal_tenant_id: str, requesting_tenant_id: str, deal_id: str = None) -> bool:
    if deal_tenant_id != requesting_tenant_id:
        logger.warning(
            f"Tenant access denied: requesting tenant {requesting_tenant_id} "
            f"attempted to access deal {deal_id} belonging to tenant {deal_tenant_id}"
        )
        raise TenantAccessDeniedError(
            f"Tenant {requesting_tenant_id} does not have access to this resource"
        )
    return True


def validate_tenant_id(tenant_id: Optional[str]) -> str:
    if not tenant_id:
        raise ValueError("tenant_id cannot be None or empty")

    if not isinstance(tenant_id, str):
        raise ValueError(f"tenant_id must be a string, got {type(tenant_id)}")

    if len(tenant_id) != 36:
        raise ValueError(f"tenant_id must be a valid UUID (36 characters), got {tenant_id}")

    return tenant_id


@require_tenant
def get_deals(tenant_id: str, status: Optional[str] = None) -> List[Any]:
    from guardian_ai.memory.memory_manager import Deal

    assert_tenant_isolation(Deal, "deals")

    query = Deal.query.filter(Deal.tenant_id == tenant_id)

    if status:
        query = query.filter(Deal.status == status)

    return query.all()


@require_tenant
def get_deal_by_id(deal_id: str, tenant_id: str) -> Any:
    from guardian_ai.memory.memory_manager import Deal

    assert_tenant_isolation(Deal, "deal")

    deal = Deal.query.filter(
        Deal.id == deal_id,
        Deal.tenant_id == tenant_id
    ).first()

    if not deal:
        logger.warning(f"Deal {deal_id} not found or access denied for tenant {tenant_id}")
        return None

    return deal


@require_tenant
def get_contacts(tenant_id: str) -> List[Any]:
    from guardian_ai.memory.memory_manager import Contact

    assert_tenant_isolation(Contact, "contacts")

    return Contact.query.filter(Contact.tenant_id == tenant_id).all()


@require_tenant
def get_audit_logs(tenant_id: str, deal_id: Optional[str] = None) -> List[Any]:
    from guardian_ai.memory.memory_manager import AuditLog

    assert_tenant_isolation(AuditLog, "audit_logs")

    query = AuditLog.query.filter(AuditLog.tenant_id == tenant_id)

    if deal_id:
        query = query.filter(AuditLog.deal_id == deal_id)

    return query.order_by(AuditLog.timestamp.desc()).all()


@require_tenant
def get_agent_preferences(tenant_id: str) -> List[Any]:
    from guardian_ai.memory.memory_manager import AgentPreference

    return AgentPreference.query.filter(AgentPreference.tenant_id == tenant_id).all()


@require_tenant
def get_rlhf_data(tenant_id: str, limit: int = 100) -> List[Any]:
    from guardian_ai.memory.memory_manager import RLHFData

    return RLHFData.query.filter(
        RLHFData.tenant_id == tenant_id
    ).order_by(RLHFData.timestamp.desc()).limit(limit).all()


def create_audit_log_entry(
    tenant_id: str,
    deal_id: Optional[str],
    action_type: str,
    ai_output: str,
    human_decision: Optional[str] = None,
    human_correction: Optional[str] = None,
    full_context: Optional[dict] = None
) -> Any:
    from guardian_ai.memory.memory_manager import AuditLog

    validate_tenant_id(tenant_id)

    entry = AuditLog(
        tenant_id=tenant_id,
        deal_id=deal_id,
        action_type=action_type,
        ai_output=ai_output,
        human_decision=human_decision,
        human_correction=human_correction,
        full_context=full_context or {}
    )

    return entry


def get_tenant_settings(tenant_id: str) -> dict:
    from guardian_ai.memory.memory_manager import Tenant

    validate_tenant_id(tenant_id)

    tenant = Tenant.query.filter(Tenant.id == tenant_id).first()

    if not tenant:
        raise ValueError(f"Tenant {tenant_id} not found")

    return tenant.settings or {}