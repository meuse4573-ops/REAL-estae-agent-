"""
Memory Manager — Abstract data access layer using SQLAlchemy ORM

File: guardian_ai/memory/memory_manager.py

Provides methods for storing and retrieving deal context, contact baselines,
agent preferences, RLHF training signals, documents, and communications.

All methods enforce tenant_id isolation via tenant_guard.
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import json
import logging

from sqlalchemy import create_engine, Column, String, Text, Boolean, Integer, DECIMAL, TIMESTAMP, Date, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session

from guardian_ai.core.tenant_guard import (
    get_current_tenant_id,
    require_tenant,
    validate_tenant_id,
    get_tenant_settings
)

logger = logging.getLogger(__name__)

Base = declarative_base()

engine = create_engine('postgresql://localhost/guardian_ai', echo=False)
Session = scoped_session(sessionmaker(bind=engine))


class Tenant(Base):
    __tablename__ = 'tenants'

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(255), nullable=False)
    settings = Column(JSON, default={})
    created_at = Column(TIMESTAMP, default=datetime.utcnow)


class Deal(Base):
    __tablename__ = 'deals'

    id = Column(UUID(as_uuid=True), primary_key=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id'), nullable=False)
    address = Column(Text, nullable=False)
    buyer_name = Column(Text)
    seller_name = Column(Text)
    status = Column(String(50))
    deal_safety_score = Column(DECIMAL(5, 2))
    contract_date = Column(Date)
    closing_date = Column(Date)
    listing_number = Column(String(50))
    mls_number = Column(String(50))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    documents = relationship('Document', back_populates='deal', cascade='all, delete-orphan')
    communications = relationship('Communication', back_populates='deal', cascade='all, delete-orphan')
    tasks = relationship('Task', back_populates='deal', cascade='all, delete-orphan')
    risks = relationship('DealRisk', back_populates='deal', cascade='all, delete-orphan')
    audit_logs = relationship('AuditLog', back_populates='deal')


class Document(Base):
    __tablename__ = 'documents'

    id = Column(UUID(as_uuid=True), primary_key=True)
    deal_id = Column(UUID(as_uuid=True), ForeignKey('deals.id'), nullable=False)
    type = Column(String(50))
    name = Column(String(255))
    file_path = Column(Text)
    extracted_data = Column(JSON, default={})
    ocr_confidence = Column(DECIMAL(5, 2))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    deal = relationship('Deal', back_populates='documents')


class Communication(Base):
    __tablename__ = 'communications'

    id = Column(UUID(as_uuid=True), primary_key=True)
    deal_id = Column(UUID(as_uuid=True), ForeignKey('deals.id'), nullable=False)
    channel = Column(String(20))
    sender = Column(String(255))
    recipient = Column(String(255))
    subject = Column(Text)
    content = Column(Text)
    sentiment_score = Column(DECIMAL(5, 2))
    urgency_flag = Column(Boolean, default=False)
    is_deal_related = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    deal = relationship('Deal', back_populates='communications')


class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(UUID(as_uuid=True), primary_key=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id'), nullable=False)
    name = Column(String(255))
    role = Column(String(50))
    email = Column(String(255))
    phone = Column(String(50))
    company = Column(String(255))
    avg_response_time_minutes = Column(Integer)
    sentiment_baseline = Column(DECIMAL(5, 2))
    communication_style = Column(JSON, default={})
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    baselines = relationship('CommunicationBaseline', back_populates='contact', cascade='all, delete-orphan')


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(UUID(as_uuid=True), primary_key=True)
    deal_id = Column(UUID(as_uuid=True), ForeignKey('deals.id'), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(Integer)
    deadline = Column(TIMESTAMP)
    status = Column(String(20))
    created_by_ai = Column(Boolean, default=True)
    completed_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    deal = relationship('Deal', back_populates='tasks')


class AuditLog(Base):
    __tablename__ = 'audit_logs'

    id = Column(UUID(as_uuid=True), primary_key=True)
    deal_id = Column(UUID(as_uuid=True), ForeignKey('deals.id'))
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id'), nullable=False)
    action_type = Column(String(50))
    ai_output = Column(Text)
    human_decision = Column(String(20))
    human_correction = Column(Text)
    full_context = Column(JSON, default={})
    timestamp = Column(TIMESTAMP, default=datetime.utcnow)

    deal = relationship('Deal', back_populates='audit_logs')


class AgentPreference(Base):
    __tablename__ = 'agent_preferences'

    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id'), primary_key=True)
    preference_key = Column(String(100), primary_key=True)
    preference_value = Column(Text)
    confidence_score = Column(DECIMAL(5, 2))
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)


class RLHFData(Base):
    __tablename__ = 'rlhf_data'

    id = Column(UUID(as_uuid=True), primary_key=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey('tenants.id'), nullable=False)
    input_context = Column(Text)
    ai_output = Column(Text)
    human_correction = Column(Text)
    correction_type = Column(String(50))
    timestamp = Column(TIMESTAMP, default=datetime.utcnow)


class CommunicationBaseline(Base):
    __tablename__ = 'communication_baselines'

    contact_id = Column(UUID(as_uuid=True), ForeignKey('contacts.id'), primary_key=True)
    role = Column(String(50))
    avg_response_minutes = Column(DECIMAL(10, 2))
    response_variance = Column(DECIMAL(10, 2))
    last_updated = Column(TIMESTAMP, default=datetime.utcnow)

    contact = relationship('Contact', back_populates='baselines')


class DealRisk(Base):
    __tablename__ = 'deal_risks'

    id = Column(UUID(as_uuid=True), primary_key=True)
    deal_id = Column(UUID(as_uuid=True), ForeignKey('deals.id'), nullable=False)
    risk_type = Column(String(50))
    severity = Column(Integer)
    description = Column(Text)
    detected_at = Column(TIMESTAMP, default=datetime.utcnow)
    resolved_at = Column(TIMESTAMP)
    resolution = Column(Text)

    deal = relationship('Deal', back_populates='risks')


def get_session():
    return Session()


def store_deal_context(deal_id: str, context: dict, tenant_id: Optional[str] = None) -> Dict[str, Any]:
    if not tenant_id:
        tenant_id = get_current_tenant_id()

    validate_tenant_id(tenant_id)

    session = get_session()
    try:
        deal = session.query(Deal).filter(
            Deal.id == deal_id,
            Deal.tenant_id == tenant_id
        ).first()

        if not deal:
            logger.warning(f"Deal {deal_id} not found for tenant {tenant_id}")
            return {"error": "Deal not found", "deal_id": deal_id}

        for key, value in context.items():
            if hasattr(deal, key):
                setattr(deal, key, value)

        session.commit()
        logger.info(f"Updated deal context for deal {deal_id}")

        return {
            "success": True,
            "deal_id": deal_id,
            "updated_fields": list(context.keys())
        }
    except Exception as e:
        session.rollback()
        logger.error(f"Error storing deal context: {e}")
        raise
    finally:
        session.close()


def get_deal_history(deal_id: str, tenant_id: Optional[str] = None) -> Dict[str, Any]:
    if not tenant_id:
        tenant_id = get_current_tenant_id()

    validate_tenant_id(tenant_id)

    session = get_session()
    try:
        deal = session.query(Deal).filter(
            Deal.id == deal_id,
            Deal.tenant_id == tenant_id
        ).first()

        if not deal:
            return {"error": "Deal not found", "deal_id": deal_id}

        documents = session.query(Document).filter(Document.deal_id == deal_id).all()
        communications = session.query(Communication).filter(Communication.deal_id == deal_id).order_by(Communication.created_at.desc()).all()
        tasks = session.query(Task).filter(Task.deal_id == deal_id).order_by(Task.deadline).all()
        audit_logs = session.query(AuditLog).filter(AuditLog.deal_id == deal_id).order_by(AuditLog.timestamp.desc()).limit(100).all()
        risks = session.query(DealRisk).filter(DealRisk.deal_id == deal_id).all()

        return {
            "deal_id": deal_id,
            "deal": {
                "address": deal.address,
                "status": deal.status,
                "buyer_name": deal.buyer_name,
                "seller_name": deal.seller_name,
                "contract_date": str(deal.contract_date) if deal.contract_date else None,
                "closing_date": str(deal.closing_date) if deal.closing_date else None,
                "deal_safety_score": float(deal.deal_safety_score) if deal.deal_safety_score else None
            },
            "documents": [
                {
                    "id": str(d.id),
                    "type": d.type,
                    "name": d.name,
                    "ocr_confidence": float(d.ocr_confidence) if d.ocr_confidence else None,
                    "created_at": str(d.created_at)
                }
                for d in documents
            ],
            "communications": [
                {
                    "id": str(c.id),
                    "channel": c.channel,
                    "sender": c.sender,
                    "subject": c.subject,
                    "sentiment_score": float(c.sentiment_score) if c.sentiment_score else None,
                    "urgency_flag": c.urgency_flag,
                    "created_at": str(c.created_at)
                }
                for c in communications
            ],
            "tasks": [
                {
                    "id": str(t.id),
                    "description": t.description,
                    "priority": t.priority,
                    "status": t.status,
                    "deadline": str(t.deadline) if t.deadline else None,
                    "completed_at": str(t.completed_at) if t.completed_at else None
                }
                for t in tasks
            ],
            "audit_logs": [
                {
                    "id": str(a.id),
                    "action_type": a.action_type,
                    "ai_output": a.ai_output,
                    "human_decision": a.human_decision,
                    "timestamp": str(a.timestamp)
                }
                for a in audit_logs
            ],
            "risks": [
                {
                    "id": str(r.id),
                    "risk_type": r.risk_type,
                    "severity": r.severity,
                    "description": r.description,
                    "detected_at": str(r.detected_at),
                    "resolved_at": str(r.resolved_at) if r.resolved_at else None,
                    "resolution": r.resolution
                }
                for r in risks
            ]
        }
    finally:
        session.close()


def store_contact_baseline(contact_id: str, metrics: dict, tenant_id: Optional[str] = None) -> Dict[str, Any]:
    if not tenant_id:
        tenant_id = get_current_tenant_id()

    validate_tenant_id(tenant_id)

    session = get_session()
    try:
        contact = session.query(Contact).filter(Contact.id == contact_id).first()

        if not contact:
            return {"error": "Contact not found", "contact_id": contact_id}

        if 'avg_response_time_minutes' in metrics:
            contact.avg_response_time_minutes = metrics['avg_response_time_minutes']

        if 'sentiment_baseline' in metrics:
            contact.sentiment_baseline = metrics['sentiment_baseline']

        if 'communication_style' in metrics:
            contact.communication_style = metrics['communication_style']

        baseline = session.query(CommunicationBaseline).filter(
            CommunicationBaseline.contact_id == contact_id
        ).first()

        if baseline:
            if 'avg_response_minutes' in metrics:
                baseline.avg_response_minutes = metrics['avg_response_minutes']
            if 'response_variance' in metrics:
                baseline.response_variance = metrics['response_variance']
            if 'role' in metrics:
                baseline.role = metrics['role']
            baseline.last_updated = datetime.utcnow()
        else:
            baseline = CommunicationBaseline(
                contact_id=contact_id,
                role=metrics.get('role'),
                avg_response_minutes=metrics.get('avg_response_minutes'),
                response_variance=metrics.get('response_variance'),
                last_updated=datetime.utcnow()
            )
            session.add(baseline)

        session.commit()
        logger.info(f"Updated contact baseline for contact {contact_id}")

        return {
            "success": True,
            "contact_id": contact_id,
            "updated_metrics": list(metrics.keys())
        }
    except Exception as e:
        session.rollback()
        logger.error(f"Error storing contact baseline: {e}")
        raise
    finally:
        session.close()


def get_agent_preferences(tenant_id: str) -> List[Dict[str, Any]]:
    validate_tenant_id(tenant_id)

    session = get_session()
    try:
        preferences = session.query(AgentPreference).filter(
            AgentPreference.tenant_id == tenant_id
        ).all()

        return [
            {
                "preference_key": p.preference_key,
                "preference_value": p.preference_value,
                "confidence_score": float(p.confidence_score) if p.confidence_score else None,
                "updated_at": str(p.updated_at)
            }
            for p in preferences
        ]
    finally:
        session.close()


def log_rlhf_signal(tenant_id: str, correction: dict) -> Dict[str, Any]:
    validate_tenant_id(tenant_id)

    session = get_session()
    try:
        rlhf_entry = RLHFData(
            tenant_id=tenant_id,
            input_context=correction.get('input_context'),
            ai_output=correction.get('ai_output'),
            human_correction=correction.get('human_correction'),
            correction_type=correction.get('correction_type'),
            timestamp=datetime.utcnow()
        )

        session.add(rlhf_entry)
        session.commit()

        logger.info(f"Logged RLHF signal for tenant {tenant_id}: {correction.get('correction_type')}")

        return {
            "success": True,
            "rlhf_id": str(rlhf_entry.id),
            "correction_type": correction.get('correction_type')
        }
    except Exception as e:
        session.rollback()
        logger.error(f"Error logging RLHF signal: {e}")
        raise
    finally:
        session.close()


def get_deal_documents(deal_id: str, tenant_id: Optional[str] = None) -> List[Dict[str, Any]]:
    if not tenant_id:
        tenant_id = get_current_tenant_id()

    validate_tenant_id(tenant_id)

    session = get_session()
    try:
        deal = session.query(Deal).filter(
            Deal.id == deal_id,
            Deal.tenant_id == tenant_id
        ).first()

        if not deal:
            return []

        documents = session.query(Document).filter(Document.deal_id == deal_id).all()

        return [
            {
                "id": str(d.id),
                "type": d.type,
                "name": d.name,
                "file_path": d.file_path,
                "extracted_data": d.extracted_data,
                "ocr_confidence": float(d.ocr_confidence) if d.ocr_confidence else None,
                "created_at": str(d.created_at)
            }
            for d in documents
        ]
    finally:
        session.close()


def get_deal_communications(deal_id: str, days_back: int = 30, tenant_id: Optional[str] = None) -> List[Dict[str, Any]]:
    if not tenant_id:
        tenant_id = get_current_tenant_id()

    validate_tenant_id(tenant_id)

    session = get_session()
    try:
        deal = session.query(Deal).filter(
            Deal.id == deal_id,
            Deal.tenant_id == tenant_id
        ).first()

        if not deal:
            return []

        cutoff_date = datetime.utcnow() - timedelta(days=days_back)

        communications = session.query(Communication).filter(
            Communication.deal_id == deal_id,
            Communication.created_at >= cutoff_date
        ).order_by(Communication.created_at.desc()).all()

        return [
            {
                "id": str(c.id),
                "channel": c.channel,
                "sender": c.sender,
                "recipient": c.recipient,
                "subject": c.subject,
                "content": c.content,
                "sentiment_score": float(c.sentiment_score) if c.sentiment_score else None,
                "urgency_flag": c.urgency_flag,
                "is_deal_related": c.is_deal_related,
                "created_at": str(c.created_at)
            }
            for c in communications
        ]
    finally:
        session.close()


def create_deal(tenant_id: str, address: str, **kwargs) -> Dict[str, Any]:
    validate_tenant_id(tenant_id)

    session = get_session()
    try:
        deal = Deal(
            tenant_id=tenant_id,
            address=address,
            buyer_name=kwargs.get('buyer_name'),
            seller_name=kwargs.get('seller_name'),
            status=kwargs.get('status', 'pending'),
            deal_safety_score=kwargs.get('deal_safety_score'),
            contract_date=kwargs.get('contract_date'),
            closing_date=kwargs.get('closing_date'),
            listing_number=kwargs.get('listing_number'),
            mls_number=kwargs.get('mls_number')
        )

        session.add(deal)
        session.commit()

        logger.info(f"Created new deal {deal.id} for tenant {tenant_id}")

        return {
            "success": True,
            "deal_id": str(deal.id),
            "address": deal.address
        }
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating deal: {e}")
        raise
    finally:
        session.close()


def get_all_deals(tenant_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
    validate_tenant_id(tenant_id)

    session = get_session()
    try:
        query = session.query(Deal).filter(Deal.tenant_id == tenant_id)

        if status:
            query = query.filter(Deal.status == status)

        deals = query.order_by(Deal.created_at.desc()).all()

        return [
            {
                "id": str(d.id),
                "address": d.address,
                "status": d.status,
                "deal_safety_score": float(d.deal_safety_score) if d.deal_safety_score else None,
                "contract_date": str(d.contract_date) if d.contract_date else None,
                "closing_date": str(d.closing_date) if d.closing_date else None,
                "created_at": str(d.created_at)
            }
            for d in deals
        ]
    finally:
        session.close()