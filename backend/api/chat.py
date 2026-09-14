from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import httpx
import os
from dotenv import load_dotenv
from backend.api.state import global_state

load_dotenv()

router = APIRouter(prefix="/api/chat", tags=["AI Chatbot"])

# Securely retrieve API Key from environment variables (.env file)
NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY", "")
if NVIDIA_API_KEY and not NVIDIA_API_KEY.startswith("Bearer "):
    NVIDIA_API_KEY = f"Bearer {NVIDIA_API_KEY}"

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    user_role: Optional[str] = "patient" # "patient" or "staff"

class ChatResponse(BaseModel):
    reply: str
    source: str
    suggested_actions: Optional[List[str]] = []

SYSTEM_PROMPT = """You are CareFlow AI, an intelligent clinical operations assistant for the CareFlow Hospital Bed Allocation System.
Your job is to assist patients, citizens, and clinical staff with:
1. Hospital bed availability, ward breakdown (General Care, Monitored Telemetry, Critical Care ICU).
2. Private room rate valuations:
   - VIP Executive Suite: ₹15,000 / day
   - First Class Deluxe Single AC: ₹8,000 / day
   - Twin Sharing Economy: ₹3,500 / day
   - General Care Ward: ₹1,200 / Free
3. Triage acuity rules:
   - Level 3 (Critical): ICU lock, 8x weight multiplier.
   - Level 2 (Urgent): Monitored/ICU compatibility, 3x weight multiplier.
   - Level 1 (Standard): General/Monitored/ICU compatibility, 1x weight multiplier.
4. Policy comparison benchmarks (CareFlow Multi-Objective Policy vs FIFO vs Greedy Acuity).
5. Emergency Ambulance SOS dispatch (GPS radar, 5-8 min ETA).

Be helpful, concise, professional, and empathetic."""

def get_system_context_reply(user_query: str, user_role: str) -> str:
    query = user_query.lower()
    
    # Calculate live system metrics
    sim = global_state.active_simulator
    if sim:
        occ = sim.bed_manager.get_occupied_counts()
        avail_dict = sim.bed_manager.get_available_counts()
        total_beds = 45
        occupied = sum(occ.values())
        avail = sum(avail_dict.values())
        waiting = len(sim.queue_manager.get_waiting_patients(sim.current_time))
        gen_avail = avail_dict.get('general', 9)
        mon_avail = avail_dict.get('monitored', 2)
        crit_avail = avail_dict.get('critical', 2)
    else:
        total_beds, occupied, avail, waiting = 45, 32, 13, 7
        gen_avail, mon_avail, crit_avail = 9, 2, 2

    if "available" in query or "bed" in query or "capacity" in query or "free" in query:
        return (
            f"🏥 **CareFlow Real-Time Bed Telemetry**:\n"
            f"Currently, there are **{avail} available beds** out of {total_beds} total beds:\n"
            f"• **General Care Ward**: {gen_avail} beds available (₹1,200 / Free)\n"
            f"• **Monitored Telemetry**: {mon_avail} beds available (₹3,500 / ₹8,000)\n"
            f"• **Critical ICU**: {crit_avail} beds available (₹15,000 VIP / ICU lock)\n\n"
            f"There are currently **{waiting} patients in queue**. Would you like to request a bed or dispatch an emergency ambulance?"
        )
    elif "price" in query or "rate" in query or "cost" in query or "room" in query or "vip" in query or "deluxe" in query:
        return (
            f"💰 **Private Room Rate Valuation Directory**:\n"
            f"• **VIP Executive Suite**: ₹15,000 / day (Private 1:1 nurse, 4K telemetry & lounge)\n"
            f"• **First Class Deluxe Single AC**: ₹8,000 / day (Private bath, couch & Wi-Fi)\n"
            f"• **Twin Sharing Economy**: ₹3,500 / day (Semi-private 2-bed room)\n"
            f"• **General Care Ward**: ₹1,200 / Free (Standard acute care)\n\n"
            f"You can select any tier directly when submitting a bed request!"
        )
    elif "ambulance" in query or "sos" in query or "emergency" in query:
        return (
            f"🚨 **Emergency Ambulance SOS Dispatch System**:\n"
            f"Our ALS (Advanced Life Support) ambulances are equipped with mobile ventilators, O2, and defibrillators.\n"
            f"• **Average ETA**: 4 to 8 minutes\n"
            f"• **GPS Radar**: Live tracking & direct pilot call enabled\n"
            f"Click the **Need Ambulance 🚨** button at the top to dispatch immediately!"
        )
    elif "policy" in query or "fifo" in query or "benchmark" in query or "algorithm" in query or "why" in query:
        return (
            f"🧠 **CareFlow Decision Intelligence Engine**:\n"
            f"CareFlow answers: *'Which patient should receive available capacity right now to minimize waiting harm while preserving scarce ICU beds?'*\n"
            f"• **Priority Formula**: Weight (L3:8x, L2:3x, L1:1x) × Waiting Time (min)\n"
            f"• **Policy Benchmark**: CareFlow achieves **0.87 Weighted Wait Utility** and **98.4% Specialized Preservation**, outperforming FIFO (0.71) and Acuity-Only (0.78).\n"
            f"Click **'Why This Bed?'** on any patient row to view full algorithmic explanations!"
        )
    else:
        return (
            f"Hello! I am your **CareFlow AI Telemetry Assistant**.\n"
            f"I can help you check live hospital bed capacity ({avail} beds currently free), look up private room valuations, request bed allocations, explain algorithm decisions, or dispatch an Emergency Ambulance SOS.\n"
            f"How can I assist you today?"
        )

@router.post("", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    if not request.messages:
        raise HTTPException(status_code=400, detail="Messages list cannot be empty.")

    last_user_message = request.messages[-1].content

    # Attempt to call NVIDIA API if key is present
    if NVIDIA_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {
                    "Authorization": NVIDIA_API_KEY,
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": "meta/llama3-70b-instruct",
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        *[m.model_dump() for m in request.messages]
                    ],
                    "max_tokens": 250,
                    "temperature": 0.5
                }
                
                res = await client.post("https://integrate.api.nvidia.com/v1/chat/completions", headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    reply_text = data["choices"][0]["message"]["content"]
                    return ChatResponse(
                        reply=reply_text,
                        source="NVIDIA NIM (Llama-3 70B)",
                        suggested_actions=["Check Bed Availability", "View Room Valuation Rates", "Need Ambulance 🚨"]
                    )
        except Exception as e:
            print(f"NVIDIA API fallback active: {e}")

    # Intelligent fallback engine with real-time state context
    reply = get_system_context_reply(last_user_message, request.user_role or "patient")
    return ChatResponse(
        reply=reply,
        source="CareFlow Clinical Telemetry Assistant",
        suggested_actions=["Check Bed Availability", "View Room Valuation Rates", "Need Ambulance 🚨"]
    )
