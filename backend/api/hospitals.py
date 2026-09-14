from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any

router = APIRouter(prefix="/api/hospitals", tags=["Hospitals Directory"])

HOSPITALS_REGISTRY = [
    {
        "id": "h-01",
        "name": "CareFlow Metro General Hospital",
        "type": "Public / Government",
        "is_private": False,
        "rating": 4.6,
        "distance_km": 1.2,
        "address": "100 Hospital Road, Central District",
        "emergency_phone": "+91-11-2345-6789",
        "total_beds": 45,
        "occupied_beds": 32,
        "available_beds": 13,
        "icu_available": 2,
        "monitored_available": 2,
        "general_available": 9,
        "ambulance_eta_min": 5,
        "room_tiers": [
            {
                "tier_id": "general",
                "name": "General Care Ward",
                "price_per_day": 0,
                "price_formatted": "Free (Govt Subsidized)",
                "description": "Standard acute care multi-bed ward with general nursing support.",
                "amenities": ["24/7 Nursing", "Vital Telemetry", "Standard Meals"],
                "total": 30,
                "occupied": 21,
                "available": 9
            },
            {
                "tier_id": "monitored",
                "name": "Monitored Telemetry Unit",
                "price_per_day": 0,
                "price_formatted": "Free (Govt Priority)",
                "description": "Continuous cardiac & vital sign telemetry tracking unit.",
                "amenities": ["Continuous Cardiac Monitor", "Oxygen Port", "Specialized Care"],
                "total": 10,
                "occupied": 8,
                "available": 2
            },
            {
                "tier_id": "critical",
                "name": "Critical Care ICU",
                "price_per_day": 0,
                "price_formatted": "Free (Emergency Triage)",
                "description": "High-dependency intensive care isolation unit with ventilator support.",
                "amenities": ["1:1 ICU Nursing", "Mechanical Ventilator", "Isolation Chamber"],
                "total": 5,
                "occupied": 3,
                "available": 2
            }
        ]
    },
    {
        "id": "h-02",
        "name": "Apollo Apex Super Specialty Hospital",
        "type": "Private Tertiary Care",
        "is_private": True,
        "rating": 4.9,
        "distance_km": 3.5,
        "address": "45 Apex Boulevard, Sector 12",
        "emergency_phone": "+91-11-9876-5432",
        "total_beds": 65,
        "occupied_beds": 48,
        "available_beds": 17,
        "icu_available": 4,
        "monitored_available": 5,
        "general_available": 8,
        "ambulance_eta_min": 7,
        "room_tiers": [
            {
                "tier_id": "vip_suite",
                "name": "VIP Executive Suite",
                "price_per_day": 15000,
                "price_formatted": "₹15,000 / day",
                "description": "Luxury private suite with dedicated 1:1 nurse, anteroom lounge, & 4K telemetry.",
                "amenities": ["Dedicated 1:1 Nurse", "Anteroom Family Lounge", "Private Bathroom", "4K Telemetry", "Gourmet Dining"],
                "total": 5,
                "occupied": 3,
                "available": 2
            },
            {
                "tier_id": "first_class",
                "name": "First Class Deluxe Single AC",
                "price_per_day": 8000,
                "price_formatted": "₹8,000 / day",
                "description": "Private air-conditioned room with attached bath and companion couch.",
                "amenities": ["Private AC Room", "Attached Bath", "Companion Bed", "Smart TV", "Wi-Fi"],
                "total": 20,
                "occupied": 15,
                "available": 5
            },
            {
                "tier_id": "economy",
                "name": "Twin Sharing Economy Ward",
                "price_per_day": 3500,
                "price_formatted": "₹3,500 / day",
                "description": "Semi-private 2-bed room with shared AC and privacy curtain.",
                "amenities": ["2-Bed Semi-Private", "Shared AC", "Privacy Curtain", "Telemetry Monitor"],
                "total": 20,
                "occupied": 15,
                "available": 5
            },
            {
                "tier_id": "general",
                "name": "General Acute Care",
                "price_per_day": 1200,
                "price_formatted": "₹1,200 / day",
                "description": "Multi-bed ward for acute medical observation and recovery.",
                "amenities": ["Nursing Care", "Central Oxygen", "Dietary Support"],
                "total": 20,
                "occupied": 15,
                "available": 5
            }
        ]
    },
    {
        "id": "h-03",
        "name": "Fortis Heart & Emergency Institute",
        "type": "Private Specialty Hospital",
        "is_private": True,
        "rating": 4.8,
        "distance_km": 4.8,
        "address": "88 Cardiac Way, Health City",
        "emergency_phone": "+91-11-4455-6677",
        "total_beds": 50,
        "occupied_beds": 38,
        "available_beds": 12,
        "icu_available": 3,
        "monitored_available": 4,
        "general_available": 5,
        "ambulance_eta_min": 6,
        "room_tiers": [
            {
                "tier_id": "vip_suite",
                "name": "VIP Cardiac Suite",
                "price_per_day": 18000,
                "price_formatted": "₹18,000 / day",
                "description": "Ultra-specialized cardiac isolation suite with live cath-lab sync.",
                "amenities": ["Cardiac Monitor Sync", "1:1 CCU Specialist", "Private Suite", "Family Anteroom"],
                "total": 6,
                "occupied": 4,
                "available": 2
            },
            {
                "tier_id": "first_class",
                "name": "Deluxe Monitored Single AC",
                "price_per_day": 9000,
                "price_formatted": "₹9,000 / day",
                "description": "Single private telemetry room with continuous ECG monitoring.",
                "amenities": ["ECG Telemetry", "Private AC Room", "Companion Bed", "Attendant Meals"],
                "total": 14,
                "occupied": 10,
                "available": 4
            },
            {
                "tier_id": "economy",
                "name": "Twin Economy Telemetry",
                "price_per_day": 4000,
                "price_formatted": "₹4,000 / day",
                "description": "Semi-private cardiac telemetry ward.",
                "amenities": ["Semi-Private Bed", "Central Monitor", "24/7 Care"],
                "total": 30,
                "occupied": 24,
                "available": 6
            }
        ]
    },
    {
        "id": "h-04",
        "name": "St. Jude Children & Trauma Center",
        "type": "Public / Government Specialty",
        "is_private": False,
        "rating": 4.5,
        "distance_km": 2.1,
        "address": "12 Civil Lines, North Ward",
        "emergency_phone": "+91-11-1122-3344",
        "total_beds": 40,
        "occupied_beds": 28,
        "available_beds": 12,
        "icu_available": 3,
        "monitored_available": 3,
        "general_available": 6,
        "ambulance_eta_min": 4,
        "room_tiers": [
            {
                "tier_id": "general",
                "name": "Pediatric & Trauma Ward",
                "price_per_day": 0,
                "price_formatted": "Free (Govt Subsidized)",
                "description": "Specialized trauma and pediatric care ward.",
                "amenities": ["Pediatric Nursing", "Trauma Unit", "Parent Bed"],
                "total": 30,
                "occupied": 21,
                "available": 9
            },
            {
                "tier_id": "critical",
                "name": "Pediatric ICU (PICU)",
                "price_per_day": 0,
                "price_formatted": "Free (Critical Triage)",
                "description": "Intensive care unit dedicated to pediatric and severe trauma care.",
                "amenities": ["PICU Specialist", "Life Support", "Isolation"],
                "total": 10,
                "occupied": 7,
                "available": 3
            }
        ]
    },
    {
        "id": "h-05",
        "name": "Max Healthcare Institute & Research",
        "type": "Private Super Specialty",
        "is_private": True,
        "rating": 4.9,
        "distance_km": 6.2,
        "address": "200 Max Avenue, Cyber Park",
        "emergency_phone": "+91-11-8899-0011",
        "total_beds": 80,
        "occupied_beds": 58,
        "available_beds": 22,
        "icu_available": 5,
        "monitored_available": 7,
        "general_available": 10,
        "ambulance_eta_min": 8,
        "room_tiers": [
            {
                "tier_id": "vip_suite",
                "name": "Presidential Luxury Suite",
                "price_per_day": 22000,
                "price_formatted": "₹22,000 / day",
                "description": "5-Star medical suite with private butler, executive office, & 1:1 intensivist.",
                "amenities": ["Private Butler", "1:1 Senior Intensivist", "Executive Office", "Luxury Lounge", "Jacuzzi Bath"],
                "total": 4,
                "occupied": 2,
                "available": 2
            },
            {
                "tier_id": "first_class",
                "name": "VIP Executive Single AC",
                "price_per_day": 12000,
                "price_formatted": "₹12,000 / day",
                "description": "High-end private room with premium amenities and telemetry.",
                "amenities": ["Premium AC Room", "Companion Suite", "Smart Controls", "High-Speed Wi-Fi"],
                "total": 26,
                "occupied": 19,
                "available": 7
            },
            {
                "tier_id": "economy",
                "name": "Deluxe Twin Sharing",
                "price_per_day": 4500,
                "price_formatted": "₹4,500 / day",
                "description": "Spacious twin sharing room with personal entertainment screens.",
                "amenities": ["2-Bed Deluxe", "Personal Screen", "AC Room", "Telemetry"],
                "total": 50,
                "occupied": 37,
                "available": 13
            }
        ]
    }
]

@router.get("")
def get_all_hospitals():
    return HOSPITALS_REGISTRY

@router.get("/{hospital_id}")
def get_hospital_detail(hospital_id: str):
    h = next((item for item in HOSPITALS_REGISTRY if item["id"] == hospital_id), None)
    if not h:
        raise HTTPException(status_code=404, detail=f"Hospital {hospital_id} not found.")
    return h
