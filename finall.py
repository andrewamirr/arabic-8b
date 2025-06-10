import chainlit as cl


from llama_cpp import Llama


import asyncio


import logging


import os


import re


from typing import Optional


import datetime





# Custom Exception Classes


class DiagnosticError(Exception):


    """Exception raised for errors in the diagnostic process."""


    pass





class UserProfileError(Exception):


    """Exception raised for errors in user profile operations."""


    pass





class MaintenanceError(Exception):


    """Exception raised for errors in maintenance operations."""


    pass





class CostCalculationError(Exception):


    """Exception raised for errors in cost calculation operations."""


    pass





class ResponseGenerationError(Exception):


    """Exception raised for errors in response generation operations."""


    pass





# Set up enhanced logging


logging.basicConfig(


    level=logging.INFO,


    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',


    handlers=[


        logging.FileHandler('car_expert.log'),


        logging.StreamHandler()


    ]


)


logger = logging.getLogger(__name__)





class Config:


    MODEL_PATH = "./arabic-orpo-llama-3-8b-instruct.Q5_K_S.gguf"


    MAX_TOKENS = 300


    TEMPERATURE = 0.18


    N_CTX = 2048


    N_GPU_LAYERS = 0


    N_THREADS = 6


    VERBOSE = False


    BATCH_SIZE = 512


    CURRENT_DATE = "2025-06-06 19:00:25"


    CURRENT_USER = "andrewamirr"


    


    # Enhanced maintenance intervals with detailed conditions


    MAINTENANCE_INTERVALS = {


        "oil_change": {


            "city": 5000,


            "highway": 7500,


            "severe": 3000,


            "time": "6 months",


            "conditions": {


                "hot_weather": 4000,


                "dusty": 4000,


                "heavy_traffic": 4000,


                "short_trips": 3500


            }


        },


        "air_filter": {


            "normal": 15000,


            "dusty": 10000,


            "severe": 7500,


            "time": "12 months",


            "conditions": {


                "desert_areas": 7500,


                "construction_zones": 8000,


                "unpaved_roads": 7500


            }


        },


        "brake_fluid": {


            "normal": 45000,


            "severe": 30000,


            "time": "24 months",


            "conditions": {


                "mountainous": 30000,


                "heavy_traffic": 35000,


                "high_performance": 25000


            }


        },


        "transmission_fluid": {


            "normal": 60000,


            "severe": 40000,


            "time": "36 months",


            "conditions": {


                "towing": 30000,


                "sport_driving": 35000,


                "taxi_service": 30000


            }


        },


        "spark_plugs": {


            "normal": {


                "standard": 40000,


                "platinum": 60000,


                "iridium": 100000


            },


            "severe": {


                "standard": 30000,


                "platinum": 45000,


                "iridium": 80000


            }


        },


        "timing_belt": {


            "normal": 90000,


            "severe": 60000,


            "time": "60 months",


            "conditions": {


                "hot_climate": 70000,


                "frequent_stops": 75000,


                "delivery_service": 65000


            }


        }


    }





    # Vehicle categories for specific maintenance rules


    VEHICLE_CATEGORIES = {


        "economy": {


            "brands": ["toyota", "honda", "hyundai", "kia", "nissan"],


            "maintenance_factor": 1.0,


            "parts_availability": "high",


            "cost_factor": 1.0


        },


        "luxury": {


            "brands": ["bmw", "mercedes", "audi", "lexus"],


            "maintenance_factor": 0.8,


            "parts_availability": "medium",


            "cost_factor": 2.0


        },


        "performance": {


            "brands": ["porsche", "ferrari", "maserati"],


            "maintenance_factor": 0.6,


            "parts_availability": "low",


            "cost_factor": 3.0


        }


    }





# Comprehensive car knowledge base


CAR_KNOWLEDGE_BASE = {


    # Engine Oil and Lubrication System


    ("تغيير زيت الموتور", "change engine oil", "oil change", "engine oil change", "متى اغير الزيت", 


     "كل قد ايه اغير زيت", "oil service", "خدمة زيت"): {


        "en": """🔧 **Complete Engine Oil Service Guide (Egypt 2025)**





• Change Intervals by Driving Style:


  - City driving: Every 5,000 km


  - Highway driving: Every 7,500 km


  - Severe conditions: Every 3,000-4,000 km


  - Time-based: Every 6 months (whichever comes first)





• Oil Grades and Prices (4L):


  1. Full Synthetic:


     - Mobil 1: 950-1150 EGP


     - Castrol EDGE: 850-1000 EGP


     - Shell Helix Ultra: 900-1100 EGP


     


  2. Semi-Synthetic:


     - Castrol GTX: 600-800 EGP


     - Shell Helix HX7: 600-750 EGP


     - Total Quartz: 700-900 EGP


     


  3. Conventional:


     - Local brands: 350-550 EGP


     - Basic options: 300-450 EGP





• Service Components:


  - Oil Filter: 120-220 EGP


  - Labor: 120-200 EGP


  - Diagnostic check: 150-300 EGP


  - Total Service: 600-1700 EGP





• Severe Conditions Requiring More Frequent Changes:


  1. Frequent short trips (less than 10 km)


  2. Extreme heat (above 35°C)


  3. Heavy traffic driving


  4. Dusty conditions


  5. Towing or heavy loads





• Warning Signs for Immediate Oil Change:


  1. Dark/black oil color


  2. Engine noise increased


  3. Oil pressure warning light


  4. Exhaust smoke


  5. Oil level dropping quickly


  6. Engine running hotter





• Best Practices:


  1. Use synthetic oil for Egypt's heat


  2. Keep detailed service records


  3. Check oil level every 2 weeks


  4. Use manufacturer recommended grade


  5. Always replace the oil filter


  6. Consider engine age and condition





• Professional Tips:


  1. Warm engine before changing


  2. Check for leaks after service


  3. Reset oil life monitor if equipped


  4. Dispose of old oil properly


  5. Document service date and mileage""",


        


        "ar": """🔧 **دليل شامل لخدمة زيت المحرك (مصر 2025)**





• مواعيد التغيير حسب نوع القيادة:


  - داخل المدينة: كل 5000 كم


  - على الطرق السريعة: كل 7500 كم


  - الظروف القاسية: كل 3000-4000 كم


  - حسب الوقت: كل 6 شهور (أيهما يأتي أولاً)





• درجات الزيت والأسعار (4 لتر):


  1. تخليقي كامل:


     - موبيل 1: 950-1150 جنيه


     - كاسترول إيدج: 850-1000 جنيه


     - شل هيلكس ألترا: 900-1100 جنيه


     


  2. نصف تخليقي:


     - كاسترول GTX: 600-800 جنيه


     - شل هيلكس HX7: 600-750 جنيه


     - توتال كوارتز: 700-900 جنيه


     


  3. عادي:


     - ماركات محلية: 350-550 جنيه


     - خيارات أساسية: 300-450 جنيه





• مكونات الخدمة:


  - فلتر الزيت: 120-220 جنيه


  - أجرة العمل: 120-200 جنيه


  - فحص بالكمبيوتر: 150-300 جنيه


  - إجمالي الخدمة: 600-1700 جنيه





• الظروف التي تتطلب تغيير أكثر تكراراً:


  1. رحلات قصيرة متكررة (أقل من 10 كم)


  2. حرارة شديدة (فوق 35 درجة)


  3. القيادة في الزحام


  4. الأجواء المتربة


  5. سحب أحمال ثقيلة





• علامات تستدعي تغيير الزيت فوراً:


  1. لون الزيت أسود داكن


  2. زيادة صوت المحرك


  3. إضاءة لمبة ضغط الزيت


  4. دخان من العادم


  5. انخفاض مستوى الزيت سريعاً


  6. ارتفاع حرارة المحرك





• أفضل الممارسات:


  1. استخدم زيت تخليقي لحرارة مصر


  2. احتفظ بسجل صيانة مفصل


  3. افحص مستوى الزيت كل أسبوعين


  4. استخدم الدرجة الموصى بها من المصنع


  5. غيّر فلتر الزيت مع كل تغيير


  6. راعي عمر المحرك وحالته





• نصائح احترافية:


  1. سخن المحرك قبل التغيير


  2. افحص التسريبات بعد الخدمة


  3. اعد ضبط مؤشر عمر الزيت


  4. تخلص من الزيت القديم بشكل صحيح


  5. سجل تاريخ الخدمة والمسافة"""


    },


# Continuing CAR_KNOWLEDGE_BASE...


    # Engine Performance and Diagnostics


    ("مشاكل المحرك", "engine problems", "محرك", "engine performance", "قوة المحرك", "engine power", "ضعف المحرك"): {


        "en": """🔍 **Complete Engine Diagnostic Guide (Egypt 2025)**





• Common Problems by Symptom:


  1. Starting Issues:


     - No Start: Battery/Starter/Fuel pump (1200-3700 EGP)


     - Hard Start: Spark plugs/Fuel system (400-2000 EGP)


     - Intermittent: Sensors/Ignition (600-2500 EGP)





  2. Running Problems:


     - Rough Idle: Spark plugs/Injectors/MAF (500-3000 EGP)


     - Misfire: Coils/Plugs/Compression (450-4000 EGP)


     - Power Loss: Multiple systems (1000-5000 EGP)





  3. Noise Issues:


     - Ticking: Valves/Low oil (500-3000 EGP)


     - Knocking: Bearings/Timing (2000-8000 EGP)


     - Rattling: Timing chain/Mounts (1200-4000 EGP)





• Diagnostic Process:


  1. Computer Scan: 300-600 EGP


  2. Compression Test: 400-800 EGP


  3. Fuel Pressure: 300-500 EGP


  4. Smoke Analysis: 400-700 EGP





• Component Lifespans:


  - Spark Plugs: 40,000-100,000 km


  - Ignition Coils: 60,000-120,000 km


  - Fuel Injectors: 100,000-150,000 km


  - Timing Belt: 60,000-100,000 km





• Warning Signs:


  1. Check Engine Light


  2. Unusual Noises


  3. Performance Drop


  4. Excessive Smoke


  5. High Consumption





• Preventive Maintenance:


  1. Regular Oil Changes


  2. Air Filter Service


  3. Fuel System Cleaning


  4. Timing Belt Check


  5. Tune-ups





• Emergency Actions:


  - Stop if knocking occurs


  - Check oil immediately


  - Avoid high speeds


  - Get professional diagnosis""",





        "ar": """🔍 **دليل شامل لتشخيص المحرك (مصر 2025)**





• المشاكل الشائعة حسب الأعراض:


  1. مشاكل التشغيل:


     - عدم التشغيل: بطارية/مارش/طرمبة (1200-3700 جنيه)


     - صعوبة التشغيل: بوجيهات/نظام الوقود (400-2000 جنيه)


     - تقطيع: حساسات/نظام الإشعال (600-2500 جنيه)





  2. مشاكل التشغيل:


     - رعشة: بوجيهات/رشاشات/حساس هواء (500-3000 جنيه)


     - حريق: كويلات/بوجيهات/ضغط (450-4000 جنيه)


     - ضعف: أنظمة متعددة (1000-5000 جنيه)





  3. مشاكل الصوت:


     - طقطقة: صبابات/زيت منخفض (500-3000 جنيه)


     - خبط: رمان بلي/توقيت (2000-8000 جنيه)


     - خرخرة: سلسلة/مساند (1200-4000 جنيه)





• عملية التشخيص:


  1. فحص كمبيوتر: 300-600 جنيه


  2. فحص ضغط: 400-800 جنيه


  3. ضغط وقود: 300-500 جنيه


  4. تحليل دخان: 400-700 جنيه





• عمر القطع:


  - بوجيهات: 40,000-100,000 كم


  - كويلات: 60,000-120,000 كم


  - رشاشات: 100,000-150,000 كم


  - سير التيمينج: 60,000-100,000 كم





• علامات التحذير:


  1. لمبة المحرك


  2. أصوات غريبة


  3. انخفاض الأداء


  4. دخان زائد


  5. استهلاك عالي





• الصيانة الوقائية:


  1. تغيير زيت منتظم


  2. خدمة فلتر الهواء


  3. تنظيف نظام الوقود


  4. فحص سير التيمينج


  5. ضبط المحرك





• إجراءات الطوارئ:


  - توقف عند سماع خبط


  - افحص الزيت فوراً


  - تجنب السرعات العالية


  - احصل على تشخيص محترف"""


    },





    # Transmission Systems


    ("مشاكل الفتيس", "transmission problems", "فتيس", "gear problems", "ناقل الحركة"): {


        "en": """⚙️ **Transmission Systems Guide (Egypt 2025)**





• Types and Common Issues:


  1. Automatic Transmission:


     - Hard Shifts: Solenoids/Fluid (1500-3000 EGP)


     - Slipping: Clutch packs/Bands (3000-7000 EGP)


     - Fluid Leaks: Seals/Gaskets (800-2000 EGP)





  2. Manual Transmission:


     - Clutch Issues: Disc/Pressure plate (2500-5000 EGP)


     - Gear Grinding: Synchros (3000-6000 EGP)


     - Bearing Noise: Input/Output shaft (2000-4000 EGP)





• Service Costs:


  1. Fluid Change:


     - Automatic: 800-1500 EGP


     - Manual: 400-800 EGP


     - CVT: 1000-2000 EGP





  2. Major Repairs:


     - Rebuild: 8000-15000 EGP


     - Replace: 15000-30000 EGP


     - Clutch Kit: 3000-7000 EGP





• Maintenance Schedule:


  - Fluid Check: Monthly


  - Fluid Change: 40,000-60,000 km


  - Filter Change: With fluid


  - Clutch: 80,000-120,000 km





• Warning Signs:


  1. Delayed Engagement


  2. Rough Shifting


  3. Slipping Gears


  4. Strange Noises


  5. Fluid Leaks


  6. Burning Smell





• Prevention Tips:


  1. Regular Fluid Checks


  2. Proper Warm-up


  3. Avoid Overloading


  4. Gentle Shifting


  5. Regular Service""",





        "ar": """⚙️ **دليل أنظمة ناقل الحركة (مصر 2025)**





• الأنواع والمشاكل الشائعة:


  1. الفتيس الأوتوماتيك:


     - تغيير عنيف: سولونويد/زيت (1500-3000 جنيه)


     - تزحلق: دسك/طارة (3000-7000 جنيه)


     - تسريب: جوانات/مانعات (800-2000 جنيه)





  2. الفتيس العادي:


     - مشاكل الدبرياج: دسك/بلية (2500-5000 جنيه)


     - صوت تعشيق: سنكرونات (3000-6000 جنيه)


     - صوت رمان: عمود الدخل/الخروج (2000-4000 جنيه)





• تكاليف الخدمة:


  1. تغيير الزيت:


     - أوتوماتيك: 800-1500 جنيه


     - عادي: 400-800 جنيه


     - CVT: 1000-2000 جنيه





  2. إصلاحات كبيرة:


     - إصلاح: 8000-15000 جنيه


     - تغيير: 15000-30000 جنيه


     - طقم دبرياج: 3000-7000 جنيه





• جدول الصيانة:


  - فحص الزيت: شهرياً


  - تغيير الزيت: 40,000-60,000 كم


  - تغيير الفلتر: مع الزيت


  - دبرياج: 80,000-120,000 كم





• علامات التحذير:


  1. تأخر التعشيق


  2. تغيير خشن


  3. تزحلق التروس


  4. أصوات غريبة


  5. تسريب زيت


  6. رائحة حريق





• نصائح وقائية:


  1. فحص الزيت بانتظام


  2. تسخين مناسب


  3. تجنب الحمولة الزائدة


  4. تغيير ناعم


  5. صيانة منتظمة"""


    },





# Continue with more comprehensive problem categories...


    # Brake Systems


    ("مشاكل الفرامل", "brake problems", "brake system", "فرامل", "صوت فرامل", "brake noise"): {


        "en": """🛑 **Complete Brake System Guide (Egypt 2025)**





• System Components and Issues:


  1. Front Brakes:


     - Disc Pads: 400-1700 EGP/set


     - Rotors: 1200-2500 EGP/pair


     - Calipers: 1500-3000 EGP/each


     


  2. Rear Brakes:


     - Shoes: 500-1000 EGP/set


     - Drums: 900-1800 EGP/pair


     - Cylinders: 400-800 EGP/each


     


  3. Hydraulic System:


     - Master Cylinder: 1200-2500 EGP


     - Brake Lines: 400-1000 EGP


     - ABS Module: 3000-7000 EGP





• Common Problems:


  1. Noise Issues:


     - Squealing: Wear indicators


     - Grinding: Metal-on-metal


     - Clicking: Hardware loose


     


  2. Performance Issues:


     - Soft Pedal: Air/Leak


     - Hard Pedal: Booster/Master


     - Pulling: Caliper/Alignment


     


  3. Vibration Issues:


     - Pedal: Master cylinder


     - Steering: Rotors


     - Body: Suspension related





• Maintenance Schedule:


  - Pad Check: Every 10,000 km


  - Fluid Change: Every 2 years


  - Rotor Check: With pad change


  - System Flush: Every 3 years





• Emergency Signs:


  1. Pedal goes to floor


  2. Grinding noise


  3. Burning smell


  4. ABS light on


  5. Pulling to one side





• Professional Tips:


  1. Always replace in pairs


  2. Use quality parts


  3. Proper break-in


  4. Regular inspection


  5. Clean components""",





        "ar": """🛑 **دليل شامل لنظام الفرامل (مصر 2025)**





• مكونات النظام والمشاكل:


  1. الفرامل الأمامية:


     - تيل: 400-1700 جنيه/طقم


     - ديسكات: 1200-2500 جنيه/زوج


     - كاليبرات: 1500-3000 جنيه/قطعة


     


  2. الفرامل الخلفية:


     - تيل: 500-1000 جنيه/طقم


     - طنابير: 900-1800 جنيه/زوج


     - اسطوانات: 400-800 جنيه/قطعة


     


  3. النظام الهيدروليكي:


     - ماستر: 1200-2500 جنيه


     - خراطيم: 400-1000 جنيه


     - ABS: 3000-7000 جنيه





• المشاكل الشائعة:


  1. مشاكل الصوت:


     - صفير: مؤشرات التآكل


     - احتكاك: معدن بمعدن


     - طقطقة: مسامير مفكوكة


     


  2. مشاكل الأداء:


     - دواسة طرية: هواء/تسريب


     - دواسة صلبة: بوستر/ماستر


     - سحب: كاليبر/زوايا


     


  3. مشاكل الاهتزاز:


     - دواسة: ماستر


     - دركسيون: ديسكات


     - جسم: تعليق





• جدول الصيانة:


  - فحص التيل: كل 10,000 كم


  - تغيير الزيت: كل سنتين


  - فحص الديسكات: مع التيل


  - غسيل النظام: كل 3 سنوات





• علامات الطوارئ:


  1. الدواسة تنزل للأرض


  2. صوت احتكاك


  3. رائحة حريق


  4. لمبة ABS


  5. سحب لجانب





• نصائح احترافية:


  1. التغيير بالأزواج


  2. استخدام قطع جيدة


  3. تليين صحيح


  4. فحص منتظم


  5. تنظيف المكونات"""


    },


}


# Advanced Diagnostic System Implementation


class AdvancedDiagnosticSystem:


    def __init__(self):


        self.diagnostic_data = {


            "engine": {


                "symptoms": {


                    "starting": {


                        "no_crank": {


                            "causes": [


                                {"part": "battery", "probability": 0.4, "cost": "1400-2500"},


                                {"part": "starter", "probability": 0.3, "cost": "1800-3500"},


                                {"part": "alternator", "probability": 0.2, "cost": "2500-4500"}


                            ],


                            "tests": ["Battery voltage", "Starter draw", "Alternator output"]


                        },


                        "crank_no_start": {


                            "causes": [


                                {"part": "fuel_pump", "probability": 0.35, "cost": "2100-3700"},


                                {"part": "spark_plugs", "probability": 0.25, "cost": "120-270"},


                                {"part": "ignition_coil", "probability": 0.2, "cost": "450-1200"}


                            ],


                            "tests": ["Fuel pressure", "Spark test", "Compression test"]


                        }


                    },


                    "running": {


                        "misfire": {


                            "causes": [


                                {"part": "spark_plugs", "probability": 0.3, "cost": "120-270"},


                                {"part": "ignition_coils", "probability": 0.3, "cost": "450-1200"},


                                {"part": "fuel_injectors", "probability": 0.2, "cost": "1500-2800"}


                            ],


                            "tests": ["Compression test", "Spark test", "Injector balance"]


                        }


                    }


                }


            }


        }


        


    def diagnose(self, system: str, symptom: str, sub_symptom: str) -> dict:


        """Perform advanced diagnosis based on symptoms."""


        try:


            system_data = self.diagnostic_data.get(system, {})


            symptom_data = system_data.get("symptoms", {}).get(symptom, {})


            problem_data = symptom_data.get(sub_symptom, {})


            


            if not problem_data:


                raise DiagnosticError(f"Unknown problem: {system}/{symptom}/{sub_symptom}")


                


            # Calculate confidence scores


            total_probability = sum(cause["probability"] for cause in problem_data["causes"])


            normalized_causes = []


            


            for cause in problem_data["causes"]:


                normalized_causes.append({


                    "part": cause["part"],


                    "confidence": round(cause["probability"] / total_probability * 100, 2),


                    "cost": cause["cost"]


                })


                


            return {


                "possible_causes": normalized_causes,


                "recommended_tests": problem_data["tests"],


                "confidence_level": "high" if total_probability > 0.8 else "medium"


            }


            


        except Exception as e:


            logger.error(f"Diagnostic error: {str(e)}")


            raise DiagnosticError(f"Error during diagnosis: {str(e)}")





# Enhanced User Profile System


class EnhancedUserProfile:


    def __init__(self, username: str):


        self.username = username


        self.vehicles = {}


        self.service_history = {}


        self.preferences = {


            "preferred_shops": [],


            "parts_quality": "standard",


            "notification_preference": "both",  # email/sms/both


            "maintenance_style": "standard"  # economic/standard/premium


        }


        


    def add_vehicle(self, vehicle_id: str, details: dict):


        """Add or update vehicle information."""


        try:


            self.vehicles[vehicle_id] = {


                "make": details.get("make", ""),


                "model": details.get("model", ""),


                "year": details.get("year", 0),


                "mileage": details.get("mileage", 0),


                "last_service": details.get("last_service", ""),


                "service_history": [],


                "maintenance_schedule": {},


                "known_issues": []


            }


            self._update_maintenance_schedule(vehicle_id)


        except Exception as e:


            raise UserProfileError(f"Error adding vehicle: {str(e)}")





    def _update_maintenance_schedule(self, vehicle_id: str):


        """Update maintenance schedule based on vehicle information."""


        vehicle = self.vehicles.get(vehicle_id)


        if not vehicle:


            return


            


        # Calculate next service dates


        current_mileage = vehicle["mileage"]


        maintenance_scheduler = EnhancedMaintenanceScheduler()


        


        for service_type, intervals in Config.MAINTENANCE_INTERVALS.items():


            next_service = maintenance_scheduler.calculate_next_service(


                service_type=service_type,


                current_mileage=current_mileage,


                vehicle_type=self._get_vehicle_category(vehicle["make"])


            )


            vehicle["maintenance_schedule"][service_type] = next_service





    def _get_vehicle_category(self, make: str) -> str:


        """Determine vehicle category for maintenance calculations."""


        make_lower = make.lower()


        for category, data in Config.VEHICLE_CATEGORIES.items():


            if make_lower in data["brands"]:


                return category


        return "economy"  # default category





# Enhanced Maintenance Scheduling System with Weather and Conditions Adaptation


class EnhancedMaintenanceScheduler:


    def __init__(self):


        self.current_date = datetime.strptime("2025-06-06 19:11:27", "%Y-%m-%d %H:%M:%S")


        self.current_user = "andrewamirr"


        self.weather_conditions = {


            "egypt": {


                "summer": {


                    "temperature": "35-45°C",


                    "humidity": "high",


                    "dust": "severe",


                    "maintenance_factor": 0.8  # More frequent maintenance needed


                },


                "winter": {


                    "temperature": "10-25°C",


                    "humidity": "moderate",


                    "dust": "moderate",


                    "maintenance_factor": 1.0


                }


            }


        }


        


    def get_current_conditions(self) -> dict:


        """Get current weather and environmental conditions."""


        month = self.current_date.month


        if 4 <= month <= 10:  # Summer months in Egypt


            return self.weather_conditions["egypt"]["summer"]


        return self.weather_conditions["egypt"]["winter"]





    def calculate_next_service(self, service_type: str, current_mileage: int,


                             vehicle_type: str = "economy", 


                             driving_conditions: str = "normal") -> dict:


        """Calculate next service considering all factors."""


        try:


            # Get base intervals


            intervals = Config.MAINTENANCE_INTERVALS.get(service_type, {})


            base_interval = intervals.get("normal", 10000)


            


            # Adjust for vehicle type


            vehicle_factor = Config.VEHICLE_CATEGORIES[vehicle_type]["maintenance_factor"]


            


            # Adjust for weather conditions


            conditions = self.get_current_conditions()


            weather_factor = conditions["maintenance_factor"]


            


            # Adjust for driving conditions


            condition_factors = {


                "normal": 1.0,


                "severe": 0.7,


                "light": 1.2


            }


            driving_factor = condition_factors.get(driving_conditions, 1.0)


            


            # Calculate final interval


            adjusted_interval = base_interval * vehicle_factor * weather_factor * driving_factor


            


            next_service_km = current_mileage + int(adjusted_interval)


            next_service_date = self.current_date + datetime.timedelta(days=int(adjusted_interval/50))  # Assuming 50km per day average


            


            return {


                "next_service_km": next_service_km,


                "next_service_date": next_service_date.strftime("%Y-%m-%d"),


                "km_remaining": int(adjusted_interval),


                "days_remaining": int((next_service_date - self.current_date).days),


                "weather_adjustment": f"{weather_factor:.2f}",


                "urgency": self._calculate_urgency(adjusted_interval)


            }


        except Exception as e:


            raise MaintenanceError(f"Error calculating next service: {str(e)}")





    def _calculate_urgency(self, interval: float) -> str:


        """Calculate maintenance urgency level."""


        if interval <= 500:


            return "critical"


        elif interval <= 1000:


            return "urgent"


        elif interval <= 2000:


            return "soon"


        return "normal"




class QueryAnalyzer:
    # ...existing code...

    def analyze_query(self, query: str) -> dict:
        language = "ar" if is_arabic_text(query) else "en"
        query_type = self._determine_query_type(query, language)
        is_emergency = self._check_emergency(query, language)
        return {
            "query_type": query_type,
            "is_emergency": is_emergency,
            "language": language,
            "main_content": query
        }
        self.current_date = datetime.datetime.strptime("2025-06-06 20:04:01", "%Y-%m-%d %H:%M:%S")

        self.current_user = "andrewamirr"
# Advanced Cost Calculation System


class CostCalculationSystem:


    def __init__(self):


        self.labor_rates = {


            "standard": 150,  # EGP per hour


            "specialist": 250,


            "dealership": 350


        }


        self.parts_quality_factors = {


            "economy": 0.7,


            "standard": 1.0,


            "premium": 1.4


        }


        self.emergency_factor = 1.5


        


    def calculate_repair_cost(self, repair_type: str, parts_quality: str = "standard",


                            is_emergency: bool = False, shop_type: str = "standard") -> dict:


        """Calculate detailed repair cost estimate."""


        try:


            base_costs = {


                "oil_change": {


                    "parts": 800,


                    "labor_hours": 1,


                    "complexity": "low"


                },


                "brake_service": {


                    "parts": 1200,


                    "labor_hours": 2,


                    "complexity": "medium"


                },


                "timing_belt": {


                    "parts": 2500,


                    "labor_hours": 4,


                    "complexity": "high"


                }


                # Add more repair types as needed


            }


            


            if repair_type not in base_costs:


                raise ValueError(f"Unknown repair type: {repair_type}")


                


            repair_info = base_costs[repair_type]


            


            # Calculate parts cost


            parts_cost = repair_info["parts"] * self.parts_quality_factors[parts_quality]


            


            # Calculate labor cost


            labor_cost = repair_info["labor_hours"] * self.labor_rates[shop_type]


            


            # Apply emergency factor if needed


            if is_emergency:


                parts_cost *= self.emergency_factor


                labor_cost *= self.emergency_factor


                


            total_cost = parts_cost + labor_cost


            


            return {


                "repair_type": repair_type,


                "parts_cost": round(parts_cost, 2),


                "labor_cost": round(labor_cost, 2),


                "total_cost": round(total_cost, 2),


                "quality_level": parts_quality,


                "is_emergency": is_emergency,


                "shop_type": shop_type,


                "estimated_time": repair_info["labor_hours"],


                "complexity": repair_info["complexity"],


                "currency": "EGP"


            }


        except Exception as e:


            raise CostCalculationError(f"Error calculating repair cost: {str(e)}")





# Advanced Response Generation System


class ResponseGenerator:


    def __init__(self):


        self.diagnostic_system = AdvancedDiagnosticSystem()


        self.cost_calculator = CostCalculationSystem()


        self.maintenance_scheduler = EnhancedMaintenanceScheduler()


        


    def generate_response(self, query: str, user_profile: EnhancedUserProfile,


                         language: str = "en") -> dict:


        """Generate comprehensive response to user query."""


        try:


            # Analyze query


            query_type = self._analyze_query_type(query)


            is_emergency = self._check_emergency(query)


            


            # Get base response from knowledge base


            base_response = self._get_knowledge_base_response(query, language)


            


            # Get diagnostic information if needed


            if query_type == "problem":


                diagnostic_info = self.diagnostic_system.diagnose(


                    system=self._identify_system(query),


                    symptom=self._identify_symptom(query),


                    sub_symptom=self._identify_sub_symptom(query)


                )


            else:


                diagnostic_info = None


                


            # Calculate costs if applicable


            if query_type in ["repair", "maintenance"]:


                cost_info = self.cost_calculator.calculate_repair_cost(


                    repair_type=self._identify_repair_type(query),


                    parts_quality=user_profile.preferences["parts_quality"],


                    is_emergency=is_emergency


                )


            else:


                cost_info = None


                


            # Format response


            response = self._format_response(


                base_response=base_response,


                diagnostic_info=diagnostic_info,


                cost_info=cost_info,


                is_emergency=is_emergency,


                language=language


            )


            


            return response


            


        except Exception as e:


            logger.error(f"Response generation error: {str(e)}")


            raise ResponseGenerationError(f"Error generating response: {str(e)}")





    def _analyze_query_type(self, query: str) -> str:


        """Analyze query type (problem, maintenance, repair, info)."""


        # Implementation details...


        pass





    def _check_emergency(self, query: str) -> bool:


        """Check if query indicates emergency situation."""


        emergency_keywords = {


            "en": ["emergency", "urgent", "help", "stuck", "smoke", "fire"],


            "ar": ["طوارئ", "عاجل", "النجدة", "متعطل", "دخان", "حريق"]


        }


        # Implementation details...


        pass





# Continue with more implementations...


# Helper function to detect Arabic text


def is_arabic_text(text: str) -> bool:


    arabic_ranges = [


        (0x0600, 0x06FF),  # Arabic


        (0x0750, 0x077F),  # Arabic Supplement


        (0xFB50, 0xFDFF),  # Arabic Presentation Forms-A


        (0xFE70, 0xFEFF),  # Arabic Presentation Forms-B


    ]


    return any(any(ord(char) >= start and ord(char) <= end for start, end in arabic_ranges) for char in text)





# Query Analysis and Emergency Response System


import datetime
import re

def is_arabic_text(text: str) -> bool:
    """Check if text contains Arabic characters"""
    arabic_pattern = re.compile(r'[\u0600-\u06FF]')
    return bool(arabic_pattern.search(text))

class QueryAnalyzer:
    def __init__(self):
        self.current_date = datetime.datetime.strptime("2025-06-06 20:04:01", "%Y-%m-%d %H:%M:%S")
        self.current_user = "andrewamirr"
    
    def analyze_query(self, query: str) -> dict:
        """Main method to analyze user query"""
        language = "ar" if is_arabic_text(query) else "en"
        query_type = self._determine_query_type(query, language)
        is_emergency = self._check_emergency(query, language)
        return {
            "query_type": query_type,
            "is_emergency": is_emergency,
            "language": language,
            "main_content": query
        }
    
    def _determine_query_type(self, query: str, language: str) -> str:
        """Determine the type of query being asked."""
        query_lower = query.lower()
        
        # Define pattern dictionaries for each query type
        patterns = {
            "maintenance": {
                "en": ["change", "service", "maintain", "check", "when should", "how often"],
                "ar": ["تغيير", "صيانة", "فحص", "متى", "كل قد", "كام"]
            },
            "diagnostic": {
                "en": ["problem", "issue", "broken", "not working", "failed", "wrong"],
                "ar": ["مشكلة", "عطل", "مكسور", "مش شغال", "عطلان", "خربان"]
            },
            "cost": {
                "en": ["cost", "price", "expensive", "cheap", "how much", "pay"],
                "ar": ["سعر", "تكلفة", "غالي", "رخيص", "بكام", "كلفة"]
            },
            "emergency": {
                "en": ["emergency", "urgent", "help", "stuck", "smoke", "fire"],
                "ar": ["طوارئ", "عاجل", "نجدة", "متعطل", "دخان", "حريق"]
            }
        }
        
        # Check each pattern type
        for query_type, language_patterns in patterns.items():
            if any(pattern in query_lower for pattern in language_patterns[language]):
                return query_type
                
        # Default to information type if no specific pattern is matched
        return "information"

    def _check_emergency(self, query: str, language: str) -> bool:
        """Check if query indicates an emergency situation."""
        emergency_keywords = {
            "en": ["emergency", "urgent", "help", "stuck", "smoke", "fire", "accident"],
            "ar": ["طوارئ", "عاجل", "النجدة", "متعطل", "دخان", "حريق", "حادث"]
        }
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in emergency_keywords[language])


import datetime
import chainlit as cl
import logging

# Set up logger
logger = logging.getLogger(__name__)

class SessionManager:
    """Simple session manager for handling user sessions"""
    def __init__(self):
        self.sessions = {}
    
    def get_or_create_session(self, session_id: str) -> dict:
        """Get existing session or create new one"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "language": "ar",  # Default to Arabic
                "created_at": datetime.datetime.now(),
                "message_count": 0
            }
        return self.sessions[session_id]

class CarExpertSystem:
    def __init__(self):
        self.current_date = datetime.datetime.strptime("2025-06-06 19:54:22", "%Y-%m-%d %H:%M:%S")
        self.current_user = "andrewamirr"
        self.query_analyzer = QueryAnalyzer()
        self.response_generator = AdvancedResponseGenerator()
        self.session_manager = SessionManager()
        
    async def _send_response(self, response: dict, session_id: str) -> None:
        """Send response to user via chainlit"""
        try:
            # Format the response based on type
            if response.get("type") == "error":
                message = f"❌ {response['message']}"
            elif response.get("type") == "emergency":
                message = f"🚨 {response['message']}"
            else:
                message = response.get("main_content", str(response))
            
            await cl.Message(content=message).send()
            
        except Exception as e:
            logger.error(f"Error sending response: {str(e)}")
            await self._send_system_error(session_id)

    async def _send_system_error(self, session_id: str) -> None:
        """Send system error message"""
        error_messages = {
            "en": "⚠️ System Error: Please try again later or contact support.",
            "ar": "⚠️ خطأ في النظام: يرجى المحاولة لاحقاً أو الاتصال بالدعم."
        }
        
        try:
            session = self.session_manager.get_or_create_session(session_id)
            language = session.get("language", "ar")
            await cl.Message(content=error_messages[language]).send()
        except Exception as e:
            # Fallback error message if even error handling fails
            logger.error(f"Critical error in error handler: {str(e)}")
            await cl.Message(content="⚠️ Critical system error occurred").send()

    async def process_message(self, message: cl.Message) -> None:
        """Process incoming message and generate response."""
        session_id = "default_session"  # Simple session ID
        
        try:
            user_message = message.content.strip()
            
            # Analyze query
            analysis = self.query_analyzer.analyze_query(user_message)
            
            # Get or create session
            session = self.session_manager.get_or_create_session(session_id)
            session["message_count"] += 1
            
            # Generate response using the response generator
            try:
                response_content = self.response_generator.generate_response(analysis)
                
                # Create response dict
                response = {
                    "type": "emergency" if analysis.get("is_emergency") else "normal",
                    "main_content": response_content,
                    "message": response_content
                }
                
                # Send the response
                await self._send_response(response, session_id)
                
            except Exception as e:
                logger.error(f"Error generating response: {str(e)}")
                # Send error response
                error_response = self.response_generator._generate_error_response(e, analysis.get("language", "ar"))
                await self._send_response(error_response, session_id)
                
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            await self._send_system_error(session_id)

    async def _send_formatted_response(self, analysis: dict, session_id: str) -> None:
        """Send formatted response to user."""
        try:
            # Generate proper response using response generator
            response_content = self.response_generator.generate_response(analysis)
            
            if response_content:
                await cl.Message(content=response_content).send()
            else:
                await self._send_default_response(analysis, session_id)
                
        except Exception as e:
            logger.error(f"Error sending formatted response: {str(e)}")
            await self._send_system_error(session_id)

    async def _send_default_response(self, analysis: dict, session_id: str) -> None:
        """Send default response when specific content is not available."""
        default_responses = {
            "ar": "عذراً، لم أفهم سؤالك بشكل كامل. هل يمكنك إعادة صياغته بطريقة أخرى؟",
            "en": "I'm sorry, I didn't fully understand your question. Could you rephrase it?"
        }
        
        language = analysis.get("language", "ar")
        message = default_responses.get(language, default_responses["ar"])
        
        await cl.Message(content=message).send()

# Main message handler


import chainlit as cl
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize car expert system globally (before handlers)
car_expert = None

@cl.on_chat_start
async def start():
    """Initialize the chat session"""
    global car_expert
    try:
        # Initialize the car expert system
        car_expert = CarExpertSystem()
        logger.info("🚗 Car Expert System initialized successfully")
        
        welcome_message = """🚗 **Welcome to the Advanced Car Expert System!**

مرحباً بك في نظام خبير السيارات المتقدم!

**Version:** 2.5.0  
**Last Updated:** 2025-06-06 19:54:22  
**Current User:** andrewamirr

---

**I can help you with:**
• Car diagnostics and troubleshooting
• Maintenance schedules and advice  
• Emergency assistance
• Cost estimates
• Technical support

**يمكنني مساعدتك في:**
• تشخيص أعطال السيارات
• جداول الصيانة والنصائح
• المساعدة في الطوارئ
• تقدير التكاليف
• الدعم الفني

---

**How can I help you today?** / **كيف يمكنني مساعدتك اليوم؟**

*Example: "البطارية مش شغالة" or "Engine making noise"*"""
        
        await cl.Message(content=welcome_message).send()
        
    except Exception as e:
        logger.error(f"Initialization error: {str(e)}")
        error_message = """❌ **System Initialization Failed**

عذراً، فشل في تهيئة النظام. يرجى المحاولة مرة أخرى.

Sorry, system initialization failed. Please try again later."""
        await cl.Message(content=error_message).send()

@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages"""
    global car_expert
    
    try:
        # Check if car_expert is initialized
        if car_expert is None:
            logger.warning("Car expert system not initialized, creating new instance")
            car_expert = CarExpertSystem()
        
        # Process message through car expert system
        await car_expert.process_message(message)
        
    except Exception as e:
        logger.error(f"Error in main handler: {str(e)}")
        
        # Send error message in both languages
        error_message = """❌ **Error Occurred**

حدث خطأ أثناء معالجة رسالتك. يرجى المحاولة مرة أخرى.

An error occurred while processing your message. Please try again.

*If the problem persists, please restart the chat.*"""
        
        await cl.Message(content=error_message).send()

# Additional handler for when user leaves
@cl.on_chat_end
async def end():
    """Handle chat end"""
    logger.info("Chat session ended")

if __name__ == "__main__":
    # This will run when the script is executed directly
    logger.info("🚗 Car Expert System ready to start")
    print("Run with: chainlit run your_filename.py")
class AdvancedResponseGenerator:

    async def _get_main_content(self, query, language):
        # Minimal stub to avoid AttributeError
        return "This is a placeholder main content response."
    def _generate_error_response(self, error: Exception, language: str) -> dict:


        """Generate error response in the appropriate language."""


        error_messages = {


            "en": {


                "general": "Sorry, an error occurred. Please try again.",


                "maintenance": "Unable to process maintenance request.",


                "diagnostic": "Unable to complete diagnostic analysis.",


                "cost": "Unable to calculate costs at this time."


            },


            "ar": {


                "general": "عذراً، حدث خطأ. يرجى المحاولة مرة أخرى.",


                "maintenance": "تعذر معالجة طلب الصيانة.",


                "diagnostic": "تعذر إكمال التحليل التشخيصي.",


                "cost": "تعذر حساب التكاليف في الوقت الحالي."


            }


        }





        error_type = type(error).__name__


        error_category = "general"


        


        if "Maintenance" in error_type:


            error_category = "maintenance"


        elif "Diagnostic" in error_type:


            error_category = "diagnostic"


        elif "Cost" in error_type:


            error_category = "cost"





        return {


            "type": "error",


            "message": error_messages[language][error_category],


            "error_code": error_type,


            "timestamp": self.current_date.strftime("%Y-%m-%d %H:%M:%S")


        }

        self.current_date = datetime.datetime.now()



class CarExpertSystem:


    async def _send_response(self, response: dict, session_id: str) -> None:


        """Send response to the user."""


        try:


            # Format the response based on type


            if response.get("type") == "error":


                message = f"❌ {response['message']}"


            elif response.get("type") == "emergency":


                message = f"🚨 {response['message']}"


            else:


                message = self._format_response(response)





            # Send the message


            await cl.Message(content=message).send()


            


        except Exception as e:


            logger.error(f"Error sending response: {str(e)}")


            await self._send_system_error(session_id)





    def _format_response(self, response: dict) -> str:


        """Format the response for display."""


        language = response.get("language", "en")


        


        if language == "ar":


            if "maintenance_info" in response:
                return response.get("main_content", "") + "\n\n" + \
                       "معلومات الصيانة:\n" + response["maintenance_info"]


            return response.get("main_content", "")


        else:


            if "maintenance_info" in response:


                                return response.get("main_content", "") + "\n\n" + \
                "Maintenance Information:\n" + response["maintenance_info"]


            return response.get("main_content", "")





    async def _send_system_error(self, session_id: str) -> None:


        """Send system error message."""


        error_messages = {


            "en": "⚠️ System Error: Please try again later or contact support.",


            "ar": "⚠️ خطأ في النظام: يرجى المحاولة لاحقاً أو الاتصال بالدعم."


        }


        


        # Get user's language preference from session


        session = self.session_manager.get_or_create_session(session_id)


        language = session.get("language", "en")


        


        await cl.Message(content=error_messages[language]).send()





    async def _send_emergency_notification(self, response: dict, session_id: str) -> None:


        """Send emergency notification."""


        emergency_prefix = "🚨 EMERGENCY / طوارئ 🚨\n\n"


        await cl.Message(content=emergency_prefix + response.get("message", "")).send()





# Update the main message handler


@cl.on_message


async def main(message: cl.Message):


    try:


        user_message = message.content.strip()


        


        if not user_message:


            await cl.Message(content="Please enter your question. / يرجى إدخال سؤالك.").send()


            return





        # Process message through car expert system


        await car_expert.process_message(message)


        


    except Exception as e:


        logger.error(f"Error in main handler: {str(e)}")


        error_message = "An error occurred. Please try again."


        await cl.Message(content=error_message).send()





# Enhanced Multilingual Support System


class MultilingualSystem:


    def __init__(self):


        self.supported_languages = ["en", "ar"]


        self.translations = {


            "emergency_responses": {


                "en": {


                    "critical": "🚨 CRITICAL: Stop driving immediately and call emergency services!",


                    "high": "⚠️ WARNING: Get to a safe location and contact a mechanic.",


                    "medium": "📢 CAUTION: Monitor the situation and seek professional help soon.",


                    "low": "ℹ️ NOTE: Schedule a check-up at your earliest convenience."


                },


                "ar": {


                    "critical": "🚨 خطر: توقف فوراً واتصل بخدمات الطوارئ!",


                    "high": "⚠️ تحذير: توجه لمكان آمن واتصل بميكانيكي.",


                    "medium": "📢 تنبيه: راقب الوضع واطلب مساعدة فني قريباً.",


                    "low": "ℹ️ ملاحظة: احجز موعد فحص في أقرب وقت مناسب."


                }


            },


            "maintenance_terms": {


                "en": {


                    "oil_change": "Oil Change",


                    "brake_service": "Brake Service",


                    "tire_rotation": "Tire Rotation"


                },


                "ar": {


                    "oil_change": "تغيير زيت",


                    "brake_service": "صيانة فرامل",


                    "tire_rotation": "تغيير مكان الكاوتش"


                }


            }


        }


        


    def get_response(self, key: str, subkey: str, language: str) -> str:


        """Get translated response."""


        try:


            return self.translations.get(key, {}).get(language, {}).get(subkey, "")


        except Exception as e:


            logger.error(f"Translation error: {str(e)}")


            return ""





# Enhanced Error Handling System


class ErrorHandler:


    def __init__(self):


        self.error_responses = {


            "en": {


                "diagnostic_error": "Unable to complete diagnosis. Please provide more details or visit a mechanic.",


                "maintenance_error": "Error calculating maintenance schedule. Please check vehicle information.",


                "cost_error": "Unable to calculate costs. Please try again with more specific information.",


                "system_error": "System temporarily unavailable. Please try again later.",


                "invalid_input": "Please provide valid information about your vehicle issue."


            },


            "ar": {



                "diagnostic_error": "تعذر إكمال التشخيص. يرجى تقديم المزيد من التفاصيل أو زيارة ميكانيكي.",


                "maintenance_error": "خطأ في حساب جدول الصيانة. يرجى التحقق من معلومات السيارة.",


                "cost_error": "تعذر حساب التكاليف. يرجى المحاولة مرة أخرى مع معلومات أكثر تحديداً.",


                "system_error": "النظام غير متاح مؤقتاً. يرجى المحاولة لاحقاً.",


                "invalid_input": "يرجى تقديم معلومات صحيحة عن مشكلة سيارتك."


            }


        }


        


    async def handle_error(self, error: Exception, language: str) -> dict:
        logger.error(f"Error occurred: {str(error)}")
        error_type = type(error).__name__
        error_mapping = {
            "DiagnosticError": "diagnostic_error",
            "MaintenanceError": "maintenance_error",
            "CostCalculationError": "cost_error",
            "ValueError": "invalid_input",
            "Exception": "system_error"
        }
        response_key = error_mapping.get(error_type, "system_error")
        return {
            "type": "error",
            "message": self.error_responses[language][response_key]
        }





# User Interaction Flow System


class UserInteractionFlow:


    def __init__(self):


        self.current_date = datetime.strptime("2025-06-06 19:16:36", "%Y-%m-%d %H:%M:%S")


        self.current_user = "andrewamirr"


        self.query_analyzer = QueryAnalyzer()


        self.multilingual = MultilingualSystem()


        self.error_handler = ErrorHandler()


        self.session_data = {}


        


    async def handle_interaction(self, message: str, session_id: str) -> dict:


        """Handle user interaction and maintain conversation flow."""


        try:


            # Initialize or get session


            session = self.session_data.get(session_id, {


                "start_time": self.current_date,


                "language": "en",


                "context": [],


                "vehicle_info": None,


                "last_query": None


            })


            


            # Analyze query


            analysis = self.query_analyzer.analyze_query(message)


            session["language"] = analysis["language"]


            


            # Handle emergency cases first


            if analysis["is_emergency"]:


                return await self._handle_emergency(message, analysis, session)


                


            # Process normal queries


            response = await self._process_query(message, analysis, session)


            


            # Update session context


            session["context"].append({


                "timestamp": self.current_date.strftime("%Y-%m-%d %H:%M:%S"),


                "query": message,


                "response": response


            })


            


            # Trim context if too long


            if len(session["context"]) > 10:


                session["context"] = session["context"][-10:]


                


            self.session_data[session_id] = session


            return response


            


        except Exception as e:


            return await self.error_handler.handle_error(e, session.get("language", "en"))





    async def _handle_emergency(self, message: str, analysis: dict, session: dict) -> dict:


        """Handle emergency situations with priority."""


        language = session["language"]


        emergency_response = {


            "type": "emergency",


            "timestamp": self.current_date.strftime("%Y-%m-%d %H:%M:%S"),


            "urgency": "critical",


            "message": self.multilingual.get_response("emergency_responses", "critical", language),


            "actions": [


                {


                    "type": "contact",


                    "service": "emergency",


                    "number": "122"  # Egypt emergency number


                },


                {


                    "type": "contact",


                    "service": "roadside",


                    "number": "01234567890"  # Example roadside assistance


                }


            ],


            "safety_instructions": self._get_safety_instructions(analysis, language)


        }


        


        # Log emergency situation


        logger.warning(f"Emergency situation detected for user {self.current_user}: {message}")


        return emergency_response





    async def _process_query(self, message: str, analysis: dict, session: dict) -> dict:


        """Process normal queries and generate response."""


        query_type = analysis["query_type"]


        language = session["language"]


        


        processors = {


            "diagnostic": self._handle_diagnostic_query,


            "maintenance": self._handle_maintenance_query,


            "cost": self._handle_cost_query,


            "information": self._handle_information_query


        }


        


        processor = processors.get(query_type, self._handle_general_query)


        return await processor(message, analysis, session)





# External Services Integration


class ExternalServicesManager:


    def __init__(self):


        self.current_date = datetime.strptime("2025-06-06 19:16:36", "%Y-%m-%d %H:%M:%S")


        self.current_user = "andrewamirr"


        self.api_keys = {


            "weather": "xxx",


            "maps": "xxx",


            "parts_database": "xxx"


        }


        


    async def get_nearest_mechanics(self, location: dict) -> list:


        """Find nearest mechanics using Maps API."""


        try:


            # Simulated API call


            mechanics = [


                {


                    "name": "Cairo Auto Care",


                    "distance": "1.2 km",


                    "rating": 4.5,


                    "phone": "01234567890",


                    "open_now": True


                },


                {


                    "name": "Expert Mechanics",


                    "distance": "2.5 km",


                    "rating": 4.3,


                    "phone": "01234567891",


                    "open_now": True


                }


            ]


            return mechanics


        except Exception as e:


            logger.error(f"Error finding mechanics: {str(e)}")


            return []





    async def get_parts_availability(self, part_name: str, vehicle_info: dict) -> dict:


        """Check parts availability in local stores."""


        try:


            # Simulated parts database query


            return {


                "available": True,


                "locations": [


                    {


                        "store": "AutoParts Egypt",


                        "price": 1200,


                        "in_stock": 3,


                        "quality": "OEM"


                    },


                    {


                        "store": "Cairo Parts Center",


                        "price": 900,


                        "in_stock": 5,


                        "quality": "Aftermarket"


                    }


                ],


                "delivery_time": "24 hours",


                "warranty": "1 year"


            }


        except Exception as e:


            logger.error(f"Error checking parts availability: {str(e)}")


            return {"available": False, "error": str(e)}





# Advanced Vehicle Diagnostics System


class VehicleDiagnosticsSystem:


    def __init__(self):


        self.current_date = datetime.strptime("2025-06-06 19:16:36", "%Y-%m-%d %H:%M:%S")


        self.diagnostic_patterns = self._load_diagnostic_patterns()


        


    def _load_diagnostic_patterns(self) -> dict:


        """Load comprehensive diagnostic patterns."""


        return {


            "engine": {


                "starting_issues": {


                    "patterns": [


                        {"symptom": "won't start", "ar": "مش عايزة تدور"},


                        {"symptom": "hard start", "ar": "صعب في التشغيل"},


                        {"symptom": "clicking", "ar": "صوت طقطقة"}


                    ],


                    "causes": [


                        {


                            "component": "battery",


                            "probability": 0.4,


                            "tests": ["voltage test", "load test"],


                            "cost_range": "1400-2500"


                        },


                        {


                            "component": "starter",


                            "probability": 0.3,


                            "tests": ["starter draw test"],


                            "cost_range": "1800-3500"


                        }


                    ]


                }


            }


        }





    async def diagnose(self, symptoms: list, vehicle_info: dict) -> dict:


        """Perform comprehensive vehicle diagnosis."""


        try:


            matched_patterns = self._match_symptoms(symptoms)


            diagnosis = self._analyze_patterns(matched_patterns, vehicle_info)


            return {


                "timestamp": self.current_date.strftime("%Y-%m-%d %H:%M:%S"),


                "diagnosis": diagnosis,


                "confidence": self._calculate_confidence(diagnosis),


                "recommended_actions": self._get_recommendations(diagnosis)


            }


        except Exception as e:


            logger.error(f"Diagnosis error: {str(e)}")


            raise DiagnosticError(str(e))





# Complete Response Generation System


class AdvancedResponseGenerator:


    def __init__(self):


        self.current_date = datetime.strptime("2025-06-06 19:18:22", "%Y-%m-%d %H:%M:%S")


        self.current_user = "andrewamirr"


        self.multilingual = MultilingualSystem()


        self.cost_calculator = CostCalculationSystem()


        self.diagnostics = VehicleDiagnosticsSystem()


        
    def _generate_error_response(self, error: Exception, language: str) -> dict:
        error_messages = {
            "en": {
                "general": "Sorry, an error occurred. Please try again.",
                "maintenance": "Unable to process maintenance request.",
                "diagnostic": "Unable to complete diagnostic analysis.",
                "cost": "Unable to calculate costs at this time."
            },
            "ar": {
                "general": "عذراً، حدث خطأ. يرجى المحاولة مرة أخرى.",
                "maintenance": "تعذر معالجة طلب الصيانة.",
                "diagnostic": "تعذر إكمال التحليل التشخيصي.",
                "cost": "تعذر حساب التكاليف في الوقت الحالي."
            }
        }
        error_type = type(error).__name__
        error_category = "general"
        if "Maintenance" in error_type:
            error_category = "maintenance"
        elif "Diagnostic" in error_type:
            error_category = "diagnostic"
        elif "Cost" in error_type:
            error_category = "cost"
        return {
            "type": "error",
            "message": error_messages[language][error_category],
            "error_code": error_type,
            "timestamp": self.current_date.strftime("%Y-%m-%d %H:%M:%S")
        }

    async def generate_response(self, query: dict, user_profile: dict, 


                              session_data: dict) -> dict:


        """Generate comprehensive, contextual response."""


        try:


            language = query.get("language", "en")


            response_type = query.get("type", "general")


            


            base_response = {


                "timestamp": self.current_date.strftime("%Y-%m-%d %H:%M:%S"),


                "user": self.current_user,


                "language": language,


                "query_type": response_type


            }


            


            # Handle emergency cases


            if query.get("is_emergency", False):


                response = await self._generate_emergency_response(query, language)


            else:


                response = await self._generate_standard_response(query, language)


                


            # Add contextual information


            response.update(await self._add_context(query, user_profile, session_data))


            


            # Add maintenance reminders if relevant


            if self._should_add_maintenance_info(query, user_profile):


                response["maintenance_info"] = await self._get_maintenance_reminders(


                    user_profile, language


                )


                


            # Add cost estimates if applicable


            if "cost" in query.get("requested_info", []):


                response["cost_estimates"] = await self._generate_cost_estimates(


                    query, language


                )


                


            # Add recommendations


            response["recommendations"] = await self._generate_recommendations(


                query, response, language


                )


                


            return {**base_response, **response}


            


        except Exception as e:


            logger.error(f"Response generation error: {str(e)}")


            return self._generate_error_response(e, language)





    async def _generate_standard_response(self, query: dict, language: str) -> dict:


        """Generate standard response with comprehensive information."""


        response = {


            "main_content": await self._get_main_content(query, language),


            "additional_info": await self._get_additional_info(query, language),


            "related_topics": await self._get_related_topics(query, language)


        }


        


        if query.get("needs_diagnosis", False):


            response["diagnostic_info"] = await self.diagnostics.diagnose(


                query.get("symptoms", []),


                query.get("vehicle_info", {})


            )


            


        return response





# Final Integration System


class CarExpertSystem:


    def __init__(self):


        self.current_date = datetime.strptime("2025-06-06 19:18:22", "%Y-%m-%d %H:%M:%S")


        self.current_user = "andrewamirr"


        self.response_generator = AdvancedResponseGenerator()


        self.interaction_flow = UserInteractionFlow()


        self.external_services = ExternalServicesManager()


        self.error_handler = ErrorHandler()


        self.session_manager = SessionManager()


        


    async def process_message(self, message: cl.Message) -> None:


        """Main message processing pipeline."""


        try:


            # Initialize processing


            start_time = self.current_date


            session_id = message.author or "anonymous"


            user_message = message.content.strip()


            


            logger.info(f"Processing message from {session_id}: {user_message}")


            


            # Get or create session


            session = self.session_manager.get_or_create_session(session_id)


            


            # Process message


            try:


                # Analyze query


                analysis = await self.interaction_flow.handle_interaction(


                    user_message, session_id


                )


                


                # Generate response


                response = await self.response_generator.generate_response(


                    analysis,


                    session.get("user_profile", {}),


                    session


                )


                


                # Handle emergency cases


                if analysis.get("is_emergency", False):


                    await self._handle_emergency_case(response, session_id)


                


                # Send response


                await self._send_response(response, session_id)


                


                # Update session


                self.session_manager.update_session(session_id, {


                    "last_interaction": self.current_date,


                    "last_query": user_message,


                    "last_response": response


                })


                


            except Exception as e:


                error_response = await self.error_handler.handle_error(


                    e, session.get("language", "en")


                )


                await self._send_response(error_response, session_id)


                


            finally:


                # Log processing time


                processing_time = (datetime.utcnow() - start_time).total_seconds()


                logger.info(f"Message processed in {processing_time}s")


                


        except Exception as e:


            logger.error(f"Critical error in message processing: {str(e)}")


            await self._send_system_error(session_id)





    async def _handle_emergency_case(self, response: dict, session_id: str) -> None:


        """Handle emergency cases with priority."""


        try:


            # Get nearest mechanics


            mechanics = await self.external_services.get_nearest_mechanics({})


            


            # Update response with emergency information


            response["emergency_contacts"] = mechanics


            


            # Send immediate notification


            await self._send_emergency_notification(response, session_id)


            


        except Exception as e:


            logger.error(f"Error handling emergency: {str(e)}")





# Session Manager for handling user sessions


class SessionManager:


    def __init__(self):


        self.current_date = datetime.strptime("2025-06-06 19:18:22", "%Y-%m-%d %H:%M:%S")


        self.sessions = {}


        self.session_timeout = datetime.timedelta(minutes=30)


        


    def get_or_create_session(self, session_id: str) -> dict:


        """Get existing session or create new one."""


        self._cleanup_expired_sessions()


        


        if session_id not in self.sessions:


            self.sessions[session_id] = {


                "created_at": self.current_date,


                "last_active": self.current_date,


                "language": "en",


                "context": [],


                "user_profile": {}


            }


            


        return self.sessions[session_id]





    def update_session(self, session_id: str, updates: dict) -> None:


        """Update session with new information."""


        if session_id in self.sessions:


            self.sessions[session_id].update(updates)


            self.sessions[session_id]["last_active"] = self.current_date





    def _cleanup_expired_sessions(self) -> None:


        """Remove expired sessions."""


        current_time = self.current_date


        expired = [


            sid for sid, session in self.sessions.items()


            if current_time - session["last_active"] > self.session_timeout


        ]


        for sid in expired:


            del self.sessions[sid]





# Continue with Testing Scenarios and Documentation...


# Testing Scenarios and Quality Assurance System


class TestingSystem:


    def __init__(self):


        self.current_date = datetime.strptime("2025-06-06 19:19:32", "%Y-%m-%d %H:%M:%S")


        self.current_user = "andrewamirr"


        


    async def run_test_scenarios(self) -> dict:


        """Run comprehensive test scenarios."""


        results = {


            "timestamp": self.current_date.strftime("%Y-%m-%d %H:%M:%S"),


            "tester": self.current_user,


            "scenarios_run": 0,


            "passed": 0,


            "failed": 0,


            "results": []


        }


        


        # Test scenarios


        test_cases = [


            # Engine-related queries


            {


                "description": "Engine won't start",


                "input": "My car won't start",


                "expected_type": "emergency",


                "language": "en"


            },


            {



                "description": "مش عايزة تدور",


                "input": "المكنة سخنة",


                "expected_type": "emergency",


                "language": "ar"


            },


            # Maintenance queries


            {


                "description": "Oil change inquiry",


                "input": "When should I change my oil?",


                "expected_type": "maintenance",


                "language": "en"


            },


            # Cost estimation


            {


                "description": "Brake service cost",


                "input": "كم تكلفة تغيير الفرامل",


                "expected_type": "cost",


                "language": "ar"


            }


        ]


        


        for test_case in test_cases:


            try:


                result = await self._run_single_test(test_case)


                results["results"].append(result)


                results["scenarios_run"] += 1


                if result["passed"]:


                    results["passed"] += 1


                else:


                    results["failed"] += 1


            except Exception as e:


                logger.error(f"Test error: {str(e)}")


                results["failed"] += 1


                


        return results





    async def _run_single_test(self, test_case: dict) -> dict:


        """Run a single test case."""


        try:


            # Initialize test components


            car_expert = CarExpertSystem()


            








            # Create test message


            test_message = cl.Message(


                content=test_case["input"],


                author="test_user"


            )


            


            # Process message


            response = await car_expert.process_message(test_message)


            


            # Validate response


            validation = self._validate_response(response, test_case)


            


            return {


                "test_case": test_case["description"],


                "input": test_case["input"],


                "expected_type": test_case["expected_type"],


                "actual_type": response.get("type"),


                "passed": validation["passed"],


                "errors": validation.get("errors", [])


            }


            


        except Exception as e:


            return {


                "test_case": test_case["description"],


                "passed": False,


                "errors": [str(e)]


            }





# Performance Optimization System


class PerformanceOptimizer:


    def __init__(self):


        self.current_date = datetime.strptime("2025-06-06 19:19:32", "%Y-%m-%d %H:%M:%S")


        self.current_user = "andrewamirr"


        self.performance_metrics = {


            "response_times": [],


            "memory_usage": [],


            "error_rates": {}


        }


        


    async def monitor_performance(self, func):


        """Performance monitoring decorator."""


        async def wrapper(*args, **kwargs):


            start_time = datetime.utcnow()


            start_memory = self._get_memory_usage()


            


            try:


                result = await func(*args, **kwargs)


                


                # Calculate metrics


                end_time = datetime.utcnow()


                end_memory = self._get_memory_usage()


                response_time = (end_time - start_time).total_seconds()


                memory_used = end_memory - start_memory


                


                # Update metrics


                self.performance_metrics["response_times"].append(response_time)


                self.performance_metrics["memory_usage"].append(memory_used)


                


                # Trim metrics history


                self._trim_metrics_history()


                


                return result


                


            except Exception as e:


                # Track error rates


                error_type = type(e).__name__


                self.performance_metrics["error_rates"][error_type] = \
                self.performance_metrics["error_rates"].get(error_type, 0) + 1


                raise


                


        return wrapper





    def get_performance_report(self) -> dict:


        """Generate performance report."""


        return {


            "timestamp": self.current_date.strftime("%Y-%m-%d %H:%M:%S"),


            "reporter": self.current_user,


            "metrics": {


                "average_response_time": self._calculate_average(


                    self.performance_metrics["response_times"]


                ),


                "average_memory_usage": self._calculate_average(


                    self.performance_metrics["memory_usage"]


                ),


                "error_rates": self.performance_metrics["error_rates"],


                "total_requests": len(self.performance_metrics["response_times"])


            }


        }





# Deployment Configuration System


class DeploymentConfig:


    def __init__(self):


        self.current_date = datetime.strptime("2025-06-06 19:19:32", "%Y-%m-%d %H:%M:%S")


        self.current_user = "andrewamirr"


        self.config = {


            "environment": "production",


            "version": "2.5.0",


            "last_updated": self.current_date.strftime("%Y-%m-%d %H:%M:%S"),


            "updated_by": self.current_user,


            "features": {


                "multilingual": True,


                "emergency_response": True,


                "cost_estimation": True,


                "diagnostics": True,


                "maintenance_scheduling": True


            },


            "api_endpoints": {


                "main": "/api/v2/car-expert",


                "diagnostics": "/api/v2/diagnostics",


                "maintenance": "/api/v2/maintenance",


                "emergency": "/api/v2/emergency"


            },


            "rate_limits": {


                "normal": 100,  # requests per minute


                "emergency": 200,  # requests per minute


                "burst": 300     # maximum burst


            },


            "timeouts": {


                "response": 30,  # seconds


                "session": 1800, # seconds


                "cache": 3600   # seconds


            }


        }





    def get_config(self, environment: str = "production") -> dict:


        """Get configuration for specified environment."""


        if environment not in ["production", "staging", "development"]:


            raise ValueError(f"Invalid environment: {environment}")


            


        return {


            **self.config,


            "environment": environment,


            "debug": environment != "production"


        }





# Main application setup


@cl.on_chat_start


async def start():


    global car_expert


    try:


        car_expert = CarExpertSystem()


        logger.info("🚗 Car Expert System initialized successfully")


        


        welcome_message = """Welcome to the Advanced Car Expert System! 


        


مرحباً بك في نظام خبير السيارات المتقدم!





Version: 2.5.0


Last Updated: 2025-06-06 19:19:32


        


How can I help you today? / كيف يمكنني مساعدتك اليوم؟"""


        


        await cl.Message(content=welcome_message).send()


        


    except Exception as e:


        logger.error(f"Initialization error: {str(e)}")


        error_message = "System initialization failed. Please try again later."


        await cl.Message(content=error_message).send()





# Main message handler


@cl.on_message


async def main(message: cl.Message):


    try:


        # Process message through car expert system


        await car_expert.process_message(message)


        


    except Exception as e:


        logger.error(f"Error in main handler: {str(e)}")


        error_message = "An error occurred. Please try again."


        await cl.Message(content=error_message).send()





if __name__ == "__main__":


    print(f"🚀 Starting Car Expert System v2.5.0")


    print(f"📅 Current Date: 2025-06-06 19:19:32")


    print(f"👤 Current User: andrewamirr")


    print("🔧 System initialized and ready")


    print("📝 Run with: chainlit run finall.py")