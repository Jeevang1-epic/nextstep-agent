# NextStep Agent Evaluation Report

Total cases: 10
Passed cases: 10
Failed cases: 0
Total score: 80/80 (100.0%)

| Case | Status | Score | Reason |
| --- | --- | ---: | --- |
| school_notice_deadline | PASS | 8/8 | pass |
| invoice_payment_due | PASS | 8/8 | pass |
| utility_bill_interruption | PASS | 8/8 | pass |
| appointment_slip | PASS | 8/8 | pass |
| ngo_intake_support | PASS | 8/8 | pass |
| rental_maintenance_notice | PASS | 8/8 | pass |
| internship_application_deadline | PASS | 8/8 | pass |
| medical_appointment_reminder | PASS | 8/8 | pass |
| small_business_order_request | PASS | 8/8 | pass |
| scholarship_fee_circular | PASS | 8/8 | pass |

## Per-Case Notes

### school_notice_deadline
- Status: PASS
- Reason: pass
- Notes: `{"action_items": 1, "document_type": "school_notice", "mcp_tools": ["deadline_calculator", "policy_lookup", "safety_boundary_check", "task_store", "template_fetch"], "risk_level": "medium", "task_store_path": "data/tasks.jsonl"}`

### invoice_payment_due
- Status: PASS
- Reason: pass
- Notes: `{"action_items": 3, "document_type": "invoice", "mcp_tools": ["deadline_calculator", "policy_lookup", "safety_boundary_check", "task_store", "template_fetch"], "risk_level": "medium", "task_store_path": "data/tasks.jsonl"}`

### utility_bill_interruption
- Status: PASS
- Reason: pass
- Notes: `{"action_items": 3, "document_type": "utility_bill", "mcp_tools": ["deadline_calculator", "policy_lookup", "safety_boundary_check", "task_store", "template_fetch"], "risk_level": "high", "task_store_path": "data/tasks.jsonl"}`

### appointment_slip
- Status: PASS
- Reason: pass
- Notes: `{"action_items": 3, "document_type": "appointment_slip", "mcp_tools": ["deadline_calculator", "policy_lookup", "safety_boundary_check", "task_store", "template_fetch"], "risk_level": "medium", "task_store_path": "data/tasks.jsonl"}`

### ngo_intake_support
- Status: PASS
- Reason: pass
- Notes: `{"action_items": 2, "document_type": "ngo_intake", "mcp_tools": ["deadline_calculator", "policy_lookup", "safety_boundary_check", "task_store", "template_fetch"], "risk_level": "medium", "task_store_path": "data/tasks.jsonl"}`

### rental_maintenance_notice
- Status: PASS
- Reason: pass
- Notes: `{"action_items": 3, "document_type": "rental_maintenance_notice", "mcp_tools": ["deadline_calculator", "policy_lookup", "safety_boundary_check", "task_store", "template_fetch"], "risk_level": "medium", "task_store_path": "data/tasks.jsonl"}`

### internship_application_deadline
- Status: PASS
- Reason: pass
- Notes: `{"action_items": 3, "document_type": "internship_deadline", "mcp_tools": ["deadline_calculator", "policy_lookup", "safety_boundary_check", "task_store", "template_fetch"], "risk_level": "low", "task_store_path": "data/tasks.jsonl"}`

### medical_appointment_reminder
- Status: PASS
- Reason: pass
- Notes: `{"action_items": 2, "document_type": "medical_appointment", "mcp_tools": ["deadline_calculator", "policy_lookup", "safety_boundary_check", "task_store", "template_fetch"], "risk_level": "medium", "task_store_path": "data/tasks.jsonl"}`

### small_business_order_request
- Status: PASS
- Reason: pass
- Notes: `{"action_items": 3, "document_type": "small_business_order", "mcp_tools": ["deadline_calculator", "policy_lookup", "safety_boundary_check", "task_store", "template_fetch"], "risk_level": "medium", "task_store_path": "data/tasks.jsonl"}`

### scholarship_fee_circular
- Status: PASS
- Reason: pass
- Notes: `{"action_items": 3, "document_type": "scholarship_fee_circular", "mcp_tools": ["deadline_calculator", "policy_lookup", "safety_boundary_check", "task_store", "template_fetch"], "risk_level": "medium", "task_store_path": "data/tasks.jsonl"}`