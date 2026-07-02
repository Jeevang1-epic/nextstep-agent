# Invoice JSON

```json
{
  "facts": {
    "document_type": "invoice",
    "source_name": "[REDACTED_IDENTIFIER]",
    "sender": "Northside Office Supplies",
    "recipient": "To: Bright Leaf Studio",
    "dates": [
      "July 1, 2026",
      "July 12, 2026"
    ],
    "deadlines": [
      "Payment due by July 12, 2026."
    ],
    "amounts": [
      "$342.50"
    ],
    "identifiers": [
      "[REDACTED_IDENTIFIER]"
    ],
    "required_actions": [
      "Payment due by July 12, 2026.",
      "Amount due: $342.50",
      "Please verify the delivery list and pay by bank transfer before the due date.",
      "For questions, email [REDACTED_EMAIL]."
    ],
    "contact_methods": [
      "[REDACTED_EMAIL]"
    ],
    "sensitive_fields": [
      "EMAIL",
      "IDENTIFIER"
    ]
  },
  "risk": {
    "level": "medium",
    "flags": [
      "payment_or_amount_detected"
    ],
    "explanation": "Risk is based on deadline timing, consequences, document type, and payment signals.",
    "requires_human_review": false
  },
  "plan": {
    "summary": "Invoice requires 4 next step(s).",
    "action_items": [
      {
        "id": "A1",
        "title": "Payment due by July 12, 2026",
        "details": "Payment due by July 12, 2026.",
        "due_date": "2026-07-12",
        "priority": 3,
        "status": "open",
        "owner": "user",
        "source_evidence": "Payment due by July 12, 2026."
      },
      {
        "id": "A2",
        "title": "Amount due: $342.50",
        "details": "Amount due: $342.50",
        "due_date": "2026-07-12",
        "priority": 3,
        "status": "open",
        "owner": "user",
        "source_evidence": "Amount due: $342.50"
      },
      {
        "id": "A3",
        "title": "verify the delivery list and pay by bank transfer before the due date",
        "details": "Please verify the delivery list and pay by bank transfer before the due date.",
        "due_date": "2026-07-12",
        "priority": 3,
        "status": "open",
        "owner": "user",
        "source_evidence": "Please verify the delivery list and pay by bank transfer before the due date."
      },
      {
        "id": "A4",
        "title": "For questions, email [REDACTED_EMAIL]",
        "details": "For questions, email [REDACTED_EMAIL].",
        "due_date": "2026-07-12",
        "priority": 3,
        "status": "open",
        "owner": "user",
        "source_evidence": "For questions, email [REDACTED_EMAIL]."
      }
    ],
    "resources": [
      "Invoice validation"
    ],
    "risk_assessment": {
      "level": "medium",
      "flags": [
        "payment_or_amount_detected"
      ],
      "explanation": "Risk is based on deadline timing, consequences, document type, and payment signals.",
      "requires_human_review": false
    }
  },
  "draft": {
    "intent": "invoice_payment_check",
    "subject": "Invoice review and payment checklist",
    "body": "Hello Northside Office Supplies,\n\nI am reviewing the invoice and will verify the amount, due date, and payment instructions before taking action. Current next steps:\n- Payment due by July 12, 2026\n- Amount due: $342.50\n- verify the delivery list and pay by bank transfer before the due date\n- For questions, email [REDACTED_EMAIL]\n\nIf anything is missing or incorrect, please send clarification before 2026-07-12.\n\nThank you.",
    "checklist": [
      "Payment due by July 12, 2026 by 2026-07-12",
      "Amount due: $342.50 by 2026-07-12",
      "verify the delivery list and pay by bank transfer before the due date by 2026-07-12",
      "For questions, email [REDACTED_EMAIL] by 2026-07-12"
    ],
    "assumptions": [
      "The draft is based only on the provided document text.",
      "No payment, submission, or appointment change is performed by this tool."
    ],
    "redacted": true
  },
  "verification": {
    "passed": true,
    "issues": [],
    "unsupported_claims": [],
    "missing_required_actions": [],
    "source_alignment_score": 1.0
  },
  "redacted_output": "NextStep summary\nDocument type: invoice\nRisk: medium\nVerification passed: True\n\nPrioritized actions:\n- P3: Payment due by July 12, 2026 due 2026-07-12\n- P3: Amount due: $342.50 due 2026-07-12\n- P3: verify the delivery list and pay by bank transfer before the due date due 2026-07-12\n- P3: For questions, email [REDACTED_EMAIL] due 2026-07-12\n\nSaved tasks: 4\nTask store: data/tasks.jsonl\n\nDraft:\nHello Northside Office Supplies,\n\nI am reviewing the invoice and will verify the amount, due date, and payment instructions before taking action. Current next steps:\n- Payment due by July 12, 2026\n- Amount due: $342.50\n- verify the delivery list and pay by bank transfer before the due date\n- For questions, email [REDACTED_EMAIL]\n\nIf anything is missing or incorrect, please send clarification before 2026-07-12.\n\nThank you.",
  "mcp_trace": [
    "deadline_calculator:2026-07-12",
    "policy_lookup:billing",
    "template_fetch:invoice_payment_check",
    "task_store:4",
    "safety_boundary_check:allowed"
  ],
  "metadata": {
    "current_date": "2026-07-02",
    "session_id": "run-60012b7e2a73",
    "extraction": {
      "mode": "heuristic",
      "used": false,
      "fallback_reason": null
    },
    "trace": [
      {
        "stage": "Intake Agent",
        "detail": "Normalized document text and confirmed non-empty input."
      },
      {
        "stage": "Extraction Agent",
        "detail": "Extracted facts using heuristic mode."
      },
      {
        "stage": "Risk & Priority Agent",
        "detail": "Assigned medium risk with flags: payment_or_amount_detected."
      },
      {
        "stage": "Resource Lookup Agent",
        "detail": "Called MCP policy and template tools for grounded local context."
      },
      {
        "stage": "Action Planner Agent",
        "detail": "Created 4 prioritized action item(s)."
      },
      {
        "stage": "Drafting Agent",
        "detail": "Drafted a invoice_payment_check response and checklist."
      },
      {
        "stage": "Verification Agent",
        "detail": "Verification passed with score 1.0."
      },
      {
        "stage": "Redaction Agent",
        "detail": "Sanitized sensitive fields before final presentation."
      }
    ],
    "mcp_calls": [
      {
        "tool": "deadline_calculator",
        "why": "Normalize deadline text and compute urgency against the current date.",
        "result": {
          "input": "Payment due by July 12, 2026.",
          "source_text": "Payment due by July 12, 2026.",
          "current_date": "2026-07-02",
          "due_date": "2026-07-12",
          "days_remaining": 10,
          "status": "upcoming",
          "confidence": "medium",
          "notes": []
        }
      },
      {
        "tool": "policy_lookup",
        "why": "Find local guidance relevant to the document category and extracted actions.",
        "result": {
          "matches": [
            "Invoice validation"
          ]
        }
      },
      {
        "tool": "template_fetch",
        "why": "Fetch a safe response template for the detected user intent.",
        "result": {
          "intent": "invoice_payment_check",
          "subject": "Invoice review and payment checklist"
        }
      },
      {
        "tool": "task_store",
        "why": "Store the planned actions in the local task sink for demo continuity.",
        "result": {
          "session_id": "run-60012b7e2a73",
          "stored_count": 4,
          "total_count": 4,
          "task_store_path": "data/tasks.jsonl",
          "tasks": [
            {
              "session_id": "run-60012b7e2a73",
              "stored_at": "2026-07-02T08:16:25.755334+00:00",
              "sequence": 1,
              "id": "A1",
              "title": "Payment due by July 12, 2026",
              "due_date": "2026-07-12",
              "priority": 3,
              "status": "open",
              "owner": "user",
              "source_evidence": "Payment due by July 12, 2026."
            },
            {
              "session_id": "run-60012b7e2a73",
              "stored_at": "2026-07-02T08:16:25.755334+00:00",
              "sequence": 2,
              "id": "A2",
              "title": "Amount due: $342.50",
              "due_date": "2026-07-12",
              "priority": 3,
              "status": "open",
              "owner": "user",
              "source_evidence": "Amount due: $342.50"
            },
            {
              "session_id": "run-60012b7e2a73",
              "stored_at": "2026-07-02T08:16:25.755334+00:00",
              "sequence": 3,
              "id": "A3",
              "title": "verify the delivery list and pay by bank transfer before the due date",
              "due_date": "2026-07-12",
              "priority": 3,
              "status": "open",
              "owner": "user",
              "source_evidence": "Please verify the delivery list and pay by bank transfer before the due date."
            },
            {
              "session_id": "run-60012b7e2a73",
              "stored_at": "2026-07-02T08:16:25.755334+00:00",
              "sequence": 4,
              "id": "A4",
              "title": "For questions, email [REDACTED_EMAIL]",
              "due_date": "2026-07-12",
              "priority": 3,
              "status": "open",
              "owner": "user",
              "source_evidence": "For questions, email [REDACTED_EMAIL]."
            }
          ]
        }
      },
      {
        "tool": "safety_boundary_check",
        "why": "Check the draft for unsafe claims or unredacted sensitive information.",
        "result": {
          "allowed": true,
          "warnings": [],
          "sensitive_findings": []
        }
      }
    ],
    "saved_tasks": {
      "session_id": "run-60012b7e2a73",
      "stored_count": 4,
      "total_count": 4,
      "task_store_path": "data/tasks.jsonl",
      "tasks": [
        {
          "session_id": "run-60012b7e2a73",
          "stored_at": "2026-07-02T08:16:25.755334+00:00",
          "sequence": 1,
          "id": "A1",
          "title": "Payment due by July 12, 2026",
          "due_date": "2026-07-12",
          "priority": 3,
          "status": "open",
          "owner": "user",
          "source_evidence": "Payment due by July 12, 2026."
        },
        {
          "session_id": "run-60012b7e2a73",
          "stored_at": "2026-07-02T08:16:25.755334+00:00",
          "sequence": 2,
          "id": "A2",
          "title": "Amount due: $342.50",
          "due_date": "2026-07-12",
          "priority": 3,
          "status": "open",
          "owner": "user",
          "source_evidence": "Amount due: $342.50"
        },
        {
          "session_id": "run-60012b7e2a73",
          "stored_at": "2026-07-02T08:16:25.755334+00:00",
          "sequence": 3,
          "id": "A3",
          "title": "verify the delivery list and pay by bank transfer before the due date",
          "due_date": "2026-07-12",
          "priority": 3,
          "status": "open",
          "owner": "user",
          "source_evidence": "Please verify the delivery list and pay by bank transfer before the due date."
        },
        {
          "session_id": "run-60012b7e2a73",
          "stored_at": "2026-07-02T08:16:25.755334+00:00",
          "sequence": 4,
          "id": "A4",
          "title": "For questions, email [REDACTED_EMAIL]",
          "due_date": "2026-07-12",
          "priority": 3,
          "status": "open",
          "owner": "user",
          "source_evidence": "For questions, email [REDACTED_EMAIL]."
        }
      ]
    },
    "agent_count": 8
  }
}
```
