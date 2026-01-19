"""
Hikvision qurilma bilan ishlash servisi.
DS-K1T343EFWX va boshqa Hikvision Access Control qurilmalari uchun.
"""

import requests
from requests.auth import HTTPDigestAuth
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from django.conf import settings
from django.utils import timezone
import xml.etree.ElementTree as ET
import json
import logging

logger = logging.getLogger(__name__)


class HikvisionService:
    """Hikvision qurilma bilan ishlash uchun servis."""

    # ISAPI namespace - DS-K1T343EFWX uchun
    NS_ISAPI = 'http://www.isapi.org/ver20/XMLSchema'
    NS_HIK = 'http://www.hikvision.com/ver20/XMLSchema'

    def __init__(self, ip: str, port: int = 80, username: str = 'admin', password: str = 'admin123'):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.base_url = f"http://{ip}:{port}"
        self.auth = HTTPDigestAuth(username, password)
        self.timeout = 30

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: str = None,
        params: dict = None,
        json_format: bool = False
    ) -> requests.Response:
        """HTTP so'rov yuborish."""
        url = f"{self.base_url}{endpoint}"

        if json_format:
            headers = {'Content-Type': 'application/json'}
        elif data:
            headers = {'Content-Type': 'application/xml'}
        else:
            headers = {}

        try:
            response = requests.request(
                method=method,
                url=url,
                auth=self.auth,
                data=data,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Hikvision so'rovda xatolik: {e}")
            raise

    def _find_xml_element(self, root, tag: str):
        """XML elementni topish - har ikkala namespace bilan."""
        # ISAPI namespace bilan
        elem = root.find(f'.//{{{self.NS_ISAPI}}}{tag}')
        if elem is not None:
            return elem
        # Hikvision namespace bilan
        elem = root.find(f'.//{{{self.NS_HIK}}}{tag}')
        if elem is not None:
            return elem
        # Namespace'siz
        elem = root.find(f'.//{tag}')
        return elem

    def _get_xml_text(self, root, tag: str) -> Optional[str]:
        """XML elementdan text olish."""
        elem = self._find_xml_element(root, tag)
        return elem.text if elem is not None else None

    def check_connection(self) -> Dict[str, Any]:
        """Qurilma bilan aloqani tekshirish."""
        try:
            response = self._make_request('GET', '/ISAPI/System/deviceInfo')
            root = ET.fromstring(response.content)

            return {
                'status': 'online',
                'device_name': self._get_xml_text(root, 'deviceName'),
                'model': self._get_xml_text(root, 'model'),
                'serial_number': self._get_xml_text(root, 'serialNumber'),
                'firmware': self._get_xml_text(root, 'firmwareVersion'),
            }
        except Exception as e:
            logger.error(f"Qurilma bilan bog'lanib bo'lmadi: {e}")
            return {
                'status': 'offline',
                'error': str(e)
            }

    def get_user_count(self) -> Dict[str, Any]:
        """Qurilmadagi foydalanuvchilar sonini olish."""
        try:
            response = self._make_request('GET', '/ISAPI/AccessControl/UserInfo/Count')
            data = response.json()
            return {
                'success': True,
                'data': data
            }
        except Exception as e:
            logger.error(f"Foydalanuvchilar sonini olishda xatolik: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_user_list(self) -> Dict[str, Any]:
        """Qurilmadagi barcha foydalanuvchilar ro'yxatini olish (pagination bilan)."""
        all_users = []
        search_position = 0
        max_results_per_request = 30  # Hikvision API 30 ta limit

        try:
            while True:
                search_data = {
                    "UserInfoSearchCond": {
                        "searchID": "1",
                        "searchResultPosition": search_position,
                        "maxResults": max_results_per_request
                    }
                }

                response = self._make_request(
                    'POST',
                    '/ISAPI/AccessControl/UserInfo/Search?format=json',
                    data=json.dumps(search_data),
                    json_format=True
                )
                data = response.json()

                # UserInfo ro'yxatini olish
                user_info_list = data.get('UserInfoSearch', {}).get('UserInfo', [])

                if not user_info_list:
                    break

                # Single user uchun dict bo'lsa, list ga aylantirib olish
                if isinstance(user_info_list, dict):
                    user_info_list = [user_info_list]

                all_users.extend(user_info_list)

                # Agar barcha userlar o'qilsa, to'xta
                total_matches = data.get('UserInfoSearch', {}).get('totalMatches', 0)
                if isinstance(total_matches, str):
                    total_matches = int(total_matches)

                if search_position + max_results_per_request >= total_matches:
                    break

                search_position += max_results_per_request

            return {
                'success': True,
                'data': {
                    'UserInfoSearch': {
                        'totalMatches': len(all_users),
                        'UserInfo': all_users
                    }
                }
            }
        except requests.exceptions.HTTPError as e:
            logger.warning(f"JSON format ishlamadi, XML bilan urinmoqda: {e}")
            return self._get_user_list_xml_paginated()
        except Exception as e:
            logger.error(f"Foydalanuvchilar ro'yxatini olishda xatolik: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _get_user_list_xml_paginated(self) -> Dict[str, Any]:
        """XML format bilan pagination bilan foydalanuvchilar ro'yxatini olish."""
        all_users = []
        search_position = 0
        max_results_per_request = 30

        try:
            while True:
                search_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<UserInfoSearchCond version="2.0" xmlns="{self.NS_ISAPI}">
    <searchID>1</searchID>
    <searchResultPosition>{search_position}</searchResultPosition>
    <maxResults>{max_results_per_request}</maxResults>
</UserInfoSearchCond>"""

                response = self._make_request(
                    'POST',
                    '/ISAPI/AccessControl/UserInfo/Search',
                    data=search_xml
                )

                try:
                    data = response.json()
                except:
                    data = self._parse_xml_users(response.content)

                user_info_list = data.get('UserInfoSearch', {}).get('UserInfo', [])

                if not user_info_list:
                    break

                # Single user uchun dict bo'lsa, list ga aylantirib olish
                if isinstance(user_info_list, dict):
                    user_info_list = [user_info_list]

                all_users.extend(user_info_list)

                total_matches = data.get('UserInfoSearch', {}).get('totalMatches', 0)
                if isinstance(total_matches, str):
                    total_matches = int(total_matches)

                if search_position + max_results_per_request >= total_matches:
                    break

                search_position += max_results_per_request

            return {
                'success': True,
                'data': {
                    'UserInfoSearch': {
                        'totalMatches': len(all_users),
                        'UserInfo': all_users
                    }
                }
            }
        except Exception as e:
            logger.error(f"XML pagination bilan olishda xatolik: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _parse_xml_users(self, xml_content: bytes) -> Dict[str, Any]:
        """XML formatdagi userlarni parse qilish."""
        root = ET.fromstring(xml_content)

        users = []
        # Har ikkala namespace bilan qidirish
        for ns_uri in [self.NS_ISAPI, self.NS_HIK, '']:
            if ns_uri:
                user_elements = root.findall(f'.//{{{ns_uri}}}UserInfo')
            else:
                user_elements = root.findall('.//UserInfo')

            for user in user_elements:
                user_data = {
                    'employeeNo': self._get_xml_text(user, 'employeeNo'),
                    'name': self._get_xml_text(user, 'name'),
                    'userType': self._get_xml_text(user, 'userType'),
                }
                users.append(user_data)

            if users:
                break

        return {
            'UserInfoSearch': {
                'totalMatches': len(users),
                'UserInfo': users
            }
        }

    def get_access_control_events(
        self,
        start_time: datetime = None,
        end_time: datetime = None,
        search_position: int = 0,
        max_results: int = 100
    ) -> Dict[str, Any]:
        """
        Access Control Event log olish.
        Bu hodimlarning kirish/chiqish yozuvlari.
        """
        if not start_time:
            start_time = datetime.now() - timedelta(days=1)
        if not end_time:
            end_time = datetime.now()

        # ISO format with timezone
        start_str = start_time.strftime('%Y-%m-%dT%H:%M:%S+05:00')
        end_str = end_time.strftime('%Y-%m-%dT%H:%M:%S+05:00')

        # JSON format bilan so'rov
        search_data = {
            "AcsEventCond": {
                "searchID": "1",
                "searchResultPosition": search_position,
                "maxResults": max_results,
                "major": 0,
                "minor": 0,
                "startTime": start_str,
                "endTime": end_str
            }
        }

        try:
            response = self._make_request(
                'POST',
                '/ISAPI/AccessControl/AcsEvent?format=json',
                data=json.dumps(search_data),
                json_format=True
            )
            data = response.json()
            return {
                'success': True,
                'data': data
            }
        except requests.exceptions.HTTPError as e:
            # Agar JSON ishlamasa, XML bilan sinash
            logger.warning(f"JSON format ishlamadi, XML bilan urinmoqda: {e}")
            return self._get_events_xml(start_str, end_str, search_position, max_results)
        except Exception as e:
            logger.error(f"Event log olishda xatolik: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _get_events_xml(self, start_str: str, end_str: str, search_position: int, max_results: int) -> Dict[str, Any]:
        """XML format bilan eventlarni olish."""
        search_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<AcsEventCond version="2.0" xmlns="{self.NS_ISAPI}">
    <searchID>1</searchID>
    <searchResultPosition>{search_position}</searchResultPosition>
    <maxResults>{max_results}</maxResults>
    <major>0</major>
    <minor>0</minor>
    <startTime>{start_str}</startTime>
    <endTime>{end_str}</endTime>
</AcsEventCond>"""

        try:
            response = self._make_request(
                'POST',
                '/ISAPI/AccessControl/AcsEvent',
                data=search_xml
            )

            try:
                data = response.json()
            except:
                data = self._parse_xml_events(response.content)

            return {
                'success': True,
                'data': data
            }
        except Exception as e:
            logger.error(f"XML bilan event olishda xatolik: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _parse_xml_events(self, xml_content: bytes) -> Dict[str, Any]:
        """XML formatdagi eventlarni parse qilish."""
        root = ET.fromstring(xml_content)

        events = []
        # Har ikkala namespace bilan qidirish
        for ns_uri in [self.NS_ISAPI, self.NS_HIK, '']:
            if ns_uri:
                event_elements = root.findall(f'.//{{{ns_uri}}}AcsEvent')
            else:
                event_elements = root.findall('.//AcsEvent')

            for event in event_elements:
                event_data = {
                    'time': self._get_xml_text(event, 'time'),
                    'employeeNoString': self._get_xml_text(event, 'employeeNoString'),
                    'name': self._get_xml_text(event, 'name'),
                    'cardNo': self._get_xml_text(event, 'cardNo'),
                    'major': self._get_xml_text(event, 'major'),
                    'minor': self._get_xml_text(event, 'minor'),
                    'eventType': self._get_xml_text(event, 'eventType'),
                    'currentVerifyMode': self._get_xml_text(event, 'currentVerifyMode'),
                    'serialNo': self._get_xml_text(event, 'serialNo'),
                }
                events.append(event_data)

            if events:
                break

        total_matches = self._get_xml_text(root, 'totalMatches')

        return {
            'AcsEventSearchResult': {
                'totalMatches': int(total_matches) if total_matches else len(events),
                'MatchList': events
            }
        }

    def sync_attendance_events(
        self,
        start_time: datetime = None,
        end_time: datetime = None
    ) -> List[Dict[str, Any]]:
        """
        Barcha attendance eventlarni sinxronlashtirish.
        Pagination bilan ishlaydi.
        """
        all_events = []
        position = 0
        batch_size = 100

        while True:
            result = self.get_access_control_events(
                start_time=start_time,
                end_time=end_time,
                search_position=position,
                max_results=batch_size
            )

            if not result['success']:
                logger.error(f"Event olishda xatolik: {result.get('error')}")
                break

            data = result['data']

            # JSON strukturaga qarab parse qilish
            events = []
            if 'AcsEventSearchResult' in data:
                match_list = data['AcsEventSearchResult'].get('MatchList', [])
                if isinstance(match_list, dict):
                    events = match_list.get('AcsEvent', [])
                    if isinstance(events, dict):
                        events = [events]
                elif isinstance(match_list, list):
                    events = match_list
            elif 'AcsEvent' in data:
                acs_event = data['AcsEvent']
                if isinstance(acs_event, dict) and 'InfoList' in acs_event:
                    events = acs_event.get('InfoList', [])
                else:
                    events = acs_event
                if isinstance(events, dict):
                    events = [events]

            if not events:
                break

            all_events.extend(events)
            position += batch_size

            # Agar barcha natijalar olindi bo'lsa
            total = data.get('AcsEventSearchResult', {}).get('totalMatches', 0)
            if not total and isinstance(data.get('AcsEvent'), dict):
                total = data['AcsEvent'].get('totalMatches') or data['AcsEvent'].get('numOfMatches')
            if isinstance(total, str):
                total = int(total)
            if total and position >= total:
                break
            if not total and len(events) < batch_size:
                break

        return all_events


def get_hikvision_service(device=None) -> HikvisionService:
    """
    HikvisionService instance olish.
    device parametri berilmasa, settings dan oladi.
    """
    if device:
        return HikvisionService(
            ip=device.ip_address,
            port=device.port,
            username=device.username,
            password=device.password
        )

    config = settings.HIKVISION_DEVICE
    return HikvisionService(
        ip=config['IP'],
        port=int(config['PORT']),
        username=config['USERNAME'],
        password=config['PASSWORD']
    )
