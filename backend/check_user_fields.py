"""
Hikvision qurilmadan foydalanuvchi ma'lumotlarini to'liq ko'rish.
"""

import requests
from requests.auth import HTTPDigestAuth
import json

# Qurilma sozlamalari
IP = "192.168.1.252"
PORT = 80
USERNAME = "admin"
PASSWORD = "Baccardi2020"

BASE_URL = f"http://{IP}:{PORT}"
AUTH = HTTPDigestAuth(USERNAME, PASSWORD)


def get_user_count():
    """Foydalanuvchilar soni."""
    print("\n" + "="*70)
    print("   FOYDALANUVCHILAR SONI")
    print("="*70)

    try:
        response = requests.get(
            f"{BASE_URL}/ISAPI/AccessControl/UserInfo/Count",
            auth=AUTH,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return data
    except Exception as e:
        print(f"Xatolik: {e}")
    return None


def get_user_list_full():
    """To'liq foydalanuvchi ma'lumotlari."""
    print("\n" + "="*70)
    print("   BITTA FOYDALANUVCHI TO'LIQ MA'LUMOTLARI")
    print("="*70)

    search_data = {
        "UserInfoSearchCond": {
            "searchID": "1",
            "searchResultPosition": 0,
            "maxResults": 5  # Faqat 5 ta ko'ramiz
        }
    }

    try:
        response = requests.post(
            f"{BASE_URL}/ISAPI/AccessControl/UserInfo/Search?format=json",
            auth=AUTH,
            json=search_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()

            # Barcha maydonlarni ko'rsatish
            if 'UserInfoSearch' in data:
                users = data['UserInfoSearch'].get('UserInfo', [])
                if users:
                    print("\n--- BIRINCHI FOYDALANUVCHI BARCHA MAYDONLARI ---")
                    print(json.dumps(users[0], indent=2, ensure_ascii=False))

                    print("\n--- MAVJUD MAYDONLAR RO'YXATI ---")
                    for key in users[0].keys():
                        value = users[0][key]
                        print(f"  {key}: {type(value).__name__} = {value}")

            return data
    except Exception as e:
        print(f"Xatolik: {e}")
    return None


def get_user_capabilities():
    """Qurilma qanday maydonlarni qo'llab-quvvatlashini tekshirish."""
    print("\n" + "="*70)
    print("   USERINFO CAPABILITIES (Qo'llab-quvvatlanadigan maydonlar)")
    print("="*70)

    try:
        response = requests.get(
            f"{BASE_URL}/ISAPI/AccessControl/UserInfo/capabilities?format=json",
            auth=AUTH,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return data
        else:
            print(f"Status: {response.status_code}")
            print(response.text[:500])
    except Exception as e:
        print(f"Xatolik: {e}")
    return None


def get_card_info():
    """Karta ma'lumotlari."""
    print("\n" + "="*70)
    print("   KARTA MA'LUMOTLARI")
    print("="*70)

    search_data = {
        "CardInfoSearchCond": {
            "searchID": "1",
            "searchResultPosition": 0,
            "maxResults": 5
        }
    }

    try:
        response = requests.post(
            f"{BASE_URL}/ISAPI/AccessControl/CardInfo/Search?format=json",
            auth=AUTH,
            json=search_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return data
        else:
            print(f"Status: {response.status_code}")
    except Exception as e:
        print(f"Xatolik: {e}")
    return None


def get_finger_print_count():
    """Barmoq izi ma'lumotlari."""
    print("\n" + "="*70)
    print("   BARMOQ IZI MA'LUMOTLARI")
    print("="*70)

    try:
        response = requests.get(
            f"{BASE_URL}/ISAPI/AccessControl/FingerPrintCfg/capabilities?format=json",
            auth=AUTH,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"Status: {response.status_code}")
    except Exception as e:
        print(f"Xatolik: {e}")


def get_face_info():
    """Yuz ma'lumotlari."""
    print("\n" + "="*70)
    print("   YUZ (FACE) MA'LUMOTLARI")
    print("="*70)

    search_data = {
        "FaceInfoSearchCond": {
            "searchID": "1",
            "searchResultPosition": 0,
            "maxResults": 3
        }
    }

    try:
        response = requests.post(
            f"{BASE_URL}/ISAPI/Intelligent/FDLib/FDSearch?format=json",
            auth=AUTH,
            json=search_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"Status: {response.status_code}")
            # Boshqa endpoint sinash
            response2 = requests.get(
                f"{BASE_URL}/ISAPI/AccessControl/FaceDataRecord/capabilities?format=json",
                auth=AUTH,
                timeout=10
            )
            if response2.status_code == 200:
                print("\nFaceDataRecord capabilities:")
                print(json.dumps(response2.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Xatolik: {e}")


def get_single_user_detail(employee_no):
    """Bitta foydalanuvchining to'liq ma'lumotlari."""
    print(f"\n" + "="*70)
    print(f"   FOYDALANUVCHI {employee_no} TO'LIQ MA'LUMOTLARI")
    print("="*70)

    search_data = {
        "UserInfoSearchCond": {
            "searchID": "1",
            "searchResultPosition": 0,
            "maxResults": 1,
            "EmployeeNoList": [{"employeeNo": employee_no}]
        }
    }

    try:
        response = requests.post(
            f"{BASE_URL}/ISAPI/AccessControl/UserInfo/Search?format=json",
            auth=AUTH,
            json=search_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"Status: {response.status_code}")
    except Exception as e:
        print(f"Xatolik: {e}")


def get_event_sample():
    """Bitta event namunasi."""
    print("\n" + "="*70)
    print("   EVENT (DAVOMAT) NAMUNASI")
    print("="*70)

    from datetime import datetime, timedelta
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)

    search_data = {
        "AcsEventCond": {
            "searchID": "1",
            "searchResultPosition": 0,
            "maxResults": 3,
            "major": 0,
            "minor": 0,
            "startTime": start_time.strftime('%Y-%m-%dT%H:%M:%S+05:00'),
            "endTime": end_time.strftime('%Y-%m-%dT%H:%M:%S+05:00')
        }
    }

    try:
        response = requests.post(
            f"{BASE_URL}/ISAPI/AccessControl/AcsEvent?format=json",
            auth=AUTH,
            json=search_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            if 'AcsEventSearchResult' in data:
                events = data['AcsEventSearchResult'].get('MatchList', [])
                if events:
                    print("\n--- BIRINCHI EVENT BARCHA MAYDONLARI ---")
                    if isinstance(events, list) and len(events) > 0:
                        print(json.dumps(events[0], indent=2, ensure_ascii=False))
                    elif isinstance(events, dict):
                        print(json.dumps(events, indent=2, ensure_ascii=False))
        else:
            print(f"Status: {response.status_code}")
    except Exception as e:
        print(f"Xatolik: {e}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("   HIKVISION DS-K1T343EFWX MA'LUMOTLAR TAHLILI")
    print("="*70)

    # 1. Foydalanuvchilar soni
    count_data = get_user_count()

    # 2. To'liq foydalanuvchi ma'lumotlari
    user_data = get_user_list_full()

    # 3. Capabilities
    get_user_capabilities()

    # 4. Karta ma'lumotlari
    get_card_info()

    # 5. Barmoq izi
    get_finger_print_count()

    # 6. Yuz ma'lumotlari
    get_face_info()

    # 7. Event namunasi
    get_event_sample()

    print("\n" + "="*70)
    print("   TAHLIL TUGADI")
    print("="*70 + "\n")
