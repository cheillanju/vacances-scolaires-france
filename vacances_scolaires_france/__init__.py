# -*- coding: utf-8 -*-
import datetime
import http.client
import json
import urllib.parse
import urllib.request
from typing import List, Dict

import pytz

from vacances_scolaires_france.settings import API_URL


class UnsupportedYearException(Exception):
    pass


class UnsupportedZoneException(Exception):
    pass


class UnsupportedHolidayException(Exception):
    pass


def format_records(records: List[Dict] = None) -> Dict:
    france_timezone = pytz.timezone("Europe/Paris")
    holidays = {}
    for record in records:
        start_date = datetime.datetime.fromisoformat(record['start_date']).astimezone(france_timezone).date()
        end_date = datetime.datetime.fromisoformat(record['end_date']).astimezone(france_timezone).date()
        nb_days = (end_date - start_date).days
        for day in range(nb_days):
            date_holidays = start_date + datetime.timedelta(days=day)
            holidays[date_holidays] = {
                'date': date_holidays,
                'vacances_zone_a': record['zones'] == 'Zone A',
                'vacances_zone_b': record['zones'] == 'Zone B',
                'vacances_zone_c': record['zones'] == 'Zone C',
                'nom_vacances': record['description'],
            }
    return holidays


def get_records(response: http.client.HTTPResponse = None) -> Dict:
    if response.status == 200:
        response_json = json.loads(response.read().decode('utf-8'))
        return format_records(response_json)
    else:
        return {}


class SchoolHolidayDates:
    SUPPORTED_ZONES = ["Zone A", "Zone B", " Zone C"]
    SUPPORTED_HOLIDAY_NAMES = [
        "Vacances de Noël",
        "Vacances d'Hiver",
        "Vacances de Printemps",
        "Vacances d'Été",
        "Vacances de la Toussaint",
        "Pont de l'Ascension",
    ]

    def __init__(self):
        super(SchoolHolidayDates, self).__init__()

    def check_zone(self, zone: str) -> bool:
        if zone not in self.SUPPORTED_ZONES:
            raise UnsupportedZoneException(f"Unsupported zone: '{zone}'. Must be in {self.SUPPORTED_ZONES}")
        return True

    def check_name(self, name: str) -> bool:
        if name not in self.SUPPORTED_HOLIDAY_NAMES:
            raise UnsupportedHolidayException(
                f"Unknown holiday name: '{name}'. Must be in {self.SUPPORTED_HOLIDAY_NAMES}")
        return True

    def get_holidays_for_params(self, params):
        with urllib.request.urlopen(
                f'{API_URL}?{urllib.parse.urlencode(params, quote_via=urllib.parse.quote)}') as response:
            return get_records(response)

    def is_holiday(self, date: datetime.date) -> bool:
        if not type(date) is datetime.date:
            raise ValueError("date should be a datetime.date")

        date_str = datetime.date.strftime(date, '%Y-%m-%d')
        params = {
            'where': f'start_date <= "{date_str}" AND end_date >= "{date_str}" AND zones IN ("Zone A", "Zone B", "Zone C")',
            'order_by': 'start_date'
        }
        with urllib.request.urlopen(
                f'{API_URL}?{urllib.parse.urlencode(params, quote_via=urllib.parse.quote)}') as response:
            return len(get_records(response)) > 0

    def is_holiday_for_zone(self, date: datetime.date, zone: str) -> bool:
        if not type(date) is datetime.date:
            raise ValueError("date should be a datetime.date")

        date_str = datetime.date.strftime(date, '%Y-%m-%d')
        params = {
            'where': f'start_date <= "{date_str}" AND end_date >= "{date_str}" AND zones = "{zone}"',
            'order_by': 'start_date'
        }
        with urllib.request.urlopen(
                f'{API_URL}?{urllib.parse.urlencode(params, quote_via=urllib.parse.quote)}') as response:
            return len(get_records(response)) > 0

    def holidays_for_year(self, year: int) -> Dict:
        params = {
            'where': f'start_date >= {year} AND start_date <= {year}',
            'order_by': 'start_date'
        }
        return self.get_holidays_for_params(params)

    def holiday_for_year_by_name(self, year: int, name: str) -> Dict:
        self.check_name(name)
        params = {
            'where': f'start_date >= {year} AND start_date <= {year} AND description = "{name}"',
            'order_by': 'start_date'
        }
        return self.get_holidays_for_params(params)

    def holidays_for_year_and_zone(self, year: int, zone: str) -> Dict:
        self.check_zone(zone)
        params = {
            'where': f'start_date >= {year} AND start_date <= {year} AND zones = "{zone}"',
            'order_by': 'start_date'
        }
        return self.get_holidays_for_params(params)

    def holidays_for_year_zone_and_name(self, year: int, zone: str, name: str) -> Dict:
        self.check_zone(zone)
        self.check_name(name)
        params = {
            'where': f'start_date >= {year} AND start_date <= {year} AND zones = "{zone}" AND description = "{name}"',
            'order_by': 'start_date'
        }
        return self.get_holidays_for_params(params)
