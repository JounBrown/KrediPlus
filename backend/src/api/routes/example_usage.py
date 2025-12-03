"""
Example usage of Loan Application endpoints

All endpoints use snake_case as requested.
Base URL: http://localhost:8000/api/v1/loan_applications
"""

# Example requests for testing the API

EXAMPLE_REQUESTS = {
    "create_application": {
        "method": "POST",
        "url": "/api/v1/loan_applications/",
        "body": {
            "name": "Juan Pérez García",
            "cedula": "12345678901",
            "convenio": "Empleados Públicos",
            "telefono": "3001234567",
            "fecha_nacimiento": "1985-03-15",
            "monto_solicitado": 5000000.0,
            "plazo": 24
        }
    },
    
    "get_application": {
        "method": "GET",
        "url": "/api/v1/loan_applications/1",
        "description": "Get application with ID 1"
    },
    
    "list_all_applications": {
        "method": "GET",
        "url": "/api/v1/loan_applications/?skip=0&limit=20",
        "description": "List first 20 applications"
    },
    
    "list_applications_by_status": {
        "method": "GET",
        "url": "/api/v1/loan_applications/?status_filter=nueva&skip=0&limit=10",
        "description": "List first 10 'nueva' applications"
    },
    
    "get_applications_by_cedula": {
        "method": "GET",
        "url": "/api/v1/loan_applications/by_cedula/12345678901?skip=0&limit=10",
        "description": "Get applications for specific cedula"
    },
    
    "get_client_summary": {
        "method": "GET",
        "url": "/api/v1/loan_applications/by_cedula/12345678901/summary",
        "description": "Get summary of client's applications"
    },
    
    "get_pending_applications": {
        "method": "GET",
        "url": "/api/v1/loan_applications/by_cedula/12345678901/pending",
        "description": "Get only pending applications for client"
    },
    
    "update_status": {
        "method": "PUT",
        "url": "/api/v1/loan_applications/1/status",
        "body": {
            "application_id": 1,
            "new_status": "en_proceso",
            "notes": "Revisión inicial completada"
        }
    },
    
    "approve_application": {
        "method": "PUT",
        "url": "/api/v1/loan_applications/1/approve",
        "description": "Approve application with ID 1"
    },
    
    "reject_application": {
        "method": "PUT",
        "url": "/api/v1/loan_applications/1/reject?notes=Ingresos insuficientes",
        "description": "Reject application with notes"
    },
    
    "cancel_application": {
        "method": "PUT",
        "url": "/api/v1/loan_applications/1/cancel?notes=Solicitado por el cliente",
        "description": "Cancel application with notes"
    },
    
    "search_by_name": {
        "method": "GET",
        "url": "/api/v1/loan_applications/search/by_name?name=Juan&skip=0&limit=10",
        "description": "Search applications by name"
    },
    
    "get_statistics": {
        "method": "GET",
        "url": "/api/v1/loan_applications/statistics/summary",
        "description": "Get application statistics"
    },
    
    "delete_application": {
        "method": "DELETE",
        "url": "/api/v1/loan_applications/1",
        "description": "Delete application (use with caution)"
    }
}

# Example responses
EXAMPLE_RESPONSES = {
    "application_response": {
        "id": 1,
        "name": "Juan Pérez García",
        "cedula": "12345678901",
        "convenio": "Empleados Públicos",
        "telefono": "3001234567",
        "fecha_nacimiento": "1985-03-15",
        "monto_solicitado": 5000000.0,
        "plazo": 24,
        "estado": "nueva",
        "created_at": "2024-12-02T10:30:00Z",
        "estimated_monthly_payment": 278947.0
    },
    
    "list_response": {
        "applications": [
            # Array of application_response objects
        ],
        "total": 150,
        "page": 1,
        "page_size": 20,
        "total_pages": 8
    },
    
    "client_summary": {
        "total_applications": 3,
        "has_pending": True,
        "has_approved": False,
        "latest_status": "en_proceso",
        "total_requested": 15000000.0,
        "latest_application_date": "2024-12-02T10:30:00Z"
    },
    
    "statistics_response": {
        "total_applications": 1250,
        "nueva": 45,
        "en_proceso": 23,
        "aprobada": 890,
        "rechazada": 267,
        "cancelada": 25,
        "total_amount_requested": 2500000000.0,
        "average_amount": 2000000.0,
        "average_term": 28.5
    }
}

# cURL examples for testing
CURL_EXAMPLES = """
# Create new application
curl -X POST "http://localhost:8000/api/v1/loan_applications/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Juan Pérez García",
    "cedula": "12345678901",
    "convenio": "Empleados Públicos",
    "telefono": "3001234567",
    "fecha_nacimiento": "1985-03-15",
    "monto_solicitado": 5000000.0,
    "plazo": 24
  }'

# Get application by ID
curl -X GET "http://localhost:8000/api/v1/loan_applications/1"

# List applications with pagination
curl -X GET "http://localhost:8000/api/v1/loan_applications/?skip=0&limit=20"

# Get applications by cedula
curl -X GET "http://localhost:8000/api/v1/loan_applications/by_cedula/12345678901"

# Update application status
curl -X PUT "http://localhost:8000/api/v1/loan_applications/1/status" \
  -H "Content-Type: application/json" \
  -d '{
    "application_id": 1,
    "new_status": "aprobada",
    "notes": "Cumple todos los requisitos"
  }'

# Approve application
curl -X PUT "http://localhost:8000/api/v1/loan_applications/1/approve"

# Get statistics
curl -X GET "http://localhost:8000/api/v1/loan_applications/statistics/summary"
"""