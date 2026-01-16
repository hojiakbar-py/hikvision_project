"""
Hikvision qurilmani test qilish skripti.
Ishga tushirish: python test_device.py
"""

import requests
from requests.auth import HTTPDigestAuth
import json
import sys

# Qurilma sozlamalari
IP = "192.168.1.252"
PORT = 80
USERNAME = "admin"
PASSWORD = "Baccardi2020"

BASE_URL = f"http://{IP}:{PORT}"
AUTH = HTTPDigestAuth(USERNAME, PASSWORD)
NS_ISAPI = "http://www.isapi.org/ver20/XMLSchema"


def test_connection():
    """Qurilma bilan ulanishni tekshirish."""
    print(f"\n{'='*60}")
    print(f"   HIKVISION DS-K1T343EFWX TEST")
    print(f"{'='*60}")
    print(f"\nQurilma: {IP}:{PORT}")
    print(f"Login: {USERNAME}")

    try:
        response = requests.get(
            f"{BASE_URL}/ISAPI/System/deviceInfo",
            auth=AUTH,
            timeout=10
        )
        if response.status_code == 200:
            print(f"\n[OK] Qurilma bilan ulanish muvaffaqiyatli!")
            print(f"    Model: DS-K1T343EFWX")
            return True
        else:
            print(f"\n[ERROR] Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"\n[ERROR] Ulanib bo'lmadi: {e}")
        return False


def test_user_count():
    """Foydalanuvchilar sonini olish."""
    print(f"\n{'='*60}")
    print("   FOYDALANUVCHILAR SONI")
    print(f"{'='*60}")

    try:
        response = requests.get(
            f"{BASE_URL}/ISAPI/AccessControl/UserInfo/Count",
            auth=AUTH,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"\n[OK] Foydalanuvchilar soni:")
            print(f"    Jami: {data['UserInfoCount']['userNumber']}")
            print(f"    Yuz bilan: {data['UserInfoCount']['bindFaceUserNumber']}")
            print(f"    Barmoq izi: {data['UserInfoCount']['bindFingerprintUserNumber']}")
            print(f"    Karta bilan: {data['UserInfoCount']['bindCardUserNumber']}")
            return True
    except Exception as e:
        print(f"\n[ERROR] {e}")
    return False


def test_user_list_json():
    """JSON format bilan foydalanuvchilar ro'yxati."""
    print(f"\n{'='*60}")
    print("   FOYDALANUVCHILAR RO'YXATI (JSON)")
    print(f"{'='*60}")

    search_data = {
        "UserInfoSearchCond": {
            "searchID": "1",
            "searchResultPosition": 0,
            "maxResults": 10
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
        print(f"\n    Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"    [OK] JSON ishlaydi!")
            if 'UserInfoSearch' in data:
                users = data['UserInfoSearch'].get('UserInfo', [])
                print(f"    Topildi: {len(users)} foydalanuvchi")
                for i, user in enumerate(users[:5]):
                    print(f"      {i+1}. {user.get('employeeNo')} - {user.get('name')}")
            return True
        else:
            print(f"    Response: {response.text[:200]}")
    except Exception as e:
        print(f"\n    [ERROR] {e}")
    return False


def test_user_list_xml():
    """XML format bilan foydalanuvchilar ro'yxati."""
    print(f"\n{'='*60}")
    print("   FOYDALANUVCHILAR RO'YXATI (XML)")
    print(f"{'='*60}")

    search_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<UserInfoSearchCond version="2.0" xmlns="{NS_ISAPI}">
    <searchID>1</searchID>
    <searchResultPosition>0</searchResultPosition>
    <maxResults>10</maxResults>
</UserInfoSearchCond>"""

    try:
        response = requests.post(
            f"{BASE_URL}/ISAPI/AccessControl/UserInfo/Search",
            auth=AUTH,
            data=search_xml,
            headers={"Content-Type": "application/xml"},
            timeout=15
        )
        print(f"\n    Status: {response.status_code}")
        if response.status_code == 200:
            print(f"    [OK] XML ishlaydi!")
            print(f"    Response (first 500 chars):")
            print(f"    {response.text[:500]}")
            return True
        else:
            print(f"    Response: {response.text[:200]}")
    except Exception as e:
        print(f"\n    [ERROR] {e}")
    return False


def test_events_json():
    """JSON format bilan eventlar."""
    print(f"\n{'='*60}")
    print("   ACCESS CONTROL EVENTS (JSON)")
    print(f"{'='*60}")

    from datetime import datetime, timedelta
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)

    search_data = {
        "AcsEventCond": {
            "searchID": "1",
            "searchResultPosition": 0,
            "maxResults": 10,
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
        print(f"\n    Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"    [OK] JSON ishlaydi!")
            if 'AcsEventSearchResult' in data:
                total = data['AcsEventSearchResult'].get('totalMatches', 0)
                print(f"    Jami eventlar: {total}")
                events = data['AcsEventSearchResult'].get('MatchList', [])
                if isinstance(events, list):
                    for i, event in enumerate(events[:5]):
                        print(f"      {i+1}. {event.get('time')} - {event.get('name')} ({event.get('employeeNoString')})")
            return True
        else:
            print(f"    Response: {response.text[:300]}")
    except Exception as e:
        print(f"\n    [ERROR] {e}")
    return False


def test_events_xml():
    """XML format bilan eventlar."""
    print(f"\n{'='*60}")
    print("   ACCESS CONTROL EVENTS (XML)")
    print(f"{'='*60}")

    from datetime import datetime, timedelta
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)

    search_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<AcsEventCond version="2.0" xmlns="{NS_ISAPI}">
    <searchID>1</searchID>
    <searchResultPosition>0</searchResultPosition>
    <maxResults>10</maxResults>
    <major>0</major>
    <minor>0</minor>
    <startTime>{start_time.strftime('%Y-%m-%dT%H:%M:%S+05:00')}</startTime>
    <endTime>{end_time.strftime('%Y-%m-%dT%H:%M:%S+05:00')}</endTime>
</AcsEventCond>"""

    try:
        response = requests.post(
            f"{BASE_URL}/ISAPI/AccessControl/AcsEvent",
            auth=AUTH,
            data=search_xml,
            headers={"Content-Type": "application/xml"},
            timeout=15
        )
        print(f"\n    Status: {response.status_code}")
        if response.status_code == 200:
            print(f"    [OK] XML ishlaydi!")
            print(f"    Response (first 500 chars):")
            print(f"    {response.text[:500]}")
            return True
        else:
            print(f"    Response: {response.text[:300]}")
    except Exception as e:
        print(f"\n    [ERROR] {e}")
    return False


if __name__ == "__main__":
    if test_connection():
        test_user_count()

        # JSON va XML ni sinab ko'rish
        json_users = test_user_list_json()
        if not json_users:
            test_user_list_xml()

        json_events = test_events_json()
        if not json_events:
            test_events_xml()

    print(f"\n{'='*60}")
    print("   TEST TUGADI")
    print(f"{'='*60}\n")
