"""
Hikvision qurilmadagi guruhlarni tekshirish.
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


def get_user_groups():
    """Foydalanuvchi guruhlarini olish."""
    print("\n" + "="*70)
    print("   FOYDALANUVCHI GURUHLARI")
    print("="*70)

    try:
        # UserGroup endpoint
        response = requests.get(
            f"{BASE_URL}/ISAPI/AccessControl/UserGroup?format=json",
            auth=AUTH,
            timeout=10
        )
        print(f"\nUserGroup Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return data
        else:
            print(f"Response: {response.text[:500]}")
    except Exception as e:
        print(f"Xatolik: {e}")

    # Boshqa endpoint
    try:
        response = requests.get(
            f"{BASE_URL}/ISAPI/AccessControl/UserGroup/Count?format=json",
            auth=AUTH,
            timeout=10
        )
        print(f"\nUserGroup Count Status: {response.status_code}")
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Count xatolik: {e}")

    return None


def search_user_groups():
    """Guruhlarni qidirish."""
    print("\n" + "="*70)
    print("   GURUHLARNI QIDIRISH")
    print("="*70)

    search_data = {
        "UserGroupSearchCond": {
            "searchID": "1",
            "searchResultPosition": 0,
            "maxResults": 100
        }
    }

    try:
        response = requests.post(
            f"{BASE_URL}/ISAPI/AccessControl/UserGroup/Search?format=json",
            auth=AUTH,
            json=search_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        print(f"\nStatus: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return data
        else:
            print(f"Response: {response.text[:500]}")
    except Exception as e:
        print(f"Xatolik: {e}")

    return None


def get_department_groups():
    """Bo'limlarni olish."""
    print("\n" + "="*70)
    print("   BO'LIMLAR (DEPARTMENTS)")
    print("="*70)

    try:
        response = requests.get(
            f"{BASE_URL}/ISAPI/AccessControl/departments?format=json",
            auth=AUTH,
            timeout=10
        )
        print(f"\nDepartments Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return data
        else:
            print(f"Response: {response.text[:500]}")
    except Exception as e:
        print(f"Xatolik: {e}")

    return None


def get_users_with_groups():
    """Foydalanuvchilarni guruh ma'lumotlari bilan olish."""
    print("\n" + "="*70)
    print("   FOYDALANUVCHILAR GURUH MA'LUMOTLARI BILAN")
    print("="*70)

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
        if response.status_code == 200:
            data = response.json()
            if 'UserInfoSearch' in data:
                users = data['UserInfoSearch'].get('UserInfo', [])
                print(f"\nTopildi: {len(users)} foydalanuvchi")
                for i, user in enumerate(users[:10]):
                    print(f"\n--- Foydalanuvchi {i+1} ---")
                    print(f"  employeeNo: {user.get('employeeNo')}")
                    print(f"  name: {user.get('name')}")
                    print(f"  belongGroup: {user.get('belongGroup')}")
                    print(f"  groupId: {user.get('groupId')}")
                    print(f"  userType: {user.get('userType')}")
                    # Boshqa mumkin bo'lgan maydonlar
                    for key in ['department', 'departmentNo', 'orgNo', 'organization']:
                        if key in user:
                            print(f"  {key}: {user.get(key)}")
    except Exception as e:
        print(f"Xatolik: {e}")


def get_organization_info():
    """Tashkilot ma'lumotlarini olish."""
    print("\n" + "="*70)
    print("   TASHKILOT MA'LUMOTLARI")
    print("="*70)

    endpoints = [
        "/ISAPI/AccessControl/Organization",
        "/ISAPI/AccessControl/Organization/Search",
        "/ISAPI/AccessControl/AcsOrganization",
        "/ISAPI/System/Organization",
    ]

    for endpoint in endpoints:
        try:
            response = requests.get(
                f"{BASE_URL}{endpoint}?format=json",
                auth=AUTH,
                timeout=10
            )
            print(f"\n{endpoint}: {response.status_code}")
            if response.status_code == 200:
                print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"  Xatolik: {e}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("   HIKVISION GURUHLAR/BO'LIMLAR TEKSHIRUVI")
    print("="*70)

    get_user_groups()
    search_user_groups()
    get_department_groups()
    get_users_with_groups()
    get_organization_info()

    print("\n" + "="*70)
    print("   TEKSHIRUV TUGADI")
    print("="*70 + "\n")
