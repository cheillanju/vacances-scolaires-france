# -*- coding: utf-8 -*-
import unittest
from datetime import date
from unittest.mock import patch, MagicMock

from vacances_scolaires_france import SchoolHolidayDates,\
    UnsupportedZoneException,\
    UnsupportedHolidayException,\
    get_records,\
    format_records


URL = 'https://data.education.gouv.fr/api/v2/catalog/datasets/fr-en-calendrier-scolaire/exports/json'

mocked_response_read = bytes("""
        [
            {
                "description": "Vacances d'Hiver",
                "start_date": "2023-02-03T23:00:00+00:00",
                "end_date": "2023-02-06T23:00:00+00:00",
                "annee_scolaire": "2022-2023",
                "zones": "Zone A"
            }
        ]""", 'utf-8')


class TestInit(unittest.TestCase):
    def test_check_zone_OK(self):
        # GIVEN
        holidays = SchoolHolidayDates()
        zone = "Zone A"

        # WHEN
        actual = holidays.check_zone(zone)

        # THEN
        self.assertEqual(True, actual)

    def test_check_zone_KO(self):
        # GIVEN
        holidays = SchoolHolidayDates()
        zone = "Zone not supported"

        # WHEN / THEN
        self.assertRaises(UnsupportedZoneException, holidays.check_zone, zone)

    def test_check_name_OK(self):
        # GIVEN
        holidays = SchoolHolidayDates()
        name = "Vacances d'Hiver"

        # WHEN
        actual = holidays.check_name(name)

        # THEN
        self.assertEqual(True, actual)

    def test_check_name_KO(self):
        # GIVEN
        holidays = SchoolHolidayDates()
        name = "Name not supported"

        # WHEN / THEN
        self.assertRaises(UnsupportedHolidayException, holidays.check_name, name)

    def test_format_records(self):
        # GIVEN
        holidays = SchoolHolidayDates()
        records = [
            {
                "description": "Vacances d'Hiver",
                "start_date": "2023-02-03T23:00:00+00:00",
                "end_date": "2023-02-06T23:00:00+00:00",
                "annee_scolaire": "2022-2023",
                "zones": "Zone A"
            },
            {
                "description": "Vacances de Printemps",
                "start_date": "2023-04-14T22:00:00+00:00",
                "end_date": "2023-04-18T22:00:00+00:00",
                "zones": "Zone B",
                "annee_scolaire": "2022-2023"
            }
        ]
        expected_holidays = {
            date(2023, 2, 4): {
                'date': date(2023, 2, 4),
                'vacances_zone_a': True,
                'vacances_zone_b': False,
                'vacances_zone_c': False,
                'nom_vacances': "Vacances d'Hiver"
            },
            date(2023, 2, 5): {
                'date': date(2023, 2, 5),
                'vacances_zone_a': True,
                'vacances_zone_b': False,
                'vacances_zone_c': False,
                'nom_vacances': "Vacances d'Hiver"
            },
            date(2023, 2, 6): {
                'date': date(2023, 2, 6),
                'vacances_zone_a': True,
                'vacances_zone_b': False,
                'vacances_zone_c': False,
                'nom_vacances': "Vacances d'Hiver"
            },
            date(2023, 4, 15): {
                'date': date(2023, 4, 15),
                'vacances_zone_a': False,
                'vacances_zone_b': True,
                'vacances_zone_c': False,
                'nom_vacances': "Vacances de Printemps"
            },
            date(2023, 4, 16): {
                'date': date(2023, 4, 16),
                'vacances_zone_a': False,
                'vacances_zone_b': True,
                'vacances_zone_c': False,
                'nom_vacances': "Vacances de Printemps"
            },
            date(2023, 4, 17): {
                'date': date(2023, 4, 17),
                'vacances_zone_a': False,
                'vacances_zone_b': True,
                'vacances_zone_c': False,
                'nom_vacances': "Vacances de Printemps"
            },
            date(2023, 4, 18): {
                'date': date(2023, 4, 18),
                'vacances_zone_a': False,
                'vacances_zone_b': True,
                'vacances_zone_c': False,
                'nom_vacances': "Vacances de Printemps"
            }
        }

        # WHEN
        actual_holidays = format_records(records=records)

        # THEN
        self.assertEqual(expected_holidays, actual_holidays)

    @patch('urllib.request.urlopen')
    def test_holidays_for_year(self, mock_holidays_for_year):
        # GIVEN
        holidays = SchoolHolidayDates()
        year = 2023

        mock_holidays_for_year.return_value.__enter__.return_value.status = 200
        mock_holidays_for_year.return_value.__enter__.return_value.read.return_value = mocked_response_read

        expected_params = 'where=start_date%20%3E%3D%202023%20' \
                          'AND%20start_date%20%3C%3D%202023' \
                          '&order_by=start_date'
        expected_url = f'{URL}?{expected_params}'

        # WHEN
        actual_holidays = holidays.holidays_for_year(year=year)

        # THEN
        mock_holidays_for_year.assert_called_with(expected_url)

    @patch('urllib.request.urlopen')
    def test_holidays_for_year_by_name(self, mock_holidays_for_year_by_name):
        # GIVEN
        holidays = SchoolHolidayDates()
        year = 2023
        name = "Vacances d'Hiver"

        mock_holidays_for_year_by_name.return_value.__enter__.return_value.status = 200
        mock_holidays_for_year_by_name.return_value.__enter__.return_value.read.return_value = mocked_response_read

        expected_params = 'where=start_date%20%3E%3D%202023%20' \
                          'AND%20start_date%20%3C%3D%202023%20' \
                          'AND%20description%20%3D%20%22Vacances%20d%27Hiver%22' \
                          '&order_by=start_date'
        expected_url = f'{URL}?{expected_params}'

        # WHEN
        actual_holidays = holidays.holiday_for_year_by_name(year=year, name=name)

        # THEN
        mock_holidays_for_year_by_name.assert_called_with(expected_url)

    @patch('urllib.request.urlopen')
    def test_holidays_for_year_and_zone(self, mock_holidays_for_year_and_zone):
        # GIVEN
        holidays = SchoolHolidayDates()
        year = 2023
        zone = 'Zone A'

        mock_holidays_for_year_and_zone.return_value.__enter__.return_value.status = 200
        mock_holidays_for_year_and_zone.return_value.__enter__.return_value.read.return_value = mocked_response_read

        expected_params = 'where=start_date%20%3E%3D%202023%20' \
                          'AND%20start_date%20%3C%3D%202023%20' \
                          'AND%20zones%20%3D%20%22Zone%20A%22' \
                          '&order_by=start_date'
        expected_url = f'{URL}?{expected_params}'

        # WHEN
        actual_holidays = holidays.holidays_for_year_and_zone(year=year, zone=zone)

        # THEN
        mock_holidays_for_year_and_zone.assert_called_with(expected_url)

    @patch('urllib.request.urlopen')
    def test_holidays_for_year_zone_and_name(self, mock_holidays_for_year_zone_and_name):
        # GIVEN
        holidays = SchoolHolidayDates()
        year = 2023
        zone = 'Zone A'
        name = "Vacances d'Hiver"

        mock_holidays_for_year_zone_and_name.return_value.__enter__.return_value.status = 200
        mock_holidays_for_year_zone_and_name.return_value.__enter__.return_value.read.return_value = mocked_response_read

        expected_params = 'where=start_date%20%3E%3D%202023%20' \
                          'AND%20start_date%20%3C%3D%202023%20' \
                          'AND%20zones%20%3D%20%22Zone%20A%22%20' \
                          'AND%20description%20%3D%20%22Vacances%20d%27Hiver%22' \
                          '&order_by=start_date'
        expected_url = f'{URL}?{expected_params}'

        # WHEN
        actual_holidays = holidays.holidays_for_year_zone_and_name(year=year, zone=zone, name=name)

        # THEN
        mock_holidays_for_year_zone_and_name.assert_called_with(expected_url)

    def test_get_records_with_OK_response(self):
        # GIVEN
        holidays = SchoolHolidayDates()
        mock_http_response = MagicMock(name='HTTPResponse')
        mock_http_response.status = 200
        mock_http_response.read.return_value = mocked_response_read

        expected_records = {
            date(2023, 2, 4): {
                'date': date(2023, 2, 4),
                'vacances_zone_a': True,
                'vacances_zone_b': False,
                'vacances_zone_c': False,
                'nom_vacances': "Vacances d'Hiver"
            },
            date(2023, 2, 5): {
                'date': date(2023, 2, 5),
                'vacances_zone_a': True,
                'vacances_zone_b': False,
                'vacances_zone_c': False,
                'nom_vacances': "Vacances d'Hiver"
            },
            date(2023, 2, 6): {
                'date': date(2023, 2, 6),
                'vacances_zone_a': True,
                'vacances_zone_b': False,
                'vacances_zone_c': False,
                'nom_vacances': "Vacances d'Hiver"
            }
        }

        # WHEN
        actual_records = get_records(mock_http_response)

        # THEN
        self.assertEqual(expected_records, actual_records)

    def test_get_records_with_KO_response(self):
        # GIVEN
        holidays = SchoolHolidayDates()
        mock_http_response = MagicMock(name='HTTPResponse')
        mock_http_response.status = 500

        expected_records = {}

        # WHEN / THEN
        actual_records = get_records(mock_http_response)

        # THEN
        self.assertEqual(expected_records, actual_records)

    @patch('urllib.request.urlopen')
    def test_is_holiday_when_date_is_holiday(self, mock_is_holiday):
        # GIVEN
        holidays = SchoolHolidayDates()
        day = date(2023, 2, 4)

        mock_is_holiday.return_value.__enter__.return_value.status = 200
        mock_is_holiday.return_value.__enter__.return_value.read.return_value = mocked_response_read

        expected = True

        # WHEN
        actual = holidays.is_holiday(day)

        # THEN
        self.assertEqual(expected, actual)

    @patch('urllib.request.urlopen')
    def test_is_holiday_when_date_is_not_holiday(self, mock_is_holiday):
        # GIVEN
        holidays = SchoolHolidayDates()
        day = date(2023, 1, 30)

        mock_is_holiday.return_value.__enter__.return_value.status = 200
        mock_is_holiday.return_value.__enter__.return_value.read.return_value = bytes("[]", 'utf-8')

        expected = False

        # WHEN
        actual = holidays.is_holiday(day)

        # THEN
        self.assertEqual(expected, actual)

    @patch('urllib.request.urlopen')
    def test_is_holiday_for_zone_when_date_is_holiday(self, mock_is_holiday):
        # GIVEN
        holidays = SchoolHolidayDates()
        day = date(2023, 2, 4)
        zone = 'Zone A'

        mock_is_holiday.return_value.__enter__.return_value.status = 200
        mock_is_holiday.return_value.__enter__.return_value.read.return_value = mocked_response_read

        expected = True

        # WHEN
        actual = holidays.is_holiday(day)

        # THEN
        self.assertEqual(expected, actual)

    @patch('urllib.request.urlopen')
    def test_is_holiday_for_zone_when_date_is_not_holiday(self, mock_is_holiday):
        # GIVEN
        holidays = SchoolHolidayDates()
        day = date(2023, 2, 4)
        zone = 'Zone C'

        mock_is_holiday.return_value.__enter__.return_value.status = 200
        mock_is_holiday.return_value.__enter__.return_value.read.return_value = bytes("[]", 'utf-8')

        expected = False

        # WHEN
        actual = holidays.is_holiday(day)

        # THEN
        self.assertEqual(expected, actual)
